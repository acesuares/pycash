#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#
#       Copyright 2010-2016 Mike Evans <mikee@millstreamcomputing.co.uk>
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

Dump the DB with:
mysqldump kicad_sqlparts -p --routines> kicad_sqlparts.sql


Convert confirmation mail from Rapid Electronics (UK) to CSV.
Saved mails from claws are base64 encoded but the mail can be saves as plain text.
Alternatively, in claws-mail create an action to pipe this through this script.

rapid_mail2gnucash.py  %p %u

This will pop up a prompt for your invoice number.
The CSV can then be imported in the usual way.



The csv output data should look like:
line number,product code,quantity,availability,product description,unit price,discounts,line total,delivery,sub total,vat,grand total

Obviously the various hard coded paths here should be changed.

'''

import sys
import os
from os.path import expanduser
import csv
import base64
from datetime import datetime
#from bs4 import BeautifulSoup
from decimal import Decimal
import logging
import codecs

#logger = logging.getLogger("librarian")
logging.basicConfig(level=logging.DEBUG, format='%(module)s: LINE %(lineno)d: %(levelname)s: %(message)s')
#logging.disable(logging.INFO)
DEBUG = logging.debug
INFO = logging.info

HOME = expanduser("~")
VENDOR_ID ="000013" # Obviously this needs to match your vendor ID for this supplier
INV_ID = None

try:
    INFILE=sys.argv[1]
except:
    print ("No input files specified.")
    print ("Useage: Useage: rapid2gnucash.py  \"SAVED_RAPID_CONFIRMATION_MAIL\" \"ORDER_NUMBER\" \"OPT_ACCOUNT\"")
    quit(1)
try:
    INV_ID=sys.argv[2]
except:
    print ("No order number specified. Using the order number in the e-mail.")
    print ("Useage: Useage: rapid2gnucash.py  \"SAVED_RAPID_CONFIRMATION_MAIL\" \"ORDER_NUMBER\" \"OPT_ACCOUT\"")
    INV_ID="foo" # Just prevent None type errors later.
try:
    ACCOUNT=sys.argv[3]
except:
    ACCOUNT="Business Expenses" # Default if absent on the command line.  Edit to suit your account tree


OUTFILE = INFILE + ".csv"
# Load the file
infile = open(INFILE, 'rb')
data = infile.readlines()
#soup = BeautifulSoup(infile)
infile.close()
#print(data)
encoded = ""
start64 = False
print ("")
csv_data = []
csv_data.append("line_num,part_num,desc,unit_price,qty,amnt")
linenum = 1
date_opened=""
my_ref = None
ord_num = None
ord_date = None


data = iter(data)
header = True
items = False
footer = False
desc = ''
running_total = Decimal(0.0)
for line in data:
    if header:
        # Do the header stuff
        if line.startswith('Your Rapid web order number is'):
            ord_num = line.split('Your Rapid web order number is')[1].strip()
            DEBUG(ord_num)
        if line.startswith('Your Reference:'):
            line = next(data)
            tmp = line.strip()
            if tmp == '': # Then use the supplied INV_ID
                pass
            else:
                INV_ID = tmp
            DEBUG("INV_ID = " + str(INV_ID))
        elif line.startswith('Order Date:'):
            line = next(data)
            date_str = line.strip().encode('utf8')
            pydate = datetime.strptime(date_str, "%d/%m/%Y %H:%M:%S")
            date_opened = datetime.strftime(pydate,'%Y-%m-%d')
            DEBUG(date_opened)
        elif line.startswith('PayPal'):
            header = False # Processed
            items = True
    if not header and items and not footer:
        # Now the parts stuff
        DEBUG(line)
        if line.startswith('Description:'):
            desc = line.split('Description:')[1].strip()
        elif line.strip().startswith("Order code:"):
            part_num = line.split("Order code:")[1].strip()
            DEBUG(part_num)
        elif line.strip().startswith("Quantity:"):
            qty = line.split("Quantity:")[1].strip()
        elif line.strip().startswith("Unit Price:"):
            DEBUG(line)
            unit_price = line.replace('££', '£').split("Unit Price:")[1].split("£")[-1].strip()
            DEBUG(unit_price)
            running_total += Decimal(unit_price) * Decimal(qty)# We need this to adjust for rounding errors
            csv_data.append(str(linenum) + ", " + part_num + ", " + desc + ", " + unit_price + ", " + qty + ", " + ", ")
            desc = ''
        elif line.find("Order Total") == 0: # Nearly done
            #print "Nearly done"
            items = False
            footer = True
            #print line
    if footer:
        #print "footer"
        # Cost per item shown on e-mail are rounded we need to adjust for that.
        if line.strip().startswith("Total"):
            print (line)
            line = next(data)
            DEBUG(line)
            amnt = line.split("£")[1].strip()
            csv_data.append(", , Rounding adjustment, " + str(Decimal(amnt) - running_total) + ", " + "1" + ", " + str(Decimal(amnt) - running_total))
        if line.strip().startswith("VAT"):
            line = next(data)
            amnt = line.replace('££', '£').split("£")[1].encode('utf8').strip()
            csv_data.append(", , VAT, " + amnt + ", " + "1" + ", " + amnt)
            linenum += 1
        elif line.strip().startswith("Delivery:"):
            line = next(data)
            if not line.startswith('Free'):
                amnt = line.replace('££', '£').split("£")[1].strip()
                csv_data.append( ", , DELIVERY, " + amnt + ", " + "1" + ", " + amnt)
            linenum += 1
footer = False





# Now format this to
#id,date_opened,vendor_id,billing__id,notes,date,desc,action,account,quantity,price,disc_type,disc_how,discount,taxable,taxincluded,tax_table,date_posted,due_date,account_posted,memo_posted,accu_splits,
Reader = csv.reader(csv_data, delimiter=',')
footerRow = 0 # Footer rows are: Order Subtotal, Delivery Charge, VAT, Order Grand Total
SEP = ',' # Field separator.
MONEY = "£"

ofile = open("/home/mikee/downloads/" + INV_ID + '.csv','w')
for row in Reader:
    outline = ""
    if row[0].isdigit(): # We only use numbered lines
        outline=(INV_ID + SEP + date_opened + SEP + VENDOR_ID + SEP*3 + date_opened + SEP + row[1] + " > " + row[2] + SEP + "ea" + SEP +
            ACCOUNT + SEP + row[4] + SEP + row[3].replace(MONEY, "") + SEP*4 + "no" + SEP*7)


# Deal with the footer rows
    else:
        if row[2].strip() == "DELIVERY":
            delivery = row[3].replace(MONEY, "")
            outline = (INV_ID + SEP + date_opened + SEP + VENDOR_ID + SEP*3 + date_opened + SEP + "DELIVERY" + SEP + "ea" + SEP +
            "Business Expenses" + SEP + "1" + SEP + delivery  + SEP*4 + "no" + SEP*7)
            #print outline # pipe to file for GnuCash import
        elif row[2].strip() == "Rounding adjustment":
            adjustment = row[3].replace(MONEY, "")
            outline = (INV_ID + SEP + date_opened + SEP + VENDOR_ID + SEP*2 +
                "Rounding is appled to the confirmation mail so this has to be accounted for here" +
                SEP + date_opened + SEP + "Rounding adjustment" + SEP +"ea" + SEP +
                "Business Expenses" + SEP + "1" + SEP + adjustment + SEP*4 +  "no" + SEP*7)
        elif row[2].strip() == "VAT":
            vat = row[3].replace(MONEY, "")
            outline = (INV_ID + SEP + date_opened + SEP + VENDOR_ID + SEP*3 + date_opened + SEP + "VAT" + SEP +"tax" +SEP +
            "Business Expenses" + SEP + "1" + SEP + vat + SEP*4 +  "no" + SEP*7)
            #print outline # pipe to file for GnuCash import
        footerRow += 1
    outline += os.linesep
    print (outline)

    ofile.write(outline)
ofile.close()


# Now insert the data into a MySQl database.parts_auth.
import MySQLdb
import MySQLdb.cursors

Reader = csv.reader(csv_data, delimiter=',')
import parts_auth # Users will have create this file with their db auth data
db = MySQLdb.connect(host = parts_auth.host, db = parts_auth.db,  user = parts_auth.user, passwd = parts_auth.passwd)
cur = db.cursor(MySQLdb.cursors.DictCursor)

bid=None
try:
    cur.execute("INSERT INTO orders(bill_id, supp_id, datetime, ord_num) VALUES(%s,%s,%s,%s)",(INV_ID, 1,ord_date, ord_num ))
    db.commit()
    cur.execute("Select id from orders where bill_id = %s",(INV_ID,))
    bid = cur.fetchone()['id']
except:
    print ("Already in database")
    #quit(0)



Reader.next() # Skip first row.
for row in Reader:
    print (row[1], row[2], row[3])
    cur.execute("INSERT INTO parts(supp_id, partnum,descrip,unit_price, orders_id, qty) VALUES(%s,%s,%s,%s,%s,%s)",
        (1, row[1],row[2], row[3], bid, row[4]))
cur.execute("DELETE FROM parts WHERE partnum = ''");
# Trim any spaces
cur.execute("update parts set partnum = trim(partnum)");
cur.execute("update parts set descrip = trim(descrip)");
db.commit()

# Now update the multiples.
# NB: This should be done somewhere above rather than a separate thing
# TODO: Also for lengths, weights...
# TODO: Don't add new lines for same parts, just increment the count.

cur.execute("SELECT * from parts WHERE descrip LIKE '%pack%'")
parts = cur.fetchall()

for part in parts:
    multi = multi.split()[-1].strip()
    print (part['id'], multi)
    cur.execute("UPDATE parts SET multi = %s WHERE id = %s",(multi, part['id']))
    cur.execute("UPDATE parts SET multi = 1 WHERE multi IS NULL")
db.commit()

