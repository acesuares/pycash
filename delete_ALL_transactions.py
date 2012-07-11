#!/bin/env/python


'''Delete ALL the transactions in a GnuCash XML file to leave only the
account data

NOTE I said ALL '''




indoc = '/home/mikee/Docs/MEC/gnucash/MEC-test.gnucash'
outdoc = 'MEC-bare.gnucash'

from xml.dom.minidom import parse
import sys
import codecs

try:
  if sys.argv[1]: indoc = sys.argv[1]
except: pass

dom = parse(indoc)

# TODO make it only delete transactions that are old by data
for node in dom.getElementsByTagName('gnc:transaction'):  # visit every node <bar />
  '''#for sub in node.getElementsByTagName('ts:date'):
    # Test if date is old enought to delete perhaps.
    #node.parentNode.removeChild(node)
    #print sub.toxml()
    #node.unlink()'''
  #print node.toxml()
  node.parentNode.removeChild(node)
  node.unlink()
  

#print dom.toxml()


f = codecs.open(outdoc, 'w', "utf-8")
dom.writexml(f)
f.close()
