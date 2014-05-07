#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
# Create a GnuCash bill froman e-bay e-mail confirmation.
# This is command line version.
# A GUI version could just take pasted text from e-mails
# In my case these are always paid using PayPal so consider them paid.
# The transfer account varias though so perhaps don't.
# The relevent part looks like:
# See mail.txt for a complicated example.
# Use transaction as the bill ID as then we can trace these back, perhaps prepend ebay-

import sys
import csv
import email
import pycash
import json
import copy


# Add the Gnucash Python stuff
#sys.path.append('/home/mikee/progs/gnucash-master/lib/python2.7/site-packages')
#import gnucash
#import gnucash.gnucash_business

class EbayBill():
    items = [] # list
    sellers = {}
    #item = [] # List not Dictionary
    #seller = {} # Seller data. Use seller.update({'xxx':'xxxxx'}) to add stuff
    
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
        
        print json.dumps(self.sellers,sort_keys=True, indent=4)
        print json.dumps(self.items,sort_keys=True, indent=4)
    
        #print session.vendor_search("E Bay", 100)
        #self.session.close() # Supply save=True to save on close.
                        

    def parse_seller_information(self,plain):
        foo = plain.split("\n")
        seller = ""
        #print foo
        item_dict = {}
        for line in foo:   
            if line.find("Seller:") != -1:
                seller_dict = {}
                seller = line.rpartition('Seller:')[2].lstrip(' ')
                #seller_dict.update({'Seller':seller}) ## Just the name. we need address
                seller_dict.update({'Addr1':seller}) # Dummy address
                seller_dict.update({'Addr2':"2 Addr Dummy"}) # Dummy address
                self.sellers.update({seller:seller_dict}) # Add to the sellers dict
            else:
                for needle in self.item_search_terms:
                    if line.find(needle) != -1:
                        item_dict.update({line.rpartition(needle)[1].strip(':'):\
                            line.rpartition(needle)[2].lstrip(' ').decode('ascii','ignore').encode('utf8')})
        self.items.append({seller.lstrip(' '):copy.deepcopy(item_dict)})
        item_dict.clear()

                    

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
            for needle in self.item_search_terms:
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

