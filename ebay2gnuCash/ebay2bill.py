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

import sys, os
import csv
import email
import pycash
import json
import copy
import logging
import uuid
import fcntl
import time
from decimal import Decimal

logging.basicConfig(level=logging.DEBUG, format='%(module)s: LINE %(lineno)d: %(levelname)s: %(message)s')

class Vendor:
    guid = None
    items = [] # List of items from this vendor.

    def __init__(self):
        self.guid = uuid.uuid4()
        self.addr = []
        self.email = ''
        self.name = ''
        self.addr_name = ''
        return

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
    # Class attributes
    attribs = None
    guid = None
    item_search_terms=( "Item name", #
                        "Item number:", #
                        "transaction::",  #
                        "Price:", #
                        #"P&amp;P price:", # This is a special case and needs to be handled.  FIXME
                        "Quantity:", #
                        "Item total:",  #
                        "Paid on ",
                        "transaction::")  #

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
                if line.find(needle) != -1:
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
    #attribs = {}
    def __init__(self, data):
        # Define stuff
        #self.attribs = {}
        self.search_term="P&amp;P price:"
        self.postage = 0.0
        self.seller = ''
        self.discount = 0.0
        # Do stuff
        self.parse_item_information(data)
        #logging.info(data)
        
    def parse_item_information(self,data):
        for line in data:
            #print '-------\n',line
            if line.find(self.search_term) != -1:
                try:
                    self.postage += float(line.rpartition(self.search_term)[2].lstrip(' ').strip('£'))
                    #self.attribs['Postage and packing'] = self.postage
                except: pass
                    #self.attribs['Postage and packing'] = self.postage
                #logging.info(self.postage)
            if line.find("Postage discount from seller") != -1: # Discount line
                #logging.info("Found discount for this seller.")
                #logging.info(line)
                self.discount = float(line.rpartition(("Postage discount from seller").lstrip().strip('£'))[2].rpartition(":")[2].lstrip())
                self.seller = line.rpartition("Postage discount from seller")[2].rpartition(":")[0].strip()
        #logging.info("Discount = %f",self.discount)
        #if self.postage > 0:
        #    self.postage -= self.discount
        #    logging.info("%s postage = %f",self.seller, self.postage)
        
    # TODO Deal with postage discounts for multiples like:
    # Postage discount from seller  bright_components : £1.98 
    
    
#### END CLASS POSTAGE ########
class Purchase:
    ''' A purchase from a single vendor and may be one or more items.
    Probably should be called purchase?
    '''
    items = None # A Purchase has one or more items
    vendor = None # from a single vendor
    purchase_data = None
    guid = None
    #postage = Postage(None)

    def __init__(self, purchase_data):
        self.guid = uuid.uuid4()
        self.vendor =  Vendor()
        self.items = []
        self.purchase_data =  purchase_data
        if not type(purchase_data) == list: return
        #logging.info("\n\n"+str(self.guid)+"\n"+str(self.purchase_data)) ## DEBUG
        self.parse_vendor(self.purchase_data)
        self.parse_purchase(self.purchase_data)
        #self.postage_item = self.parse_postage(self.purchase_data)
        self.do_postage(self.purchase_data)
        
    def parse_vendor(self, data):
        self.vendor.name=data[0].rpartition('Seller:')[2].lstrip(' ') # Always
        if data[3] [0:3] != '---':
            self.vendor.addr_name=data[3].rpartition('Seller:')[2].lstrip(' ') # Always
            for i in range(4,8):
                if data[i][0:3] == '---':
                    self.vendor.addr.append(self.vendor.name) # Need this or we get errors later
                    break ## See mail.txt for why
                self.vendor.addr.append(data[i].lstrip(' ').rstrip(' '))
        else: 
            self.vendor.addr_name = data[0].rpartition('Seller:')[2].lstrip(' ')
            self.vendor.addr.append("Ebay")

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

    def print_purchase(self):
        print '\nVendor Data:\n'
        self.vendor.print_vendor()
        print '\nItem data:\n'
        for item in self.items:
            item.print_items()
        return
        
    def do_postage(self, data):
        postage_object = Postage(data)
        postage = postage_object.postage
        if postage_object.seller == self.vendor.name:
            postage -= postage_object.discount
        item = Item(None)
        item.attribs['Item name'] = "Postage and packing" 
        item.attribs['Quantity'] = 1 
        item.attribs['Price'] = postage
        self.items.append(item)
        
        
        
    def get_items(self):
        return self.items

    def get_vendor(self):
        return self.vendor

###### END CLASS Purchase ########


class EbayMail():
    purchases = [] # List of Purchases in email, usually just the one but mutiples are possible.
    mail_date = ''
    def __init__(self,billmail, cashfile):
        self.INFILE = billmail
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
        #logging.info(type(plist))
        #print plist
        idxs = [] # list of occurrences.
        pdidx = None
        for line in plist:
            if line.find("Date: ") != -1:
                self.mail_date = line.rpartition("Date: ")[2].lstrip(' ')
            if line.find("Seller:") != -1:
                #print line
                idxs.append(plist.index(line))
            if line.find("Subtotal:") != -1:
                #print line
                idxs.append(plist.index(line))
            if line.find("Postage discount from seller ") != -1:
                pdidx = plist.index(line)
                #logging.info(plist[pdidx])
            idxs.sort()
            #logging.info(idxs)
        for i in range(len(idxs)-1):
            pl = plist[idxs[i]:idxs[i+1]]
            if pdidx: pl.append(plist[pdidx])
            #logging.info(pl)
            purchase = Purchase(pl)
            self.purchases.append(purchase)
            

##### END CLASS EBAYBILL ############



# START HERE
# Default values are convenience for my test runs.  Not at all useful to anyone else
# without editing.  Arguably I should be calling this from a test Bash script.
# Make this accept multiple files alse we get BACKEnD_LOCKED errors when mutiple files
# are selected in Claws-Mail.
if __name__ == "__main__":
    '''pid_file = 'program.pid'
    fp = open(pid_file, 'w')
    #while 1:
    try:
        fcntl.lockf(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)        
    except IOError:
        print "another instance is running"
        sys.exit(1)
        #print "waiting"
        #time.sleep(5)
    #main()
    '''
    '''
    We can recieve input that looks like:
    "/home/mikee/claws_mail/E Bay/269" "/home/mikee/claws_mail/E Bay/327" "/home/mikee/claws_mail/E Bay/326" "/home/mikee/claws_mail/E Bay/265" "/home/mikee/claws_mail/E Bay/335" "/home/mikee/claws_mail/E Bay/285" "/home/mikee/claws_mail/E Bay/303" "/home/mikee/claws_mail/E Bay/307"
    /home/mikee/claws_mail/E Bay/269
    Note the last one isn't quoted and is a copy of the first one. :(
    So we either parse this input or we gat called mutipl times and use locking. :(
    '''
    HERE = os.path.dirname(os.path.realpath(__file__))
    
    # Test for insufficient args
    if len(sys.argv) < 2:
        print "No arge supplied"
        sys.exit(1)
        
    if sys.argv[1] != None:
        GNUFILE = sys.argv[1]
    else:
        GNUFILE = HERE+"/example.gnucash"
    GNUFILE = HERE+"/example.gnucash"
    print "GNUFILE",GNUFILE

    try: MAILFILES = sys.argv[2:]# May be more than one
    except: MAILFILES = "Confirmation of your order of Voltage Regulator LM7805 LM7812 LM317T Adjustable Linear 7805 7812 UK..."
    for MAILFILE in MAILFILES:
        print "foo",MAILFILE,"bar"
        #continue
        ebay_mail = EbayMail(MAILFILE,GNUFILE)
        plain = ebay_mail.get_plain_mail(ebay_mail.msg)
        plist = plain.lstrip(' ').decode('ascii','ignore').encode('utf8').split('\n')
        ebay_mail.parse_mail(plist)
        
        #sys.exit(1)
        print "\nParsing done, now inserting the data into GnuCash\n"
        # ooh jthis innefficient FIXME
        pysession = pycash.Session(GNUFILE)
        pysession.open()
        for p in ebay_mail.purchases:
            pysession.make_invoice_from_purchase(p)
        pysession.close(save = True)



