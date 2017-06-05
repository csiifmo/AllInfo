#######################################################################
## \file
#  \section sdhlibrary_python__init__py_general General file information
#
#    \author   Dirk Osswald
#    \date     2007-06-11
#
#  \brief  
#    Initialization of the sdh package
#
#  \section sdhlibrary_python__init__py_copyright Copyright
#
#  - Copyright (c) 2007 SCHUNK GmbH & Co. KG
#
#  <HR>
#  \internal
#
#    \subsection sdhlibrary_python__init__py_details SVN related, detailed file specific information:
#      $LastChangedBy: Osswald2 $
#      $LastChangedDate: 2010-12-03 12:46:13 +0100 (Fri, 03 Dec 2010) $
#      \par SVN file revision:
#        $Id: __init__.py 6269 2010-12-03 11:46:13Z Osswald2 $
#
#  \subsection sdhlibrary_python__init__py_changelog Changelog of this file:
#      \include __init__.py.log
#
#######################################################################


from sdh import *

#######################################################################
## \anchor sdhlibrary_python__init__py_python_vars
#  \name   Python specific variables
#  
#  Some definitions that describe the module for python
#
#  @{

__doc__       = """The python package to control a SDH (SCHUNK Dexterous Hand).

                The python __doc__ strings here provide only a very
                brief documentation, see the doxygen generated
                documentation (html or pdf) for details.

                In short: the cSDH class provides the end user interface to
                access a SDH. """
__author__    = "Dirk Osswald: dirk.osswald@de.schunk.com"
__url__       = "http://www.schunk.com"
__version__   = release.PROJECT_RELEASE
__copyright__ = "Copyright (c) 2007 SCHUNK GmbH & Co. KG"

#   end of doxygen name group sdhlibrary_python__init__py_python_vars
##  @} 
#
######################################################################

#######################################################################
#
## \package sdh
#
#  \brief  
#    Implementation of the python package to control a SDH (SCHUNK Dexterous Hand).
#
#    \anchor sdhlibrary_python__init__py_package_overview
#    This is a python package. It is meant to be imported by
#    other modules and scripts. It provides constants, functions and
#    classes to communicate with a SDH (SCHUNK Dexterous Hand) device
#    connected to a PC. The sdh python import module is the interface
#    for user applications to access the SDH.
#
#    \section sdhlibrary_python__init__py_sdhpackage_overview Overview
#    \par Naming convention:
#      As a convention \b "SDH" (capital letters) is used to refer to
#      the physical device, the three fingered SCHUNK Dexterous Hand,
#      while \b "sdh" (small letters) refers to the PC-software that
#      communicates with the physical SDH device. Within the "sdh"
#      PC-software further entities can be distinguished: The pyhton
#      import library \b "sdh.py" that contains the complete sdh package
#      and the python classes \ref sdh.sdh.cSDH "sdh.cSDH" and \b sdh.dsa.cDSA with
#      the main user interfaces.
#      The sdh.sdh.cSDH class will be described in detail below.
#
#    \par Basic structure:
#      The basic structure of the components looks like this:
#
#      \dot
#        digraph sdhlibrary_python {
#          node [fontsize=9, shape=box];
#          edge [fontsize=9];
#          subgraph cluster_pc {
#            label = "PC"; labeljust="l";
#            user_app_py           [label="User application in python\l(USERAPP.py, e.g. demo-simple.py)"];
#            sdh_py                [label="sdh Python package\l(sdh.py)" URL="\ref sdh"];
#            user_app_py -> sdh_py [ label="object instantiation,\lfunction/method calls" dir="both"];
#          }
#        
#          subgraph cluster_sdh {
#            label = "SDH"; labeljust="l";
#            sdh_firmware          [label="SDH firmware"];
#            sdh_hardware          [label="SDH hardware"];
#            sdh_firmware -> sdh_hardware [label="device access" dir="both"];
#          }
#          sdh_py -> sdh_firmware [label="RS232 serial communication" dir="both"];
#        }
#      \enddot
#
#    \par Basic architecture:
#      There are several classes defined here in sdh:
#      
#      - \ref sdh.sdh.cSDH "sdh.cSDH" is the primary class used to communicate with the SDH. This class
#        provides the functional interface of the SDH. It should be
#        used by end users, as its interface is considered more stable
#        than that of other (low-level) classes.
#      - sdh.dsa.cDSA is the primary class to communicate with the tactile
#        sensor controller DSACON32m within the SDH
#      - Other classes, like \ref sdh.sdhbase.cSDHBase "sdh.cSDHBase" and \ref sdh.sdhserial.cSDHSerial "sdh.cSDHSerial", are used by \ref sdh.sdh.cSDH "sdh.cSDH"
#        and provide more low level services and should \b NOT be used directly, as
#        their interfaces are subject to change in future releases. 
#      - \ref sdh.sdhbase.cSDHError "sdh.cSDHError" and derivatives: these are used when an exception is raised
#
#    \par Example use:
#      An exemplary use of the sdh package in a python
#      script might look like this:
#      \code
#        ...
#        # Import the sdh.py python import module:
#        import sdh
#
#        # Create an instance "hand" of the class cSDH:
#        hand = sdh.cSDH()
#
#        # Open communication to the SDH device via default serial port 0 == "COM1"
#        hand.Open()
#
#        # Perform some action:
#        #   get the current actual axis angles of finger 0
#        faa = hand.GetFingerActualAngle( 0 )
#
#        #   modify these by decreasing the proximal and the distal axis angles:
#        fta = list(faa)
#        fta[1] -= 10
#        fta[2] -= 10
#
#        #   set modified angles as new target angles:
#        hand.SetFingerTargetAngle( 0, fta )
#
#        #   now make the Finger move there:
#        hand.MoveFinger( 0 )
#  
#        # Finally close connection to SDH again, this switches the axis controllers off:
#        hand.Close()
#      \endcode
#
#      Real example code is available in the demo-*.py \ref sdh_library_python_demo_scripts_group "demonstration scripts". 
#
#  \section sdhlibrary_python__init__py_dependencies Dependencies
#    The sdh package makes use of many standard python packages like:
#    - sys, time, re, math, array, OptionParser
#    - Tkinter for demo-gui.py or demo-tactile.py
#
#    Additionally some 3rd party non-standard python packages are used.
#    These are listed \ref sdhlibrary_python_dox_additional_modules "here".
#      
#  \section sdhlibrary_python__init__py_copyright Copyright
#
#  - Copyright (c) 2007 SCHUNK GmbH & Co. KG
#
#######################################################################

#######################################################################
## \defgroup sdh_library_python_demo_scripts_group Demonstration scripts
#  @{
#  Some demonstration scripts are provided which show the usage of the
#  sdh python package:
#  @}
#######################################################################

#######################################################################
## \defgroup sdh_library_python_onlinehelp_group Online help of demonstration scripts
#  @{
#  The provided \ref sdh_library_python_demo_scripts_group "demonstration scripts" 
#  have an online help which is shown below:
#  @}
#######################################################################

#######################################################################
## \defgroup sdh_library_python_primary_user_interface_classes_group Primary user interface classes
#  @{
#  The primary user interface classes:
#  @}
#######################################################################
