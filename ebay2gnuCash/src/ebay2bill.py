#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
# Copyright 2014 Mike Evans <mikee@mutant-ant.com>
# Create a GnuCash bill froman e-bay e-mail confirmation.
# This is command line version.
# A GUI version could just take pasted text from e-mails
# In my case these are always paid using PayPal so consider them paid.
# The transfer account varias though so perhaps don't.
# The relevent part looks like:
# See mail.txt for a complicated example.
# Use transaction as the bill ID as then we can trace these back, perhaps prepend ebay-

import sys, os
import csv
import email
import pycash
import json
import copy
import logging
import uuid
import time
from decimal import Decimal

logging.basicConfig(level=logging.DEBUG, format='%(module)s: LINE %(lineno)d: %(levelname)s: %(message)s')

class Person:
    guid = None
    items = [] # List of items from this person.

    def __init__(self):
        self.guid = uuid.uuid4()
        self.addr = []
        self.email = ''
        self.name = ''
        self.addr_name = ''
        return

    def parse_person_data(self, data):
        return

    def add_item(self, item):
        self.items.append(item)

    def print_person(self):
        print self.name
        for add in self.addr:
            print add



###### END CLASS person ########


class Item:
    # Class attributes
    attribs = None
    guid = None
    item_search_terms=( "Item name", #
                        "Item number", #
                        "Price:", #
                        "Quantity", #
                        "Item total",  #
                        "Paid on ", #
                        "transaction") #

    def __init__(self, item_data):
        # Object attributes
        self.postage = 0.0
        self.attribs = {}
        self.guid = uuid.uuid4()
        # Do stuff
        if item_data == None: return
        self.parse_item_information(item_data)

    def parse_item_information(self,data):
        for line in data:
            for needle in self.item_search_terms:
                logging.debug("%s %s",line.find(needle), needle)
               
                if line.find(needle) == 0:
                    self.attribs[needle.strip(':').rstrip(' ')] = line.rpartition(needle)[2].lstrip(' ').strip('£')
    
        
    def print_items(self):
        #print self.attribs.items()
        for key, value in self.attribs.items():
            print key, '->', value

    def get_attribs(self):
        return attribs

#### END CLASS ITEM #######
class Postage():
    ''' Just the postage
    '''
    def __init__(self, data):
        # Define stuff
        self.search_term="P&amp;P price:"
        self.postage = 0.0
        self.seller = ''
        self.discount = 0.0
        # Do stuff
        self.parse_item_information(data)
        #logging.debug(data)
        
    def parse_item_information(self,data):
        for line in data:
            if line.find(self.search_term) != -1:
                try:
                    self.postage += float(line.rpartition(self.search_term)[2].lstrip(' ').strip('£'))
                except: pass
            if line.find("Postage discount from seller") != -1: # Discount line
                #logging.info("Found discount for this seller.")
                self.discount = float(line.rpartition(("Postage discount from seller").lstrip().strip('£'))[2].rpartition(":")[2].lstrip())
                self.seller = line.rpartition("Postage discount from seller")[2].rpartition(":")[0].strip()
    
    
#### END CLASS POSTAGE ########
class Purchase:
    ''' A purchase from a single person and may be one or more items.
    '''
    items = None # A Purchase has one or more items
    person = None # from a single person
    purchase_data = None
    guid = None
    purchase_type = None

    def __init__(self, purchase_data, purchase_type): # Can be "PURCHASE" or "SALE"
        self.purchase_type = purchase_type
        self.guid = uuid.uuid4()
        self.person = Person()
        self.items = []
        self.purchase_data =  purchase_data
        #logging.debug(self.purchase_data)
        if not type(purchase_data) == list: return
        if self.purchase_type == 'PURCHASE':
            self.parse_seller(self.purchase_data)
            self.parse_purchase(self.purchase_data)
        if self.purchase_type == 'SALE':
            self.parse_buyer(self.purchase_data)
            self.parse_sale(self.purchase_data)
        self.do_postage(self.purchase_data)
        
    def parse_seller(self, data):
        p = 'Seller'
        self.person.name=data[0].rpartition(p+':')[2].lstrip(' ') # Always
        if data[3] [0:3] != '---':
            self.person.addr_name=data[3].rpartition(p+':')[2].lstrip(' ') # Always
            for i in range(4,8):
                if data[i][0:3] == '---':
                    self.person.addr.append(self.person.name) # Need this or we get errors later
                    break ## See mail.txt for why
                self.person.addr.append(data[i].lstrip(' ').rstrip(' '))
        else: 
            self.person.addr_name = data[0].rpartition(p+':')[2].lstrip(' ')
            self.person.addr.append("Ebay")
        #logging.debug("Person: %s",self.person.addr)

    def parse_buyer(self,data):
        p = "Buyer"
        self.person.name=data[5].rpartition(p+':')[2].lstrip(' ') # Always
        self.person.addr_name = self.person.name
        #self.person.addr.append(data[10])
        self.person.addr.append(data[11])
        self.person.addr.append(data[12])
        self.person.addr.append(data[13])
        logging.debug("Person: %s\nAddress:%s\n%s",self.person.name,self.person.addr_name,self.person.addr)
        logging.debug("FOO")
        
    def parse_purchase(self, data):
        idxs = []
        for i in range(len(data)-1):
            if data[i].find('Item name ') != -1:
                idxs.append(i)
        idxs.append(len(data))
        for i in range(len(idxs)-1):
            item = Item(data[idxs[i]:idxs[i+1]])
            self.items.append(item)
        return

    def parse_sale(self,data):
        idxs = []
        for i in range(len(data)-1):
            if data[i].find('Item name:') != -1:
                logging.debug(data[i].find('Item name:'))
                idxs.append(i)
        idxs.append(len(data))
        for i in range(len(idxs)-1):
             item = Item(data[idxs[i]:idxs[i+1]])
             
             self.items.append(item)
                
    def print_purchase(self):
        print '\nperson Data:\n'
        self.person.print_person()
        print '\nItem data:\n'
        for item in self.items:
            item.print_items()
        return
        
    def do_postage(self, data):
        postage_object = Postage(data)
        postage = postage_object.postage
        if postage_object.seller == self.person.name:
            postage -= postage_object.discount
        item = Item(None)
        item.attribs['Item name'] = "Postage and packing" 
        item.attribs['Quantity'] = 1 
        item.attribs['Price'] = postage
        self.items.append(item)
        
        
        
    def get_items(self):
        return self.items

    def get_person(self):
        return self.person

###### END CLASS Purchase ########


class EbayMail:
    purchases = [] # List of Purchases in email, usually just the one but mutiples are possible.
    mail_date = ''
    purchase_type = None
    person = None
    
    def __init__(self,billmail,purchase_type):
        self.purchase_type = purchase_type
        if self.purchase_type == 'PURCHASE': self.person = 'Seller'
        else: self.person = 'Buyer'
        self.INFILE = billmail
        self.purchases = []
        f = open(self.INFILE)
        self.msg = email.message_from_file(f)
        if self.msg == None: return # Should raise an exception too.
        f.close()
        #self.test_subject(self.msg)
        
    def test_subject(self, msg):
        '''Check that the subject line is what we expect.'''
        logging.debug(msg['Subject'][:27])
        #if msg['Subject'][:29] != "Confirmation of your order of" \
        #    and msg['Subject'][:26] != "You've sold your eBay item:":
        #    print "Wrong kind of mail."
        #    return
        

    def get_plain_mail(self,mail):
        ''' Get the plain text part of the mail.'''
        for part in mail.walk():
            # each part is a either non-multipart, or another multipart message
            # that contains further parts... Message is organized like a tree
            if part.get_content_type() == 'text/plain':
                return part.get_payload(None, True) # Make a string of the text.

    def parse_mail(self,plist):
        ''' Parse the mail.
        Collect the indices of where the search terms occur, then split the file
        using the indices and send these chunks for further parsing.
        '''
        idxs = [] # list of occurrences.
        pdidx = None
        for line in plist:
            if line.find("Date: ") != -1:
                self.mail_date = line.rpartition("Date: ")[2].lstrip(' ')
            if line.find("Sale date: ") != -1:
                self.mail_date = line.rpartition("Sale date: ")[2].lstrip(' ')
                logging.debug(line)
            if line.find("Seller:") != -1:  # Split mail here...
                idxs.append(plist.index(line))
                logging.debug(line)
            if line.find("Item name:") != -1: # or here
                idxs.append(plist.index(line))
                logging.debug(line)   
            if line.find("Subtotal:") != -1: # End of split here...
                idxs.append(plist.index(line))
            if line.find("You've sold your eBay item:") != -1: # or here...
                idxs.append(plist.index(line))
                
            if line.find("Postage discount from seller ") != -1:
                pdidx = plist.index(line)
        idxs.sort()
        print idxs
        for i in range(len(idxs)-1):
            pl = plist[idxs[i]:idxs[i+1]]
            if pdidx: pl.append(plist[pdidx])
            purchase = Purchase(pl, self.purchase_type)
            self.purchases.append(purchase)
            

##### END CLASS EBAYBILL ############



# START HERE
if __name__ == "__main__":
    '''
    We can recieve input that looks like:
    "/home/mikee/claws_mail/E Bay/269" "/home/mikee/claws_mail/E Bay/327" "/home/mikee/claws_mail/E Bay/326" "/home/mikee/claws_mail/E Bay/265" "/home/mikee/claws_mail/E Bay/335" "/home/mikee/claws_mail/E Bay/285" "/home/mikee/claws_mail/E Bay/303" "/home/mikee/claws_mail/E Bay/307"
    '''
    
    # Test for insufficient args
    if len(sys.argv) < 1:
        print "No arguments supplied"
        sys.exit(1)
        
    #pysession = pycash.Session()
    #pysession.open()
    MAILFILES = sys.argv[2:]# May be more than one
    TYPE =  sys.argv[1].upper()
    for MAILFILE in MAILFILES:
        logging.debug(MAILFILE)
        #continue
        ebay_mail = EbayMail(MAILFILE, TYPE)
        plain = ebay_mail.get_plain_mail(ebay_mail.msg)
        #print plain
        plist = plain.lstrip(' ').decode('ascii','ignore').encode('utf8').split('\n')
        ebay_mail.parse_mail(plist)
        
        #sys.exit(1)
        print "\nParsing done, now inserting the data into GnuCash\n"
        for p in ebay_mail.purchases:
            p.print_purchase()
            continue
            pysession.make_invoice_from_purchase(p)
    #pysession.close(save = True)
    print "\nFinished\n"



