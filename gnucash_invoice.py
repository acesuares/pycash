#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
'''
An object to represent averything in a Gnucash Invoice/Bill
'''

class Invoice():
    ID=None
    entry = Entry
    '''
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
    entry.SetInvTaxIncluded(False)'''
    def __init__(self):
        return
        
    
class Entry():
    book = None
    invoice = None
    date = None
    date_entered = None
    description = ""
    action = ""
    inv_account = ""
    quantity= 0
    price = 0
    tax_table = ""
    tax_included = False
    ''' 
    An invoice may have many entries but has at least one.
    '''
    
