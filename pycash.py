#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
'''
An object to represent averything in a Gnucash Invoice/Bill
'''

import sys
import csv
import logging
import datetime
from decimal import Decimal

logging.basicConfig(level=logging.DEBUG, format='%(module)s: LINE %(lineno)d: %(levelname)s: %(message)s')


# Add the Gnucash Python stuff
sys.path.append('/home/mikee/progs/gnucash-master/lib/python2.7/site-packages')
import gnucash
import gnucash.gnucash_business
#import gnucash.gnucash_core.GnuCashBackendException
#from gnucash.gnucash_business import Vendor, Invoice, Entry

class Session():
    def __init__(self, gnufile):
        self.gnufile = gnufile;
        return
        
    def open(self):
        try:
          self.session = gnucash.Session("xml://%s" % self.gnufile, False, True)
        except gnucash.GnuCashBackendException as (errno):
          print "{0}".format(errno)
          print "Unknown error occurred. Stopping"
          quit(1)


        self.root = self.session.book.get_root_account()
        self.book = self.session.book
        #self.sales = self.root.lookup_by_name('Sales')
        #self.bank  = self.root.lookup_by_name('Business Account')
        #self.assets = self.root.lookup_by_name("Assets")
        #self.recievables = self.assets.lookup_by_name("Accounts Recievable")
        #self.income = self.root.lookup_by_name("Sales")
        self.comm_table = self.book.get_table()
        self.currency = self.comm_table.lookup("CURRENCY", "GBP")
        
    def close(self,save = False):
        if save: self.session.save() #
        self.session.end()
        self.session.destroy()
            
    def vendor_search(self,name_string, max_id):
        ''' Find vendor by name. 
        This probably needs to handle leading and trailing spaces.
        '''
        found = False
        search_id=1
        while  search_id < max_id:
            search_string = '%0*d' % (6, search_id)
            possible = self.book.VendorLookupByID(search_string)
            if possible: 
                if possible.GetName() == name_string:
                    return  possible.GetID(), name_string
            search_id += 1
        return False
        
    def invoice_search(self,name_string, max_id): # this can also be a bill
        vendor_search(name_string, max_id)
        
    def make_new_vendor(self,vendor_name, address1="The Internet"):
        new_vendor = gnucash.gnucash_business.Vendor(self.book,self.book.VendorNextID(),self.currency)
        new_vendor.BeginEdit()
        new_vendor.SetName(vendor_name)
        # Has to have at least one address line
        addr =  new_vendor.GetAddr()
        addr.BeginEdit()
        addr.SetName(vendor_name)
        addr.SetAddr1(address1)
        addr.CommitEdit()
        new_vendor.CommitEdit()
    
    def new_vendor_from_object(self,vendor, update = False):
        ''' Create a vendor from a Vendor object.
        @Param update IF set to True then update the vendor TODO
        '''
        new_vendor = gnucash.gnucash_business.Vendor(self.book,
            self.book.VendorNextID(),
            self.currency)
        new_vendor.BeginEdit()
        new_vendor.SetName(vendor.name)
        new_vendor.CommitEdit()
        addr = new_vendor.GetAddr()
        addr.BeginEdit()
        addr.SetName(vendor.addr_name)
        try:addr.SetAddr1(vendor.addr[0])
        except:pass
        try:addr.SetAddr2(vendor.addr[1])
        except:pass
        try:addr.SetAddr3(vendor.addr[2])
        except:pass
        try:addr.SetAddr4(vendor.addr[3])
        except:pass
        addr.CommitEdit()
        return new_vendor.GetID()
    
    def add_invoice_items(self, invoice):
        
        return

    def make_invoice_from_purchase(self,purchase_object):
        ''' Create an invoice from a Purchase Object
        '''
        po = purchase_object
        #print str(po.vendor.addr[0])
        account = self.root.lookup_by_full_name("Business Expenses.Miscellaneous")
        assert(account != None)
        print account
        v_name = po.vendor.name
        vid = ''
        #logging.info(self.vendor_search(v_name, 100))
        if not self.vendor_search(v_name, 100):
            vid = self.new_vendor_from_object(po.vendor)[0]
        
        vid = self.vendor_search(v_name, 100)[0]
            
        vendor =  self.book.VendorLookupByID(vid)
        bill_num = po.items[0].attribs['transaction']
        bill = gnucash.gnucash_business.Invoice(self.book, bill_num, self.currency, vendor ) 
        bill.SetNotes("Transaction ID: " + po.items[0].attribs['transaction'])
        assert(isinstance(bill, gnucash.gnucash_business.Invoice))
        bill.SetDateOpened(datetime.date.today())
        # Add each line item entry
        for i in po.items: 
            entry = gnucash.gnucash_business.Entry(self.book, bill)
            entry.SetDate(datetime.date.today()) # FIXME get from mail.
            entry.SetDate(datetime.datetime.strptime(i.attribs['Paid on'], "%d-%b-%y"))
            entry.SetDateEntered(datetime.date.today())
            entry.SetDescription (i.attribs['Item name'])
            logging.info(entry.GetDate())
            entry.SetAction("EA")
            entry.SetBillAccount(account)
            entry.SetQuantity(gnucash.GncNumeric(int(i.attribs['Quantity']) ))
            gnc_price = gnucash.GncNumeric(int(Decimal(i.attribs['Price'])*100), 100) ## = pricex100 then set denom to 100!
            entry.SetBillPrice(gnc_price)
            logging.info(entry.GetBillPrice().num())
            entry.SetBillTaxTable(self.book.TaxTableLookupByName("VAT"))
            entry.SetBillTaxable(False)
            entry.SetBillTaxIncluded(False)
            #bill.AddEntry(entry)
            
    
################################################################################        

    
# Test code goes here.
if __name__ == "__main__":
    session = Session("example.gnucash")
    session.open()
    print session.vendor_search("E Bay", 100)
    print session.vendor_search("quasarcomponents",100)
    session.close()
