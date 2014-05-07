#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
# Create a GnuCash bill froman e-bay e-mail confirmation.
# This is command line version.
# A GUI version could just take pasted text from e-mails
# In my case these are always paid using PayPal so consider them paid.
# The transfer account varias though so perhaps don't.
# The relevent part looks like:
'''
Item name  Acer Aspire 5520 ICW50 5720 5315 5715 Webcam Camera Module
Item URL:  http://rover.ebay.com/rover/0/e11401.m1842.l3160/7?euid=ae9d4293bf13401583ed51cb7fa10c8c&loc=http%3A%2F%2Fcgi.ebay.co.uk%2Fws%2FeBayISAPI.dll%3FViewItem%26item%3D171266857661%26ssPageName%3DADME%3AL%3AOU%3AGB%3A3160&exe=10014&ext=100027sojTags=exe=exe,ext=ext
Item number:  171266857661
transaction::  1202476642007
Price:  £1.97     
P&amp;P price:  Free
Quantity:  1
Item total:  £1.97
Paid on 03-May-14Dispatched on  06-May-14 
Royal Mail 1st Class
 Estimated delivery:  Wed. 7 May.

-----------------------------------------------------------------
-----------------------------------------------------------------
Email reference id: [#ae9d4293bf13401583ed51cb7fa10c8c#]
-----------------------------------------------------------------
'''
# Use transaction as the bill ID as then we can trace these back, perhaps prepend ebay-

import sys
import csv
import email

VENDOR_ID="000013" # Obviously this needs to match your vendor ID for this supplier

try:
	INFILE=sys.argv[1]
except:
	print "No input files specified."
	print "Useage: Useage: ebay2bill Expense_account"
	quit(1)
	
try:
	ACCOUNT=sys.argv[2]
except:
	ACCOUNT="Business Expenses" # Default if absent on the command line.  Edit to suit your account tree

Reader = csv.reader(open(INFILE), delimiter=',')

# Need to ignore 1st and last rows.

MONEY = "£"

search_terms=("Item name", #Diffused LEDs 3mm/5mm Red,Blue,White,Green,Yellow,Orange - 1st C=
# lass Post # Yep there's a fucking line break in there.
            "Item number:", # 290921972162
            "transaction::",  # 1010018076019
            "Price:", #  =C2=A31.45    =20
            "P&amp;P price:", #  P&P £30.99
            "Quantity:", #  1
            "Item total:",  #  =C2=A31.45
            "Paid on")  # 26-Apr-14)#  =C2=A31.45

f = open(INFILE)
msg = msg = email.message_from_file(f)
lines = f.readlines()
f.close()

plane = ""
for part in msg.walk():
        # each part is a either non-multipart, or another multipart message
        # that contains further parts... Message is organized like a tree
        if part.get_content_type() == 'text/plain':
                plane +=  part.get_payload(None, True) # prints the raw text

plane = plane.split("\n")


def needle_found(needle, line):
    ''' Get the data part of the line; '''
    print  needle, line.rpartition(needle)[2]
    #if needle == "Item name":
    return
    
def make_invoice():
    
    return
    
    
    
for line in plane:
    for needle in search_terms:
        idx = line.find(needle)
        if idx != -1:
            needle_found(needle, line)
