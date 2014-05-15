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
import logging
import uuid

logging.basicConfig(level=logging.DEBUG, format='%(module)s: LINE %(lineno)d: %(levelname)s: %(message)s')

class Vendor:
    guid = None
    name = ''
    addr = []
    email = ''
    items = [] # List of items from this vendor.

    def __init__(self):
        self.guid = uuid.uuid4()
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
                        "P&amp;P price:", #
                        "Quantity:", #
                        "Item total:",  #
                        "Paid on")  #

    def __init__(self, item_data):
        # Object attributes
        self.attribs = {}
        self.guid = uuid.uuid4()
        # Do stuff
        self.parse_item_information(item_data)

    def parse_item_information(self,data):
        for line in data:
            for needle in self.item_search_terms:
                if line.find(needle) != -1:
                    self.attribs[needle.strip(':')] = line.rpartition(needle)[2].lstrip(' ')

    def print_items(self):
        #print self.attribs.items()
        for key, value in self.attribs.items():
            print key, '->', value

    def get_attribs(self):
        return attribs

#### END CLASS ITEM #######


class Purchase:
    ''' A purchase from a single vendor and may be one or more items.
    Probably should be called purchase?
    '''
    items = None # A Purchase has one or more items
    vendor = None # from a single vendor
    purchase_data = None
    guid = None

    def __init__(self, purchase_data):
        self.guid = uuid.uuid4()
        self.vendor =  Vendor()
        self.items = []
        self.purchase_data =  purchase_data
        if not type(purchase_data) == list: return
        #logging.info("\n\n"+str(self.guid)+"\n"+str(self.purchase_data)) ## DEBUG
        self.parse_vendor(self.purchase_data)
        self.parse_purchase(self.purchase_data)

    def parse_vendor(self, data):
        self.vendor.name=data[0].rpartition('Seller:')[2].lstrip(' ') # Always
        for i in range(4,8):
            if data[i][0:3] == '---': break ## See mail.txt for why
            self.vendor.addr.append(data[i].lstrip(' ').rstrip(' '))

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

    def get_items(self):
        return self.items

    def get_vendor(self):
        return self.vendor

###### END CLASS Purchase ########


class EbayMail():
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
        #logging.info(str(idxs))
        # Each section we have defined above is a purchase
        for i in range(len(idxs)-1):
            purchase = Purchase(plist[idxs[i]:idxs[i+1]])
            self.purchases.append(purchase)

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

ebay_mail = EbayMail(MAILFILE,GNUFILE, ACCOUNT)
plain = ebay_mail.get_plain_mail(ebay_mail.msg)
plist = plain.lstrip(' ').decode('ascii','ignore').encode('utf8').split('\n')
ebay_mail.parse_mail(plist)
for p in ebay_mail.purchases:
    print p.guid
    #print p.purchase_data
    print "\tVendor -",p.vendor.guid, p.vendor.name
    for i in p.items:
        print "\tItem -",i.guid, i.attribs['Item name']

    #p.print_purchase()

