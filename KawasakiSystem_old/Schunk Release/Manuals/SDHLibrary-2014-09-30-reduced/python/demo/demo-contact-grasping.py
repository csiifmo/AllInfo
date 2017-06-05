#!/usr/bin/env python
# -*- coding: latin-1 -*-
## \addtogroup sdh_library_python_demo_scripts_group
#  @{

#######################################################################
## \file
#  \section sdhlibrary_python_demo_contact_grasping_py_general General file information
#
#    \author   Dirk Osswald
#    \date     2007-05-08
#
#  \brief  
#    Simple script to do grasping using tactile sensor info feedback. 
#    See demo-contact-grasping.__doc__ and the online help ("-h" or "--help") 
#    for a list of available options.
#
#  \section sdhlibrary_python_demo_contact_grasping_py_copyright Copyright
#
#  - Copyright (c) 2007 SCHUNK GmbH & Co. KG
#
#  <HR>
#  \internal
#
#    \subsection sdhlibrary_python_demo_contact_grasping_py_details SVN related, detailed file specific information:
#      $LastChangedBy: Osswald2 $
#      $LastChangedDate: 2013-06-18 18:28:14 +0200 (Di, 18 Jun 2013) $
#      \par SVN file revision:
#        $Id: demo-contact-grasping.py 10351 2013-06-18 16:28:14Z Osswald2 $
#
#  \subsection sdhlibrary_python_demo_contact_grasping_py_changelog Changelog of this file:
#      \include demo-contact-grasping.py.log
#
#######################################################################

## 
#  @}


#######################################################################
## \anchor sdhlibrary_python_demo_contact_grasping_python_vars
#  \name   Python specific variables
#  
#  Some definitions that describe the script for python
#
#  @{

# pylint: disable-msg=W0622
## The docstring describing the purpose of the script:
__doc__ = '''Simple script to do grasping with tactile sensor info feedback:
The hand will move to a pregrasp pose (open hand). You can then
reach an object to grasp into the hand. The actual grasping
is started as soon as a contact is detected. The finger
joints then try to move inwards until a certain 
force is reached on the corresponding tactile sensors.
  
- Example usage:
  - Start grasping using an SDH that is connected via Ethernet:
    The SDH and the tactile sensors have a common IP-Address,
    here 192.168.1.42. The joint controller is attached to the
    TCP port 23 and the tactile sensors to TCP port 13000 (default).
    (Requires at least SDH-firmware v0.0.3.2)
    > demo-contact-grasping.py --tcp=192.168.1.42:23 --dsa_tcp=
    
    
  - Start grasping using an SDH that is connected to:
    - port 2 = COM3 (joint controllers) and 
    - port 3 = COM4 (tactile sensor controller) 
    > demo-contact-grasping.py -p 2 --dsaport=3
    
    
  - Start grasping using an SDH that is connected to:
    - USB to RS232 converter 0 (joint controllers) and 
    - USB to RS232 converter 1 (tactile sensor controller) 
    > demo-contact-grasping.py --sdh_rs_device=/dev/ttyUSB0 --dsa_rs_device=/dev/ttyUSB1
    
    
  - Get the version info of both the joint controllers and the tactile 
    sensor firmware from an SDH connected via Ethernet. 
    The SDH and the tactile sensors have a common IP-Address,
    here 192.168.1.42. The joint controller is attached to the
    TCP port 23 and the tactile sensors to TCP port 13000.
    (Requires at least SDH-firmware v0.0.3.2)
    > demo-contact-grasping.py --tcp=192.168.1.42:23 --dsa_tcp=:13000 -v


  - Get the version info of both the joint controllers and the tactile 
    sensor firmware from an SDH connected to 
    - port 2 = COM3 (joint controllers) and 
    - port 3 = COM4 (tactile sensor controller) 
    > demo-contact-grasping.py -p 2 --dsaport=3 -v
'''

__author__    = "Dirk Osswald: dirk.osswald@de.schunk.com"
__url__       = "http://www.schunk.com"
__version__   = "$Id: demo-contact-grasping.py 10351 2013-06-18 16:28:14Z Osswald2 $"
__copyright__ = "Copyright (c) 2007 SCHUNK GmbH & Co. KG"

#  end of doxygen name group sdhlibrary_python_demo_contact_grasping_python_vars
#  @}
######################################################################

import sys
import time

import sdh
import sdh.dsa

######################################################################
# Command line option handling:


def CreateOptionParser():
    '''Create an option parser specifically for this demo program.
    '''
    ## Create an option parser object to parse common command line options:
    parser = sdh.cSDHOptionParser( usage    =  __doc__ + "\nusage: %prog [options]",
                                   revision = __version__ )

    # Remove options not applicable for this script
    parser.remove_option( "-R" ) # will also remove --radians
    parser.remove_option( "-F" ) # will also remove --fahrenheit
    parser.remove_option( "-r" ) # will also remove --framerate

    parser.add_option( "--desired-force",
                       dest="desired_force", default=5.0, type=float, metavar="DESIRED_FORCE",
                       help="Desired force that every tactile sensor should reach, default = 5.0." )
                       
    parser.add_option( "--vel-per-force",
                       dest="vel_per_force", default=1.25, type=float, metavar="VEL_PER_FORCE",
                       help="Desired velocity per force factor, default = 1.25." )
                       
    parser.add_option( "--dsadebug",
                       dest="dsa_debug_level", default=0, type=int, metavar="LEVEL",
                       help="Print debug messages of the cDSA object of level LEVEL or lower while processing the python script. Level 0 (default): No messages,\r 1: cDSA-level messages, 2: cSDHSerial-level messages" )
    parser.add_option( "--dsadebuglog",
                       dest="dsa_debug_output", default=sys.stderr, type=str, metavar="LOGFILE",
                       action="callback", callback=parser.CBDebugLog,
                       help="Redirect the printed dsa debug messages to LOGFILE instead of standard error (default). If LOGFILE starts with '+' then the output will be appended to the file (without the leading '+'), else the file will be rewritten." )
                   
    return parser
    
#
######################################################################

def GotoStartPose( hand, msg ):
    print msg,
    sys.stdout.flush() # (seems to be necessary after starting a thread on native windows python interpreters)
    hand.SetController( hand.eControllerType["eCT_POSE"] )
    hand.SetAxisTargetVelocity( sdh.All, 83 )
          #fa = [ 0, 0, 0, 0, 0, 0, 0 ]
    fa = [ 45, -90, 45, -90, 45, -90, 45 ]
    #fa = [ 90, -50, 45, -90, -90, -50, 45 ]
    hand.SetAxisTargetAngle( sdh.All, fa )
    hand.MoveAxis( sdh.All )
    print "OK"
    sys.stdout.flush() # (seems to be necessary after starting a thread on native windows python interpreters)

######################################################################
# The main function
def main():
    '''Main function of demo script.
    Parses command line and reacts accordingly.
    '''
    
    # Parse (and handle, if possible) the command line options of the script:
    parser = CreateOptionParser()
    (options, args) = parser.parse_args()
    
    # The parsed command line options are now stored in the options
    # object. E.g. options.port is the communication port to use, either
    # the default one or the one read from the -p | --port command line
    # option
    
    ## An object to print script-level debug messages, if requested.
    _dbg = sdh.dbg.tDBG( flag=options.debug_level>0, fd=options.debug_output )
    _dbg << "Debug messages of script are printed like this.\n" # pylint: disable-msg=W0104
    _dbg << sdh.PrettyStruct( "options", options )  # pylint: disable-msg=W0104
    
    # reduce debug level for subsystems
    options.debug_level-=1

    # overwrite user given value
    options.framerate = 30
    options.timeout = 1.0  # a real timeout is needed to make the closing of the connections work in case of errors / interrupt 

    # ------------------------
    # The actual processing:
    
    ## Create a global instance "hand" of the class cSDH according to the given options:
    print "Connecting to joint controller...",    
    hand = sdh.cSDH( options=options.__dict__ )
    _dbg << "Successfully created cSDH instance\n"  # pylint: disable-msg=W0104
    
    # Open configured communication to the SDH device
    hand.Open()
    _dbg << "Successfully opened communication to SDH\n" # pylint: disable-msg=W0104
    print "OK"
    
    ## Create a global instance "ts" (tactile sensor) of the class cDSA according to the given options:
    print "Connecting to tactile sensor controller. This may take up to 8 seconds...",    
    ts = sdh.dsa.cDSA( port=options.dsaport, debug_level=options.dsa_debug_level, debug_output=options.dsa_debug_output )
    print "OK"
    
    # Pack the actual movement commands in a try block
    try:
        ####
        # Prepare for grasping: open hand:
        GotoStartPose( hand, "\nPreparing for grasping, opening hand (using POSE controller)..." )
        ####
        
        # Start reading tactile sensor info in a thread:
        ts.StartUpdater( framerate=options.framerate, do_RLE = True )

        
        ####
        # for debugging, just output the local preprocessing results:
        while False: #True:
            a=ts.GetContactArea( sdh.dsa.All, sdh.dsa.All )
            print "area=%6.1f" % a,
            for fi in range(0,3):
                for part in range(0,2):  
                    (force, cog_x, cog_y, area) = ts.GetContactForce( fi, part )
                    #print "  force=%6.3f x=%6.1f y=%6.1f area=%6.1f" % (force, cog_x, cog_y, area),
                    print "  force=%6.3f area=%6.1f" % (force, area),
            print
            sys.stdout.flush() # (seems to be necessary after starting a thread on native windows python interpreters)
        ####

        
        ####
        # wait for contact to start grasping
        desired_start_contact_area = 0.0 ## 13.04 50.0
        print "\nPress any tactile sensor on the SDH to start searching for contact..."
        sys.stdout.flush() # (seems to be necessary after starting a thread on native windows python interpreters)
        while ts.GetContactArea( sdh.dsa.All, sdh.dsa.All ) < desired_start_contact_area:
            _dbg << "  contact area too small %f < %f\n" % (ts.GetContactArea( sdh.dsa.All, sdh.dsa.All ), desired_start_contact_area) # pylint: disable-msg=W0104
            time.sleep( 0.2 )
        # wait until that contact is released on the middle finger
        while ts.GetContactArea( 1, sdh.dsa.All ) > desired_start_contact_area:
            time.sleep( 0.2 )
    
        print "  OK, contact detected %f\n" % (ts.GetContactArea( sdh.dsa.All, sdh.dsa.All ))
        sys.stdout.flush() # (seems to be necessary after starting a thread on native windows python interpreters)
        ####
        
        
        ####
        # start grasping
        desired_force = options.desired_force # the desired force that every sensor patch should reach
        vel_per_force = options.vel_per_force #1.25     # factor for converting force to velocity
        loop_time = 0.01
        
        finished = False
        print "Simple force based grasping starts:"
        print "  Joints of the opposing fingers 1 and 3 (axes 1,2,5,6) will move in"
        print "  positive direction (inwards) as long as the contact force measured"
        print "  by the tactile sensor patch of that joint is less than"
        print "  the desired force %f" % desired_force
        print "  This will use the velocity with acceleration ramp controller."
        print ""
        print "  Press a tactile sensor on the middle finger 2 to stop!"
        sys.stdout.flush() # (seems to be necessary after starting a thread on native windows python interpreters)

        # switch to velocity with acceleration ramp controller type:        
        hand.SetController( hand.eControllerType["eCT_VELOCITY_ACCELERATION"] )
        hand.SetAxisTargetAcceleration( sdh.All, 100 )
        _dbg << "min=" << hand.min_angular_velocity_a << "max=" << hand.max_angular_velocity_a << "\n"
         
        ftv = hand.GetAxisTargetVelocity( sdh.All )
        while True:#not finished:
            nb_ok = 0
            
            ####
            # check for stop condition (contact on middle finger)
            
            (force, cog_x, cog_y, area0) = ts.GetContactForce( 1, 0 )
            (force, cog_x, cog_y, area1) = ts.GetContactForce( 1, 1 )
           # if ( area1 + area0 > desired_start_contact_area ):
            #    print "\nContact on middle finger detected! Stopping demonstration."
             #   sys.stdout.flush() # (seems to be necessary after starting a thread on native windows python interpreters)
              #  finished = True
               # break
            #
            ####
            
            
            # Get current position of axes:
            # (Limited to the allowed range. This is necessary since near the 
            #  range limits an axis might report an angle slightly off range.)
            faa = sdh.ToRange_a( hand.GetAxisActualAngle(sdh.All), hand.min_angle_a, hand.max_angle_a )
            fta = faa
            
            # for the selected axes:
            for (ai,fi,part) in zip( [1,2,5,6] , [0,0, 2,2], [0,1, 0,1 ] ):
                # read the contact force of the tactile sensor of the axis
                (force, cog_x, cog_y, area) = ts.GetContactForce( fi, part )
                #_dbg << "%d,%d,%d  force=%6.1f x=%6.1f y=%6.1f area=%6.1f\n" % (ai, fi, part, force, cog_x, cog_y, area) # pylint: disable-msg=W0104
                _dbg << "%d,%d,%d  force=%6.1f  =>  " % (ai, fi, part, force) # pylint: disable-msg=W0104
                
                # translate the measured force into a new velocity for the axis
                # in order to reach the desired_force
                ftv[ai] = (desired_force - force) * vel_per_force
                
                # limit the calculated target velocities to the allowed range:
                ftv[ai] = sdh.ToRange( ftv[ai], hand.min_angular_velocity_a[ai], hand.max_angular_velocity_a[ai] )
                
                if force < desired_force:
                    _dbg << "closing with %+7.1f deg/s\n" % (ftv[ai]) # pylint: disable-msg=W0104
                elif force > desired_force:
                    _dbg << "opening with %+7.1f deg/s\n" % (ftv[ai]) # pylint: disable-msg=W0104
                else:
                    _dbg << "ok\n" % (ai,fi,part) # pylint: disable-msg=W0104
                    nb_ok += 1
                    

                ####
                # check if the fingers would get closer than 10mm with the calculated position:
                    
                # calculate future position roughly according to determined velocity:
                fta[ai] += ftv[ai] * loop_time # s = v * t  =>  s(t') = s(t) + v * dt
                 
                fingers_angles = hand._AxisAnglesToFingerAngles( fta )
                (cxy, (c01,d01), (c02,d02), (c12,d12)) = hand.CheckFingerCollisions( fingers_angles[0], fingers_angles[1], fingers_angles[2] )
                d_min = min( d01, d02, d12)
                if ( (cxy or d_min < 2.0)  and force < desired_force ):
                    # if there would be a collision then do not move the current axis there
                    print "not moving axis %d further due to internal collision (d_min=%f)" % (ai,d_min)
                    sys.stdout.flush() # (seems to be necessary after starting a thread on native windows python interpreters)
                    fta[ai] = faa[ai]
                    ftv[ai] = 0.0
                #
                ####
                
            # a new target velocity has been calculated from the tactile sensor data, so move accordingly 
            _dbg << "moving with %6.2f %6.2f %6.2f %6.2f %6.2f %6.2f %6.2f deg/s\n" % tuple(ftv)     # pylint: disable-msg=W0104
            hand.SetAxisTargetVelocity( sdh.All, ftv )
            finished = (nb_ok == 6) 
    
            time.sleep( loop_time )
    
        _dbg << "after endless loop\n" # pylint: disable-msg=W0104

        ####
        # open up again
        ##GotoStartPose( hand, "\nReopening hand (using POSE controller)..." )
        #
        ####
                
    except sdh.cSDHError,e:
        _dbg << "caught exception: " << e << "\n"    # pylint: disable-msg=W0104
        print "caught exception: %r" % e
    finally:
        # Close the connection to the SDH in an except/finally clause. This
        # way we can stop the hand even if an error or a user interruption
        # (KeyboardInterrupt) occurs.
        hand.Close()
        _dbg << "Successfully disabled joint controllers of SDH and closed connection\n"  # pylint: disable-msg=W0104
    
        # stop sensor:
        ts.Close()
        _dbg << "Successfully disabled tactile sensor controller of SDH and closed connection\n"  # pylint: disable-msg=W0104

#
######################################################################

if __name__ == "__main__":
    #import pdb
    #pdb.runcall( main )
    main()

#
######################################################################
