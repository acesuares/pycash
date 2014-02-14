#!/bin/env python

'''
 Create a GnuCash printable invoice.pdf that includes a BitCoin payment QRCode
 and does separate subtotals for goods, postage and materials.
 Obtain the invoice data from GnuCash using the invoice ID (Yay I wrote that code!)
 Obtain the current BitCoin exchange rate from Mt. Gox
 Create the QRCode using the format below.
 Create the invoice with the QRCode and details of how to pay in bitcoins as a pdf.
 Save to disk, and/or mail it or whatever.
 We need to set gnucash-env before running this
 Run with 
 and Gnucash which has fixed python bindings :)
 ~/progs/gnucash-trunk/bin/gnucash-env ./goods_sale_invoice.py invoice_number gnucash_file
 Edit the __main__ section to add a default GnuCash file.
 Better yet, improve the whole thing, do a pull request and send me some beer 
 money to say thankyou.
 
 For conversion to pdf we need:
 wkhtmltopdf from repos or sources 
 and
 pdfkit from  https://pypi.python.org/pypi/pdfkit
'''

import sys, os
from urllib import urlencode
import urllib2
import time
from hashlib import sha512
from hmac import HMAC
import base64
import json
import gnucash
from gnucash.gnucash_core import *
import textwrap
import qrencode 

# For the pdf output    
import jinja2 # For the html
import pdfkit # For the pdf

from os.path import expanduser
home = expanduser("~") +'/'
print home
if home == '': quit()
cwd = os.getcwd() +'/'
print cwd

templateLoader = jinja2.FileSystemLoader( searchpath = cwd )
templateEnv = jinja2.Environment( loader = templateLoader )
TEMPLATE_FILE = "tax-invoice.jinja"
template = templateEnv.get_template( TEMPLATE_FILE )
MULTIBIT = '/MultiBit/multibit.info'
mtgox_url = "https://data.mtgox.com/api/2/BTCGBP/money/ticker_fast"



def get_bitcoin_address(search_string = ''):
    '''
    this assumes you wallet is stored in ~/Multibit
    @param Description string of bitcoin address
    @return The required address and the tranformed search string
    '''
    # Need to fix URL string.
    import urllib
    search = urllib.quote(search_string)
    try: f = open(home + MULTIBIT, 'r')
    except:
        print "Can't find MultiBit directory in rour home directory."
        print "Edit me for correct path.  If you're not using MultBit then more editing may be required."
        quit(0)
    lines = f.readlines()
    f.close()
    for line in lines:
        if line.find(search) > 0:
            return line.split(',')[1], search # Return the second part = the address
    # Else just return the first one without a description
    for line in lines:
        if line.find('receive') == 0 and not line.split(',')[2].strip():
            return line.split(',')[1], search
            
        
    

def get_latest_price():

    req = urllib2.Request(mtgox_url)
    res = urllib2.urlopen(req)
    price = json.load(res)['data']['buy']['value']
    return float(price)

def open_book(account_file):
    '''
    Open a GnuCash file and load the invoice
    '''
    try: session = Session("xml://%s" % account_file, False, False, False)
    except:
        print ' Failed to open GnuCash file.  Please check and try again/'
        quit(0)
    root = session.book.get_root_account()
    book = session.book
    return session, book
    
def close_session(session, save):
    '''
    @session gnucash.Session
    @param save Boolean, save the session?
    '''
    if save: session.save()
    session.end()
    session.destroy()

def open_invoice(book,inv_num):
    '''
    @param book.
    @param inv_num Invoice number as a string
    '''
    try: invoice = book.InvoiceLookupByID(inv_num)
    except: return None
    return invoice

def create_qr_code(invoice_id, invoice_total ,exch_rate):
    qr_data = 'bitcoin:' \
        + get_bitcoin_address('Work Done')[0] \
        + '?amount=' + str(round(invoice_total/exch_rate,8)) \
        + "&label=" + get_bitcoin_address('Work Done')[1] # FIXME: Search term shouldn't be hard coded here
    qr = qrencode.encode(qr_data)
    # Rescale using the size and add a 1 px border
    size = qr[1]
    qr = qrencode.encode_scaled(qr_data, (size*4))
    img = qr[2] #'invoice-' + str(invoice_id) +'.png'
    img.save('qr.png', 'png')
    
    
    # remove temporary files
    os.remove('qr.png')
    os.remove("invoice-" + str(invoice_id) + ".html")
    
def create_printable_invoice(invoice):
    # Prep the document
    
    filename = "invoice-" + invoice.GetID() + ".pdf"

     
    # TODO Add Customer, You stuff
    
    # Get all the invoice data.
    exch_rate = get_latest_price()
    invoice_id =  invoice.GetID()
    notes = invoice.GetNotes()
    #invoice_type = invoice.GetTypeString()
    date_posted = invoice.GetDatePosted()
    date_due = invoice.GetDateDue()
    invoice_total = invoice.GetTotal().to_double()
    is_paid = invoice.IsPaid()
    currency = invoice.GetCurrency()
    c_symbol = currency.get_user_symbol()#.decode('raw-unicode-escape') #????
    owner = invoice.GetOwner()
    job_name = None
    if type(owner) == gnucash.gnucash_business.Job:
        job = invoice.GetOwner()
        job_name =  job.GetName()
        customer = job.GetOwner()
    else: customer = invoice.GetOwner()
    customer_name = customer.GetName() 
    customer_balance = customer.GetBalanceInCurrency(customer.GetCurrency()).to_double()
    amnt_due = 0 # TODO
    tax = 0 # TODO
    address = customer.GetAddr()
    adr1 = address.GetAddr1()
    adr2 = address.GetAddr2()
    adr3 = address.GetAddr3()
    adr4 = address.GetAddr4()
    email = address.GetEmail()
    
    # Start building the invoice.pdf
     
    entries = invoice.GetEntries()
    # Table headersParagraph(model.get_value(myiter, 9),styles["Normal"])
    # arrays for creating the invoice items
    date = []
    qty = []
    action = []
    price = []
    description = []
    line_price = []
    accounts = []
    goods_total = 0
    postage_total = 0
    for entry in entries:
        tmp = entry.GetInvAccount()
        accounts.append(tmp.GetName())
        date.append(entry.GetDate())
        qty.append(entry.GetQuantity().to_double())
        action.append(entry.GetAction())
        price.append(entry.GetInvPrice().to_double())
        
        description.append(entry.GetDescription())
        line_price.append(price[-1] * qty[-1])
        if accounts[-1] == "Reimbersed Postage":
            postage_total += price[-1] * qty[-1]
        else: goods_total += price[-1] * qty[-1]
    
    # Test print stuff. delete when done with 
    zipped = zip(date, description, qty, action, price, line_price, accounts)
    for da,de,q,a,p, lp, acc in zipped:
         print da,de,q,a,p,lp,acc
    print "paid =",is_paid

    
    # End test stuff
           
    # TODO: Notes, payment details

    # Build the html page
    bitcoins = True # or False :)
    template_vars = { "invoice_id":invoice_id, "customer_name":customer_name,
                   "date_due":date_due,"date_posted":date_posted,"zipped":zipped,
                    "due":invoice_total,"btc_due":round(invoice_total/exch_rate,8),
                    "is_paid":is_paid, "bitcoins":bitcoins,#"c_symbol":c_symbol,
                    "customer_name":customer_name,"cust_contact":adr1,
                    "addr_2":adr2,"addr_3":adr3,"addr_4":adr4,"job_name":job_name,
                    'notes':notes, 'bitcoin_address':get_bitcoin_address('Work Done')[0],
                    'cwd':cwd, 'accounts':accounts, 'goods':goods_total, 
                    'postage':postage_total}
                    
    # Now create a QR code
    if bitcoins == True: create_qr_code(invoice_id, invoice_total ,exch_rate)
    # Render the HTML
    outputText = template.render( template_vars )
    # to save the results
    import codecs
    file = codecs.open("invoice-" + str(invoice_id) + ".html", "w", "utf-8")
    file.write(outputText)
    file.close()
    pdfkit.from_string(outputText, 'invoice-' + str(invoice_id) +'.pdf')
    
# Test code
if __name__ == "__main__":
    try: invoice_num = str(sys.arv[1])
    except: invoice_num = "000133" # For testing
    try: account_file = str(sys.argv[2])
    except: account_file="../../bitcoin/example.gnucash" # For testing
    print "Latest Bitcoin->GBP =", str(get_latest_price())
    session, book = open_book(account_file)
    invoice = open_invoice(book,invoice_num) # A multi-line invoice
    create_printable_invoice(invoice)
    close_session(session, False) # Close session but don't save


    
    

