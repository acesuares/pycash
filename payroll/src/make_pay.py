#!/bin/env python
# -*- coding: iso-8859-15 -*-
'''
Based on the text below from: 
http://linas.org/mirrors/www.aerospacesoftware.com/2003.06.21/GNU_Cash_for_Business_users_Howto_Guide.html.  
See ../doc/paying_wages.asc

Simple Payroll Account Layout:

-Assets
   -Checking
-Liabilities
   -Tax1  (short term "storage" account)
   -Tax2  (short term "storage" account)
-Expenses
   -Salaries
   -Taxes
   
Actual deductions are calculated usung HMRC's tool.  The CSV produced is 
read by this app and the appropriate ebtries made in GnuCash.
'''
import os,sys
from os.path import expanduser
import csv
import logging
import datetime
from decimal import Decimal
import ConfigParser

sys.path.append('/home/mikee/progs/gnucash-maint/lib/python2.7/site-packages')
import gnucash
import gnucash.gnucash_business
from gnucash.gnucash_core_c import * # Type definitions.

HERE = os.path.dirname(os.path.realpath(__file__))
HOME = expanduser("~")

Config = ConfigParser.ConfigParser()
Config.read(HOME+"/.pybay.conf") # This needs to be in users home dir.

logging.basicConfig(level=logging.DEBUG, 
		format='%(module)s: LINE %(lineno)d: %(levelname)s: %(message)s')
############### CLASS SALARY ###########################################  
class Salary:
	gross_for_tax = 0.0
	gross_for_nics = 0.0
	net = 0.0
	paye = 0.0
	ni_employee = 0.0
	ni_employer = 0.0
	student_loan = 0.0
	pension_employee = 0.0
	pension_employer = 0.0
	
	
	def __init__(self):
		
		return
		
	def print_salary(self):
		print "Gross Pay for Tax",self.gross_for_tax
		print "PAYE", self.paye
		print "NICS",self.ni_employee
		print "Student Loan",self.student_loan
		print "Net Pay", self.net
	
		
	def calc_salary(self):
		self.net = self.gross_for_tax - self.paye - self.ni_employee - self.student_loan - self.pension_employee
		return self.net
################ END CLASS SALARY ######################################

################ CLASS UKPAYROLL #######################################		
class UkPayRoll:
	tax_code = None
	employee_name = None
	employee_code = None
	
	
	def __init__(self):
		self.employee = None
		self.account = None
		self.salary = Salary()
		
	def read_csv(self,filename):
		self.filename = filename
		''' 
		The data file has a two line CSV format.  
		Line 1 of the pair contains the field name.
		Line 2 contains the data.
		The fields appear to separated by varying numbers of commas.
Example lines:
Benefits Taxed via Payroll,,Benefits Subject to Class 1a NICs,,Pension Contributions Paid,,Pension Contributions Not Paid,,Gross Pay For Tax,,Gross Pay For NICs
0.00,,0.00,,0.00,,0.00,,2000.00,,2000.00

Total Tax Deducted,,Employee NICs,,Student Loan,,Net Pay After Statutory Deductions
233.00,,160.44,,53.00,,1553.56
'''
		f = open(self.filename,'r')
		lines = f.readlines()
		f.close()
		ilines = iter(lines)
		for line in ilines:
			#print line
			terms = line.split(',')
			if terms[0] == 'Payment Pay For Tax':
				line = next(ilines) #
				terms =  line.split(',')
				salary.gross_for_tax = float(terms[0])
			if terms[0] == 'Total Tax Deducted':
				line = next(ilines) #
				terms =  line.split(',')
				salary.paye = float(terms[0])
				salary.ni_employee =float(terms[2])
				salary.student_loan = float (terms[4])
		return
				
			
		
	
	def open_book(self, gnufile):
		''' This uses the GnuCash XLM file as a data store.  If you are experimenting 
		with DB storage you will have to edit this section to suit. Note that GnuCash
		recommends using the XML file storage for production use as the database storage
		is still in development and should only be used for testing.
		
		try:
		  self.session = gnucash.Session("pay-test.gnucash", True, False, False)
		except gnucash.GnuCashBackendException as (errno):
		  print "{0}".format(errno)
		  print "Stopping.  Is Gnucash running?  Make sure GnuCash is not running \
				and that if you are using an XML file storage make sure that a \
				lock file doesn't exist in the gnucash file directory."
		  quit(1)
'''
		self.session = gnucash.Session(gnufile, True, False, False)
		self.book = self.session.book
		self.root = self.book.get_root_account()
		self.comm_table = self.book.get_table()
		#CURRENCY = {'GBP':'gbp'}
		self.currency = self.comm_table.lookup("CURRENCY", "GBP")
		self.acc_bank = self.root.lookup_by_name('Business Account')
		#print self.acc_bank.GetName()
		self.acc_exp_salaries = self.root.lookup_by_full_name("Expenses.Salaries")
		self.acct_liab_NI = self.root.lookup_by_full_name("Liabilities.NI")
		self.acct_liab_PAYE = self.root.lookup_by_full_name("Liabilities.PAYE")
		self.acct_liab_student_loan = self.root.lookup_by_full_name("Liabilities.Student Loan")
		#print self.acc_bank.GetName()
		return
		
		
	def add_salary(self, salary):
		''' Need to write splits to a transaction in account Expenses.Salaries
		'''
		trans1 = gnucash.Transaction(self.book)
		trans1.BeginEdit()
		split1 = gnucash.Split(self.book)

		split1.SetParent(trans1)
		trans1.SetCurrency(self.currency)  # It fails the first time, then succeeds, else
		split1.SetParent(trans1) # it just crashes

		num = gnucash.GncNumeric(100*salary.gross_for_tax, 100)
		split1.SetAccount(self.acc_exp_salaries)
		split1.SetValue(num)

		num = gnucash.GncNumeric(100*salary.calc_salary(), 100)
		split2 = gnucash.Split(self.book)
		split2.SetParent(trans1)
		split2.SetAccount(self.acc_bank)
		split2.SetValue(gnucash.GncNumeric.neg(num))

		num = gnucash.GncNumeric(100*salary.ni_employee,100)
		split3 = gnucash.Split(self.book)
		split3.SetParent(trans1)
		split3.SetAccount(self.acct_liab_NI)
		split3.SetValue(gnucash.GncNumeric.neg(num))
		#logging.debug("Doing NICS %s",salary.ni_employee)


		split4 = gnucash.Split(self.book)
		split4.SetParent(trans1)
		split4.SetAccount(self.acct_liab_PAYE)
		num = gnucash.GncNumeric(100*salary.paye,100)
		split4.SetValue(gnucash.GncNumeric.neg(num))

		split5 = gnucash.Split(self.book)
		split5.SetParent(trans1)
		split5.SetAccount(self.acct_liab_student_loan)
		num = gnucash.GncNumeric(100*salary.student_loan,100)
		split5.SetValue(gnucash.GncNumeric.neg(num))
		
		trans1.SetDescription("Mike Evans")
		trans1.SetDate(datetime.date.today().day,datetime.date.today().month,datetime.date.today().year) #DONE get this from datetime.date.today() as day month year

		
		trans1.CommitEdit()
		logging.debug("Done transaction")
		self.session.save()
		
		
		return
		
		
			
	def close_book(self,save = False):
		if save: self.session.save() #
		self.session.end()
		#self.session.destroy()
		return
		
		
#################### END CLASS UKPAYROLL ###############################		

	
	

######################### START HERE ###################################
if __name__ == "__main__":
	for arg in sys.argv:
		print arg
	try: 
		payfile = sys.argv[1]
		gnufile = sys.argv[2]
	except:
		payfile ="payment_2014-08-01_1.csv"
		gnufile = 'pay-test.gnucash'
	
	payroll = UkPayRoll()
	salary = Salary()
	payroll.read_csv(payfile)
	salary.calc_salary()
	salary.print_salary()
	payroll.open_book(gnufile)
	payroll.add_salary(salary)
	#payroll.close_book(True)
	'''
#Paste into ipython and make it work

import os       
import sys      
sys.path.append('/home/mikee/progs/gnucash-maint/lib/python2.7/site-packages')
import gnucash                                                                
from  gnucash import Session                                                  
import gnucash.gnucash_business                                               
#from gnucash import *                                                        
from gnucash.gnucash_core_c import *                                          
from gnucash.gnucash_business import *                                        
from gnucash.gnucash_core import *                                            
from datetime import date                                                     
from decimal import Decimal                                                   
CURRENCY = {'GBP':'gbp'}                                                      
session = Session('/home/mikee/Projects/pycash/payroll/src/pay-test.gnucash', True, False, False)      
root = session.book.get_root_account()                                                                 
book = session.book                                                                                    
sales = root.lookup_by_name('Sales')                                                                   
bank  = root.lookup_by_name('Business Account')  
nics  = root.lookup_by_name('NI')         
paye  = root.lookup_by_name('PAYE')                                             
assets = root.lookup_by_name("Assets")                                                                 
recievables = assets.lookup_by_name("Accounts Recievable")
salaries = root.lookup_by_name("Salaries")
loan = root.lookup_by_name("Student Loan")
comm_table = book.get_table()
gbp = comm_table.lookup("CURRENCY", "GBP")

import ctypes
libgnc_qof = ctypes.CDLL('/home/mikee/progs/gnucash-maint/lib/libgnc-qof.so') #maint
#libgnc_qof = ctypes.CDLL('/home/mikee/progs/gnucash-master/lib/gnucash/libgncmod-engine.so') # master
libgnc_qof.kvp_value_get_string.restype = ctypes.c_char_p
libgnc_qof.kvp_frame_get_slot_path.restype = ctypes.c_void_p
libgnc_qof.qof_book_get_slots.restype = ctypes.c_void_p


class BusinessSlots(object):
    def __init__(self, book):
        self._slots = libgnc_qof.qof_book_get_slots(ctypes.c_void_p(book.instance.__long__()))
    def __getitem__(self, key):
        kvpv = libgnc_qof.kvp_frame_get_slot_path(
        self._slots, 'options', 'Business', key, None)
        val = libgnc_qof.kvp_value_get_string(kvpv)
        return val

slots = BusinessSlots(book)
slots['Company ID']
slots['Company Contact Person']
slots['Company Email Address']
slots['Company Phone Number']
slots['Company Address']
slots['Company Website URL']

    
trans1 = Transaction(book)
trans1.BeginEdit()
#trans2 = Transaction(book)
split1 = Split(book)
#split2 = Split(book)
#split3 = Split(book)

split1.SetParent(trans1)
#split2.SetParent(trans2) # For some reason we have to do this twice
trans1.SetCurrency(gbp)  # It fails the first time, then succeeds, else
#trans2.SetCurrency(gbp)
split1.SetParent(trans1) # it just crashes
#split2.SetParent(trans2) 
#split3.SetParent(trans1)
# OK to here

num = GncNumeric(100, 1)
split1.SetAccount(salaries)
split1.SetValue(num)

num = GncNumeric(40, 1)
split2 = Split(book)
split2.SetParent(trans1)
split2.SetAccount(bank)
split2.SetValue(GncNumeric.neg(num))

num = GncNumeric(20, 1)
split3 = Split(book)
split3.SetParent(trans1)
split3.SetAccount(nics)
split3.SetValue(GncNumeric.neg(num))

split4 = Split(book)
split4.SetParent(trans1)
split4.SetAccount(paye)
split4.SetValue(GncNumeric.neg(num))

split4 = Split(book)
split4.SetParent(trans1)
split4.SetAccount(loan)
split4.SetValue(GncNumeric.neg(num))


trans1.SetDescription("Mike Evans")
trans1.SetDate(datetime.date.today().day,datetime.date.today().month,datetime.date.today().year) #DONE get this from datetime.date.today() as day month year


trans1.CommitEdit()  
   
session.save()
'''



