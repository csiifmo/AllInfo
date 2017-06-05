#!/usr/bin/env python
# -*- coding: latin-1 -*-
## \addtogroup sdh_library_python_demo_scripts_group
#  @{

## \file
#
#  \brief 
#    Demonstration script of the sdh python package: Make the SDH move one finger
#    in "velocity with acceleration ramp" control mode. 
#    See demo-simple.__doc__ and online help ("-h" or "--help") for available options.
#

## 
#  @}


#######################################################################
## \anchor sdhlibrary_python_demo_velocity_acceleration_python_vars
#  \name   Python specific variables
#  
#  Some definitions that describe the script for python
#
#  @{

# pylint: disable-msg=W0622
## The docstring describing the purpose of the script:
__doc__ = '''
Very simple python demo script using the sdh package.
Will move first finger in "velocity with acceleration ramp" control mode.

- Example usage:
  - Make SDH connected via Ethernet move.
    The SDH has IP-Address 192.168.1.42 and is attached to TCP port 23.
    (Requires at least SDH-firmware v0.0.3.1)
    > demo-velocity-acceleration.py --tcp=192.168.1.42:23 
     
  - Make SDH connected to port 2 = COM3 move:
    > demo-velocity-acceleration.py -p 2
     
  - Make SDH connected to USB to RS232 converter 0 move:
    > demo-velocity-acceleration.py --dsa_rs_device=/dev/ttyUSB0
     
  - Get the version info of both the joint controllers and the tactile 
    sensor firmware from an SDH connected via Ethernet. 
    The SDH and the tactile sensors have a common IP-Address,
    here 192.168.1.42. The joint controller is attached to the
    TCP port 23 and the tactile sensors to TCP port 13000.
    (Requires at least SDH-firmware v0.0.3.2)
    > demo-velocity-acceleration.py --tcp=192.168.1.42:23 --dsa_tcp=:13000 -v

  - Get the version info of both the joint controllers and the tactile 
    sensor firmware from an SDH connected to:
    - port 2 = COM3 (joint controllers) and 
    - port 3 = COM4 (tactile sensor controller) 
    > demo-velocity-acceleration.py --port=2 --dsaport=3 -v
'''

__author__    = "Dirk Osswald: dirk.osswald@de.schunk.com"
__url__       = "http://www.schunk.com"
__version__   = "$Id: demo-velocity-acceleration.py 10351 2013-06-18 16:28:14Z Osswald2 $"
__copyright__ = "Copyright (c) 2007 SCHUNK GmbH & Co. KG"

#  end of doxygen name group sdhlibrary_python_demo_velocity_acceleration_python_vars
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

# Reduce debug level for subsystems
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
    ###############
    # Preparations: Move the hand to a pose that is adequate for this demo:
    print 'Preparation:'
    print '  Moving to start position with "pose" controller type:\n'
    # Switch to "pose" controller mode first, then move to "home"
    hand.SetController( hand.eControllerType["eCT_POSE"] );
    
    hand.SetAxisTargetVelocity( sdh.All, [ 40.0 ] * 7 )
    hand.SetAxisTargetAngle(    sdh.All, [ 0.0 ] * 7 )
    hand.MoveHand()
    #
    ###############


    ###############
    # Do some movements with "velocity with acceleration ramp" controller type,
    # move with different velocities and accelerations.
    print 'Moving in "velocity with acceleration ramp" controller type:'
    print '  Now move back and forth with increasing acceleration'
    print '  and target velocities of alternating sign:'
    
    # Now switch to "velocity control with acceleration ramp" controller mode.
    hand.SetController( hand.eControllerType["eCT_VELOCITY_ACCELERATION"] );
    
    # Use one axis only:
    axis_index = 2
    
    # In this controller mode we must switch the power on explicitly:
    # (OK, here the power is switched on already since we used hand.MoveHand() before.)
    hand.SetAxisEnable( axis_index, True )
    
    velocity = 40
    for (acceleration) in [ 10, 20, 40, 80, 160 ]:
        # set desired acceleration (only absolute value):
        hand.SetAxisTargetAcceleration( axis_index, acceleration)
            
        for sign in [-1.0,1.0]:
            print "Setting target acceleration,velocity= %7.2f deg/(s*s)  %7.2f deg/s" % (acceleration, sign*velocity)
            
            # set the desired target velocity. This will make the axis move!
            hand.SetAxisTargetVelocity( axis_index, sign*velocity)    
            
            # keep current velocity (and acceleration) as long as the axis |angle| < 10 deg, 
            # when 10 deg are exceeded then invert the velocity sign (and probably use next acceleration)
            position_reached = False
            while not position_reached:
                # print out some debug data while moving:
                dbg << "  Actual angle: %7.2f deg,  actual velocity: %7.2f deg/s,  reference velocity: %7.2f deg/s\n" % (hand.GetAxisActualAngle( axis_index ), hand.GetAxisActualVelocity(axis_index), hand.GetAxisReferenceVelocity(axis_index))
                if ( sign > 0.0 ):
                    position_reached = (hand.GetAxisActualAngle(axis_index) >= 10.0)
                else:  
                    position_reached = (hand.GetAxisActualAngle(axis_index) <= -10.0) 
                time.sleep(0.05)
    #
    ###############

        
    ###############
    # Stop movement:

    print "Setting target acceleration,velocity= %7.2f deg/(s*s), %7.2f deg/s (for stopping)" % (100.0,0.0)

    # set a default acceleration:
    hand.SetAxisTargetAcceleration( axis_index,  100 )
    
    # set the desired target velocity to 0.0. This will make the axis slow down until stop.
    hand.SetAxisTargetVelocity(     axis_index, 0.0 )
    
    # wait until the joint has stopped to give the SDH time for slowing down:
    #   Solution one: 
    #     Simply wait for the time needed to reach velocity 0.0
    #     (v = a * t hence t= v/a)
    #time.sleep( hand.GetAxisReferenceVelocity( axis_index ) / 100.0 );

    #   Solution two: 
    #     Wait until SDH reports "IDLE":
    hand.WaitAxis( axis_index, 5.0 )
    
    #
    ###############
    
finally:     
    # Finally close connection to SDH again, this switches the axis controllers off
    hand.Close()
    dbg << "Successfully disabled controllers of SDH and closed connection\n" # pylint: disable-msg=W0104
