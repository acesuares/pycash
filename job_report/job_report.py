#!/bin/env python
# -*- coding: iso-8859-15 -*-
'''
Create a job report from a GnuCash Job
The current GnuCash Job report is not fit for purpose.  There is a bug 742329 filed
to enhance the report but I'm not holding my breath.
List all transactions connected to a job and summarise.
'''
import os,sys
from os.path import expanduser
import csv
import logging
import datetime
from decimal import Decimal
import ConfigParser

# For the pdf output    
import jinja2 # For the html
import pdfkit # For the pdf

HERE = os.path.dirname(os.path.realpath(__file__))
HOME = expanduser("~")


sys.path.append('/home/mikee/progs/gnucash-maint/lib/python2.7/site-packages')
import gnucash
import gnucash.gnucash_business
from gnucash.gnucash_core_c import * # Type definitions.

templateLoader = jinja2.FileSystemLoader( searchpath = '.' )
templateEnv = jinja2.Environment( loader = templateLoader )
TEMPLATE_FILE = "template.jinja"
template = templateEnv.get_template( TEMPLATE_FILE )


Config = ConfigParser.ConfigParser()
Config.read(HOME+"/.pybay.conf") # This needs to be in users home dir.

logging.basicConfig(level=logging.DEBUG, 
		format='%(module)s: LINE %(lineno)d: %(levelname)s: %(message)s')

class job_report:
    def __init__(self):
        self.make_report()
        self.print_report()
        
        
#-------------------------------------------------------------------------------
    def close_session(self, session, save):
        '''
        @session gnucash.Session
        @param save Boolean, save the session?
        '''
        if save: session.save()
        session.end()
        session.destroy()

#-------------------------------------------------------------------------------
    def open_invoice(self, book,inv_num):
        '''
        @param book.
        @param inv_num Invoice number as a string
        '''
        try: invoice = book.InvoiceLookupByID(inv_num)
        except: return None
        return invoice

#-------------------------------------------------------------------------------
    def open_book(self, account_file):
        '''
        Open a GnuCash file and load the invoice
        '''
        try: session = Session("xml://%s" % account_file, True, False, False)
        except:
            print ' Failed to open GnuCash file.  Please check and try again/'
            quit(0)
        root = session.book.get_root_account()
        book = session.book
        return session, book

#-------------------------------------------------------------------------------
    def make_report(self):
        pass
        
    def print_report(self):
        pass

    

def print_usage():
    print "\n\nUsage:job_report.py \"Job name\"\n\n"

if __name__ == "__main__":
    for arg in sys.argv:
        print arg
    try: 
		payfile = sys.argv[1]
    except: print_usage()

    app = job_report()
