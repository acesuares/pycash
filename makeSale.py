#!/usr/bin/env python
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.
#
#
# Set up with: export PYTHONPATH=$PYTHONPATH:/usr/local/lib/python2.7/site-packages
# Then: gnucash-env ipython
# Or: gnucash-env python makeSale.py
# Records a sale in the Sales and bank accounts
# TODO: Parsing of input options.  Connect to php.  Variables for account names etc.
# FIXED:  For some reason all of the Customers and Vendors are lost during this process
#   I'm convinced it's not anything in here.  But then I'm often very wrong
#   when it comes to understanding GnuCash.

import gnucash
from  gnucash import Session
import gnucash.gnucash_business
#from gnucash import *
from gnucash.gnucash_core_c import *
from gnucash.gnucash_business import *
from gnucash.gnucash_core import *
import os
import sys
from datetime import date
from decimal import Decimal
for arg in sys.argv:
    print arg # Or realistically assign them to our constants

BANK_ACC = ''
SALES_ACC = ''
SALE_AMOUNT = 0
SALE_COMMENT = ''
CURRENCY = {'GBP':'gbp'}
URI = ''

def gnc_numeric_from_decimal(decimal_value):
    sign, digits, exponent = decimal_value.as_tuple()
    numerator = 0
    TEN = int(Decimal(0).radix()) #
    numerator_place_value = 1
    for i in xrange(len(digits)-1,-1,-1):
        numerator += digits[i] * numerator_place_value
        numerator_place_value *= TEN
    if decimal_value.is_signed():
        numerator = -numerator
    if exponent < 0 :
        denominator = TEN ** (-exponent)
    else:
        numerator *= TEN ** exponent
        denominator = 1
    return GncNumeric(numerator, denominator)


# Very basic try for database opening.
try:
  session = Session('/home/mikee/Docs/MEC/gnucash/MEC-test.gnucash', True, False, False)
except GnuCashBackendException:
  print "ERROR:  Cannot create session.  Quitting.  Do have GnuCash open?"
  quit()



root = session.book.get_root_account()
book = session.book
sales = root.lookup_by_name('Sales')
bank  = root.lookup_by_name('Business Account')
assets = root.lookup_by_name("Assets")
recievables = assets.lookup_by_name("Accounts Recievable")
income = root.lookup_by_name("Sales")
comm_table = book.get_table()
gbp = comm_table.lookup("CURRENCY", "GBP")

'''
# Some test code
coo = gnucash.gnucash_core_c.search_customer_on_id("000011",book.instance)
if coo:
  customer = gnucash.gnucash_business.Customer(instance=coo)
  print "Found customer!"

moo = gnucash.gnucash_core_c.search_invoice_on_id("000057",book.instance)
if moo:
  print "Found Invoice!"
  invoice =  gnucash.gnucash_business.Invoice(instance=moo)
  if invoice.IsPosted () or invoice.IsPaid():
    print "Cannot modify posted or paid invoices"
    #quit() ## Should do something more useful
else: # No currebt invoice found so create a new invoice TODO need to lookup next free Invoice ID perhaps
    print "Creating a new invoice"
    invoice = Invoice(book, 'TEST', gbp, customer ) # I know, need to chack of this exists too!!  But this is a test script so...
    invoice.SetDate(datetime.date.today())

if invoice: # Test code
  invoice.GetID()

# Create a new entry and populate it.  Loop for each entry required
entry = gnucash.gnucash_business.Entry(book, invoice)
entry.SetDate(datetime.date(2010, 7, 24))
entry.SetDescription ("Some stuff I sold")
entry.SetAction("Material")
entry.SetInvAccount(income)
entry.SetQuantity( GncNumeric(1) )
gnc_price = GncNumeric(1040, 100) ## = pricex100 then set denom to 100!
entry.SetInvPrice(gnc_price)
#entry.SetInvTaxTable(tax_table)
entry.SetInvTaxIncluded(False)
'''


#invoice.PostToAccount(recievables, datetime.date.today(), datetime.date.today(), "", True)




## OR just make a cash sale without an invoice.



trans1 = Transaction(book)
trans2 = Transaction(book)
split1 = Split(book)
split3 = Split(book)


# The sale price
num = GncNumeric(40, 1)

# Now do the sale
split3.SetValue(num)
split3.SetAccount(bank)
split3.SetParent(trans2) # For some reason we have to do this twice
trans2.SetCurrency(gbp)  # It fails the first time, then succeeds, else
trans1.SetCurrency(gbp)  # It fails the first time, then succeeds, else
split3.SetParent(trans2) # it just crashes

trans2.SetDescription("Sold some stuff")
trans2.SetDate(datetime.date.today().day,datetime.date.today().month,datetime.date.today().year) #DONE get this from datetime.date.today() as day month year

split4 = split3.GetOtherSplit()
split4.SetAccount(sales)

#session.save() #
session.end()
session.destroy()


