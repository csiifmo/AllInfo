# -*- coding: latin-1 -*-
#######################################################################
#
## \file
#  \section sdhlibrary_python_release_py_general General file information
#
#    \author   Dirk Osswald
#    \date     2007-06-13
#
#  \brief  
#    Definition and documentation of the project name and the release
#    name ("version") of the package. The doxygen comments of the
#    release name serve as the change log of the project. 
#
#  \section sdhlibrary_python_release_py_copyright Copyright
#
#  Copyright (c) 2014 SCHUNK GmbH & Co. KG
#
#  <HR>
#  \internal
#
#    \subsection sdhlibrary_python_release_py_details SVN related, detailed file specific information:
#      $LastChangedBy: Osswald2 $
#      $LastChangedDate: 2014-09-30 09:44:33 +0200 (Tue, 30 Sep 2014) $
#      \par SVN file revision:
#        $Id: release.py 12281 2014-09-30 07:44:33Z Osswald2 $
#
#  \subsection sdhlibrary_python_release_py_changelog Changelog of this file:
#      \include release.py.log
#
#######################################################################

#######################################################################
## \anchor sdhlibrary_python_release_py_python_vars
#  \name   Python specific variables
#  
#  Some definitions that describe the module for python.
#
#  @{

__doc__       = """Definition and documentation of the project name and the release name ("version") for sdh package"""
__author__    = "Dirk Osswald: dirk.osswald@de.schunk.com"
__url__       = "http://www.schunk.com"
__version__   = "$Id: release.py 12281 2014-09-30 07:44:33Z Osswald2 $"
__copyright__ = "Copyright (c) 2013 SCHUNK GmbH & Co. KG"

#  end of doxygen name group sdhlibrary_python_release_py_python_vars
#  @}
######################################################################

######################################################################
# Define some variables

## \brief Name of the software project. 
#
#  \anchor project_name_sdhlibrary_python
#  The name of the "SDH" (SCHUNK Dextrous Hand) import-library for python.
#
#    \internal
#    \remark 
#    - This name is extracted by the makefile and then used by doxygen:
#      - As name of the project within the generated documentation.
#      - As base name of the generated install directory and pdf files.
#    - The name should \b NOT contain spaces!
#
PROJECT_NAME = "SDHLibrary-python" 

##  \anchor firmware_release_recommended_sdhlibrary_python
#    The recommended release of the firmware of an SDH used by this library
#
FIRMWARE_RELEASE_RECOMMENDED = "0.0.3.3"

## \brief Release name of the whole software project (a.k.a. as the \e "version" of the project). 
#
#    \anchor project_release_sdhlibrary_python
#    The release name of the "SDHLibrary-python" project. The doxygen comment below
#    contains the changelog of the project. 
#
#    A suffix of "-dev" indicates a work in progress, i.e. a not yet finished release.
#    A suffix of "-a", "-b", ... indicates a bugfix release.
#
#    From newest to oldest the releases have the following names and features:
#
#    - \b 0.0.2.9: 2014-09-30
#      - made library compatible with pyserial 2.7, which has yet another way of reporting errors
#      - improved interface selection of demo-gui.py: now remembers last used setting; interface selector quit stops program as expected
#      - added -nocolor option to miniterm.py
#
#    - \b 0.0.2.8: 2014-02-28
#      - added windows installer exe for Windows 64bit for SDHLibrary-python
#      - now using --user-access-control=auto to create windows installers as bugfix for 
#        bug 1473: Bug: SDHLibrary-python Installer funktioniert nicht unter Windows 7 https://192.168.101.101/mechatronik/show_bug.cgi?id=1473 
#      - bugfix for bug 1517: Bug: assertion failure in util.cpp:207 in NumerifyRelease()
#
#    - \b 0.0.2.7: 2013-11-27
#      - fixed minor issues with miniterm.py
#      - bugfix for bug 1462: Bug: limit checking is buggy when using radians https://192.168.101.101/mechatronik/show_bug.cgi?id=1462
#        - fixed limit checking for angles, angular velcities and angular
#          accelerations when using SDHLibrary with "Radians" as unit system,
#          according to a bug report from Matei Ciocalie. Thanks.
#
#    - \b 0.0.2.6: 2013-06-18
#      - first version with recommended firmware 0.0.3.2 with ethernet TCP/IP support for tactile sensor data
#
#    - \b 0.0.2.5: 2013-02-04
#      - first version with recommended firmware 0.0.3.1 with ethernet TCP/IP support
#
#    - \b 0.0.2.4:
#      - bugfix corrected parameter calling order for ntcan.CIF.__init__()
#      - made searching for COM ports work again in windows with new pyserial v2.6
#      - made demo-gui.py/demo-tactile.py work in cygwin / tkinter (ignoring errors about invalid icons)
# 
#    - \b 0.0.2.3: 2012-02-18    
#      - enhanced miniterm.py to send data from file using command line parameters
#      - made tactile sensor calibration stuff work again in demo-dsa.py
#      - Enhancement <a href="https://192.168.101.101/mechatronik/show_bug.cgi?id=1088">Bug 1088: Task: Implement functions to check compatibility of SDH firmware</a>
#        - added cSDH.CheckFirmwareRelease() and cSDH.GetFirmwareReleaseRecommended() to be able to
#          check the actual versus the recommended SDH firmware release.
#          Needed for compatibility with the C++ version where it was added
#          for the new SDH driver for ROS, see <a href="http://www.ros.org/doc/api/cob_sdh/html/index.html">http://www.ros.org/doc/api/cob_sdh/html/index.html</a>
#
#    - \b 0.0.2.2:
#      - fixed <a href="https://192.168.101.101/mechatronik/show_bug.cgi?id=1013">Bug 1013: Bug: python script demo-gui.py does not show window on Linux</a>
#        - probing for serial ports on linux disturbs communication to already opened ports
#      - fixed serial.readline issue: On newer Linuxen the readline function available does no
#        longer accept the keyword parameter eol. Removed since the default "\n" was used anyway
#      - fixed readline module issue: made use of readline module optional in miniterm.py. On some Linuxen that module might not be available.
#      - fixed virtual port issue: the "virtual" port -1 could not be specified on the command line
#    
#    - \b 0.0.2.1: 
#      - added <a href="https://192.168.101.101/mechatronik/show_bug.cgi?id=996">Bug 996: Task: Version numbering of DSACON32m firmware has changed since 2011-02-15</a>
#        software version numbers for DSACON32m are reported correctly for the new firmwares
#      - fixed <a href="https://192.168.101.101/mechatronik/show_bug.cgi?id=983">Bug 983: Bug: demo-dsa.py does not work on some laptops</a>
#        The default baudrate for the RS232 port was not set correctly. So if 
#        the port was configured correctly before everything was OK, but if
#        the port used another baudrate before then no communication was possible.
#      - fixed <a href="https://192.168.101.101/mechatronik/show_bug.cgi?id=703">Bug 703: Bug: Tactile sensor frames cannot be read reliably in single frame mode</a>
#        - Some firmware versions of the DSACON32m are not able to do single frame acquisition and enter push-mode. This might fill up the RS232 input buffer and leads to problems like reading of outdated frames or frame loss.
#        - Added workaround to stop push mode immediately after it was entered unintentionally 
#
#    - \b 0.0.2.0: 2011-02-08
#      - added support for communication via TCP (requires at least SDH firmware 0.0.3.0)
#        - enhancement <a href="https://192.168.101.101/mechatronik/show_bug.cgi?id=874">Bug 874: Task: Enable TCP communication in SDHLibrary</a>
#      - added support for special "-2fo" and "-dev" firmware version <a href="https://192.168.101.101/mechatronik/show_bug.cgi?id=915">Bug 915: Bug: SDHLibrary-python does not work with 2fo version of firmware</a>
#      - renamed cSDH.OpenRS232() to cSDH.Open() since the open function can now handle 
#        CAN and TCP besides RS232. Kept OpenRS232() for compatibility reasons as well
#      - Doxygen documentation is now generated with doxygen-1.7.3 with included javascript search engine
#
#    - \b 0.0.1.21: 2010-05-11    
#      - enhanced demo-gui.py: now the motor current limits can be adjusted
#      - renamed EmergencyStop stuff to FastStop (according to new SMP nomenclature)
#      - Enhancement made acquiring of single tactile sensor frames available
#
#    - \b 0.0.1.20: 2010-04-12
#      - bugfix: <a href="https://192.168.101.101/mechatronik/show_bug.cgi?id=680"> Bug 680: cDSA fails to communicate with Release 276 of DSACON32m Firmware</a>
#    
#    - \b 0.0.1.19: 2010-03-05
#      - changed command line parameters for demo-dsa.py, demo-tactile.py, demo-gui.py regarding
#        the tactile sensor adjustment for sensitivity and threshold. See online help for details. 
#        - Now a specific sensor can be modified independently.
#        - Now the sensor parameters can be reset to the factory default.
#
#    - \b 0.0.1.18: 2010-02-02
#      - Added setting/getting of controller PID parameters from demo-gui.py (see Debug->PID adjust)      
#      - bugfix (firmware 0.0.2.10): <a href="https://192.168.101.101/mechatronik/show_bug.cgi?id=630">Bug 630: Bug: setting of pid parameters does not work</a>
#
#    - \b 0.0.1.17: 2009-11-07
#      - added online help of demonstration programs to doxygen documentation
#      - added description of DSACON32m update process to SDH2_configuration-and-update.doc
#    
#    - \b 0.0.1.16: 2009-10-05
#      - corrected checking of environment variable "OS" for the automatic disabling 
#        of the use of color in output. OS is "WINNT" on German windows XP,
#        but "Windows_NT" on US-English Windows XP... Phhh
#      - bugfix: <a href="https://192.168.101.101/mechatronik/show_bug.cgi?id=389"> Bug 389: miniterm.py --can states "Operation timed out" when called from windows python</a>
#      - bugfix: <a href="https://192.168.101.101/mechatronik/show_bug.cgi?id=452"> Bug 452: current demo-gui.py fails when connected to an old SDH v0.0.2.0</a>
#        added firmware version specific code to sdh.cSDH.GetAxisLimitAcceleration()
#      - enhancement: <a href="https://192.168.101.101/mechatronik/show_bug.cgi?id=456"> Bug 456: Add support for adjust sensitivity of tactile sensors"</a>
#        - added cDSA.SetMatrixSensitivity()
#        - added command line options to demo-dsa.py to adjust matrix sensitivity
#        - added support for new adjust threshold of tactgile sensors as well (needs DSACON32m Firmware >= R268)
#        - the sensitivity and the threshold can now be saved persistently to configuration memory of the DSACON32m
#        - added appropriate command line options to demo-dsa.py, demo-tactile.py and demo-gui.py
#      - enhancement <a href="https://192.168.101.101/mechatronik/show_bug.cgi?id=479>Bug 479: Add support for new --sdh_rs_device and --dsa_rs_device command line options in SDHLibrary python</a>  
#        - The actual device names are now stored in auxiliary.cSDHOptionParser.port and auxiliary.cSDHOptionParser.dsaport after command line option parsing
#        - Changed the routines to check for available ports as well
#        - On native windows available ports are listed as COMx (while command line option -p 0 still means COM1, even on native windows)
#        - On cygwin available ports are listed as /dev/ttySx
#        - On linux available ports are listed as /dev/ttySx and /dev/ttyUSBx
#      - bugfix: <a href="https://192.168.101.101/mechatronik/show_bug.cgi?id=481">Bug 481: demo-gui handling of guidat files is unintuitive</a>
#        - Now the guidat extension is automatically added if not explicitly given on save
#        - the user can select "all (*.*)" on load
#      - modified Makefile-doc, Makefile, Doxyfile to be able to use target specific variables to exclude/include files from documentation depending on whether internal or external docu is generated
#
#    - \b 0.0.1.15: 2009-06-17
#      - bugfix: <a href="https://192.168.101.101/mechatronik/show_bug.cgi?id=410">Bug 410: demo-gui.py --can fails</a>
#      - bugfix: demo-gui.py "NUMBER_OF_GRIPS" is not a valid grip
#      - bugfix: demo-gui.py did not work when hand was not in eCT_POSE controller type
#      - internal: bugfix: made py.test work again
#      - internal: enhancement: got rid of cygwin symbolic links which confused eclipse and tortoise
#      - internal: moved testing stuff to test/subdir
#      - adjusted Library for new behaviour of firmware 0.0.2.7 in eCT_VELOCITY_ACCELERATION controller type:
#        - acceleration must no longer be given with correct sign. The sign of the acceleration
#          is now determined automatically from the signs and magnitudes of the current reference velocity and the target velocity
#        - Adjusted WaitAxis() since the state is now reported correctly by the firmware, even if in a speed based controller mode
#        - adjusted doxygen documentation and demo-velocity-acceleration.cpp
#        - current controller_type is now cached in cSDH object
#        - Now using the same acceleration limits as the firmware
#      - corrected doxygen description of GetTemperature()
#      - bugfix: <a href="https://192.168.101.101/mechatronik/show_bug.cgi?id=433"> Bug 433: Invalid negative velocities remain set when switching from speed based controllers back to pose controller</a>
#        Adjusted documentation for SetController() accordingly
#      - internal enhancement: added --parameter option to sdhrecord.py to specify which parameters to record
#      - internal enhancement: made jtagserial.py use windows paths when called from a native windows interpreter. But miniterm.py -j still does not work.
#      - bugfix <a href="https://192.168.101.101/mechatronik/show_bug.cgi?id=411"> Bug 411: Calling "perform grip" from demo-gui.py produces tracebacks when connected via CAN</a>
#        - problem was actually in canserial where the timeouts where not handled properly
#        - fixed that and enhanced documentation of tCANSerial
#      - enhancement: <a href="https://192.168.101.101/mechatronik/show_bug.cgi?id=439"> Bug 439: enhance demo-contact-grasping</a>
#        - now using the new velocity with acceleration ramp controller for this demo which makes it run much smoother
#        - grasping with 2 fingers only, middle finger can be used as safety switch to end the demo
#      - bugfix: error replies from the firmware were ignored or reported as cSDHErrorCommunication, which triggered a resend
#        - this is not adequate e.g. for range errors, so now for such errors a cSDHErrorInvalidArgument is raised which
#          is not handled on library level (but can and should be handled on application level)
#      - internal: added test_v_limit to check bug 440
#      - enhancement: <a href="https://192.168.101.101/mechatronik/show_bug.cgi?id=445">Bug 445: demo-gui.py generates sdh.iv whereever its called from </a>
#        - added parameter --ivfile to demo-gui.py to keep demo-gui.py from generating the (very limited usefull) sdh.iv file automatically
#      - enhancement: <a href="https://192.168.101.101/mechatronik/show_bug.cgi?id=442">Bug 442: acceleration limits cannot be queried from the firmware</a>
#        - added new commands to read acceleration limits from firmware 
#      - internal: added test_con to check con() and bug 433, added test_alim, added test_GripHand
#      - internal: added --interactive to pytest_options to be able to do py.test tests step by step
#      - enhancement: updated / corrected doxygen comments
#        - updated known bugs
#        - guarded text "SDH" with "%SDH" in doxygen comments to prevent doxygen from auto-linking to SDH namespaceup
#
#    - \b 0.0.1.14: 2009-05-18
#      - enhancement: <a href="https://192.168.101.101/mechatronik/show_bug.cgi?id=263">Enhancement 263: Provide access to speed controller of SDH joints</a>
#        - provide access to the 2 additional controller types eCT_VELOCITY and eCT_VELOCITY_ACCELERATION which are provided by the firmware 0.0.2.6
#        - added new command cSDH.GetAxisReferenceVelocity() to access the internal reference velocity of the eCT_VELOCITY_ACCELERATION controller type 
#        - added new demonstration script demo-velocity-acceleration.py
#        - the allowed lower limits for velocity and acceleration now have to be adjusted when the controller type changes.
#      - enhancement: a cSDH object now has a release_firmware string member after connection to an SDH. This can be used together with new auxiliary.CompareReleases() member function for version specific code.   
#      - bugfix: <a href="https://192.168.101.101/mechatronik/show_bug.cgi?id=404"> Bug 404: reactivate grip hand stuff in demo-gui.py</a> since selgrip and grip work again in firmware 0.0.2.6
#
#    - \b 0.0.1.13: 2009-05-05
#      - bugfix: <a href="https://192.168.101.101/mechatronik/show_bug.cgi?id=372"> Bug 372: Disabled colored debug output on windows consoles</a> for better readability of debug messages on native windows
#      - bugfix: <a href="https://192.168.101.101/mechatronik/show_bug.cgi?id=377"> Bug 377: demo-dsa.py -c / -s / -m do not work properly</a>
#      - replaced "== None" / "!= None" with "is None" / "is not None" according to PEP 8 see http://www.python.org/dev/peps/pep-0008/
#      - prefixed non public helper functions in cDSA with '_' to mark them as internal
#      - many minor code changes according to pylint recommendations and conventions
#      - now using doxypy filter in order to be able to use native python docstrings for documentation, see http://code.foosel.org/doxypy
#      - added Doxyfile to distribution 
#      - enhancement: the "-v" command line option now tries to read and print the version info of the tactile sensors as well.
#      - the generated documentation has been improved by better grouping, cross linking and generally more documenting.
#      - changed internal package imports to use relative import command according to PEP 328: http://docs.python.org/whatsnew/2.5.html#pep-328-absolute-and-relative-imports
#      - bugfix: <a href="https://192.168.101.101/mechatronik/show_bug.cgi?id=380"> Bug 380: Graphical display of tactile sensors does not work in demo-gui.py</a>
#        Now works, see also demo-tactile.py for a standalone tactile sensor graphical display demo
#      - bugfix: <a href="https://192.168.101.101/mechatronik/show_bug.cgi?id=304"> Bug 304: demo-dsa.py does not work at all</a>
#        Working again, will work more robust
#      - bugfix: <a href="https://192.168.101.101/mechatronik/show_bug.cgi?id=338"> Bug 338: demo-contact-grasping does not work</a>
#        GetContactForce and GetContactArea do work now. Grasping does work now, althoug still not perfect. As long as only
#        position controller is available in the SDH firmware the movements will be somewhat 'jerkily'. 
#      - bugfix: <a href="https://192.168.101.101/mechatronik/show_bug.cgi?id=387"> Bug 387: index file for sdhlibrary-python doxygen documentation installed with windows installer is wrong</a>
#      - bugfix: <a href="https://192.168.101.101/mechatronik/show_bug.cgi?id=388"> Bug 388: miniterm.py installed with windows installer does not find CAN</a>
#      - bugfix: <a href="https://192.168.101.101/mechatronik/show_bug.cgi?id=376"> Bug 376: First call to demo-dsa after powering SDH fails for python also</a>
#
#    - \b 0.0.1.12: 2009-04-17
#      - Bugfix: <a href="https://192.168.101.101/mechatronik/show_bug.cgi?id=335">Bug 335: importing of module canserial is wrong</a>
#
#    - \b 0.0.1.11:
#      - removed non working skill selection stuff from demo-gui.py
#      - added interface selection window to demo-gui.py You can now start the demo-gui and miniterm.py without -p parameter and you will be queried for the RS232 port to use
#      - added schunk icon to demo-gui.py
#      - changed sdh.auxiliary.GetAvailablePorts() now it returns a list of tuples of (portnumber, occupied) instead of just the portnumber.
#        needed for new demo-gui.py interface selection window
#      - windemo dir is no longer included in the distribution (not usefull any longer)
#      - miniterm.py now also has the possibility to ask interactively for the communication channel to use
#      - updated copying of misc packages into distribution 
#
#    - \b 0.0.1.10:
#      - bugfix: <a href="https://192.168.101.101/mechatronik/show_bug.cgi?id=322"> Bug 322: AxisTargetVelocity cannot be set higher than 100 deg/s</a>
#      - enhancement: display of ° (degree symbol) changed to use unicode strings, so that it displays correctly when used with native windows python interpreter
#      - demo-gui.py sets the velocity according to the velocity slider, but reduces the velocity axis-wise if the slider exceeds a specific axis' velocity
#      - enhancement: <a href="https://192.168.101.101/mechatronik/show_bug.cgi?id=315">Enhancement 315: Add documentation files to distribution</a>
# 
#    - \b 0.0.1.9:
#      - bugfix: <a href="https://192.168.101.101/mechatronik/show_bug.cgi?id=114">Bug 114: demo-gui erlaubt Bewegungen, obwohl Kollisionserkennung "rot" anzeigt</a>     
#      - enhancement: demo-gui.py now remembers the last directory used when saving/loading *.guidat pose files
#      - enhancement: < href="https://192.168.101.101/mechatronik/show_bug.cgi?id=269"> Bug 269: Add shortcut to uninstaller of python windows package to start menue</a>
# 
#      
#    - \b 0.0.1.8: 2008-10-14
#      - added cSDHSerial::vlim() and cSDH::GetAxisLimitVelocity() to read velocity limits
#      - corrected / enhanced setup.py: 
#        - docu is now included as pdf not doc
#        - guidat file is include in distro
#        - SCHUNK logo in windows installer
#      - corrected / enhanced postinstall_sdh.py
#        - bugfix: Bug: SDHLibrary/sdhflash generated shortcuts in py windows installers do not work if scripts are in dirs with spaces
#      - included html footer in doc into SVN 
#      - enhancement: Enable debugging to logfile in SDHLibrary-python and in all demo scripts
#      - added auxiliary.GetAvailablePorts() to scan for available RS232 ports
#      - enhanced the printing of SDHLibrary and SDH firmware version info.
#        besides release numbers the release dates, python interpreter info and
#        SoC info is printed 
#      - demo-gui.py enhancements:
#        - SDH version info can be displayed in a popup
#        - only really available ports are listed in the menus, but still changing of port at runtime is not possible
#        - disabled menus for not longer needed ref commands
#      - made jtagserial.py more robust. Added auto-restart in case of error, e.g. due to SDH power cycle
#        this way you don't have to restart the error log via jtag every time you restart the SDH
#      - added missing cSDH.IsOpen()
#      - enhancement: added long missing command line option support for python/demo/demo-simple* scripts
# 
#    - \b 0.0.1.7: 2008-08-08
#      - while chasing <a href="https://192.168.101.101/mechatronik/show_bug.cgi?id=125"> Bug 125: Small joint velocities cause movements to be stopped before the target position is reached</a>
#        - added more tests to Makefile-plot 
#        - corrected ramp.py
#      - added jtagserial to enable miniterm.py to use the jtag-uart
#      - added support for new firmware v0.0.2.0 commands
#        - soc, soc_date, ver_date
#        - GetDuration
#      - corrected / updated eErrorCode pseudo enum in cSDHBase
#      - corrected cases where parameter All was not handled correctly in axis related commands in sdhserial
#      - made py.test work again and added a few more tests
#
#    - \b 0.0.1.6: 2008-06-13
#      - minor changes to keep python DSA interface compatible to new C++ DSA interface
#
#    - \b 0.0.1.5: 2008-06-06
#      - made the reading of tactile sensor info work again (with DSACON32m Firmware 143)
#
#    - \b 0.0.1.4: 2008-05-16
#      - added support for new temperature sensors in library and demos
#
#    - \b 0.0.1.3: 2008-03-19
#      - enhanced windows installer: creates shortcuts to demo-gui and docu
#      
#    - \b 0.0.1.2: 2008-02-29
#      - release for preliminary support of SDH2
#        - CAN based communication on Windows with ESD card
#
#    - \b 0.0.1.1: 2007-12-27
#      - release for RoboCluster, Denmark
#        - fixes to make library work with SDH-003
#
#    - \b 0.0.1.0: 2007-08-30
#      - restructured sdh package completely
#        - The 5600 lines of the monolithic sdh.py were broken into more manageable units
#        - made it a real python package with __init__.py and stuff
#        - package contents were moved from ./sdh.py to ./sdh/*
#        - demo scripts were moved to ./demo/
#        - data files were moved to ./data/
#      - Made makefiles more modular:
#        - extracted generation of distribution to Makefile-dist
#        - not all sub-makefiles need to be distributed any more
#          (esp. Makefile-doc and Makefile-dist can be kept secret)
#      - added support for new firmware features (for IBMT):
#        - referencing of axes against mechanical block
#        - saving of axis positions to non volatile memory 
#      
#    - \b 0.0.0.12: 2007-06-11
#      - added support for new firmware features: getting and setting of min/max/offset angles
#
#    - \b 0.0.0.11-a: 2007-06-06
#      - Release modified according to bug report from Martin Huelse (Uni Wales)
#        - changes were needed almost exclusively in the C++ part
#        
#      - Release including bugfixes for 
#    - \b 0.0.0.11: 2007-05-24
#      - Release for care-o-bot (IPA, Stuttgart), Mai 2007
#      - Added missing MoveAxis() command
#      - Added max_angular_acceleration_a
#      - Added dsa.py: module for accessing DSA (Tactile Sensor Controller)
#        - Added command line options for dealing with DSA (Tactile Sensor Controller)
#          (adjusted options of other scripts to make them consistent)
#        - Added demo scripts for tactile sensor access demo-dsa.py, demo-tactile.py, demo-contact-grasping.py
#      - Added setup.py to create a distribution with distutils
#      - while preparing release for IPA care-o-bot:
#        - since line endings are corrected in firmware now removed the special EOL treatmnt in readline
#        - enhanced generation of distribution
#        - extended/added README files
#        - added demo-simple3 in cpp and python
#        - added missing demo-simple2.py
#        - added requested functions GetAxisActualState() and WaitAxis() in cpp and python library
#        - added eAxisState enums from firmware
#        - corrected some yet undetected errors
#        - corrected / enhanced some doxygen comments
#        - made demo-GetAxisActualAngle.py work again when -s option is not given
#        - removed use of Numeric.array in sdh.py , now using array.arrray since Numeric package is not available everywhere
#          (test_sdh.py still uses Numeric)
#        - tried to find bug:
#          - firmware not moving from 5,-5,0,0,0,0,0 to 20,0,0,0,0,0,0: 
#          - axis 1 is stuck at 1.4...
#          - bug could not be resolved (does not happen for for larger movements)
#
#    - \b 0.0.0.10:  2007-04-05
#      -Release for demo at ICRA2007 (Rome), April 2007
#      - Added support for the new commands of the firmware:
#        - "A" command to get/set acceleration: Get/SetAxisTargetAcceleration()
#        - "VP" command to get/set velocity profile: Get/SetVelocityProfile() and eVelocityProfile enums
#        - "VEL" command to get actual velocity: GetAxisActualVelocity
#        - new unit converter for angular accelerations
#      - Added internal collision detection from Pedro Glogowski
#        - CheckFingerCollisions() and helper functions
#        - added check_collisions parameter to MoveFinger() and MoveHand()
#        - incorporated calculating_angles.py into sdh.py
#        - added helper functions like Square(), _AnglesToRad()
#        - helper class cSphere
#        - new exception cSDHErrorInternalCollision
#        - added parameters to _GetFingerXYZ()
#      - enhanced demo-gui.py:
#        - looping over selected poses is possible
#        - correct file extension is set in load/save file dialogs
#        - SetToActual can now be made cyclic
#        - Setting of Velocity profile is included but yet disabled since still buggy in the firmware
#        
#    - \b 0.0.0.9: 2007-03-19
#      - Release for demo at NASA, march 2007
#        - enhanced Makefiles slightly (better dist generation)
#        - adjusted expected lines for "m" command (it now prints one line debug output for every axis)
#        - added -m/--move and -V/--velocity command line options to demo-GetAxisActualAngle.py
#          now this script can be used to record movements
#        - added script demo-torquemeasurement for measuring axes torques
#        - added word doc Startup.doc (forgotten from previous release 0.0.0.7 for Uni Wales)
#        - corrected syntax error in sdh.py (introduced at visit Uni Wales)
#        
#
#    - \b 0.0.0.8: 2007-03-09
#      - Release modified at visit Uni-Wales, march 2007
#        - Changes to make everything work on Ubuntu-Linux
#        - Enhanced Makefile a little bit to be more comfortable for the end user
#        
#    - \b 0.0.0.7: 2007-03-07
#      - Release for Uni-Wales, march 2007
#      
#    - \b 0.0.0.6:
#      - final release for SDH firmware 0.1
#      
#    - \b 0.0.0.5: 2007-02-12
#      - enhanced doxygen docu for functions (added hint for unit conversion, where appropriate)
#      - added/updated gnuplot scripts / makefile for visualizing the workspace
#      - For RoboCluster on 2007-02-08:
#        - added dist target to Makefile
#        - added Inbetriebnahme.doc docu
#        - added eye-candy *.bat and icon files
#      - starting with kinematics calculation
#       - manually deduced and implemented forward kinematics 
#       - finger angles -> fingertip position calculation in sdh.py
#       - display functions for cartesian workspace in new demo-calc-workspace.py
#       - new target in Makefile-plot to visualize the workspace with gnuplot
#    
#    - \b 0.0.0.4:  2007-02-06
#      - sdh.py
#        - Set/GetAxisMotorCurrent() for all modes (move, grip, hold)
#        - added unit converter for motor current
#        - added GripHand()
#      - demo-gui.py:
#        - temperature display
#        - poses are converted to internal unit when saved and converted back to external when loaded
#        - added menu to change ports/unit-systems/debug-settings interactively
#        - now using cSDH only (no more cSDH.interface cheating)
#        
#    - \b 0.0.0.3:  2007-02-05
#      - demo-gui.py:
#        - SCHUNK logo
#        - Grip/selgrip widget
#        - Save/restore Pose widget
#      - sdh.py:
#        - external:
#          - in cSDH now all fingers have NUMBER_OF_AXES_PER_FINGER=3 axes (finger 1 has a virtual axis),
#            this simplifies the use very much, like e.g. in demo-gui.py
#          - added extra arrays to cSDH that include min/max angles/velocities for the virtual axis
#          - added Set/GetAxisMotorCurrent()  - yet untested
#          - added GetAxisMin/MaxAngle and tests
#          - added GetFingerMin/MaxAngle and tests
#          - added GetGripMaxVelocity - yet untested
#        - internal:
#          - renamed cSDHErrorInvalidArgument to cSDHErrorInvalidParameter (more intuitive)
#          - changed cSDHBase.eErrorCode from lightweight object (utils.Struct) to normal dictionary to ease iteration over elements
#          - changed cSDHBase.eGraspId from lightweight object (utils.Struct) to normal dictionary to ease iteration over elements
#          - added CheckRange() CheckIndex() to check parameter and raise cSDHErrorInvalidParameter 
#          - replaced asserts by CheckRange()/ CheckIndex() so that a cSDHErrorInvalidParameter is raised in case of error,
#            this way the error messages can be much more descriptive and hintfull
#          - _ToIndexList now checks the indices and raises exception if invalid
#          - cSDHSerial now uses a "virtual" port if options["port"] < 0 (for testing offline without a SDH connected)
#          - added doxygen comment describing the axis indices and finger axis indices
#      - added demo-endurance-run.py
#      
#    - \b 0.0.0.2:  2007-01-31
#      - many many changes while extending and refactoring sdh.h
#        - now using cEnhancedSerial instead of hackish myreadline()  workaround
#        - Added customized OptionParser cSDHOptionParser to simplify
#          handling of the usual command line parameters in (demo) scripts
#        - Changed handling of passing options to cSDHBase and derived
#          classes: options can now be given as a dictionary of
#          keyword:value pairs.  This way the output from the
#          cSDHOptionParser can be used directly which simplifies and
#          unifies (demo) scripts very much.
#        - Added cUnitConverter class and predefined unit converter objects
#          for setting/getting parameters in user or application
#          specific unit sytems
#      - Enhanced doxygen documentation very much
#        - dot graph for overview 
#        - many code examples
#
#    - \b 0.0.0.1:  2007-01-19
#      - Initial "release" of the code 
#        - Doxygen documentation can be generated
#        - Some functionality of sdh.py already available
#        - all tests defined in test_sdh.py are OK (everything green)
#
PROJECT_RELEASE = "0.0.2.9"

## \brief Date of the release of the software project.
#
#    \anchor project_date_sdhlibrary_python
#    The date of the release of the project. 
#
PROJECT_DATE = "2014-09-30"
