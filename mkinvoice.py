#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
# Copyright 2014 Mike Evans <mikee@mutant-ant.com>
'''
Donationware.  If you use this then a donation to:
https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=3SQCKHY7AU3JU
would be greatly appreciated.
Please donate because, honestly, I need the money for food.
'''

import sys,os
from os.path import expanduser
import csv
import logging
import datetime
from decimal import Decimal
import ConfigParser


HERE = os.path.dirname(os.path.realpath(__file__))
HOME = expanduser("~")

Config = ConfigParser.ConfigParser()
Config.read(HERE+"/pycash.conf") # This needs to be in users home dir.

logging.basicConfig(level=logging.DEBUG, 
        format='%(module)s: LINE %(lineno)d: %(levelname)s: %(message)s')
#root_logger = logging.getLogger()
#root_logger.disabled = False # Set to True do disable logging.

# Add the Gnucash Python stuff
sys.path.append('/home/mikee/progs/gnucash-maint/lib/python2.7/site-packages')
import gnucash
import gnucash.gnucash_business
from gnucash.gnucash_core_c import * # Type definitions.

 
# Change the next set of values to match your actual CnuCash account setup.
# The inflexability of accounts here may not suit everybodys taste but invoices can always
# be altered later.
try:
    EXPENSE_ACCOUNT = Config.get("CONFIG","EXPENSE_ACCOUNT")
    PAYABLE_ACCOUNT = Config.get("CONFIG","PAYABLE_ACCOUNT")
    XFER_ACCOUNT = Config.get("CONFIG","XFER_ACCOUNT")
    CURRENCY = Config.get("CONFIG","CURRENCY") # Probably should get the account default currency.  TODO
    PAY_BILL = Config.getboolean("CONFIG","PAY_BILL") # Boolean
    POST_BILL = Config.getboolean("CONFIG","POST_BILL") # Boolean
except ConfigParser.Error as e:
    print "\n\nProblems reading config file.  Check values."
    print e
    sys.exit(1)
#logging.debug(type(XFER_ACCOUNT))


class Item():
    ''' A line in an invoice.
    '''
    date = None
    description = None
    action = None
    account = None
    quantity = None
    unit_price = None
    discount_type = None
    discount = None
    taxable = None
    tax_included = None
    tax_table = None
    
    
    def __init__(self):
        pass
        
    def make_item(self, params):
        '''
        @params a complete item line of data as a list of string values or booleans.  Need ALL of them
        '''
        try:
            self.date = params[0]
            self.description = params[1]
            self.action = params[2]
            self.account = params[3]
            self.quantity = params[4]
            self.unit_price = params[5]
            self.discount_type = params[6]
            self.discount = params[7]
            self.taxable = params[8]
            self.tax_included = params[9]
            self.tax_table = params[10]
        except Exception as e:
            print e
            return False
        return True
            
        
        
########### END ITEMCLASS ############


class Invoice():
    ''' All data needed to create an invoice
    Type defaults to GNC_INVOICE_CUST_INVOICE
    '''
    invoice_type = GNC_INVOICE_CUST_INVOICE#  or GNC_INVOICE_VEND_INVOICE, GNC_INVOICE_EMPL_INVOICE or XXX_CREDIT_NOTE
    invoice_id = None
    owner_id = None # Customer, vendor, employee or job
    owner = None
    items = None
    date_opened = None
    date_posted = None
    posted_account = None
    bill_terms = None
    billing_id = None
    notes = None
    
    
    def __init__(self):
        self.items = []
        self.owner_id = ''
        #self.invoice
    
    def add_item(self, item):
        self.items.append(item)

########### END INVOICE CLASS ############
    

class Session():
    def __init__(self, ):
        self.gnufile = HERE + "/" + Config.get("CONFIG","GNUFILE");
        #logging.debug(self.gnufile)
        return
        
    def open(self):
        ''' This uses the GnuCash XLM file as a data store.  If you are experimenting 
        with DB storage you will have to edit this section to suit. Note that GnuCash
        recommends using the XML file storage for production use as the database storage
        is still in development and should only be used for testing.
        '''
        try:
          self.session = gnucash.Session("xml://%s" % self.gnufile, False, True)
        except gnucash.GnuCashBackendException as (errno):
          print "{0}".format(errno)
          print "Stopping.  Is Gnucash running?  Make sure GnuCash is not running \
                and that if you are using an XML file storage make sure that a \
                lock file doesn't exist in the gnucash file directory."
          quit(1)


        self.root = self.session.book.get_root_account()
        self.book = self.session.book
        self.comm_table = self.book.get_table()
        self.currency = self.comm_table.lookup("CURRENCY", CURRENCY)
        self.exp_account = self.root.lookup_by_full_name(EXPENSE_ACCOUNT)
        self.payable = self.root.lookup_by_full_name(PAYABLE_ACCOUNT)
        self.xfer_account = self.root.lookup_by_full_name(XFER_ACCOUNT)
        assert(self.xfer_account != None)
        assert(self.exp_account != None)
        assert(self.payable != None)
        
        
    def get_invoices(self, inv_type = GNC_INVOICE_CUST_INVOICE, is_paid = True, is_active = True):
        ''' 
        Get and return a list of Invoice objects
        Not using the is_ params here but leaving them here anyway for reference
        @param inv_type: type of invoices to get. Default to GNC_INVOICE_CUST_INVOICE
        @param is_paid True or False
        @param is_active True or False
        '''

        query = gnucash.Query()
        query.search_for("gncInvoice")
        query.set_book(self.book)

        #query.add_boolean_match([gnucash.INVOICE_IS_PAID], is_paid, gnucash.QOF_QUERY_AND)

        # active = JOB_IS_ACTIVE
        #query.add_boolean_match(gnucash.JOB_IS_ACTIVE, is_active, gnucash.QOF_QUERY_AND)

        # return only GNC_INVOICE_VEND_INVOICE type. From  gnucash.gnucash_core_c.
        pred_data = gnucash.QueryInt32Predicate(gnucash.QOF_COMPARE_EQUAL, inv_type)
        query.add_term([gnucash.INVOICE_TYPE], pred_data, gnucash.QOF_QUERY_AND)

        invoices = []

        for result in query.run():
            #invoices.append(gnucash_simple.invoiceToDict(gnucash.gnucash_business.Invoice(instance=result)))
            invoices.append(gnucash.gnucash_business.Invoice(instance=result))
        
        query.destroy()

        #return json.dumps(invoices)
        return invoices
        
        
    def test_exists_invoiceID(self,bid):
        invoice_list = self.get_invoices(self)
        for invoice in invoice_list:
            if invoice.GetBillingID() == str(bid): return True
        return False
        
        

    def close(self,save = False):
        if save: self.session.save() #
        self.session.end()
        self.session.destroy()
            
    def owner_search(self,name_string, max_id):
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
        
    def get_next_invoice_id(self, owner):
        assert type(owner) != None
        owner_type = owner.GetType()
        if  owner_type == GNC_OWNER_VENDOR:
            return self.book.BillNextID(owner)
        elif owner_type == GNC_OWNER_CUSTOMER:
            return self.book.InvoiceNextID(owner)
        elif owner_type == GNC_OWNER_EMPLOYEE:
            return None# TODO
        elif owner_type == GNC_OWNER_JOB:
            return None# TODO
        else :
            return None
            
    def get_gnc_owner(self, owner_id, owner_type):
        if  owner_type == GNC_OWNER_VENDOR:
            return self.book.VendorLookupByID(owner_id)
            
        elif owner_type == GNC_OWNER_CUSTOMER:
            return self.book.CustomerLookupByID(owner_id)
             
        elif owner_type == GNC_OWNER_EMPLOYEE:
            return None# TODO
        elif owner_type == GNC_OWNER_JOB:
            return None# TODO
        else :
            return None

    
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

    def make_invoice(self,invoice_object):
        ''' Create a gnc_invoice from an Invoice Object
        '''
        io = invoice_object
        today = datetime.date.today()
        logging.debug(str(io.invoice_type))
        if io.invoice_type == GNC_INVOICE_CUST_INVOICE:
            invoice = gnucash.gnucash_business.Invoice(self.book, io.invoice_id, self.currency, io.owner ) 
        if io.invoice_type == GNC_INVOICE_VEND_INVOICE:
            invoice = gnucash.gnucash_business.Bill(self.book, io.invoice_id, self.currency, io.owner )         
        logging.debug(type(invoice))
        invoice.SetNotes(io.notes)
        invoice.SetBillingID(io.billing_id)
        invoice.SetDateOpened(datetime.datetime.strptime(io.date_opened,"%Y-%m-%d"))
        # Add each line item entry
        for i in io.items:
            entry_date = datetime.datetime.strptime(i.date, "%Y-%m-%d")
            account = self.root.lookup_by_full_name(i.account)
            entry = gnucash.gnucash_business.Entry(self.book, invoice)
            entry.SetDateEntered(entry_date)
            entry.SetDate(entry_date)
            entry.SetDescription (i.description)
            entry.SetQuantity(gnucash.GncNumeric(int(i.quantity )))
            gnc_price = gnucash.GncNumeric((i.unit_price*100), 100) ## = pricex100 then set denom to 100!
            entry.SetAction(i.action)
            
            if io.invoice_type == GNC_INVOICE_CUST_INVOICE:
                entry.SetInvPrice(gnc_price)
                entry.SetInvAccount(account)
                #logging.info(entry.GetBillPrice().num())
                entry.SetInvTaxTable(self.book.TaxTableLookupByName(i.tax_table))
                entry.SetInvTaxable(False)
                entry.SetInvTaxIncluded(False)
            
            if io.invoice_type == GNC_INVOICE_VEND_INVOICE:
                entry.SetBillPrice(gnc_price)
                entry.SetBillAccount(account)
                #logging.info(entry.GetBillPrice().num())
                entry.SetBillTaxTable(self.book.TaxTableLookupByName(i.tax_table))
                entry.SetBillTaxable(False)
                entry.SetBillTaxIncluded(False)
            
        #if POST_BILL: txn = io.PostToAccount(self.payable,
        #                self.invoice_date, self.invoice_date, "Yay!", True, False)
        
        if POST_BILL:#Pay FIXME ? Or don't.
            '''vendor.ApplyPayment(invoice,
                            self.payable,
                            self.xfer_account,
                            gnc_price,
                            gnucash.GncNumeric(1,1),
                            self.invoice_date,
                            "memo","num")
            '''
            pass
            
            
################################################################################             
# Test malarky
def test():
    invoice = Invoice()
    # Populate invoice
    invoice.owner_id = '000001'
    invoice.date_opened = "2014-05-26"
    item = Item()
    if not item.make_item(["2014-05-29", "Bobcat. Live", "EA","Income.Earned Income", 1, 12.26, "%", 0, False,False,"VAT"]):
        quit(1)
    print item.description
    invoice.add_item(item)
    #quit(0)
    session = Session()
    session.open()
    gnc_owner = session.get_gnc_owner(invoice.owner_id,GNC_OWNER_CUSTOMER)
    print "Owner name:",gnc_owner.GetName()
    invoice.invoice_id = session.get_next_invoice_id(gnc_owner)
    print "Invoice number:",invoice.invoice_id
    invoice.owner = gnc_owner
    session.make_invoice(invoice)


    session.close(True)
    
################################################################################        
# YOUR CODE STARTS HERE
if __name__ == "__main__":
    test()
    
    
    
    
   
