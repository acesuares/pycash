#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
# Wot's this do then?
# It's just for fun.
# It analysis your account data and tests if the data conform to Bentford's Law.
# You need to export your data to a csv file first.
# Bentford's Law?  Look it up.

import os, sys
import csv
from decimal import Decimal as dec
import matplotlib.pyplot as plt


INFILE=sys.argv[1]
OUTFILE=''

nd = {}
# Set initial values for dictionary
for x in range(1,9):
    nd[x] = 0
with open(INFILE,'rb') as f:
    reader = csv.reader(f,quoting=csv.QUOTE_ALL)
    for row in reader:
        if row[0] == '':continue
        try:
            #if dec(row[12]) < 1: continue
            n =  (dec(row[12][0]))
            #print n
            if n > 0: nd[n] += 1
            
            
        except:pass
print nd

# Plot it
plt.bar(range(len(nd)), nd.values(), align='center')
plt.xticks(range(len(nd)), nd.keys())
for k,v in nd.iteritems():
    plt.text(k-1, v+0.2, str(v),ha='center')  
plt.title("Bentford Plot of Bank Tansaction Data")
plt.show()
