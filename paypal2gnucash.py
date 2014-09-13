#!/bin/env python
# -*- coding: utf-8 -*- 
# Take input from a PayPal activity download and produce something suitable for
# import into GnuCash.  Produces a tab delimited file, redirect the output 
# to a file with > then import CSV.

import os
from os import path
from datetime import date
import re # For regex stuff
import sys
import csv
#import itertools, collections
from decimal import Decimal


#def consume(iterator, n):
#    collections.deque(itertools.islice(iterator, n))
    
    
try:
    INFILE=sys.argv[1]
except:
    print "No input files specified."
    print "Useage: Useage: rapid2gnucash.py  DOWNLOADED_BASKET.csv \"ORDER_NUMBER\""
    quit(1)

Reader = csv.reader(open(INFILE), delimiter=',')

#iterator = Reader.__iter__()
 
 
for row in Reader:
    wanted = None
    if row[4] == "PayPal Express Checkout Payment Sent":
        wanted = row[0] + '\t' + row[3] + ' : ' + row[16] + '\t' # date, vendor, description
        #print row
        if row[6] != "GBP": ## Sale is not in GBP, we need the converted value, which is 2 rows later
             row = Reader.next()
             row = Reader.next()
             #consume(Reader, 1)
             wanted += '\t' + str(-Decimal(row[7]))
        else: wanted += '\t' +  str(-Decimal(row[7]))
    #wanted = row[0] + "," + row[3] + ',' + row[16]
    if wanted: print wanted
