#!/usr/bin/env python

'''Delete ALL the transactions in a GnuCash XML file to leave only the
account data, invoices, customers etc.
Acts directly on the XML file and NOT through GnuCash API.
Even though invoices are retained they will have lost their reference to
their transaction so cusing errors on file loading such as:
* 12:38:42  CRIT <gnc.backend.xml> invoice_posttxn_handler: assertion `txn' failed
This is probably not good and maybe invoices etc. should be removed too?

NOTE I said ALL transactions.'''
# Modified to delete transactions older that daysolder, edit value to suit.

outdoc = 'bare.gnucash'

from xml.dom.minidom import parse
import sys
import codecs
from datetime import datetime, timedelta
import types

try:
  if sys.argv[1]: indoc = sys.argv[1]
except: pass

daysolder = 365 * 3 # number of days of data to keep.
dom = parse(indoc)
now = datetime.now()

# TODO make it only delete transactions that are old by data
for node in dom.getElementsByTagName('gnc:transaction'): 
  for sub in node.getElementsByTagName('ts:date'):
    # Test if date is old enough to delete.
    # Example date: 2010-09-05 11:00:12 +0100
    try: datestring = sub.firstChild.nodeValue # Get the date string
    except: continue
    datestring = datestring.split(' ')[0] # Strip off the offset
    datestring = datestring.encode() #from unicode
    try: date = datetime.strptime(datestring,"%Y-%m-%d")
    except: continue
    td = datetime.now() - date
    #print td.days
    if td.days > daysolder:
      print td.days
      node.parentNode.removeChild(node)
      node.unlink()

  

f = codecs.open(outdoc, 'w', "utf-8")
dom.writexml(f)
f.close()
