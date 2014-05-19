#!/bin/env python
# Get config data from file
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
'''

import sys
import ConfigParser
import os, stat
import gettext
import locale



locale.setlocale(locale.LC_ALL, '')
APP = 'librarian'
gettext.textdomain(APP)
_ = gettext.gettext

# Get the real location of this file
iamhere = os.path.dirname( os.path.realpath( __file__ ) )
home = os.environ['HOME']

class load_config:
  ''' Load the config data for use by applications.
  If a config file is not found it writes a stub file to the current dir
  and informs the user to about filling the config fields.'''
  def __init__(self):
    self.get_config()

  def get_config(self):
    config_file = "pybay.conf"
    config = ConfigParser.ConfigParser()
    config.read(config_file)
    if not config.sections():
      #print "Cannot read config file, exiting.\n"
      # Pop up a message
      import messages
      messages.pop_info(_('No config file found.\nA template file file has been written to disk.\nPlease edit ') 
        + config_file + _(' to contain the correct login details for your databases.\nNote that is is a hidden file'))

      f = open(config_file,"w")
      # Write a dummy config file if one doesn't exist
      #The python way, but it converts everything to LOWER case! 
      parser = ConfigParser.SafeConfigParser()
      parser.add_section('CONFIG')

      parser.set('CONFIG', 'GNUFILE' ,"example.gnucash")

      parser.write(f)
      # Set access mode to owner only
      os.fchmod(f.fileno(),stat.S_IREAD|stat.S_IWRITE)
      f.close()
      del f

    else:
      # Now read the file
      self.GNUFILE = config.get('CONFIG','GNUFILE')

        
  def print_config(self):
    ''' print some values for testing.  Take care not to expose secret data.
    '''
    print "GNUFILE =", self.GNUFILE



# For testing
if __name__ == "__main__":
  app = load_config()
  app.print_config()



