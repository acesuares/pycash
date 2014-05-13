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
#import pycash
import json
import copy

class Vendor:
    def __init__(self):
        self.name = ''
        self.addr1 = ''
        self.addr2 = ''
        self.addr3 = ''
        self.addr4 = ''
        self.email = ''
        
###### END CLASS VENDOR ########


class Item:
    vendor = Vendor
    name=''
    number=''
    transaction=''
    price = 0.0
    pnp = 0.0
    quantity = 0
    total = 0
    paid_on = '' 
    item_search_terms=(  "Item name", #Diffused LEDs 3mm/5mm Red,Blue,White,Green,Yellow,Orange - 1st C=
                "Item number:", # 290921972162
                "transaction::",  # 1010018076019 Use this for bill ID
                "Price:", #  =C2=A31.45    =20
                "P&amp;P price:", #  P&P £30.99
                "Quantity:", #  1
                "Item total:",  #  =C2=A31.45
                "Paid on")  # 26-Apr-14)#  =C2=A31.45
    def __init__(self, item_data):
        self.parse_item_information(item_data)

        
    def parse_item_information(self,plain):
        print '\n\n'
        for line in plain:
            for needle in self.item_search_terms:
                idx = line.find(needle)
                if idx != -1:
                    print line
        return
        
#### END CLASS ITEM #######
                    




class Sale:
    items = [] # A sale has one or more items
    vendor = Vendor() # from a single vendor
    def __init__(self, sale_data):
        self.parse_sale(sale_data)
        
    def parse_sale(self, data):
        ''' All stuff from a single seller. '''
        idxs = []
        #print '\n\nMONKEY\n\n'#,plist ## DEBUG
        #for line in plist:
        for i in range(len(plist)-1):
            if plist[i].find('Item name ') != -1:
                idxs.append(i)
        idxs.append(len(plist))
        #print idxs    
        for i in range(len(idxs)-1):
            item = Item(plist[idxs[i]:idxs[i+1]])
            self.items.append(item)
        return

###### END CLASS SALE ########    
    
    
class EbayBill():
    items = [] # list of Item instances
    sellers = [] # List of Vendor instances
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
        self.msg = email.message_from_file(f)
        f.close()
        
        '''
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
        '''
        
    def get_plain_mail(self,mail):
        ''' Get the plain text part of the mail.'''
        for part in mail.walk():
            # each part is a either non-multipart, or another multipart message
            # that contains further parts... Message is organized like a tree
            if part.get_content_type() == 'text/plain':
                return part.get_payload(None, True) # Make a string of the text.
     
    def parse_mail(self,plist):
        ''' Parse the mail '''
        idxs = [] # list of occurrences.
        for line in plist:
            if line.find("Seller:") != -1:
                #print line
                idxs.append(plist.index(line))
            if line.find("Subtotal:") != -1:
                #print line
                idxs.append(plist.index(line))
        for i in range(len(idxs)-1):
            #print '\n\nMONKEY\n\n',plist[idxs[i]:idxs[i+1]]
            self.parse_sale(plist[idxs[i]:idxs[i+1]])
        return   
         
    def parse_sale(self,plist):
        ''' All stuff from a single seller. '''
        idxs = []
        sale = Sale(plist)
        #print '\n\nMONKEY\n\n'#,plist ## DEBUG
        #for line in plist:
        for i in range(len(plist)-1):
            if plist[i].find('Item name ') != -1:
                idxs.append(i)
        idxs.append(len(plist))
        #print idxs    
        for i in range(len(idxs)-1):
            self.parse_item_information(plist[idxs[i]:idxs[i+1]])
        return

    def parse_item_information(self,plain):
        item = Item(plain)
        print '\n\n'
        for line in plain:
            for needle in self.item_search_terms:
                idx = line.find(needle)
                if idx != -1:
                    print line
    
    def parse_seller(plist):
        ''' Each seller has ...''' 
        return
        
    '''
    def parse_seller_information(self,plain):
        foo = plain.split("\n")
        seller = ""
        #print foo
        item_dict = {}
        item_list = []
        for line in foo:   
            if line.find("Seller:") != -1:
                seller_dict = {}
                seller = line.rpartition('Seller:')[2].lstrip(' ')
                #seller_dict.update({'Seller':seller}) ## Just the name. we need address
                seller_dict.update({'Addr1':seller}) # Dummy address
                seller_dict.update({'Addr2':"2 Addr Dummy"}) # Dummy address
                self.sellers.update({seller:seller_dict}) # Add to the sellers dict
                self.items.append(seller)
            else:
                for needle in self.item_search_terms:
                    if line.find(needle) != -1:
                       
                        item_dict.update({line.rpartition(needle)[1].strip(':'):\
                            line.rpartition(needle)[2].lstrip(' ').decode('ascii','ignore').encode('utf8')})
                        self.items.append( line.rpartition(needle)[2].lstrip(' ').decode('ascii','ignore').encode('utf8'))
                #item_dict.update({seller:self.items})
        print 
    '''
                    
        
    def make_invoice(self):
        session = bill.Session("example.gnucash")
        session.open()
        
        print session.vendor_search("E Bay", 100)
        session.close()    
        return

    
    def parse_totals(self,plain):
        
        return
                    
##### END CLASS EBAYBILL ############


    
# START HERE
if __name__ == "__main__":
    VENDOR_ID="000019" # All ebay stuff in here.

try:
	INFILE=sys.argv[1]
except:
    INFILE="example.gnucash"
	
try:
	ACCOUNT=sys.argv[2]
except:
	ACCOUNT="Business Expenses" # Default if absent on the command line.  Edit to suit your account tree

ebay_bill = EbayBill('mail.txt',INFILE, ACCOUNT)
plain = ebay_bill.get_plain_mail(ebay_bill.msg)
plist = plain.lstrip(' ').decode('ascii','ignore').encode('utf8').split('\n')
ebay_bill.parse_mail(plist)

