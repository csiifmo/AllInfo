#!/usr/bin/env python
# -*- coding: latin-1 -*-
## \addtogroup sdh_library_python_demo_scripts_group
#  @{


## \file
#
#  \brief 
#    Very simple demonstration of the sdh python package: Make the SDH move 3 axes.
#    See demo-simple3.__doc__ and online help ("-h" or "--help") for available options.
#
#  This script contains only the very basicst use of sdh.py features.
#  For more sophisticated applications see the other demo-*.py
#  scripts, or of course the html/pdf documentation.

## 
#  @}


#######################################################################
## \anchor sdhlibrary_python_demo_simple_python_vars
#  \name   Python specific variables
#  
#  Some definitions that describe the script for python
#
#  @{

# pylint: disable-msg=W0622
## The docstring describing the purpose of the script:
__doc__ = '''
Very simple python demo script using the sdh package.
Will move axes 1,2 and 3 to a fixed position, then
return back to the home position.
The movement will be started 'non sequentially' and
the scripts then waits for the movement to be finished.

- Example usage:
  - Make SDH connected connected via Ethernet move:
    The SDH has IP-Address 192.168.1.42 and is attached to TCP port 23.
    (Requires at least SDH-firmware v0.0.3.1)
    > demo-simple3.py --tcp=192.168.1.42:23 
     
  - Make SDH connected to port 2 = COM3 move:
    > demo-simple3.py -p 2
     
  - Make SDH connected to USB to RS232 converter 0 move:
    > demo-simple3.py --sdh_rs_device=/dev/ttyUSB0
     
  - Get the version info of both the joint controllers and the tactile 
    sensor firmware from an SDH connected via Ethernet. 
    The SDH and the tactile sensors have a common IP-Address,
    here 192.168.1.42. The joint controller is attached to the
    TCP port 23 and the tactile sensors to TCP port 13000.
    (Requires at least SDH-firmware v0.0.3.2)
    > demo-simple3.py --tcp=192.168.1.42:23 --dsa_tcp=:13000 -v

- Get the version info of both the joint controllers and the tactile 
    sensor firmware from an SDH connected to:
    - port 2 = COM3 (joint controllers) and 
    - port 3 = COM4 (tactile sensor controller) 
    > demo-simple3.py --port=2 --dsaport=3 -v
'''

__author__    = "Dirk Osswald: dirk.osswald@de.schunk.com"
__url__       = "http://www.schunk.com"
__version__   = "$Id: demo-simple3.py 10351 2013-06-18 16:28:14Z Osswald2 $"
__copyright__ = "Copyright (c) 2007 SCHUNK GmbH & Co. KG"

#  end of doxygen name group sdhlibrary_python_demo_simple_python_vars
#  @}
######################################################################

import time

# Import the sdh.py python import module:
import sdh

######################################################################
# Command line option handling:

## Create an option parser object to parse common command line options:
parser = sdh.cSDHOptionParser( usage    =  __doc__ + "\nusage: %prog [options]",
                               revision = __version__ )

# Parse (and handle, if possible) the command line options of the script:
(options, args) = parser.parse_args()

# The parsed command line options are now stored in the options
# object. E.g. options.port is the communication port to use, either
# the default one or the one read from the -p | --port command line
# option

## An object to print script-level debug messages, if requested.
dbg = sdh.dbg.tDBG( flag=options.debug_level>0, fd=options.debug_output )
dbg << "Debug messages of script are printed like this.\n" # pylint: disable-msg=W0104

# reduce debug level for subsystems
options.debug_level-=1

#
######################################################################

# Create an instance "hand" of the class cSDH:
hand = sdh.cSDH( options=options.__dict__ )
dbg << "Successfully created cSDH instance\n"  # pylint: disable-msg=W0104

# Open communication to the SDH device using the interface given on the 
# command line or via default RS232 port 0 = COM1.
hand.Open()
dbg << "Successfully opened communication to SDH\n" # pylint: disable-msg=W0104

# Pack the rest of this demo into a try block so that we can recover in case of an error:
try:
    ## do some prepartions:
    # Switch to "pose" controller mode and set default velocities first:
    hand.SetController( hand.eControllerType["eCT_POSE"] )
    hand.SetAxisTargetVelocity( sdh.All, [ 40.0 ] * 7 )

    # Perform some action:
    
    # Set a new target pose for axis 1,2 and 3
    hand.SetAxisTargetAngle( [1, 2, 3], [-10,-20,-90] )
    
    # Move axes there non sequentially:
    hand.MoveAxis( [1, 2, 3], False )
    
    # The last call returned immediately so we now have time to
    # do something else while the hand is moving:
    # ... insert any calculation here ...
    
    print "Waiting while moving to %s" % hand.GetAxisTargetAngle(sdh.All)
    # Before doing something else with the hand make shure the
    # selected axes have finished the last movement:
    #    
    # \attention With SDH firmwares prior to 0.0.2.6 this did not work as expected!
    #   Hack: We have to wait a very short time to give the joint controller 
    #   a chance to react and start moving.
    # => Resolved with SDH firmware 0.0.2.6
    ##time.sleep(0.1)  # no longer needed    
    hand.WaitAxis( [1, 2, 3] )
    print "OK we're there\n"
    
    # go back home (all angles to 0.0):
    hand.SetAxisTargetAngle( sdh.All, 0.0 )
    
    # Move all axes there non sequentially:
    hand.MoveAxis( sdh.All, False )
    
    print "Waiting while moving back to %s" % hand.GetAxisTargetAngle(sdh.All)
    # Wait until all axes are there:
    #
    # \attention With SDH firmwares prior to 0.0.2.6 this did not work as expected!
    #   Hack: We have to wait a very short time to give the joint controller 
    #   a chance to react and start moving.
    # => Resolved with SDH firmware 0.0.2.6
    ##time.sleep(0.1)  # no longer needed    
    hand.WaitAxis()
    print "OK we're there.\n"

finally:
    # Finally close connection to SDH again, this switches the axis controllers off
    hand.Close()
    dbg << "Successfully disabled controllers of SDH and closed connection\n" # pylint: disable-msg=W0104
