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
sys.path.append('/home/mikee/progs/gnucash-master/lib/python2.7/site-packages')
import gnucash
import gnucash.gnucash_business
from gnucash.gnucash_core_c import * # Type definitions.

 
# Change the next set of values to match your actual CnuCash account setup.
# The inflexability of accounts here may not suit everybodys taste but bills can always
# be altered later.
try:
    EXPENSE_ACCOUNT = Config.get("CONFIG","EXPENSE_ACCOUNT")
    PAYABLE_ACCOUNT = Config.get("CONFIG","PAYABLE_ACCOUNT")
    XFER_ACCOUNT = Config.get("CONFIG","XFER_ACCOUNT")
    CURRENCY = Config.get("CONFIG","CURRENCY") # Probably should get the account default currency.  TODO
    PAY_BILL = Config.getboolean("CONFIG","PAY_BILL") # Boolean
    POST_BILL = Config.getboolean("CONFIG","POST_BILL") # Boolean
except ConfigParser.Error as e:
    print "\n\nProblems reading config file.  Check values.\n"
    print e
    sys.exit(1)
#logging.debug(type(XFER_ACCOUNT))

class Session():
    def __init__(self):
        self.gnufile = Config.get("CONFIG","GNUFILE");
        #logging.debug(self.gnufile)
        #self.gnufile = "../example.gnucash"
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
        self.payable = self.root.lookup_by_full_name(PAYABLE_ACCOUNT)
        self.xfer_account = self.root.lookup_by_full_name(XFER_ACCOUNT)
        assert(self.xfer_account != None)
        assert(self.exp_account != None)
        assert(self.payable != None)
        
        
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
        pred_data = gnucash.QueryInt32Predicate(gnucash.QOF_COMPARE_EQUAL, GNC_INVOICE_VEND_INVOICE)
        query.add_term([gnucash.INVOICE_TYPE], pred_data, gnucash.QOF_QUERY_AND)

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
            if bill.GetBillingID() == str(bid): return True
        return False
        
        

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
        self.today = datetime.date.today()
        self.bill_date = datetime.datetime.strptime(po.items[0].attribs['Paid on'], "%d-%b-%y")
        v_name = po.vendor.name
        vid = ''
        #logging.info(self.vendor_search(v_name, 100))
        if not self.vendor_search(v_name, 100):
            vid = self.new_vendor_from_object(po.vendor)[0]
        
        vid = self.vendor_search(v_name, 100)[0]
            
        vendor =  self.book.VendorLookupByID(vid)
        logging.debug(vendor.GetName())
        billingID = po.items[0].attribs['transaction']
        # Check for duplicate invoice IDs
        test = self.test_exists_billingID(billingID)
        logging.info(billingID)
        if test == True:
            print "We have a duplicate Billing ID.  Do a manual insert if required"
            return
        bill_num = self.book.BillNextID(vendor)
        bill = gnucash.gnucash_business.Bill(self.book, bill_num, self.currency, vendor ) 
        #bill.SetNotes("Transaction ID: " + po.items[0].attribs['transaction'])
        bill.SetBillingID(str(po.items[0].attribs['transaction']))

        assert(isinstance(bill, gnucash.gnucash_business.Invoice))
        bill.SetDateOpened(self.bill_date)
        # Add each line item entry
        for i in po.items: 
            entry = gnucash.gnucash_business.Entry(self.book, bill)
            entry.SetDateEntered(self.bill_date)
            entry.SetDate(self.bill_date)
            entry.SetDescription (i.attribs['Item name'])
            entry.SetQuantity(gnucash.GncNumeric(int(i.attribs['Quantity']) ))
            gnc_price = gnucash.GncNumeric(int(Decimal(i.attribs['Price'])*100), 100) ## = pricex100 then set denom to 100!
            entry.SetBillPrice(gnc_price)
            entry.SetAction("EA")
            entry.SetBillAccount(self.exp_account)
            entry.SetBillAccount(self.exp_account)
            #logging.info(entry.GetBillPrice().num())
            entry.SetBillTaxTable(self.book.TaxTableLookupByName("VAT"))
            entry.SetBillTaxable(False)
            entry.SetBillTaxIncluded(False)
            
        if POST_BILL: txn = bill.PostToAccount(self.payable,
                        self.bill_date, self.bill_date, "", True, False)
        
        if POST_BILL:#Pay FIXME ? Or don't.
            '''vendor.ApplyPayment(bill,
                            self.payable,
                            self.xfer_account,
                            gnc_price,
                            gnucash.GncNumeric(1,1),
                            self.bill_date,
                            "memo","num")
            '''
            pass

            
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
    
    
   
