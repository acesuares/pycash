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

Convert a CSV file exported from Rapid Electronics (UK) to a form importable by GnuCash
Line format is:
line number,product code,quantity,availability,product description,unit price,discounts,line total,delivery,sub total,vat,grand total

Useage: rapid2gnucash.py  DOWNLOADED_BASKET.csv "ORDER_NUMBER" <"Expense account">  >  output.csv

We need to remove first line and totals

Format needs to be:
#id,date_opened,vendor_id,billing_id,notes,date,desc,action,account,quantity,price,disc_type,disc_how,discount,taxable,taxincluded,tax_table,date_posted,due_date,account_posted,memo_posted,accu_splits,
Not all fields need to have values but the delimiters (,) do.
Some fields are compulsory: id, vendor_id, action, quantity, price, taxable
'''
import sys
import csv

VENDOR_ID="000013" # Obviously this needs to match your vendor ID for this supplier

try:
	INFILE=sys.argv[1]
except:
	print "No input files specified."
	print "Useage: Useage: rapid2gnucash.py  DOWNLOADED_BASKET.csv \"ORDER_NUMBER\""
	quit(1)
try:
	INV_ID=sys.argv[2]
except:
	print "No order number  specified."
	print "Useage: Useage: rapid2gnucash.py  DOWNLOADED_BASKET.csv \"ORDER_NUMBER\""
	quit(1)
try:
	ACCOUNT=sys.argv[3]
except:
	ACCOUNT="Business Expenses" # Default if absent on the command line.  Edit to suit your account tree

Reader = csv.reader(open(INFILE), delimiter=',')

# Need to ignore 1st and last rows.

footerRow = 0 # Footer rows are: Order Subtotal, Delivery Charge, VAT, Order Grand Total
SEP = ',' # Field separator.
MONEY = "£"

for row in Reader:
	if row[0].isdigit(): # We only use numbered lines
		# If field 5 is not money then we have errant separators somewhere, 
		# so just concat the previous field until we do.
		while not "£" in row[5]:
			row[4] =  row[4] + row[5]
		row[4] = row[4].replace(SEP, ":")
		outline=(INV_ID + SEP*2 + VENDOR_ID + SEP*4 + row[1] + " > " + row[4] + SEP + "ea" + SEP +
			ACCOUNT + SEP + row[2] + SEP + row[5].replace(MONEY, "") + SEP*4 + "no" + SEP*8)
		print outline

# Deal with the footer rows		
	elif not row[0]: # We only need the VAT row and Postage
		if footerRow == 1: 
			delivery = row[7].replace(MONEY, "")
			outline=(INV_ID + SEP*2 + VENDOR_ID + SEP*4 + "DELIVERY" + SEP + "ea" + SEP +
			"Business Expenses:Postage and Delivery" + SEP + "1" + SEP + delivery  + SEP*4 + "no" + SEP*8)
			print outline # pipe to file for GnuCash import
		if footerRow == 2: 
			vat = row[7].replace(MONEY, "")
			outline=(INV_ID + SEP*2 + VENDOR_ID + SEP*4 + "VAT" + SEP +"tax" +SEP +
			"Business Expenses:VAT" + SEP + "1" + SEP + vat + SEP*4 +  "no" + SEP*8)
			print outline # pipe to file for GnuCash import
		footerRow += 1

