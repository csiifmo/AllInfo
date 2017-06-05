#!/usr/bin/env python
# -*- coding: latin-1 -*-
## \addtogroup sdh_library_python_demo_scripts_group
#  @{

#######################################################################
#
## \file
#  \section sdhlibrary_python_demo_workspace_general General file information
#
#    \author   Dirk Osswald
#    \date     2007-01-29
#
#  \brief  
#    Move fingers to show workspace of SDH. (Python demo script using the sdh.py import library.)
#
#    Start the script with \c "-h" or \c "--help" command line option
#    to see the online help.
#
#  \section sdhlibrary_python_demo_workspace_copyright Copyright
#
#  Copyright (c) 2007 SCHUNK GmbH & Co. KG
#
#  <HR>
#  \internal
#
#    \subsection sdhlibrary_python_demo_workspace_details SVN related, detailed file specific information:
#      $LastChangedBy: Osswald2 $
#      $LastChangedDate: 2010-12-03 12:46:13 +0100 (Fr, 03 Dez 2010) $
#      \par SVN file revision:
#        $Id: demo-workspace.py 6269 2010-12-03 11:46:13Z Osswald2 $
#
#  \subsection sdhlibrary_python_demo_workspace_changelog Changelog of this file:
#      \include demo-workspace.py.log
#
#######################################################################

## 
#  @}


#######################################################################
## \anchor sdhlibrary_python_demo_workspace_python_vars
#  \name   Python specific variables
#  
#  Some definitions that describe the script for python
#
#  @{
'''
Move fingers to show workspace of SDH. (Python demo script using the sdh.py import library.)
'''

__author__    = "Dirk Osswald: dirk.osswald@de.schunk.com"
__url__       = "http://www.schunk.com"
__version__   = "$Id: demo-workspace.py 6269 2010-12-03 11:46:13Z Osswald2 $"
__copyright__ = "Copyright (c) 2007 SCHUNK GmbH & Co. KG"

#  end of doxygen name group sdhlibrary_python_demo_workspace_python_vars
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
# The actual script code 

## Create a global instance "hand" of the class cSDH according to the given options:
hand = sdh.cSDH( options=options.__dict__ )
dbg << "Successfully created cSDH instance\n"  # pylint: disable-msg=W0104

# Open configured communication to the SDH device
hand.Open()
dbg << "Successfully opened communication to SDH\n" # pylint: disable-msg=W0104


# Pack the actual movement commands in a try block
try:
    
    for ata in [ (  0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0),
                 ( 90.0, -90.0, -90.0, -90.0, -90.0, -90.0, -90.0),
                 ( 90.0, -90.0, -90.0,  90.0,  60.0, -90.0, -90.0),
                 ( 90.0, -90.0, -90.0,  40.0,  10.0, -90.0, -90.0),
                 (  0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0) ]:
        # Now ata a a vector of angles in internal units (degrees).

        # But the user may have selected another unit system as
        # external units. So convert to that external units first:
        ata = map( hand.uc_angle.ToExternal, ata )
        # now ata is a vector of angles in external units (degrees).
        
        print "Moving axes to %s (in %s [%s])" % (str(ata), hand.uc_angle.name, hand.uc_angle.symbol)

        # Set ata as new target angle for axes:
        hand.SetAxisTargetAngle( sdh.All, ata )

        # And move hand there:
        t = hand.MoveHand()
    
        print "Took %.2f %s" % (t, hand.uc_time.symbol )

# Close the connection to the SDH in an except/finally clause. This
# way we can stop the hand even if an error or a user interruption
# (KeyboardInterrupt) occurs.
finally:
    hand.Close()
    dbg << "Successfully disabled controllers of SDH and closed connection\n" # pylint: disable-msg=W0104


#
######################################################################
