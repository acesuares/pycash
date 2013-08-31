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

VENDOR_ID="000013" # Obviously this needs to match your vendor ID
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
sep=',' # Field separator.
money = "£"

# Make sure that field 5 is a numeric field by detecting £ sign
# This can occur if the download has errant separator chars in descriptions


for row in Reader:
	if row[0].isdigit(): # We only use numbered lines
		for 
		
		row[3] = row[3].replace(",", ";")
		if not "£" in row[5]: # Concat previous two fields
			row[4] =  row[4] + row[5]
			row[4] = row[4].replace(",", ";")
		outline=(INV_ID + sep*2 + VENDOR_ID + sep*4 + row[1] + " > " + row[4] + sep + "ea" + sep +
			ACCOUNT + sep + row[2] + sep + row[5].replace("£", "") + sep*4 + "no" + sep*8)
		print outline

# Deal with the footer rows		
	elif not row[0]: # We only need the VAT row.
		
		if footerRow == 1: 
			delivery = row[7].replace("£", "")
			outline=(INV_ID + sep*2 + VENDOR_ID + sep*4 + "DELIVERY" + sep + "ea" + sep +
			"Expenses:Postage and Delivery" + sep + "1" + sep + delivery +  "no" + sep*8)
			print outline # pipe to file for GnuCash import
		if footerRow == 2: 
			vat = row[7].replace("£", "")
			outline=(INV_ID + sep*2 + VENDOR_ID + sep*4 + "VAT" + sep +"tax" +sep +
			"Expenses:VAT" + sep + "1" + sep + vat +  "no" + sep*8)
			print outline # pipe to file for GnuCash import
		footerRow+= 1
