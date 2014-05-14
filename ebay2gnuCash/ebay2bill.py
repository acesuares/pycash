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
    name = ''
    addr = []
    email = ''
    items = [] # List of items from this vendor.
        
    def __init__(self):
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
            
    def parse_vendor_data(self, data):
        return
        
    def add_item(self, item):
        self.items.append(item)
        
    def print_vendor(self):
        print self.name
        for add in self.addr:
            print add
        

        
###### END CLASS VENDOR ########


class Item:
    items = {} # Dict
    item_search_terms=( "Item name", #
                        "Item number:", #
                        "transaction::",  #
                        "Price:", #
                        "P&amp;P price:", #
                        "Quantity:", #
                        "Item total:",  #
                        "Paid on")  #
    
    def __init__(self, item_data):
        self.parse_item_information(item_data)
        
    def parse_item_information(self,plain):
        for line in plain:
            for needle in self.item_search_terms:
                if line.find(needle) != -1:
                    var = line.rpartition(needle)[2].lstrip(' ')
                    self.items[needle.strip(':')] = var
        return
        
    def print_items(self):
        for item in self.items:
            print item
        
#### END CLASS ITEM #######
                    



class Purchase:
    ''' A purchase from a single vendor and may be one or more items.
    Probably should be called purchase? 
    '''
    items = [] # A Purchase has one or more items
    vendor = Vendor() # from a single vendor
    
    def __init__(self, Purchase_data):
        self.parse_vendor(Purchase_data)
        self.parse_purchase(Purchase_data)
        
    def parse_purchase(self, data):
        ''' All stuff from a single seller. '''
        idxs = []
        for i in range(len(data)-1):
            if data[i].find('Item name ') != -1:
                idxs.append(i)
        idxs.append(len(data))
        for i in range(len(idxs)-1):
            item = Item(data[idxs[i]:idxs[i+1]])
            self.items.append(item)
            self.vendor.add_item(item)
            
        return
        
        
    def parse_vendor(self, data):
        self.vendor.name=data[0].rpartition('Seller:')[2].lstrip(' ') # Always
        for i in range(4,8):
            if data[i][0:3] == '---': break
            self.vendor.addr.append(data[i].lstrip(' '))
        
    def print_purchase(self):
        self.vendor.print_vendor()
        print '\n\n'
        ''' Print the Purchase data, mostly for debugging purposes. '''
        print '\n\n'
        return

###### END CLASS Purchase ########    
    
    
class EbayBill():
    purchases = [] # List of Purchases in email, usually just the one but mutiples are possible.
     
    def __init__(self,billmail, cashfile, account):
        self.INFILE = billmail
        self.account = account
        f = open(self.INFILE)
        self.msg = email.message_from_file(f)
        f.close()
        
    def get_plain_mail(self,mail):
        ''' Get the plain text part of the mail.'''
        for part in mail.walk():
            # each part is a either non-multipart, or another multipart message
            # that contains further parts... Message is organized like a tree
            if part.get_content_type() == 'text/plain':
                return part.get_payload(None, True) # Make a string of the text.
     
    def parse_mail(self,plist):
        ''' Parse the mail.
        Collect the indices of where the serch terms occur, then split the file
        using the indices and send these chunks for further parsing.
        '''
        idxs = [] # list of occurrences.
        for line in plist:
            if line.find("Seller:") != -1:
                #print line
                idxs.append(plist.index(line))
            if line.find("Subtotal:") != -1:
                #print line
                idxs.append(plist.index(line))
        #print idxs
        for i in range(len(idxs)-1):           
            purchase = Purchase(plist[idxs[i]:idxs[i+1]])
            purchase.print_purchase()
            self.purchases.append(purchase)
            pass
        return   
        
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

try: GNUFILE=sys.argv[1]
except: GNUFILE="example.gnucash"
	
try: ACCOUNT=sys.argv[2]
except:	ACCOUNT="Business Expenses" # Default if absent on the command line.  Edit to suit your account tree

try: MAILFILE = sys.argv[3]
except: MAILFILE = "Confirmation of your order of Voltage Regulator LM7805 LM7812 LM317T Adjustable Linear 7805 7812 UK..."
    
ebay_bill = EbayBill(MAILFILE,GNUFILE, ACCOUNT)
plain = ebay_bill.get_plain_mail(ebay_bill.msg)
plist = plain.lstrip(' ').decode('ascii','ignore').encode('utf8').split('\n')
ebay_bill.parse_mail(plist)

