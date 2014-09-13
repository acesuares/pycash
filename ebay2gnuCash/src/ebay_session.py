#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
# Copyright 2014 Mike Evans <mikee@mutant-ant.com>
'''
An object to represent averything in a Gnucash Invoice/Bill
'''

import sys,os
from os.path import expanduser
import csv
import logging
from logging import debug, info
import datetime
from decimal import Decimal
import ConfigParser


HERE = os.path.dirname(os.path.realpath(__file__))
HOME = expanduser("~")

Config = ConfigParser.ConfigParser()
Config.read(HOME+"/.pybay.conf") # This needs to be in users home dir.

logging.basicConfig(level=logging.DEBUG, 
        format='%(module)s: LINE %(lineno)d: %(levelname)s: %(message)s')
#root_logger = logging.getLogger()
#root_logger.disabled = False # Set to True do disable logging.

# Add the Gnucash Python stuff
sys.path.append('/home/mikee/progs/gnucash-maint/lib/python2.7/site-packages')
import gnucash
import gnucash.gnucash_business
from gnucash.gnucash_core_c import * # Type definitions.

# gnucash-python doesn't have the functions we need to get the company info
# from the book. This ugly hack gets the job done.
import ctypes
libgnc_qof = ctypes.CDLL('/home/mikee/progs/gnucash-maint/lib/libgnc-qof.so') #maint
#libgnc_qof = ctypes.CDLL('/home/mikee/progs/gnucash-master/lib/gnucash/libgncmod-engine.so') # master
libgnc_qof.kvp_value_get_string.restype = ctypes.c_char_p
libgnc_qof.kvp_frame_get_slot_path.restype = ctypes.c_void_p
libgnc_qof.qof_book_get_slots.restype = ctypes.c_void_p


class BusinessSlots(object):
    ''' Get our business data with call like:
    slots = BusinessSlots(book)
    slots['Company ID']
    slots['Company Contact Person']
    slots['Company Email Address']
    slots['Company Phone Number']
    slots['Company Address']
    slots['Company Website URL']
    '''
    def __init__(self, book):
        self._slots = libgnc_qof.qof_book_get_slots(ctypes.c_void_p(book.instance.__long__()))
    def __getitem__(self, key):
        kvpv = libgnc_qof.kvp_frame_get_slot_path(
        self._slots, 'options', 'Business', key, None)
        val = libgnc_qof.kvp_value_get_string(kvpv)
        return val


    
# Change the next set of values to match your actual CnuCash account setup.
# The inflexability of accounts here may not suit everybodys taste but bills can always
# be altered later.
try:
    EXPENSE_ACCOUNT = Config.get("CONFIG","EXPENSE_ACCOUNT")
    PAYABLE_ACCOUNT = Config.get("CONFIG","PAYABLE_ACCOUNT")
    RECEIVABLE_ACCOUNT = Config.get("CONFIG","RECEIVABLE_ACCOUNT")
    XFER_ACCOUNT = Config.get("CONFIG","XFER_ACCOUNT")
    CURRENCY = Config.get("CONFIG","CURRENCY") # Probably should get the account default currency.  TODO
    PAY_BILL = Config.getboolean("CONFIG","PAY_BILL") # Boolean
    POST_BILL = Config.getboolean("CONFIG","POST_BILL") # Boolean
    INCOME_ACCOUNT = Config.get("CONFIG","INCOME_ACCOUNT") #
    REIMBERSED_ACCOUNT = Config.get("CONFIG","REIMBERSED_ACCOUNT")
    PAYPAL_ACCOUNT = Config.get("CONFIG","PAYPAL_ACCOUNT")
except ConfigParser.Error as e:
    print "\n\nProblems reading config file.  Check values.\n"
    print e
    sys.exit(1)
#logging.debug(type(XFER_ACCOUNT))

class Session():
    def __init__(self):
        self.gnufile = Config.get("CONFIG","GNUFILE");
        #logging.debug(self.gnufile)
        #self.gnufile = "/home/mikee/Projects/pycash/example.gnucash"
        #return
        
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
        self.reimbersed_account = self.root.lookup_by_full_name(REIMBERSED_ACCOUNT)
        self.income_acct = self.root.lookup_by_full_name(INCOME_ACCOUNT)
        self.payable = self.root.lookup_by_full_name(PAYABLE_ACCOUNT)
        self.receivable = self.root.lookup_by_full_name(RECEIVABLE_ACCOUNT)
        self.xfer_account = self.root.lookup_by_full_name(XFER_ACCOUNT)
        #self.xfer_account = self.root.lookup_by_full_name(PAYPAL_ACCOUNT)
        assert(self.xfer_account != None)
        assert(self.exp_account != None)
        assert(self.payable != None)
        #assert(self.reimbersed_account != None)
        
        
    def get_bills(self, is_paid = True, is_active = True):
        ''' 
        Get and return a list of Invoice objects
        Not using the params here but leave them here anyway for reference
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
        pred_data = gnucash.QueryInt32Predicate(gnucash.QOF_COMPARE_EQUAL,  GNC_INVOICE_CUST_INVOICE)
        query.add_term([gnucash.INVOICE_TYPE], pred_data, gnucash.QOF_QUERY_AND)
        pred_data = gnucash.QueryInt32Predicate(gnucash.QOF_COMPARE_EQUAL,  GNC_INVOICE_VEND_INVOICE)
        query.add_term([gnucash.INVOICE_TYPE], pred_data, gnucash.QOF_QUERY_OR)
        invoices = []

        for result in query.run():
            #invoices.append(gnucash_simple.invoiceToDict(gnucash.gnucash_business.Invoice(instance=result)))
            invoices.append(gnucash.gnucash_business.Invoice(instance=result))
        
        query.destroy()

        #return json.dumps(invoices)
        return invoices
        
        
    def test_exists_billingID(self,bid):
        bill_list = self.get_bills(self)
        for bill in bill_list:
            #debug(bill.GetBillingID())
            if bill.GetBillingID() == str(bid): return True
        return False
        
        

    def close(self,save = False):
        if save: self.session.save() #
        self.session.end()
        self.session.destroy()
            
    def person_search(self,name_string, max_id, purchase_type):
        ''' Find vendor by name. 
        This probably needs to handle leading and trailing spaces.
        '''
        found = False
        search_id=1
        while  search_id < max_id:
            possible = None
            search_string = '%0*d' % (6, search_id)
            if purchase_type == "PURCHASE":
                possible = self.book.VendorLookupByID(search_string)
                #logging.debug(possible)
            if purchase_type == "SALE":
                possible = self.book.CustomerLookupByID(search_string)
            if possible: 
                if possible.GetName() == name_string:
                    return  possible.GetID(), name_string
            search_id += 1
        return False
        
    def invoice_search(self,name_string, max_id): # this can also be a bill
        person_search(name_string, max_id)
        
    def make_new_person(self,person_name, address1, purchase_type):
        if purchase_type == "PURCHASE":
            new_person = gnucash.gnucash_business.Vendor(self.book,self.book.VendorNextID(),self.currency)
        elif purchase_type == "SALE":
            new_person = gnucash.gnucash_business.Customer(self.book,self.book.CustomerNextID(),self.currency)
        new_person.BeginEdit()
        new_person.SetName(person_name)
        # Has to have at least one address line
        addr =  new_person.GetAddr()
        addr.BeginEdit()
        addr.SetName(person_name)
        addr.SetAddr1(address1)
        addr.CommitEdit()
        new_person.CommitEdit()
    
    def new_person_from_object(self,person, po, update = False):
        ''' Create a person from a Person object.
        @Param update IF set to True then update the person TODO: this.
        '''
        new_person = None
        if po.purchase_type == "PURCHASE":
            new_person = gnucash.gnucash_business.Vendor(self.book,
                self.book.VendorNextID(),
                self.currency)
        if po.purchase_type == "SALE":
            new_person = gnucash.gnucash_business.Customer(self.book,
                self.book.CustomerNextID(),
                self.currency)
        new_person.BeginEdit()
        new_person.SetName(person.name)
        new_person.CommitEdit()
        addr = new_person.GetAddr()
        addr.BeginEdit()
        addr.SetName(person.addr_name)
        try:addr.SetAddr1(person.addr[0])
        except:pass
        try:addr.SetAddr2(person.addr[1])
        except:pass
        try:addr.SetAddr3(person.addr[2])
        except:pass
        try:addr.SetAddr4(person.addr[3])
        except:pass
        addr.CommitEdit()
        return new_person.GetID()
    
    def add_invoice_items(self, invoice):
        
        return

    def make_invoice_from_purchase(self,purchase_object):
        ''' Create an invoice from a Purchase Object
        '''
        person = None
        bill = None
        bill_date = None
        bill_num = None
        invoice = None
        invoice_date = None
        po = purchase_object
        p_name = po.person.name
        pid = ''
        entry = None
        post_and_delivey = None
        if not self.person_search(p_name, 100, po.purchase_type):
            pid = self.new_person_from_object(po.person, po)[0]
        #return ## DEBUG
        self.today = datetime.date.today()
        pid = self.person_search(p_name, 100, po.purchase_type)[0]
        billingID = po.items[0].attribs['transaction']
        # Check for duplicate invoice IDs
        test = self.test_exists_billingID(billingID)
        logging.info(billingID)
        logging.info(test)
        if test == True:
            print "We have a duplicate Billing ID.  Do a manual insert if required"
            return
        
        if po.purchase_type == "PURCHASE":
            #logging.info(self.vendor_search(v_name, 100))
            bill_date = datetime.date.today()
            person =  self.book.VendorLookupByID(pid)
            logging.debug(person.GetName())
            bill_num = self.book.BillNextID(person)
            bill = gnucash.gnucash_business.Bill(self.book, bill_num, self.currency, person ) 
            bill.BeginEdit()
            bill.SetDateOpened(bill_date)
            bill.SetBillingID(str(po.items[0].attribs['transaction']))

            assert(isinstance(bill, gnucash.gnucash_business.Invoice))
            bill.SetDateOpened(bill_date)
        if po.purchase_type == "SALE":
            person = self.book.CustomerLookupByID(pid)
            bill_date = datetime.date.today()
            bill_num = self.book.InvoiceNextID(person)
            bill = gnucash.gnucash_business.Invoice(self.book, bill_num, self.currency, person )
            assert(isinstance(bill, gnucash.gnucash_business.Invoice))
            bill.BeginEdit()
            bill.SetDateOpened(bill_date)
            bill.SetBillingID(str(po.items[0].attribs['transaction']))
            #
            
        # Add each line item entry
        for i in po.items:
            logging.debug(i.attribs)
            entry = gnucash.gnucash_business.Entry(self.book, bill)
            entry.BeginEdit()
            entry.SetDateEntered(bill_date)
            entry.SetDate(bill_date)
            entry.SetDescription (i.attribs['Description'])
            entry.SetAction("EA")
            if po.purchase_type == "PURCHASE":
                entry.SetQuantity(gnucash.GncNumeric(int(i.attribs['Quantity']) ))
                gnc_price = gnucash.GncNumeric(int(Decimal(i.attribs['Price'])*100), 100) ## = pricex100 then set denom to 100!
                entry.SetBillPrice(gnc_price)
                entry.SetBillAccount(self.exp_account)
                entry.SetBillTaxTable(self.book.TaxTableLookupByName("VAT"))
                entry.SetBillTaxable(False)
                entry.SetBillTaxIncluded(False)
            if po.purchase_type == "SALE":
                entry.SetQuantity(gnucash.GncNumeric(int(i.attribs['Quantity'])))
                gnc_price = gnucash.GncNumeric(int(Decimal(i.attribs['Price'])*100), 100) ## = pricex100 then set denom to 100!
                entry.SetInvPrice(gnc_price)
                post_and_delivey = gnc_price
                if entry.GetDescription() == "Postage and packing":
                    # This needs to be funneled into Expenses.P&P
                    entry.SetInvAccount(self.reimbersed_account)
                else: entry.SetInvAccount(self.income_acct) # 
                entry.SetInvTaxTable(self.book.TaxTableLookupByName("VAT"))
                entry.SetInvTaxable(False)
                entry.SetInvTaxIncluded(False)
            entry.CommitEdit()
                
        bill.CommitEdit()
        

        POST_BILL = False
        if POST_BILL:
            if po.purchase_type == "SALE":
                txn = bill.PostToAccount(self.receivable,
                    bill_date, bill_date, "Ebay Sale", True, False)
                # At this point the purcaser has paid so we can apply payment too
                #gncOwnerApplyPayment (const GncOwner *owner, Transaction *txn, GList *lots,
                #      Account *posted_acc, Account *xfer_acc,
                #      gnc_numeric amount, gnc_numeric exch, Timespec date,
                #      const char *memo, const char *num, gboolean auto_pay);
                person.ApplyPayment(None,None,
                            self.receivable,
                            self.xfer_account,
                            bill.GetTotal(),
                            gnucash.GncNumeric(1,1),
                            bill_date,
                            "Payment received",bill_num, True)
                # Now deal with postage and packing
                # These will come from PayPal.  But the amount charged will not
                # be the same as PayPal account as that's only postage and doesn't
                # include packing.  Packing will probably have been purchased beforehand and
                # could have been paid from any account.

        PAY_BILL = False
        if PAY_BILL:
            '''
            Payments go into PayPal then dispersed into:
            Postage
            Ebay Fees
            PayPal Fees.
            But the fees get taken BEFORE we get it so PayPal contains the amount AFTER
            fees are removed, THEN we remove postage and allocate commission as
            income and COGS as expenses.
            '''
            pass

        
            '''    
            else:
                txn = bill.PostToAccount(self.payable,
                    bill_date, bill_date, "Ebay Purchase", True, False)
            '''


            
################################################################################        

if __name__ == "__main__":
    #print Config.items("CONFIG")
    session = Session()
    session.open()
    invoices = session.get_bills(True, True)
    for invoice in invoices:
        if invoice.GetBillingID() != "": 
            print invoice.GetBillingID()
    session.close()
    pass
    
    
   
