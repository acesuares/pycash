#!/usr/bin/env python
# Test file for price database stuff
# To update the price database call
# $PATH/gnucash  --add-price-quotes=$PATHTOFILE
# before running this.
# Adding to a calling bash script would be better

import gnucash
import gnucash.gnucash_business
#from gnucash import *
from gnucash.gnucash_core_c import *
from gnucash.gnucash_business import *
from gnucash.gnucash_core import *
import os
import sys
from datetime import date
from decimal import Decimal
FILE = "/home/mikee/Docs/MEC/gnucash/MEC-test"


session = Session("xml://%s" % FILE, False, False, False)


root = session.book.get_root_account()
book = session.book
pdb = book.get_price_db()
comm_table = book.get_table()
gbp = comm_table.lookup("CURRENCY", "GBP")
arm = comm_table.lookup("NASDAQ", "ARM.L")
latest = pdb.lookup_latest(arm,gbp)
value = latest.get_value()

print(float(value.num) / (float(value.denom ))


session.end()
session.destroy()
quit()
