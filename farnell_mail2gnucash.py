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
csv_data.append("Line, Order Code / Description, Unit, Quantity, List Price, Net Price, VAT Rate, Amount")
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
    #print line
    if line.startswith('Customer Order No'):
        ord_num = line.split(':')[1].split()[0]
    if line.strip().startswith('Line'):
        try:
            while not data.next().split()[0].isdigit():
                pass
        except:
            line = data.next()
        print line
        line = data.next()
        print line
print ord_num
quit(0)


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

