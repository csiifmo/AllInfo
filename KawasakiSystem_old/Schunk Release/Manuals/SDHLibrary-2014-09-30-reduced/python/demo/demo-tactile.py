#!/usr/bin/env python
# -*- coding: latin-1 -*-
## \addtogroup sdh_library_python_demo_scripts_group
#  @{

#######################################################################
#
## \file
#  \section sdhlibrary_python_demo_tactile_general General file information
#
#    \author   Dirk Osswald
#    \date     2007-03-12
#
#  \brief  
#    Simple GUI to visualize tactile sensors of SDH. 
#    See demo-tactile.__doc__ and the online help ("-h" or "--help") for available options.
#
#  \section sdhlibrary_python_demo_tactile_copyright Copyright
#
#  Copyright (c) 2007 SCHUNK GmbH & Co. KG
#
#  <HR>
#  \internal
#
#    \subsection sdhlibrary_python_demo_tactile_details SVN related, detailed file specific information:
#      $LastChangedBy: Osswald2 $
#      $LastChangedDate: 2013-06-18 18:28:14 +0200 (Di, 18 Jun 2013) $
#      \par SVN file revision:
#        $Id: demo-tactile.py 10351 2013-06-18 16:28:14Z Osswald2 $
#
#  \subsection sdhlibrary_python_demo_tactile_changelog Changelog of this file:
#      \include demo-tactile.py.log
#
#######################################################################

## 
#  @}


#######################################################################
## \anchor sdhlibrary_python_demo_tactile_python_vars
#  \name   Python specific variables
#  
#  Some definitions that describe the script for python
#
#  @{

# pylint: disable-msg=W0622
## The docstring describing the purpose of the script:
__doc__ = '''
Simple GUI to visualize tactile sensors of SDH. (Python demo script using the sdh.py import library.)
  
- Example usage:
  - Display the tactile sensors connected via Ethernet.
    The SDH and the tactile sensors have a common IP-Address,
    here 192.168.1.42. The tactile sensors use TCP port 13000 (default).
    (Requires at least SDH-firmware v0.0.3.2)
    > demo-tactile.py --dsa_tcp=192.168.1.42

  - Display the tactile sensors connected to port 3 = COM4
    with the default style (colors, no numbers):
    > demo-tactile.py --dsaport=3
    
  - Display the tactile sensors connected to USB to RS232
    converter 0 with the default style (colors, no numbers):
    > demo-tactile.py --dsa_rs_device=/dev/ttyUSB0
    
  - Display the tactile sensors connected to port 3 = COM4
    with greycodes and numerical output in percent:
    > demo-tactile.py --dsaport=3 --style=grey --style=percent
    
  - Get the version info of both the joint controllers and the tactile 
    sensor firmware from an SDH connected to 
    - port 2 = COM3 (joint controllers) and 
    - port 3 = COM4 (tactile sensor controller) 
    > demo-tactile.py -p 2 --dsaport=3 -v
    
  - Get the version info of both the joint controllers and the tactile 
    sensor firmware from an SDH connected via Ethernet. 
    The SDH and the tactile sensors have a common IP-Address,
    here 192.168.1.42. The joint controller is attached to the
    TCP port 23 and the tactile sensors to TCP port 13000.
    (Requires at least SDH-firmware v0.0.3.2)
    > demo-tactile.py --tcp=192.168.1.42:23 --dsa_tcp=:13000 -v
'''

__author__    = "Dirk Osswald: dirk.osswald@de.schunk.com"
__url__       = "http://www.schunk.com"
__version__   = "$Id: demo-tactile.py 10351 2013-06-18 16:28:14Z Osswald2 $"
__copyright__ = "Copyright (c) 2007 SCHUNK GmbH & Co. KG"

#  end of doxygen name group sdhlibrary_python_demo_tactile_python_vars
#  @}
######################################################################


######################################################################
# Import the needed modules

# Import the sdh.py and dsa.py python import modules:
import sdh, sdh.dsa, sdh.tkdsa

# The GUI stuff
from Tkinter import *
import tkFileDialog


_dbg = sdh.dbg.tDBG( True )

#
######################################################################


            
#-----------------------------------------------------------------
class cTkSDHTactileApplication(Frame):
    '''The "Application" class of demo-tactile.py, the simple SDH tactile visualizer

    - creates the widgets
    - defines Keyboard shortcuts (see docstring of file)
    - defines callbacks to command the SDH
    '''
    
    def __init__(self, ts, framerate=10, master=None, debug_level=0, style=["color"] ):
        ''' Constructor of cTkSDHTactileApplication
        \param self        - the instance of the class that this function operates on (the "object") 
        \param ts          - the initialized cDSA object to communicate with the remote DSACON32m controller
        \param framerate   - the framerate for updating the GUI (the tactile sensors will always send at maximum speed of 30 FPS)
        \param master      - the master widget of this
        \param debug_level - level of debug messages to print 
                             - 0 = no messages
                             - 1 = print messages of this object
                             - 2 = print messages of underlying tkdsa.cTkSDHTactileSensorPatches as well
        \param style       - style for displaying tactile sensor data, see online help or tkdsa.cTkSDHTactileSensorPatches for available styles
        '''
        Frame.__init__(self, master, class_="cTkSDHTactileApplication" )
        self.grid(sticky=N+S+W+E)

        self.framerate = framerate
        self.ts = ts
        self.debug_level = debug_level
        self.style = style
        # create all subwidgets
        self.CreateWidgets()

        # Create a thread that reads the tactile sensor data continuously:
        # (For now the actual sending framerate of the remote DSACON32m is always as fast as possible (30 FPS).)
        self.ts.StartUpdater( self.framerate, do_RLE = TRUE )
        _dbg << "after StartUpdater\n"  # pylint: disable-msg=W0104
        self.UpdateTSFrame()

    #-----------------------------------------------------------------
    def UpdateTSFrame( self ):
        # The reading of the tactile sensor data is done by another thread,
        # so just paint the current frame
        self.Repaint()
        
        # arrange callback:
        timeout = sdh.ToRange( 1000/self.framerate, 1, 1000 )

        _dbg << "UpdateTSFrame updated a frame with age %d ms (next timeout in %d ms)\n" % (self.ts.GetAgeOfFrame(), timeout) # pylint: disable-msg=W0104
        self.after( timeout, self.UpdateTSFrame)

       
    #-----------------------------------------------------------------
    ## Create the GUI widgets: 
    def CreateWidgets(self):
        top=self.winfo_toplevel()
        top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.tsps = sdh.tkdsa.cTkSDHTactileSensorPatches( self.ts, master=self, debug_level=self.debug_level-1, debug_output=_dbg.GetOutput(), style=self.style )
        self.tsps.grid( row=0, column=0, sticky=N+S+W+E )

    #-----------------------------------------------------------------
    def Repaint( self ):
        self.tsps.Repaint()

            
# end of class cTkSDHTactileApplication
#######################################################################


def main():
           
    ######################################################################
    # Command line option handling:
    
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
    # redefine -r / --framrate option:
    parser.remove_option( "-r" ) # will also remove --framerate
    parser.add_option( "-r", "--framerate",
                       dest="framerate", default=10, type=int,
                       help="Framerate for updating the display. The DSACON32m controller in the SDH will always send data at the highest possible rate (ca. 30 FPS (frames per second)). The actual reachable rate of updates depends on your system (CPU/memory)." )
    parser.add_option( "-s", "--style",
                       dest="style", default=[], type=str, action="append",
                       help="Display style. Valid styles are: %s. This option can be given multiple times. So to set grey and percent use '-s grey -s percent'." % sdh.tkdsa.DisplayStyles() )

    parser.add_option( "--sensitivity",
                       dest="all_sensitivities", default=None, type=float, metavar="SENSITIVITY",
                       help="""Set the sensor sensitivities for all tactile sensor pads 
                            to the given value [0.0 .. 1.0] (0.0 is minimum, 1.0 
                            is maximum sensitivity).
                             
                            If --reset is given as well then SENSITIVITY is ignored and
                            the sensitivities are reset to the factory defaults.
                            To see the current setting for sensitivity use  
                            --showdsasettings.
                            
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
                            --showdsasettings.
                            
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
    
    # Parse (and handle, if possible) the command line options of the script:
    (options, args) = parser.parse_args()

    ## An object to print script-level debug messages, if requested.
    global _dbg
    _dbg.SetFlag( flag=options.debug_level>0 )
    _dbg.SetOutput( options.debug_output )
    _dbg << "Debug messages of script are printed like this.\n" # pylint: disable-msg=W0104

    _dbg << sdh.PrettyStruct( "options", options )  # pylint: disable-msg=W0104
    
    # Change default values if invalid:
    if ( options.framerate <= 0 ):
        options.framerate = 10
    
    if ( options.style == [] ):
        options.style = ["color"]
        
    # The parsed command line options are now stored in the options
    # object. E.g. options.port is the communication port to use, either
    # the default one or the one read from the -p | --port command line
    # option
    
    
    #
    ######################################################################
    
    
    ######################################################################
    # The actual script code 
    
    ## Create a ts (tactile sensor) object of the class cDSA according to the given options:
    print "Connecting to remote DSACON32m in SDH via RS232 port %r" % (options.dsaport)
    print "This may take up to 8 seconds..."
    ts = sdh.dsa.cDSA( port=options.dsaport, debug_level=options.debug_level-1, debug_output=options.debug_output )
    print "Connected.\n"
    
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

    
    # Pack the actual communication commands in a try block to simplify proper cleanup.
    try:
        root = Tk()
        try:
            root.wm_iconbitmap(sdh.GetIconPath())
        except tkinter.TclError,e:
            dbg << "Ignoring tkinter.TclError %r\n" % e
            pass # ignore error
        app = cTkSDHTactileApplication( ts, framerate=options.framerate, master=root, debug_level=options.debug_level-1, style=options.style )
        app.master.title("demo-tactile: Demonstration of a simple SDH tactile sensor visualizer" )
        app.mainloop()
    
    finally:
        # Close the connection to the DSA in an except/finally clause. This
        # way we can stop the tactile sensor even if an error or a user interruption
        # (KeyboardInterrupt) occurs.
        ts.Close()
    
    
# end of main
######################################################################

if __name__ == "__main__":
    #import pdb
    #pdb.runcall( main )
    main()
