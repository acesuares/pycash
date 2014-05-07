#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
'''
An object to represent averything in a Gnucash Invoice/Bill
'''

import sys
import csv


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
        self.gbp = self.comm_table.lookup("CURRENCY", "GBP")
        
    def close(self,save = False):
        if save: session.save() #
        self.session.end()
        self.session.destroy()
        
    def make_invoice(self):
        def __init__(self):
            invoice = Invoice(book)
            
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
                    return  name_string, search_string
            search_id += 1
            
    def make_new_vendor(vendor_name, address1="The Internet"):
        new_vendor = gnucash.gnucash_business.Vendor(self.book,self.book.VendorNextID(),self.gbp)
        new_vendor.SetName(vendor_name)
        # Has to have at least one address line
        addr =  new_cust.GetAddr()
        addr.SetAddr1(address1)


        

        

class Invoice():
    ID=None
    def __init__(self,book, inv_num,currency, customer):
        # Do type checking and assign
        if type(book) == gnucash.gnucash_core.Book: self.book = book
        if type(inv_num) == int: self.inv_num = '%0*d' % (6, inv_num)
        if type(inv_num) == str: self.inv_num = inv_num
        if type(currency) == gnucash.gnucash_core.GncCommodity: self.currency = currency
        if type(customer) == gnucash.gnucash_business.Customer: self.customer = customer
    
    def make_entry():
        ''' An entry has the following data.
        '''
        entry = Entry(self.book)
        
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
    ''' 
    An invoice may have many entries but has at least one.
    '''
    def add_line(line_data):
        
        return
        
    
    
    
# Test code goes here.
if __name__ == "__main__":
    session = Session("example.gnucash")
    session.open()
    print session.vendor_search("E Bay", 100)
    session.close()
