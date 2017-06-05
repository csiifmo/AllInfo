#!/usr/bin/env python
# -*- coding: latin-1 -*-
## \addtogroup sdh_library_python_demo_scripts_group
#  @{

#######################################################################
#
## \file
#  \section sdhlibrary_python_calc_workspace_general General file information
#
#    \author   Dirk Osswald
#    \date     2007-02-06
#
#  \brief 
#    Output a data file with xyz fingertip positions for all possible angles
#
#    Will not connect to a real SDH.
#    
#    Usefulle e.g. as input for gnuplot's  splot command:
#
#    - In a shell type:
#    \code
#    demo-calc-workspace.py > workspace.dat
#    \endcode
#    - Then in a gnuplot command line:
#    \code
#    splot 'workspace.dat' using 4:5:6, 'workspace.dat' using 7:8:9, 'workspace.dat' using 10:11:12
#    \endcode
#    
#    Start the script with \c "-h" or \c "--help" command line option
#    to see the online help.
#
#  \section sdhlibrary_python_calc_workspace_copyright Copyright
#
#  Copyright (c) 2007 SCHUNK GmbH & Co. KG
#
#  <HR>
#  \internal
#
#    \subsection sdhlibrary_python_calc_workspace_details SVN related, detailed file specific information:
#      $LastChangedBy: Osswald2 $
#      $LastChangedDate: 2009-05-04 19:17:39 +0200 (Mo, 04 Mai 2009) $
#      \par SVN file revision:
#        $Id: demo-calc-workspace.py 4355 2009-05-04 17:17:39Z Osswald2 $
#
#  \subsection sdhlibrary_python_calc_workspace_changelog Changelog of this file:
#      \include demo-calc-workspace.py.log
#
#######################################################################

## 
#  @}


#######################################################################
## \anchor sdhlibrary_python_calc_workspace_python_vars
#  \name   Python specific variables
#  
#  Some definitions that describe the script for python
#
#  @{
'''
Output a data file with xyz fingertip positions for all possible angles
'''

__author__    = "Dirk Osswald: dirk.osswald@de.schunk.com"
__url__       = "http://www.schunk.com"
__version__   = "$Id: demo-calc-workspace.py 4355 2009-05-04 17:17:39Z Osswald2 $"
__copyright__ = "Copyright (c) 2007 SCHUNK GmbH & Co. KG"

#  end of doxygen name group sdhlibrary_python_calc_workspace_python_vars
## @}
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

types = dict( all=0, contour=1 )
# Add an option to set step widths
parser.add_option( "--s0",
                   dest="step0", default=5, type=int, metavar="STEP",
                   help="Set step width for finger axis angle 0 to STEP, default=5.")
parser.add_option( "--s1",
                   dest="step1", default=5, type=int, metavar="STEP",
                   help="Set step width for finger axis angle 1 (axis angles 1/3/5) to STEP, default=5.")
parser.add_option( "--s2",
                   dest="step2", default=5, type=int, metavar="STEP",
                   help="Set step width for finger axis angle 2 (axis angles 2/4/6) to STEP, default=5.")

parser.add_option( "-t", "--type",
                   dest="type", default="all", type=str, metavar="TYPE",
                   help="The type of points to generate: 'all' : full workspace, 'surface' only the surface")

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

# make shure we are using the 'virutal' port
options.port = -1

## Create a global instance "hand" of the class cSDH according to the given options:
hand = sdh.cSDH( options=options.__dict__ )
dbg << "Successfully created cSDH instance\n"  # pylint: disable-msg=W0104


def Print( a0,a1,a2 ):
    print "%f %f %f  " % (a0,a1,a2),
    for fi in (0,1,2):
        if (fi==1):
            x,y,z = hand.GetFingerXYZ( fi, [0.0,a1,a2] )
        else:
            x,y,z = hand.GetFingerXYZ( fi, [a0,a1,a2] )

        print "%f %f %f  " % (x,y,z),
    print
    

if (options.type == "all"):
    for a2 in range(-90,91,options.step2):
        for a1 in range(-90,91,options.step1):
            for a0 in range(0,91,options.step0):
                Print( a0, a1, a2 )
        print
        
if (options.type =="contour"):

    phi = 90.0 - 2.0 * sdh.RadToDeg( sdh.math.atan( hand.l2 / hand.l1 ) )

    # a1 from 'out' to 'in' -90 --> 90
    for a1 in range(-90,91,options.step1):
        if (a1 == -90):
            for a2 in range(-90,1,options.step2):
                for a0 in range(0,90,options.step0):
                    Print( a0, a1, a2 )
                print

        elif (-90 < a1  and  a1 < 90):
            for a2 in [0]:
                for a0 in range(0,90,options.step0):
                    Print( a0, a1, a2 )
                print

        else:
            for a2 in range(0,91,options.step2):
                for a0 in range(0,90,options.step0):
                    Print( a0, a1, a2 )
                print

    # a1 back from 'in' to 'out'  -90 --> 90
    for a1 in range(90,-91,-options.step1):
            for a2 in [90]:
                for a0 in range(0,90,options.step0):
                    Print( a0, a1, a2 )

                print

    # missing part from a1=phi to -90 with a2=-90
    for a1 in range(-int(phi+0.5), -91, -options.step1):
            for a2 in [-90]:
                for a0 in range(0,90,options.step0):
                    Print( a0, a1, a2 )

                print


    

