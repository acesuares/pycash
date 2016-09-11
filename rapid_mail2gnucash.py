#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
'''
#       rapid2gnucash.py
#
#       Copyright 2010 Mike Evans <mikee@millstreamcomputing.co.uk>
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

Convert confirmation mail from Rapid Electronics (UK) to CSV.
Saved mails from claws are base64 encoded.

The data look like:

Description: TruOhm CR-025 1M8 Carbon Film Resistor 0.25W - Pack of 100, Item No.: 62-0448
Unit price: 1.93 GBP
Qty: 1
Amount: Â£1.93 GBP

The csv data should look like:
line number,product code,quantity,availability,product description,unit price,discounts,line total,delivery,sub total,vat,grand total
The date line is the first line:
5 Sep 2016 12:32:45 BST | Transaction ID: 33Y921378M620934F
'''

import sys
import csv
import base64
from datetime import datetime
VENDOR_ID="000013" # Obviously this needs to match your vendor ID for this supplier

try:
	INFILE=sys.argv[1]
except:
	print "No input files specified."
	print "Useage: Useage: rapid2gnucash.py  \"SAVED_RAPID_CONFIRMATION_MAIL\" \"ORDER_NUMBER\" \"OPT_ACCOUNT\""
	quit(1)
try:
	INV_ID=sys.argv[2]
except:
	print "No order number  specified."
	print "Useage: Useage: rapid2gnucash.py  \"SAVED_RAPID_CONFIRMATION_MAIL\" \"ORDER_NUMBER\" \"OPT_ACCOUT\""
	quit(1)
try:
	ACCOUNT=sys.argv[3]
except:
    ACCOUNT="Business Expenses" # Default if absent on the command line.  Edit to suit your account tree


OUTFILE = INFILE + ".csv"
# Load the file
infile = open(INFILE, 'r')
data = infile.readlines()
infile.close()
#print(data)
encoded = ""
start64 = False
print ""
csv_data = []
csv_data.append("line_num,part_num,desc,unit_price,qty,amnt")
#print "part_num,desc,unit_price,qty,amnt"
linenum = 1
date_opened=""

for line in data:
    if line.find("Transaction ID:") != -1: # Parse date
        date_str = line.split("|")[0].strip()
        #print date_str
        pydate = datetime.strptime(date_str, "%d %b %Y %H:%M:%S %Z")
        date_opened=datetime.strftime(pydate,'%Y-%m-%d')
    elif line.strip().startswith("Description:"):
        desc = line.split("Description:")[1].split(", Item No.:")[0].strip()
        part_num = line.split("Description:")[1].split(", Item No.:")[1].strip()
    elif line.strip().startswith("Unit price:"):
        unit_price = line.split("Unit price:")[1].split("GBP")[0].strip()
    elif line.strip().startswith("Qty:"):
        qty = line.split("Qty:")[1].strip()
    elif line.strip().startswith("Amount:"):
        amnt = line.split("Amount:")[1].split("GBP")[0].strip()#.replace("£","")
        #print  str(linenum) + ", " + part_num + ", " + desc + ", " + unit_price + ", " + qty + ", " + amnt
        #line number,product code,quantity,availability,product description,unit price,discounts,line total,delivery,sub total,vat,grand total
        #try:
        csv_data.append(str(linenum) + ", " + part_num + ", " + desc + ", " + unit_price + ", " + qty + ", " + amnt)
        #except:pass
        linenum += 1
    elif line.strip().startswith("Tax:"):
        amnt = line.split("Tax:")[1].split("GBP")[0].strip()
        csv_data.append(", , VAT, " + amnt + ", " + "1" + ", " + amnt)
        #except:pass
        linenum += 1
    elif line.strip().startswith("Delivery:"):
        amnt = line.split("Delivery:")[1].split("GBP")[0].strip()
        csv_data.append( ", , DELIVERY, " + amnt + ", " + "1" + ", " + amnt)
        #except:pass
        linenum += 1
#print ("\n".join(csv_data)) # Redirect to a file with > if needed
Reader = csv.reader(csv_data, delimiter=',')

#Reader = csv.reader(csv_data, delimiter=',')

# Now format this to 
#id,date_opened,vendor_id,,,,desc,action,account,quantity,price,disc_type,disc_how,discount,taxable,taxincluded,tax_table,date_posted,due_date,account_posted,memo_posted,accu_splits,

footerRow = 0 # Footer rows are: Order Subtotal, Delivery Charge, VAT, Order Grand Total
SEP = ',' # Field separator.
MONEY = "£"

for row in Reader:
    outline = ""
    #print row
    if row[0].isdigit(): # We only use numbered lines
        outline=(INV_ID + SEP + date_opened + SEP + VENDOR_ID + SEP*4 + row[1] + " > " + row[2] + SEP + "ea" + SEP +
			ACCOUNT + SEP + row[4] + SEP + row[3].replace(MONEY, "") + SEP*4 + "no" + SEP*7)
        

# Deal with the footer rows		
	#if not row[0]: # The VAT row and Postage don't have line numbers
    else:
		if row[2].strip() == "DELIVERY": 
			delivery = row[3].replace(MONEY, "")
			outline=(INV_ID + SEP + date_opened + SEP + VENDOR_ID + SEP*4 + "DELIVERY" + SEP + "ea" + SEP +
			"Business Expenses:Postage and Delivery" + SEP + "1" + SEP + delivery  + SEP*4 + "no" + SEP*7)
			#print outline # pipe to file for GnuCash import
		elif row[2].strip() == "VAT": 
			vat = row[3].replace(MONEY, "")
			outline=(INV_ID + SEP + date_opened + SEP + VENDOR_ID + SEP*4 + "VAT" + SEP +"tax" +SEP +
			"Business Expenses:VAT" + SEP + "1" + SEP + vat + SEP*4 +  "no" + SEP*7)
			#print outline # pipe to file for GnuCash import
		footerRow += 1
    print outline
