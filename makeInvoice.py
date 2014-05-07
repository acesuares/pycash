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
# @author Mike Evans <mikee@saxicola.co.uk>
# Run ipython with: "gnucash-env ipython" and copy/paste for testing
# Or: gnucash-env python makeSale.py
# Run this on a TEST database as it will insert an invoice into your system, this
# may not be what you want.

import os
import sys
sys.path.append('/home/mikee/progs/gnucash-master/lib/python2.7/site-packages')

import backend_errors
import gnucash
import gnucash.gnucash_business


from datetime import date
from decimal import Decimal
for arg in sys.argv:
    print arg # Or, more realistically assign them to our constants
    


BANK_ACC = ''
SALES_ACC = ''
SALE_AMOUNT = 0
SALE_COMMENT = ''
CURRENCY = {'GBP':'gbp'}
URI = ''
FILE = "/path/to/account.gnucash"

'''
@param
@return
From Mark Jenkins' code
'''
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
#NB:  DO NOT USE YOUR REAL DATA FILE!  This script will write the new invoice
# into the named file, you probably do not want this to happen to your real data!!
try:
  session = Session("xml://%s" % FILE, False, False, False)
except GnuCashBackendException, backend_exception:
  errno =  backend_exception.errors[0] ## get first error number
  print backend_exception
  # Do something with it
  print backend_errors.error_dic[errno]
 # print "Cannot create session.  A lockfile may exist or you have GnuCash open."
  resp = raw_input("Enter y to open anyway: ")
  if not resp =='y':
    print "Quitting on user response.  Database was not changed."
    quit()
  else:
    try:
      session = Session("xml://%s" % FILE, False, True)
    except GnuCashBackendException as (errno):
      print "{0}".format(errno)
      print "Unknown error occurred. Stopping"
      quit(1)


root = session.book.get_root_account()
book = session.book
sales = root.lookup_by_name('Sales')
bank  = root.lookup_by_name('Business Account')
assets = root.lookup_by_name("Assets")
recievables = assets.lookup_by_name("Accounts Recievable")
income = root.lookup_by_name("Sales")
comm_table = book.get_table()
gbp = comm_table.lookup("CURRENCY", "GBP")


# Some test code
customer = book.CustomerLookupByID("000011")
if customer:
  print "Found customer!"
else:
  print "No customer found.  Cannot continue"
  session.end()
  session.destroy()
  quit()

invoice = book.InvoiceLookupByID("0000157")
if invoice:
  print "Found Invoice!"
  if invoice.IsPosted () or invoice.IsPaid():
    print "Cannot modify posted or paid invoices"
    session.end()
    session.destroy()
    quit() # Or try next invoice
else: # No currebt invoice found so create a new invoice TODO need to lookup next free Invoice ID perhaps?
  print "Creating a new invoice"
  invoice = Invoice(book, 'TEST', gbp, customer ) # I know, need to check of this exists too!!  But this is a test script so...
  # NB Gnucash will happily make another invoice/bill with the same ID!  I think this is a bad thing.
  invoice.SetDateOpened(datetime.date.today())

if invoice: # Test code
  invoice.GetID()

# Create a new entry and populate it.  Normally there would be a loop for each entry required, reading from a csv or similar
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
entry.SetInvTaxIncluded(False)


session.save() #
session.end()
session.destroy()


