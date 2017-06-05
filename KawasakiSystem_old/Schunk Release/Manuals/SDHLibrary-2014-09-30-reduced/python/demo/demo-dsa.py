#!/usr/bin/env python
# -*- coding: latin-1 -*-
## \addtogroup sdh_library_python_demo_scripts_group
#  @{

#######################################################################
## \file
#  \section sdhlibrary_python_demo_dsa_py_general General file information
#
#    \author   Dirk Osswald
#    \date     2007-05-08
#
#  \brief  
#    Simple script to access tactile sensors of SDH. 
#    See demo-dsa.__doc__ and online help ("-h" or "--help") for available options.
#
#  \section sdhlibrary_python_demo_dsa_py_copyright Copyright
#
#  - Copyright (c) 2007 SCHUNK GmbH & Co. KG
#
#  <HR>
#  \internal
#
#    \subsection sdhlibrary_python_demo_dsa_py_details SVN related, detailed file specific information:
#      $LastChangedBy: Osswald2 $
#      $LastChangedDate: 2013-06-18 18:28:14 +0200 (Di, 18 Jun 2013) $
#      \par SVN file revision:
#        $Id: demo-dsa.py 10351 2013-06-18 16:28:14Z Osswald2 $
#
#  \subsection sdhlibrary_python_demo_dsa_py_changelog Changelog of this file:
#      \include demo-dsa.py.log
#
#######################################################################

## 
#  @}

#######################################################################
## \anchor sdhlibrary_python_demo_dsa_python_vars
#  \name   Python specific variables
#  
#  Some definitions that describe the script for python
#
#  @{

# pylint: disable-msg=W0622
## The docstring describing the purpose of the script:
__doc__ = '''
Simple script to demonstrate the use of the sdh.dsa module and the 
sdh.dsa.cDSA class in the sdh package.

Remarks:
- You must specify at least one of these options to see some output:
  -f | --fullframe  
  -C | --resulting
  -c | --controllerinfo 
  -s | --sensorinfoinfo
  -m | --matrixinfo=N
  
- Example usage:
  - Read a single full frame from tactile sensors connected via Ethernet.
    The SDH and the tactile sensors have a common IP-Address,
    here 192.168.1.42. The tactile sensors use TCP port 13000 (default).
    (Requires at least SDH-firmware v0.0.3.2)
    > demo-dsa.py --dsa_tcp=192.168.1.42 -f
     
  - Read a single full frame from tactile sensors connected to port 3 = COM4:
    > demo-dsa.py --dsaport=3 -f
     
  - Read a single full frame from tactile sensors connected to USB to
    RS232 converter 0:
    > demo-dsa.py --dsa_rs_device=0 -f
     
  - Read full frames continuously from tactile sensors connected to port 3 = COM4:
    > demo-dsa.py --dsaport=3 -f -r 1
     
  - Read full frames continuously 10 times per second from tactile sensors
    connected to port 3 = COM4:
    > demo-dsa --dsaport=3 -f -r 10

  - Read full frames continuously as fast as possible (DSA push-mode)
    from tactile sensors connected to port 3 = COM4:
    > demo-dsa --dsaport=3 -f -r 30

  - Read resulting values (contact area, contact force) continuously 
    from tactile sensors connected to port 3 = COM4:
    > demo-dsa.py --dsaport=3 -C -r 1
     
  - Read the sensor, controller, matrix 0 and matrix 1 infos 
    from tactile sensors connected to port 3 = COM4:
    > demo-dsa.py --dsaport=3 -s -c -m 0 -m 1
    
  - Get the version info of both the joint controllers and the tactile 
    sensor firmware from an SDH connected via Ethernet. 
    The SDH and the tactile sensors have a common IP-Address,
    here 192.168.1.42. The joint controller is attached to the
    TCP port 23 and the tactile sensors to TCP port 13000.
    (Requires at least SDH-firmware v0.0.3.2)
    > demo-dsa.py --tcp=192.168.1.42:23 --dsa_tcp=:13000 -v

  - Get the version info of both the joint controllers and the tactile 
    sensor firmware from an SDH connected to 
    - port 2 = COM3 (joint controllers) and 
    - port 3 = COM4 (tactile sensor controller): 
    > demo-dsa.py -p 2 --dsaport=3 -v
    
  - Set the sensitivity of all tactile sensor matrixes to 0.75 temporarily.
    The value will be used only temporarily (until reset or power cycle). 
    > demo-dsa.py --dsaport=3 --sensitivity=0.75 

  - Set the sensitivity of all tactile sensor matrixes to 0.75 persistently.
    The value will be stored persistently (i.e. will remain after reset or power cycle). 
    > demo-dsa.py --dsaport=3 --sensitivity=0.75 --persistent

  - Reset the sensitivity of all tactile sensor matrixes to their factory default.
    The value will be used only temporarily (until reset or power cycle). 
    > demo-dsa.py --dsaport=3 --sensitivity=0.75 --reset

  - Set the sensitivity of tactile sensor matrices 1 and 4 to individual\n"
    values temporarily.\n"
    The value will be used only temporarily (until reset or power cycle).\n"
    Sensor 1 (distal sensor of finger 1) will be set to 0.1\n"
    Sensor 4 (proximal sensor of finger 3) will be set to 0.4\n"
    > demo-dsa.py --dsaport=3 --sensitivity1=0.1 --sensitivity4=0.4 

  - Like for the sensitivity the threshold can be adjusted using
    the --threshold=VALUE or --thresholdX=VALUE arguments.
'''

__author__    = "Dirk Osswald: dirk.osswald@de.schunk.com"
__url__       = "http://www.schunk.com"
__version__   = "$Id: demo-dsa.py 10351 2013-06-18 16:28:14Z Osswald2 $"
__copyright__ = "Copyright (c) 2007 SCHUNK GmbH & Co. KG"

#  end of doxygen name group sdhlibrary_python_demo_dsa_python_vars
#  @}
######################################################################

import sdh
import sdh.dsa  # pylint: disable-msg=E0611,F0401
import time

######################################################################
# Some additional classes and functions

class cMovingAverage:
    '''Class to implement objects that calculate a moving average
    '''
    def __init__( self, window_size=7 ):
        '''Constructor, create a cMovingAverage object with the given window_size
        ''' 
        self.Reset( window_size )
        
    def Reset( self, window_size=7 ):
        '''Reset the internal state
        '''
        self.window_size = window_size
        self.data = [ 0.0 ]*self.window_size 
        self.next = 0
        
    def Add( self, v ):
        '''Add value v to the moving average calculation
        '''
        self.data[ self.next ] = v
        self.next += 1
        if self.next >= self.window_size:
            self.next = 0

    def Get( self ):
        '''Calculate and return the current moving average.
        '''
        sumv = 0
        for v in self.data:
            sumv += v
        return sumv / self.window_size
#---------------------------------------------------------------------
    

def CreateOptionParser():
    '''Create an option parser specifically for this demo program.
    '''
    ## Create an option parser object to parse common command line options:
    parser = sdh.cSDHOptionParser( usage    =  __doc__ + "\nusage: %prog [options]",
                                   revision = __version__ )
    
    # Remove options not applicable for this script
    parser.remove_option( "-c" ) # will also remove "--can"
    parser.remove_option( "-n" ) # will also remove "--net"
    parser.remove_option( "--id_read" ) 
    parser.remove_option( "--id_write" ) 
    parser.remove_option( "-R" ) # will also remove --radians
    parser.remove_option( "-F" ) # will also remove --fahrenheit
    
    # Add script specific options to the OptionParser:
    parser.add_option( "-f", "--fullframe",
                       dest="fullframes", default=False, action="store_true",
                       help="Print acquired full frames numerically." )
    
    parser.add_option( "-C", "--resulting",
                       dest="resulting", default=False, action="store_true",
                       help="Print calculated resulting values (area, force)." )
    
    parser.add_option( "-s", "--sensorinfo",
                       dest="sensorinfo", default=False, action="store_true",
                       help="Print sensor info from DSA (texel dimensions, number of texels...)." )
    
    parser.add_option( "-c", "--controllerinfo",
                       dest="controllerinfo", default=False, action="store_true",
                       help="Print controller info from DSA (version...)." )
    
    parser.add_option( "-m", "--matrixinfo",
                       dest="matrixinfo", default=[], type=int, action="append", metavar="MATRIX_INDEX",
                       help="Print matrix info for matrix with index MATRIX_INDEX from DSA. This option can be used multiple times." )
    
    parser.add_option( "--calibration",
                       dest="calibration", default=False, action="store_true",
                       help="Calibrate voltage to pressure calculation." )
    
    parser.add_option( "--calib_pressure",
                       dest="calib_pressure", default=None, type=float,
                       help="Pressure calibration value. E.g. determined using the --calibration option." )
    
    parser.add_option( "--calib_voltage",
                       dest="calib_voltage", default=None, type=float,
                       help="Voltage calibration value. E.g. determined using the --calibration option." )
    
    parser.add_option( "--calibration-force",
                       dest="calibration_force", default=0.0, type=float, metavar="CALIBRATION_FORCE",
                       help="External force applied for calibration in N (weight in kg * 9.81)." )

    parser.add_option( "--sensitivity",
                       dest="all_sensitivities", default=None, type=float, metavar="SENSITIVITY",
                       help="""Set the sensor sensitivities for all tactile sensor pads 
                            to the given value [0.0 .. 1.0] (0.0 is minimum, 1.0 
                            is maximum sensitivity).
                             
                            If --reset is given as well then SENSITIVITY is ignored and
                            the sensitivities are reset to the factory defaults.
                            To see the current setting for sensitivity use 
                            --showdsainfo.
                            
                            For setting sensitivities individually for a specific 
                            sensor X [0..5] use --sensitivityX=SENSITIVITY""" )
    for i in range(6):
        parser.add_option( "--sensitivity%d" % i,
                           dest="sensitivity%d" % i, default=None, type=float, metavar="SENSITIVITY",
                           help="Set sensor sensitivity specifically for sensor %d." % i )
    parser.add_option( "--threshold",
                       dest="all_thresholds", default=None, type=float, metavar="THRESHOLD",
                       help="""Set the sensor threshold for all tactile sensor pads 
                            to the given value [0.0 .. 1.0] (0.0 is minimum, 1.0 
                            is maximum threshold).
                            
                            If --reset is given as well then THRESHOLD is ignored
                            and the thresholds are reset to the factory defaults.
                            To see the current setting for threshold use 
                            --showdsainfo.
                            
                            For setting thresholds individually for a specific 
                            sensor X [0..5] use --thresholdX=THRESHOLD""" )
    for i in range(6):
        parser.add_option( "--threshold%d" % i,
                           dest="threshold%d" % i, default=None, type=float, metavar="THRESHOLD",
                           help="Set sensor threshold specifically for sensor %d." % i )
    parser.add_option( "--reset",
                       dest="reset", default=False, action="store_true", 
                       help="""If given, then the values given with --sensitivity(X)
                               and/or --threshold(X) are reset to their factory default.""" )
    parser.add_option( "--persistent",
                       dest="persistent", default=False, action="store_true",
                       help="""If given then all the currently set values for the
                       sensitivity or threshold are saved persistently 
                       in the configuration memory of the DSACON32m 
                       controller in the SDH.
                       
                       PLEASE NOTE: the maximum write endurance of the 
                       configuration memory is about 100.000 times!""" )
    parser.add_option( "--showdsasettings",
                       dest="showdsasettings", default=False, action="store_true", 
                       help="""If given, then current settings for sensitivity and 
                       threshold will be printed on stdout first.""" )
    
    return parser
#
######################################################################

######################################################################
# The main function
def main():
    '''Main function of demo script.
    Parses command line and reacts accordingly.
    '''
    # Create the parser object:
    parser = CreateOptionParser()
    # Parse (and handle, if possible) the command line options of the script:
    (options, args) = parser.parse_args()  # pylint: disable-msg=W0612
    
    # The parsed command line options are now stored in the options
    # object. E.g. options.port is the communication port to use, either
    # the default one or the one read from the -p | --port command line
    # option
    
    ## An object to print script-level debug messages, if requested.
    dbg = sdh.dbg.tDBG( flag=options.debug_level>0, fd=options.debug_output )
    dbg << "Debug messages of script are printed like this.\n" # pylint: disable-msg=W0104
    
    # reduce debug level for subsystems
    options.debug_level-=1
    
    dbg.var("options")
    #
    ######################################################################
    
    
    ######################################################################
    # The actual processing of the parsed arguments:

    print "Connecting to remote DSACON32m in SDH via %r." % (options.dsaport)
    print "This may take up to 8 seconds..."
    # pylint: disable-msg=E1101    
    ts = sdh.dsa.cDSA( port=options.dsaport, debug_level= options.debug_level-1, baudrate=options.baudrate, timeout=options.timeout, debug_output=options.debug_output )
    print "Connected.\n"
    
    if ( options.calib_pressure ):
        ts.calib_pressure = options.calib_pressure
    if ( options.calib_voltage ):
        ts.calib_voltage = options.calib_voltage
    
    try:
        # Print controller info if requested: 
        if ( options.controllerinfo ):
            print sdh.PrettyStruct( "Controller Info", ts.controller_info, exclude=[ 'bytes', 'payload'] )
        
        # Print sensor info if requested: 
        if ( options.sensorinfo ):
            print sdh.PrettyStruct( "Sensor Info", ts.sensor_info, exclude=[ 'bytes', 'payload'] )
    
        # Print selected matrix info if requested:
        for i in options.matrixinfo:
            print sdh.PrettyStruct( "Matrix Info %d" % i, ts.matrix_info[i], exclude=[ 'bytes', 'payload'] )
            
            if ( ts.controller_info.sw_version >= 268 ):
                print "         sensitivity = %f" % (ts.GetMatrixSensitivity(i).cur_sens)
                print " factory_sensitivity = %f" % (ts.GetMatrixSensitivity(i).fact_sens)
                print "           threshold = %d" % (ts.GetMatrixThreshold(i).threshold)
            
        #-----------
        # Prepare interactive calibration:
        if ( options.calibration ):
            ma_calib_pressure = []
            ma_calib_voltage  = []
            for m in range(ts.sensor_info.nb_matrices):
                ma_calib_pressure.append( cMovingAverage( 7 ) )
                ma_calib_voltage.append( cMovingAverage( 7 ) )

            print "Interactive calibration:"
            print "  This must be called with a framerate > 0 (-r|--framerate)"
            print "  Procedure: "

            print "  - Apply a known external force to a tactile sensor pad (e.g. a static weight)."
            print "  - Enter the value of the force below and press return."
            print "  - The measurement starts and the averaged calibration output will be"
            print "    printed for all sensor pads continuously:"
            print "    \"Calib: (calib_pressure0 calib_voltage0) ... (calib_pressure5 calib_voltage5)"
            if ( options.calibration_force == 0.0 ):
                options.calibration_force = float(raw_input( "Enter external force applied in N (weight in kg * 9.81): " ) )

        #-----------
        if ( options.showdsasettings ):
            if ( ts.controller_info.sw_version < 268 ):
                print "To be able to read the sensitivity/threshold settings you must update"
                print "the firmware of the DSACON32m (tactile sensor controller in the SDH)"
                print "to at least release R268." 
            else:
                for (i,descr) in zip( range(6), [ "finger %d %s" % (f,t) for (t,f) in zip( ["proximal", "distal"]*3, [1,1,2,2,3,3] ) ] ):
                    print "Sensor %d (%s):" % (i,descr)
                    print "         sensitivity = %f" % (ts.GetMatrixSensitivity(i).cur_sens)
                    print " factory_sensitivity = %f" % (ts.GetMatrixSensitivity(i).fact_sens)
                    print "           threshold = %d" % (ts.GetMatrixThreshold(i).threshold)
        #-----------
    
        #-----------
        # Set sensitivities if requested
        if ( options.all_sensitivities ):
            ts.SetMatrixSensitivity( 0, 
                                     options.all_sensitivities, 
                                     do_all_matrices=True, 
                                     do_reset=options.reset, 
                                     do_persistent=options.persistent )
        else:
            for mi in range(6):
                if ( getattr( options, "sensitivity%d" % mi ) ):
                    ts.SetMatrixSensitivity( mi, 
                                             getattr( options, "sensitivity%d" % mi ), 
                                             do_all_matrices=False, 
                                             do_reset=options.reset, 
                                             do_persistent=options.persistent )
    
        #-----------
        # Set thresholds if requested
        if ( options.all_thresholds ):
            ts.SetMatrixThreshold( 0, 
                                   options.all_thresholds, 
                                   do_all_matrices=True, 
                                   do_reset=options.reset, 
                                   do_persistent=options.persistent )
        else:
            for mi in range(6):
                if ( getattr( options, "threshold%d" % mi ) ):
                    ts.SetMatrixThreshold( mi, 
                                           getattr( options, "threshold%d" % mi ), 
                                           do_all_matrices=False, 
                                           do_reset=options.reset, 
                                           do_persistent=options.persistent )
        #-----------
    
    
        #-----------
        # Start acquiring full frames for further processing:
        acquire_frame = options.fullframes or options.resulting or options.calibration
        if ( acquire_frame or options.framerate > 0 ):
            do_single_frames = options.framerate < 30;

            if ( do_single_frames ):
                # Make remote tactile sensor controller stop sending data automatically as fast as possible (prepare for DSA pull-mode):
                dbg << "Starting DSA pull-mode, framerate=0 do_rle=" << options.do_RLE << " do_data_acquisition=false" <<  "\n"
                ts.SetFramerate( framerate=0, do_RLE=options.do_RLE, do_data_acquisition=False );
            else:
                # Make remote tactile sensor controller send data automatically as fast as possible (DSA push-mode):
                dbg << "Starting DSA push-mode, framerate=1 do_rle=" << options.do_RLE << " do_data_acquisition=true" <<  "\n"
                ts.SetFramerate( framerate=1, do_RLE=options.do_RLE )
                # remark: any value > 0 for framerate will make the remote DSACON32m in the SDH send data with the highest possible datarate
    
        #-----------
        # start periodic or one time processing of full frames if requested:
        period_s = 0.0
        if ( options.framerate > 0):
            period_s = 1.0 / float(options.framerate)
        remaining_s = 0.0
        nb_errors = 0
        nb_frames = 0
        start = time.time()
        now = start
        last = start
        nb_last = 0
        while ( acquire_frame ):
            #-----------
            try:
                if ( do_single_frames ):
                    start = time.time()
                    ts.SetFramerateRetries( 0, options.do_RLE, True, 3 );
                # Read and parse a full frame:
                ts.ReadFrame()
                now = time.time()
                nb_frames += 1

                #-----------
                # Print it as matrix if requested:
                if ( options.fullframes ):
                    ts.PrintFrame()

                if ( options.framerate > 0 and nb_frames>0 ):
                    if (now-last != 0.0):
                        print "Actual framerate=%.1fHz  nb_frames=%d  nb_errors=%d (%.1f%%)" % ((nb_frames-nb_last)/(now-last), nb_frames, nb_errors, ((100.0*nb_errors)/nb_frames))
                    else:
                        print "                         nb_frames=%d  nb_errors=%d (%.1f%%)" % (nb_frames, nb_errors, ((100.0*nb_errors)/nb_frames))
                if ( now - last > 3.0 ):
                    # average framerate over the last 3 seconds (required for TCP since frames come in too fast)
                    last = now
                    nb_last = nb_frames

                #-----------
                # Do some processing and print the resulting values:
                if ( options.resulting ):
                    print "Frame age: %d ms" % ts.GetAgeOfFrame()
                    for fi in ts.all_fingers:
                        for part in ts.all_parts:
                            (force, cog_x, cog_y, area) = ts.GetContactForce( fi, part )
                            print "Finger %d part %d: force = %f N  cog = (%f mm, %f mm)  area = %f mm*mm" % (fi, part, force, cog_x, cog_y, area )
                    print "Total contact area: %f mm*mm" % ts.GetContactArea()
        
                #-----------
                # Do interactive calibration:
                if ( options.calibration ):
                    for m in range(ts.sensor_info.nb_matrices):
                        sum_voltages = 0.0
                        nbcells = 0
                        for y in range( 0, ts.matrix_info[m].cells_y ):
                            for x in range( 0, ts.matrix_info[m].cells_x ):
                                v = ts.GetTexel( m, x, y )
            
                                sum_voltages += v
                                if ( v > 0 ):
                                    nbcells += 1
            
                        if nbcells > 0:
                            calib_pressure = options.calibration_force/(nbcells * ts.matrix_info[0].texel_width * ts.matrix_info[0].texel_height)/nbcells    # N/(mm*mm)
                            calib_voltage  = sum_voltages/nbcells
                        else:
                            calib_pressure = 0.0
                            calib_voltage  = 0.0
            
                        ma_calib_pressure[m].Add( calib_pressure )
                        ma_calib_voltage[m].Add( calib_voltage )
            
                        #print "Calibration values for the given external force of %f N:" % options.calibration_force
                        dbg << "matrix %d: calib_pressure / calib_voltage: %8.6f, %8.1f  (averaged: (%8.6f, %6.1f)\n" % (m, calib_pressure, calib_voltage, ma_calib_pressure[m].Get(), ma_calib_voltage[m].Get() ) # pylint: disable-msg=W0104
                    print "Calib:",
                    for m in range(ts.sensor_info.nb_matrices):
                       print " (%8.6f %6.1f)" % (ma_calib_pressure[m].Get(), ma_calib_voltage[m].Get() ),
                    print
        
                #-----------
                # Stop acquiring if only a single frame was requested:
                if ( options.framerate <= 0 ):
                    acquire_frame = False

                #-----------
                
                if ( do_single_frames ):
                    remaining_s = period_s - (time.time()-start)
                    if ( remaining_s > 0.0 ):
                        time.sleep( remaining_s )

            except sdh.dsa.cDSAError, e:
                nb_errors += 1
                dbg << "Caught and ignored cDSAError: " << repr(e) << " nb_errors=" << nb_errors << "\n"
            #-----------
    except KeyboardInterrupt:
        pass
    finally:
        print "\ncleaning up"
        # stop sensor:
        ts.Close()

#
######################################################################

if __name__ == "__main__":
    #import pdb
    #pdb.runcall( main )
    main()

######################################################################
# some usefull editing settings for emacs:
#
#;;; Local Variables: ***
#;;; mode:python ***
#;;; End: ***
#
######################################################################
