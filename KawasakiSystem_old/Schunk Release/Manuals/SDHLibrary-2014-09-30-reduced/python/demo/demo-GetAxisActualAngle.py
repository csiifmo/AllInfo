#!/usr/bin/env python
# -*- coding: latin-1 -*-
## \addtogroup sdh_library_python_demo_scripts_group
#  @{

#######################################################################
#
## \file
#  \section sdhlibrary_python_demo_getaxisactualangle_general General file information
#
#    \author   Dirk Osswald
#    \date     2007-01-29
#
#  \brief 
#    Print current actual axis angles from SDH.
#    See demo-GetAxisActualAngle.__doc__ and online help ("-h" or "--help") for available options.
#
#    Start the script with \c "-h" or \c "--help" command line option
#    to see the online help.
#
#  \section sdhlibrary_python_demo_getaxisactualangle_copyright Copyright
#
#  Copyright (c) 2007 SCHUNK GmbH & Co. KG
#
#  <HR>
#  \internal
#
#    \subsection sdhlibrary_python_demo_getaxisactualangle_details SVN related, detailed file specific information:
#      $LastChangedBy: Osswald2 $
#      $LastChangedDate: 2013-06-18 18:28:14 +0200 (Di, 18 Jun 2013) $
#      \par SVN file revision:
#        $Id: demo-GetAxisActualAngle.py 10351 2013-06-18 16:28:14Z Osswald2 $
#
#  \subsection sdhlibrary_python_demo_getaxisactualangle_changelog Changelog of this file:
#      \include demo-GetAxisActualAngle.py.log
#
#######################################################################

## 
#  @}


#######################################################################
## \anchor sdhlibrary_python_demo_getaxisactualangle_python_vars
#  \name   Python specific variables
#  
#  Some definitions that describe the script for python
#
#  @{

# pylint: disable-msg=W0622
## The docstring describing the purpose of the script:
__doc__ = '''
Print current actual axis angles from SDH.

- Example usage:
  - Print actual angles of an SDH connected via Ethernet:
    The SDH has IP-Address 192.168.1.42 and is attached to TCP port 23.
    (Requires at least SDH-firmware v0.0.3.1)
    > demo-GetAxisActualAngle.py --tcp=192.168.1.42:23 
    
  - Print actual angles of an SDH connected to port 2 = COM3 once:
    > demo-GetAxisActualAngle.py -p 2
    
  - Print actual angles of an SDH connected to port 2 = COM3 every 500ms:
    > demo-GetAxisActualAngle.py -p 2 -t 0.5
     
  - Get the version info of both the joint controllers and the tactile 
    sensor firmware from an SDH connected via Ethernet. 
    The SDH and the tactile sensors have a common IP-Address,
    here 192.168.1.42. The joint controller is attached to the
    TCP port 23 and the tactile sensors to TCP port 13000.
    (Requires at least SDH-firmware v0.0.3.2)
    > demo-GetAxisActualAngle.py --tcp=192.168.1.42:23 --dsa_tcp=:13000 -v

  - Get the version info of both the joint controllers and the tactile 
    sensor firmware from an SDH connected to:
    - port 2 = COM3 (joint controllers) and 
    - port 3 = COM4 (tactile sensor controller) 
    > demo-GetAxisActualAngle.py --port=2 --dsaport=3 -v
'''

__author__    = "Dirk Osswald: dirk.osswald@de.schunk.com"
__url__       = "http://www.schunk.com"
__version__   = "$Id: demo-GetAxisActualAngle.py 10351 2013-06-18 16:28:14Z Osswald2 $"
__copyright__ = "Copyright (c) 2007 SCHUNK GmbH & Co. KG"

#  end of doxygen name group sdhlibrary_python_demo_getaxisactualangle_python_vars
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
                   help="Time period of measurements in seconds. The default of '0' means: report once only.")

# Add another option to enable xyz forward kinematic calculation on demand
parser.add_option( "-k", "--xyz",
                   dest="do_forward_kinematics", default=False, action="store_true",
                   help="Enable calculation of forward kinematics.")

# Add another option to enable reading of actual velocity
parser.add_option( "-s", "--get_actual_velocity",
                   dest="get_actual_velocity", default=False, action="store_true",
                   help="Flag, if given then the actual velocity is read from the SDH too.")

# Add another option to enable reading of actual velocity
parser.add_option( "-P", "--velocity_profile",
                   dest="velocity_profile", default=0, type=int,
                   help="Id of the velocity profile to use (0=sin square(default), 1=ramp)")

# Add an option to set a movement command first
parser.add_option( "-m", "--move",
                   dest="move", default=None, type=str,
                   help="Target positions for a SetAxisTargetAngle command. If given the fingers are moved there while reporting Actual axis angles. Example: '0,10,2.0,-30,-44,-55,-66'.")

# Add an option to set a velocity command first
parser.add_option( "-w", "--velocity",
                   dest="velocity", default=None, type=str,
                   help="Target velocities for a SetAxisTargetVelocity command. If given the fingers are moved with the given max velocities while reporting Actual axis angles. Example: '28,40,40,40,40,40,40'.")

# Add an option to set an acceleration command first
parser.add_option( "-a", "--acceleration",
                   dest="acceleration", default=None, type=str,
                   help="Target accelerations for a SetAxisTargetAcceleration command. If given the fingers are moved with the given max accelerations while reporting Actual axis angles. Example: '100,100,100,100,100,100,100'.")


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
dbg << "  angles are reported in %s [%s]\n" % (hand.uc_angle.name, hand.uc_angle.symbol) # pylint: disable-msg=W0104
if (options.do_forward_kinematics):
    dbg << "  positions are reported in %s [%s]\n" % (hand.uc_position.name, hand.uc_position.symbol) # pylint: disable-msg=W0104


# a1 = -90.0
# a2 = 0.0
# while a1 < 90.0:
#     print "%f %f %f  " % (0.0,a1,a2),
#     for fi in (0,1,2):
#         x,y,z = hand.GetFingerXYZ( fi, [0,a1,a2] )
#         print "%f %f %f  " % (x,y,z),
#     print
#     a1 +=1

# a1 = 0.0
# a2 = -90.0
# while a2 < 90.0:
#     print "%f %f %f  " % (0.0,a1,a2),
#     for fi in (0,1,2):
#         x,y,z = hand.GetFingerXYZ( fi, [0,a1,a2] )
#         print "%f %f %f  " % (x,y,z),
#     print
#     a2 +=1
#sdh.sys.exit(0)

# Pack the actual movement commands in a try block
try:
    # a second try block to catch keyboard interrupts
    try:

        hand.SetVelocityProfile( options.velocity_profile )

        if (options.velocity is not None):
            hand.SetAxisTargetVelocity( sdh.All, eval( '[' + options.velocity + ']' ) )
 
        if (options.acceleration is not None):
            hand.SetAxisTargetAcceleration( sdh.All, eval( '[' + options.acceleration + ']' ) )
 
        if (options.move is not None):
            hand.SetAxisTargetAngle( sdh.All, eval( '[' + options.move + ']' ) )
            t = hand.MoveHand(sequ=False)
            dbg << "Movement will take %fs" % t # pylint: disable-msg=W0104
        
        start = sdh.time.time()
        while True:
            a_angles = hand.GetAxisActualAngle( sdh.All )
            if options.get_actual_velocity:
                a_velocities = hand.GetAxisActualVelocity( sdh.All )
            else:
                a_velocities = []
                
            now = sdh.time.time()
            if (options.period > 0):
                # print time only if reporting periodically
                print "%10.3f" % (now-start),
                
            for a in a_angles:
                print "%6.*f" % (hand.uc_angle.decimal_places, a),

            for v in a_velocities:
                print "%6.*f" % (hand.uc_angular_velocity.decimal_places, v),

            if (options.do_forward_kinematics):
                for fi in range( 0, hand.NUMBER_OF_FINGERS ):
                    xyz = hand.GetFingerXYZ( fi, None )
                    for k in xyz:
                        print "%6.*f" % (hand.uc_position.decimal_places, k),
            
            if (options.move is not None):
                if (now-start < t):
                    print "1",
                else:
                    print "0",
                    
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
    dbg << "Successfully disabled controllers of SDH and closed connection\n" # pylint: disable-msg=W0104


#
######################################################################
