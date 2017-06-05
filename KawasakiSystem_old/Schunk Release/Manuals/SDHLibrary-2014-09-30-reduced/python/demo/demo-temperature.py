#!/usr/bin/env python
# -*- coding: latin-1 -*-
## \addtogroup sdh_library_python_demo_scripts_group
#  @{

#######################################################################
#
## \file
#  \section sdhlibrary_python_sdh_demo_temperature_general General file information
#
#    \author   Dirk Osswald
#    \date     2007-01-18
#
#  \brief  
#    Print measured temperatures of SDH.
#    See demo-temperature.__doc__ and online help ("-h" or "--help") for available options.
#
#  \section sdhlibrary_python_sdh_demo_temperature_copyright Copyright
#
#  Copyright (c) 2007 SCHUNK GmbH & Co. KG
#
#  <HR>
#  \internal
#
#    \subsection sdhlibrary_python_sdh_demo_temperature_details SVN related, detailed file specific information:
#      $LastChangedBy: Osswald2 $
#      $LastChangedDate: 2013-06-18 18:28:14 +0200 (Di, 18 Jun 2013) $
#      \par SVN file revision:
#        $Id: demo-temperature.py 10351 2013-06-18 16:28:14Z Osswald2 $
#
#  \subsection sdhlibrary_python_sdh_demo_temperature_changelog Changelog of this file:
#      \include demo-temperature.py.log
#
#######################################################################

## 
#  @}


#######################################################################
## \anchor sdhlibrary_python_demo_temperature_python_vars
#  \name   Python specific variables
#  
#  Some definitions that describe the script for python
#
#  @{

# pylint: disable-msg=W0622
## The docstring describing the purpose of the script:
__doc__ = '''
Print measured temperatures of SDH. 
A vector of temperatures is reported. The first 7 temperatures
are from sensors close to the corresponding axes motors.
The 8th value is the temperature of the FPGA, the controller chip (CPU).
The 9th value is the temperature of the PCB (Printed circuit board)
in the body of the SDH.

- Example usage:
  - Print temperatures of an SDH connected via Ethernet:
    The SDH has IP-Address 192.168.1.42 and is attached to TCP port 23.
    (Requires at least SDH-firmware v0.0.3.1)
    > demo-temperature.py --tcp=192.168.1.42:23 
    
  - Print temperatures of an SDH connected to port 2 = COM3 once:
    > demo-temperature.py -p 2
    
  - Print temperatures of an SDH connected to USB to RS232 converter 0 once:
    > demo-temperature.py --sdh_rs_device=/dev/ttyUSB0
    
  - Print temperatures of an SDH connected to port 2 = COM3 every 500ms:
    > demo-temperature.py -p 2 -t 0.5
     
  - Get the version info of both the joint controllers and the tactile 
    sensor firmware from an SDH connected via Ethernet. 
    The SDH and the tactile sensors have a common IP-Address,
    here 192.168.1.42. The joint controller is attached to the
    TCP port 23 and the tactile sensors to TCP port 13000.
    (Requires at least SDH-firmware v0.0.3.2)
    > demo-temperature.py --tcp=192.168.1.42:23 --dsa_tcp=:13000 -v

  - Get the version info of both the joint controllers and the tactile 
    sensor firmware from an SDH connected to:
    - port 2 = COM3 (joint controllers) and 
    - port 3 = COM4 (tactile sensor controller) 
    > demo-temperature.py --port=2 --dsaport=3 -v
'''

__author__    = "Dirk Osswald: dirk.osswald@de.schunk.com"
__url__       = "http://www.schunk.com"
__version__   = "$Id: demo-temperature.py 10351 2013-06-18 16:28:14Z Osswald2 $"
__copyright__ = "Copyright (c) 2007 SCHUNK GmbH & Co. KG"

#  end of doxygen name group sdhlibrary_python_demo_temperature_python_vars
#  @}
######################################################################


######################################################################
# Import the needed modules

# Import the sdh.py python import module:
import sdh

#
######################################################################


######################################################################
# Command line option handling:

## Create an option parser object to parse common command line options:
parser = sdh.cSDHOptionParser( usage    =  __doc__ + "\nusage: %prog [options]",
                               revision = __version__ )

# Add an option to set the period of reporting
parser.add_option( "-t", "--period",
                   dest="period", default=0, type=float,
                   help="Time period of measurements in seconds. The default of '0' means: report once only. If set then the time since start of measurement is printed at beginning of every line")


# Parse (and handle, if possible) the command line options of the script:
(options, args) = parser.parse_args()

# The parsed command line options are now stored in the options
# object. E.g. options.port is the communication port to use, either
# the default one or the one read from the -p | --port command line
# option

## An object to print script-level debug messages, if requested.
dbg = sdh.dbg.tDBG( flag=options.debug_level>0, fd=options.debug_output )
dbg << "Debug messages of script are printed like this.\n"  # pylint: disable-msg=W0104

# reduce debug level for subsystems
options.debug_level-=1

#
######################################################################


######################################################################
# The actual script code:

## Create a global instance "hand" of the class cSDH according to the given options:
hand = sdh.cSDH( options=options.__dict__ )
dbg << "Successfully created cSDH instance\n"  # pylint: disable-msg=W0104

# Open configured communication to the SDH device
hand.Open()
dbg << "Successfully opened communication to SDH\n" # pylint: disable-msg=W0104


dbg << "Caption:\n" # pylint: disable-msg=W0104
if options.period: dbg << "  times are reported in seconds\n" # pylint: disable-msg=W0104
dbg << "  temperatures are reported in %s [%s]\n" % (hand.uc_temperature.name, hand.uc_temperature.symbol) # pylint: disable-msg=W0104

# Pack the actual movement commands in a try block
try:
    # a second try block to catch keyboard interrupts
    try:
        start = sdh.time.time()
        while True:
            L = hand.GetTemperature()

            if (options.period > 0):
                # print time only if reporting periodically
                print "%10.3f " % (sdh.time.time()-start),
            
            for v in L:
                print "%6.*f" % (hand.uc_temperature.decimal_places, v),
            print
            sdh.sys.stdout.flush()

            if (options.period <= 0):
                break
            sdh.time.sleep( options.period )
            
    except KeyboardInterrupt:
        # just to ignore the Traceback in case of CTRL-C
        pass

# Close the connection to the SDH in an except/finally clause. This
# way we can stop the hand even if an error or a user interruption
# (KeyboardInterrupt) occurs.
finally:
    hand.Close()
    dbg << "Successfully disabled controllers of SDH and closed connection\n"  # pylint: disable-msg=W0104

# 
######################################################################

######################################################################
# some usefull editing settings for emacs:
#
#;;; Local Variables: ***
#;;; mode:python ***
#;;; End: ***
#
######################################################################
