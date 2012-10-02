#!/usr/bin/env python
'''
  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 2 of the License, or
  (at your option) any later version.
  
  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.
  
  You should have received a copy of the GNU General Public License
  along with this program; if not, write to the Free Software
  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
  MA 02110-1301, USA.


Get customer and vendor data from XML file and export to CSV in a form
suitable for import into GnuCash via the business menu.


'''

customer_out = 'customers.csv'
vendor_out = "vendor.csv"

from xml.dom.minidom import parse
import sys
import codecs
from datetime import datetime, timedelta
import types

try:
  if sys.argv[1]: indoc = sys.argv[1]
except: 
  useage()
  exit(0)


if sys.argv[2]: c_or_v = sys.argv[2]
else: c_or_v = 'customer'

dom = parse(indoc)
now = datetime.now()

def useage():
  print "Usage:\npython get_customers_from_xml.py path_to_xml.gnucash <customers | vendors>\n\n"

def get_address(addr, ship=False):
  ''' 
  Get either shipping or billing address
  '''
  if addr[0].getElementsByTagName('addr:name'):
    name = addr[0].getElementsByTagName('addr:name')[0].firstChild.nodeValue
  else: name = ''
  if addr[0].getElementsByTagName('addr:addr1'):
    addr1 = addr[0].getElementsByTagName('addr:addr1')[0].firstChild.nodeValue
  else: addr1 = ''
  if addr[0].getElementsByTagName('addr:addr2'):
    addr2 = addr[0].getElementsByTagName('addr:addr2')[0].firstChild.nodeValue
  else: addr2 = ''
  if addr[0].getElementsByTagName('addr:addr3'):
    addr3 = addr[0].getElementsByTagName('addr:addr3')[0].firstChild.nodeValue
  else: addr3 = ''
  if addr[0].getElementsByTagName('addr:addr4'):  
    addr4 = addr[0].getElementsByTagName('addr:addr4')[0].firstChild.nodeValue
  else: addr4 = ''
  if addr[0].getElementsByTagName('addr:phone'):  
    phone = addr[0].getElementsByTagName('addr:phone')[0].firstChild.nodeValue
  else: phone = ''
  if addr[0].getElementsByTagName('addr:fax'):  
    fax = addr[0].getElementsByTagName('addr:fax')[0].firstChild.nodeValue
  else: fax = ''
  if addr[0].getElementsByTagName('addr:email'):  
    email = addr[0].getElementsByTagName('addr:email')[0].firstChild.nodeValue
  else: email = ''
  address_string = ",\"" + name + "\",\"" + addr1 + "\",\"" + addr2 + "\",\"" + addr3 + "\",\"" + addr4 + "\",\"" + phone + "\",\"" + fax + "\",\"" + email  + "\""
  if ship: return address_string
  if addr[0].getElementsByTagName('addr:notes'):  
    notes = addr[0].getElementsByTagName('addr:notes')[0].firstChild.nodeValue
  else: notes = ''
  address_string += ",\"" +  notes + "\""
  return address_string
  



def get_customers_vendors(c_or_v = 'customers'):
  '''
  Get a CSV lising of customers or vendors
  @param string 'customer' or 'vendor'
  '''
  
  if c_or_v[0].lower() == 'v':
    gnctype = 'GncVendor'
    prefix =  'vendor'
  else:
    gnctype = 'GncCustomer'
    prefix =  'cust'
  
  entities = dom.getElementsByTagName('gnc:'+gnctype)
  for entity in entities:
    e_name = entity.getElementsByTagName(prefix+':name')[0].firstChild.nodeValue
    e_id = entity.getElementsByTagName(prefix+':id')[0].firstChild.nodeValue
    addr =  entity.getElementsByTagName(prefix+':addr')
    billing_address = get_address(addr)
    
      
    sys.stdout.write("\"" + e_id + "\",\""+ e_name + "\"" +  billing_address)
    
    if prefix == 'cust': #Skip if vendors as they have no shipping addresses
      if entity.getElementsByTagName(prefix+':shipaddr') :
        shipaddr = entity.getElementsByTagName(prefix+':shipaddr')
        shipping_address = get_address(shipaddr, True)    
        sys.stdout.write(shipping_address + "\n")
    continue # Below here not needed for import into GnuCash
    eti = entity.getElementsByTagName(prefix+':taxincluded')[0] 
    print eti.firstChild.nodeValue
    ea = entity.getElementsByTagName(prefix+':active')[0] 
    print ea.firstChild.nodeValue
    ecy = entity.getElementsByTagName(prefix+':currency')[0] 
    edyspace = ecy.getElementsByTagName('cmdty:space')[0]
    print edyspace.firstChild.nodeValue
    edyid = ecy.getElementsByTagName('cmdty:id')[0]
    print edyid.firstChild.nodeValue
    if prefix == 'vendor': continue
    ed = entity.getElementsByTagName(prefix+':discount')[0] 
    print ed.firstChild.nodeValue
    ec = entity.getElementsByTagName(prefix+':credit')[0] 
    print ec.firstChild.nodeValue
    
    print "\n"  
  
  
  
  return
  # END  get_customers_vendors ###################

get_customers_vendors(c_or_v)
quit()
    

  

