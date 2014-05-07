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
import pycash

# Add the Gnucash Python stuff
#sys.path.append('/home/mikee/progs/gnucash-master/lib/python2.7/site-packages')
#import gnucash
#import gnucash.gnucash_business

class EbayBill():
    items = {} # list
    sellers = {}
    item = {} # Dictionary
    seller = {} # Seller data. Use seller.update({'xxx':'xxxxx'}) to add stuff
    
    item_search_terms=(  "Item name", #Diffused LEDs 3mm/5mm Red,Blue,White,Green,Yellow,Orange - 1st C=
                    "Item number:", # 290921972162
                    "transaction::",  # 1010018076019 Use this for bill ID
                    "Price:", #  =C2=A31.45    =20
                    "P&amp;P price:", #  P&P £30.99
                    "Quantity:", #  1
                    "Item total:",  #  =C2=A31.45
                    "Paid on")  # 26-Apr-14)#  =C2=A31.45
    
    def __init__(self,billmail, cashfile, account):
        
        #self.session=pycash.Session(cashfile) # A gnucash session
        #self.session.open()
        self.INFILE = billmail
        self.account = account
        f = open(self.INFILE)
        msg = msg = email.message_from_file(f)
        f.close()
        self.plain = ""
        for part in msg.walk():
            # each part is a either non-multipart, or another multipart message
            # that contains further parts... Message is organized like a tree
            if part.get_content_type() == 'text/plain':
                self.plain =  part.get_payload(None, True) # Make a string of the text.
        
        self.parse_seller_information(self.plain)
        #self.parse_item_information(self.plain)
        #print self.items
        print self.sellers
        #print session.vendor_search("E Bay", 100)
        #self.session.close() # Supply save=True to save on close.
                        

    def parse_seller_information(self,plain):
        foo = plain.split("\n")
        seller = ""
        #print foo
        for line in foo:   
            if line.find("Seller:") != -1:
                seller = line.rpartition('Seller:')[2]
                self.seller.update({'Seller':seller}) ## Just the name. we need address
                self.sellers.update({seller:self.seller})
            for needle in self.item_search_terms:
                if line.find(needle) != -1:
                    self.item.update({line.rpartition(needle)[1].strip(':'):\
                        line.rpartition(needle)[2].lstrip(' ').decode('ascii','ignore').encode('utf8')})
                    self.needle_found(needle, line)
                self.items.update({seller:self.item})
  
                    

    def needle_found(self, needle, line):
        ''' Get the data part of the line; '''
        print  needle, line.rpartition(needle)[2]
        f = open("ebay2cash.log","a")
        f.write(line.rpartition(needle)[1]) # The partition string
        f.write(line.rpartition(needle)[2]) # The data
        f.write("\n")
        f.close()
        #if needle == "Item name":
        return
        
    def make_invoice(self):
        session = bill.Session("example.gnucash")
        session.open()
        
        print session.vendor_search("E Bay", 100)
        session.close()    
        return

    def parse_item_information(self,plain):
        foo = plain.split('\n')
        for line in foo:
            for needle in item_self.search_terms:
                idx = line.find(needle)
                if idx != -1:
                    self.needle_found(needle, line)
                    
##### END CLASS EBAYBILL ############


    
# START HERE
if __name__ == "__main__":
    VENDOR_ID="000019" # All ebay stuff in here.

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

ebay_bill = EbayBill(INFILE,"example.gnucash", "Business Expenses")

