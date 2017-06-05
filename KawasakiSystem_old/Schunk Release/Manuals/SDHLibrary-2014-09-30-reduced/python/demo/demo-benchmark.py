#!/usr/bin/env python
# -*- coding: latin-1 -*-
## \addtogroup sdh_library_python_demo_scripts_group
#  @{

#######################################################################
## \file
#  \section sdhlibrary_python_demo_benchmark_py_general General file information
#
#    \author   Dirk Osswald
#    \date     2011-02-08
#
#  \brief  
#    Simple script to do grasping using tactile sensor info feedback. 
#    See demo-benchmark.__doc__ and the online help ("-h" or "--help") 
#    for a list of available options.
#
#  \section sdhlibrary_python_demo_benchmark_py_copyright Copyright
#
#  - Copyright (c) 2007 SCHUNK GmbH & Co. KG
#
#  <HR>
#  \internal
#
#    \subsection sdhlibrary_python_demo_benchmark_py_details SVN related, detailed file specific information:
#      $LastChangedBy: Osswald2 $
#      $LastChangedDate: 2013-06-18 18:28:14 +0200 (Di, 18 Jun 2013) $
#      \par SVN file revision:
#        $Id: demo-benchmark.py 10351 2013-06-18 16:28:14Z Osswald2 $
#
#  \subsection sdhlibrary_python_demo_benchmark_py_changelog Changelog of this file:
#      \include demo-benchmark.py.log
#
#######################################################################

## 
#  @}


#######################################################################
## \anchor sdhlibrary_python_demo_benchmark_python_vars
#  \name   Python specific variables
#  
#  Some definitions that describe the script for python
#
#  @{

# pylint: disable-msg=W0622
## The docstring describing the purpose of the script:
__doc__ = '''Simple script to benchmark communication speed of the SDH:
The hand will move to a start position in coordinated position control
mode first. Then periodic movements are performed using the velocity
with acceleration ramp controller while the communication and control
rate is printed.

- Example usage:
  - Start moving wildly using an SDH that is connected via Ethernet:
    The SDH has IP-Address 192.168.1.42 and is attached to TCP port 23.
    (Requires at least SDH-firmware v0.0.3.1)
    > demo-benchmark.py --tcp=192.168.1.42:23 
    
    
  - Start moving wildly using an SDH that is connected to:
    - port 2 = COM3 (joint controllers) and 
    > demo-benchmark.py -p 2
    
    
  - Start moving wildly using an SDH that is connected to:
    - USB to RS232 converter 0 (joint controllers) and 
    > demo-benchmark.py --sdh_rs_device=/dev/ttyUSB0 
    
    
  - Get the version info of both the joint controllers and the tactile 
    sensor firmware from an SDH connected via Ethernet. 
    The SDH and the tactile sensors have a common IP-Address,
    here 192.168.1.42. The joint controller is attached to the
    TCP port 23 and the tactile sensors to TCP port 13000.
    (Requires at least SDH-firmware v0.0.3.2)
    > demo-benchmark.py --tcp=192.168.1.42:23 --dsa_tcp=:13000 -v


  - Get the version info of both the joint controllers and the tactile 
    sensor firmware from an SDH connected to 
    - port 2 = COM3 (joint controllers) and 
    - port 3 = COM4 (tactile sensor controller) 
    > demo-benchmark.py -p 2 --dsaport=3 -v
'''

__author__    = "Dirk Osswald: dirk.osswald@de.schunk.com"
__url__       = "http://www.schunk.com"
__version__   = "$Id: demo-benchmark.py 10351 2013-06-18 16:28:14Z Osswald2 $"
__copyright__ = "Copyright (c) 2011 SCHUNK GmbH & Co. KG"

#  end of doxygen name group sdhlibrary_python_demo_benchmark_python_vars
#  @}
######################################################################

import sys
import time
import math
import copy

import sdh
import sdh.dsa

DEMO_BENCHMARK_USE_COMBINED_SET_GET = 1

######################################################################
# Command line option handling:


def CreateOptionParser():
    '''Create an option parser specifically for this demo program.
    '''
    ## Create an option parser object to parse common command line options:
    parser = sdh.cSDHOptionParser( usage    =  __doc__ + "\nusage: %prog [options]",
                                   revision = __version__ )

    return parser
    
#
######################################################################

def GotoPose( hand, ta ):
    hand.SetController( hand.eControllerType["eCT_POSE"] )
    hand.SetAxisTargetVelocity( sdh.All, 50 )
    hand.SetAxisTargetAngle( sdh.All, ta )
    hand.MoveAxis( sdh.All )

def Flat( l, sep = "" ):
    '''print flat representation of iterable l ([1,2,3] yields "1, 2, 3")
    '''
    s = ""
    for e in l:
        s += sep + str(e)
        sep = ", "
    return s 

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
    
    # Pack the actual movement commands in a try block
    try:
        max_vel = hand.GetAxisMaxVelocity( sdh.All )
        nb_axes = hand.NUMBER_OF_AXES
        ####


        ####
        # Prepare movements:

        # the given start positions:
        start_pose = [ 10, -10, 0, -10, 0, -10, 0 ]

        # the given end positions:
        end_pose = [80,-80,-80,-80,-80,-80,-80]  # axis end positions in deg

        # we want to make every axis move independently with velocity
        #   v(t)=a*sin(2*PI * t/p)
        # for given period p and amplitude a
        # the position is determined by:
        #   s(t)= a * p / (2*PI) * (1-cos(2*PI * t/p))
        # The maximum position m is at p/2
        #   m= a*p/PI
        # For fixed maximum position the amplitude thus calculates to
        #   a= m*PI/p

        # the given periods p:
        aperiod= [10.0,5.0,4.0,3.0,4.0,5.0,3.0]  # axis movement cycle periods in s

        # the calculated amplidutes p of the sinusoidal
        aamplitude = [0.0] * len(aperiod)  # axis movement velocity amplitude in deg/s
        for ai in range( nb_axes ):
            aamplitude[ai] = (end_pose[ai]-start_pose[ai]) * math.pi / aperiod[ai]
            # limit to allowed range:
            aamplitude[ai] = sdh.ToRange( aamplitude[ai], -max_vel[ai]+1.0, +max_vel[ai]-1.0 )
        ####


        ####
        # move to start pose:
        GotoPose( hand, start_pose );
        ####


        ####
        # start moving sinusoidal:
        _dbg << "  Moving with velocity with acceleration ramp controller.\n"
        _dbg.flush()

        # switch to velocity with acceleration ramp controller type:
        hand.SetController( hand.eControllerType["eCT_VELOCITY_ACCELERATION"] )
        hand.SetAxisTargetAcceleration( sdh.All, 100 );

        aaa = [0.0]*nb_axes  # axis actual angles
        aav = [0.0]*nb_axes  # axis actual velocities
        atv = [0.0]*nb_axes  # axis target velocities


        min_angles = hand.GetAxisMinAngle( sdh.All );
        max_angles = hand.GetAxisMaxAngle( sdh.All );
        max_velocities = hand.GetAxisMaxVelocity( sdh.All );


        recorded_data = [];

        ####
        # perform motion for duration seconds
        duration = 10.0; # duration in s
        t = 0
        start_time = time.time()
        while (t < duration):
            try:
                # get time elapsed since start_time
                t = time.time() - start_time
    
                # Get current position of axes:
                aaa = hand.GetAxisActualAngle( sdh.All );
    
                # calculate new target velocities for axes:
                for ai in range(nb_axes):
                    atv[ai] = aamplitude[ai] * math.sin( 2.0*math.pi/aperiod[ai] * t );
    
                if DEMO_BENCHMARK_USE_COMBINED_SET_GET:
                    # Set target velocities and get current velocities of axes:
                    aav = hand.SetAxisTargetGetAxisActualVelocity( sdh.All, atv );
                else:
                    # Get current velocities of axes:
                    aav = hand.GetAxisActualVelocity( sdh.All );
    
                    hand.SetAxisTargetVelocity( sdh.All, atv );
    
                #_dbg << t << ", " << aaa << ", " << aav << ", " << atv << "\n"
                #_dbg << t << ", " << atv << "\n"
                #_dbg.flush()
    
                recorded_data.append( ( t, aaa, aav, copy.copy(atv) ) )
            except sdh.cSDHError,e:
                _dbg << "caught exception: " << e << "(ignored)\n"    # pylint: disable-msg=W0104

        end_time = time.time()
        ####

        ####
        # stop motion softly within brake_time second
        brake_time = 0.5
        t = 0
        while ( t < brake_time ):
            t = time.time() - end_time

            for ai in range( nb_axes ):
                atv[ai] = aav[ai] * ( 1.0-t/brake_time);
            hand.SetAxisTargetVelocity( sdh.All, atv );
        ####


        ####
        # open up again
        GotoPose( hand, start_pose );
        #
        ####


        ####
        # do evaluation
        dt_min = 1000.0
        t_dt_min = 0.0
        dt_max = 0.0
        t_dt_max = 0.0
        dt = 0.0
        r = 0
        print "# combined gnuplot commands + data. Use plot.py for easy viewing"
        print "## plot using 2:3 with lines title 'dt [s]'"
        print "## plot using 2:4 with lines title 'aaa[0] [deg]'"
        print "## plot using 2:5 with lines title 'aaa[1] [deg]'"
        print "## plot using 2:6 with lines title 'aaa[2] [deg]'"
        print "## plot using 2:7 with lines title 'aaa[3] [deg]'"
        print "## plot using 2:8 with lines title 'aaa[4] [deg]'"
        print "## plot using 2:9 with lines title 'aaa[5] [deg]'"
        print "## plot using 2:10 with lines title 'aaa[6] [deg]'"
        print "## plot using 2:11 with lines title 'aav[0] [deg/s]'"
        print "## plot using 2:12 with lines title 'aav[1] [deg/s]'"
        print "## plot using 2:13 with lines title 'aav[2] [deg/s]'"
        print "## plot using 2:14 with lines title 'aav[3] [deg/s]'"
        print "## plot using 2:15 with lines title 'aav[4] [deg/s]'"
        print "## plot using 2:16 with lines title 'aav[5] [deg/s]'"
        print "## plot using 2:17 with lines title 'aav[6] [deg/s]'"
        print "## plot using 2:18 with lines title 'atv[0] [deg/s]'"
        print "## plot using 2:19 with lines title 'atv[1] [deg/s]'"
        print "## plot using 2:20 with lines title 'atv[2] [deg/s]'"
        print "## plot using 2:21 with lines title 'atv[3] [deg/s]'"
        print "## plot using 2:22 with lines title 'atv[4] [deg/s]'"
        print "## plot using 2:23 with lines title 'atv[5] [deg/s]'"
        print "## plot using 2:24 with lines title 'atv[6] [deg/s]'"
        print "## set xlabel 'Time [s]'"
        print "## set ylabel 'Control-Period / Position / Velocity [s] / [deg] / [deg/s]'"
        print "## set grid"
        print "## set title  \"demo-benchmark: SDH moving in acceleration + velocity control mode\""

        it0 = 0
        it1 = 1
        print "# i, t, dt, aaa[0..6], aav[0..6], atv[0..6]"
        print "%r, %r, %r, %s, %s, %s" % (r,recorded_data[it1][0], dt, Flat(recorded_data[it1][1]), Flat(recorded_data[it1][2]), Flat(recorded_data[it1][3]))
        while it1 < len( recorded_data ):

            dt = recorded_data[it1][0] - recorded_data[it0][0];
            if (  dt < dt_min ):
                dt_min = dt;
                t_dt_min = recorded_data[it1][0];
            if (  dt > dt_max ):
                dt_max = dt;
                t_dt_max = recorded_data[it1][0];

            print "%r, %r, %r, %s, %s, %s" % (r,recorded_data[it1][0], dt, Flat(recorded_data[it1][1]), Flat(recorded_data[it1][2]), Flat(recorded_data[it1][3]))
            
            it0 += 1
            it1 += 1
            r   += 1

        dt_avg = (end_time - start_time) / len(recorded_data)
        print "## set label 'dt_min=",dt_min,"' at ", t_dt_min, ",", dt_min, " front point"
        print "## set label 'dt_max=",dt_max,"' at ", t_dt_max, ",", dt_max, " front point"
        print "## set label 'dt_avg=",dt_avg,"' at ", recorded_data[it0][0], ",", dt_avg, " front point"
        print "## set title  \"demo-benchmark.py: SDH moving in acceleration + velocity control mode\\ndt_avg = ", dt_avg, "   fps = ", 1.0/dt_avg,
        print "\\ndebug_level = ", options.debug_level+1, "   DEMO_BENCHMARK_USE_COMBINED_SET_GET = ", DEMO_BENCHMARK_USE_COMBINED_SET_GET, "\""
        sys.stdout.flush()
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
    
#
######################################################################

if __name__ == "__main__":
    #import pdb
    #pdb.runcall( main )
    main()

#
######################################################################
