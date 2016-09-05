#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
'''
#       rapid2gnucash.py
#
#       Copyright 2010 Mike Evans <mikee@millstreamcomputing.co.uk>
#
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

Convert confirmation mail from Rapid Electronics (UK) to CSV.
Saved mails from claws are base64 encoded.
'''
import sys
import csv

try:
    INFILE=sys.argv[1]
except:
    print "No input files specified."
    print "Useage: Useage: rapid2gnucash.py  DOWNLOADED_BASKET.csv \"ORDER_NUMBER\""
    quit(1)

# Load the file
infile = open(INFILE, 'r')
data = readlines(infile)
print(data)

close(infile)
