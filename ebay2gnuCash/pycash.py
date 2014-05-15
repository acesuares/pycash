#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
'''
An object to represent averything in a Gnucash Invoice/Bill
'''

import sys
import csv
import logging

logging.basicConfig(level=logging.DEBUG, format='%(module)s: LINE %(lineno)d: %(levelname)s: %(message)s')


# Add the Gnucash Python stuff
sys.path.append('/home/mikee/progs/gnucash-master/lib/python2.7/site-packages')
import gnucash
import gnucash.gnucash_business

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
        self.sales = self.root.lookup_by_name('Sales')
        self.bank  = self.root.lookup_by_name('Business Account')
        self.assets = self.root.lookup_by_name("Assets")
        self.recievables = self.assets.lookup_by_name("Accounts Recievable")
        self.income = self.root.lookup_by_name("Sales")
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
                    return  True, name_string, search_string
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
    
    def new_vendor_from_object(self,vendor):
        #if type(vendor) != Vendor: return
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

    def make_invoice_from_purchase(self,purchase_object):
        ''' Create an invoice from a Purchase Object
        '''
        po = purchase_object
        print str(po.vendor.addr[0])
        #return
        v_name = po.vendor.name
        logging.info(self.vendor_search(v_name, 100))
        if not self.vendor_search(v_name, 100):
            #self.make_new_vendor(po.vendor.name)
            self.new_vendor_from_object(po.vendor)
            
        #invoice = Invoice(self.book, inv_num, self.currency, self.customer)
        

class Invoice():
    ID=None
    def __init__(self, book, inv_num,currency, customer):
        # Do type checking and assign
        try:
            assert(type(book) == gnucash.gnucash_core.Book)         
            assert(type(inv_num) == int or type(inv_num) == str)
            assert(type(currency) == gnucash.gnucash_core.GncCommodity)
            assert(type(customer) == gnucash.gnucash_business.Customer)
        except AssertionError:
            _,_,tb = sys.exc_info()
            
        self.customer = customer
        self.book = book
        self.inv_num = '%0*d' % (6, inv_num)
        self.currency = currency
        
        
    def add_entry(self, item):
        ''' An entry has the following data.
        '''
        entry = gnucash.gnucash_business.Entry(self.book, self)
        
    '''
    entry = gnucash.gnucash_business.Entry(book, invoice)
    entry.SetDate(datetime.date.today())
    entry.SetDateEntered(datetime.date.today())
    entry.SetDescription ("Some stuff I sold")
    entry.SetAction("Material")
    entry.SetInvAccount(income)
    entry.SetQuantity( GncNumeric(1) )
    gnc_price = GncNumeric(1040, 100) ## = price x 100 then set denom to 100
    entry.SetInvPrice(gnc_price)
    #entry.SetInvTaxTable(tax_table)
    entry.SetInvTaxIncluded(False)'''
    #def __init__(self, gnu_file):
    # invoice = Invoice(book, 'TEST', gbp, customer )    
    #    return
    
    
        
    
class Entry():
    book = None
    invoice = None
    date = None
    date_entered = None
    description = ""
    action = ""
    inv_account = ""
    quantity= 0
    price = 0
    tax_table = ""
    tax_included = False
    def __init__(self, invoice):
        if type() == gnucash.gnucash_business.Invoice: self.invoice = invoice
        
    ''' 
    An invoice may have many entries but has at least one.
    '''
    def add_line(line_data):
        
        return
        
class Address():
    '''
    add.BeginEdit                                add.SetAddr2
    add.ClearDirty                               add.SetAddr3
    add.CommitEdit                               add.SetAddr4
    add.Compare                                  add.SetEmail
    add.Create                                   add.SetFax
    add.Destroy                                  add.SetName
    add.Equal                                    add.SetPhone
    add.GetAddr1                                 add.add_constructor_and_methods_with_prefix
    add.GetAddr2                                 add.add_method
    add.GetAddr3                                 add.add_methods_with_prefix
    add.GetAddr4                                 add.decorate_functions
    add.GetEmail                                 add.do_lookup_create_oo_instance
    add.GetFax                                   add.get_instance
    add.GetName                                  add.instance
    add.GetPhone                                 add.ya_add_classmethod
    add.IsDirty                                  add.ya_add_method
    add.SetAddr1                                 
    ''' 
    
    
    
# Test code goes here.
if __name__ == "__main__":
    session = Session("example.gnucash")
    session.open()
    print session.vendor_search("E Bay", 100)
    print session.vendor_search("quasarcomponents",100)
    session.close()
