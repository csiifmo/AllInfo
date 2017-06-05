# -*- coding: latin-1 -*-
#######################################################################
#
## \file
#  \section sdhlibrary_python_sdhbase_py_general General file information
#
#    \author   Dirk Osswald
#    \date     2007-06-13
#
#  \brief  
#    Implementation of base classes to access SDH.
#
#  \section sdhlibrary_python_sdhbase_py_copyright Copyright
#
#  Copyright (c) 2007 SCHUNK GmbH & Co. KG
#
#  <HR>
#  \internal
#
#    \subsection sdhlibrary_python_sdhbase_py_details SVN related, detailed file specific information:
#      $LastChangedBy: Osswald2 $
#      $LastChangedDate: 2011-02-08 14:53:00 +0100 (Tue, 08 Feb 2011) $
#      \par SVN file revision:
#        $Id: sdhbase.py 6432 2011-02-08 13:53:00Z Osswald2 $
#
#  \subsection sdhlibrary_python_sdhbase_py_changelog Changelog of this file:
#      \include sdhbase.py.log
#
#######################################################################

# python standard modules:
import array, re

# submodules from this package:
# pylint: disable-msg=W0401,W0614
from auxiliary import *

# additional utility modules from this package:
# pylint: disable-msg=F0401
from . import dbg

#######################################################################
## \anchor sdhlibrary_python_sdhbase_py_python_vars
#  \name   Python specific variables
#  
#  Some definitions that describe the module for python.
#
#  @{

# pylint: disable-msg=W0622
__doc__       = "Base classes for sdh package"
__author__    = "Dirk Osswald: dirk.osswald@de.schunk.com"
__url__       = "http://www.schunk.com"
__version__   = "$Id: sdhbase.py 6432 2011-02-08 13:53:00Z Osswald2 $"
__copyright__ = "Copyright (c) 2007 SCHUNK GmbH & Co. KG"

#  end of doxygen name group sdhlibrary_python_sdhbase_py_python_vars
#  @}
######################################################################

## A constant to address all fingers/axes when used as a parameter in certain functions
All = None

######################################################################
# Exception classes

## Base class for exceptions in the sd module
class cSDHError(Exception):
    '''
    Base class for exceptions in the sd module.
    '''
    pass

## SDH-exception: Communication error occured in the sd module
class cSDHErrorCommunication(cSDHError):
    '''
    Communication error occured in the sd module.
    '''
    pass

## SDH-exception: Invalid parameter(s) were given
class cSDHErrorInvalidParameter(cSDHError):
    '''
    Invalid parameter(s) were given.
    '''
    pass

## SDH-exception: A (communication) timeout occured.
class cSDHErrorTimeout(cSDHError):
    '''
    A (communication) timeout occured.
    '''
    pass

## SDH-exception: The given target angles would lead to an internal collision.
class cSDHErrorInternalCollision(cSDHError):
    '''
    The given target angles would lead to an internal collision.
    '''
    pass

#
######################################################################


## \brief The base class to control the SCHUNK Dexterous Hand.
#
#  End-Users should \b NOT use this class directly, as it only provides
#  some common settings and no function interface.
#  End users should use the class cSDH instead, as it provides the
#  end-user functions to control the SDH.
#
#  <hr>
class cSDHBase:
    '''
    The base class to control the SCHUNK Dexterous Hand. See html/pdf documentation for details.
    '''
    #-----------------------------------------------------------------
    ## Constructor of cSDHBase class, initilize internal variables and settings
    #
    #  \param self    - reference to the object itself
    #  \param options - a dictionary of additional settings, like the
    #                   options.__dict__ returned from cSDHOptionParser.parse_args()
    #  - \c "debug_level" : if set, then it is used as debug level of
    #                       the created object, else a default of 0 is
    #                       used.  If the \a debug_level of an object
    #                       is > 0 then it will output debug messages.
    #  - (Subclasses of cSDHBase like cSDH or cSDHSerial use additional settings, see there.)
    #  
    def __init__( self, options=None ):
        '''
        Constructor of cSDHBase class, initilize internal variables and settings
        '''

        #---------------------
        # Extract settings from options

        # init self.options dictionary with defaults:
        self.options = dict( debug_level=0, debug_output=sys.stderr )

        # update self.options form the given options, if any
        if ( options ):   self.options.update( options )

        ## tDBG object to disable/enable debug messages on demand
        self.dbg = dbg.tDBG( flag=self.options[ "debug_level" ] > 0, color='magenta', fd=self.options[ "debug_output" ] )

        self.dbg << "Constructing %s object with options:\n" % (self.__class__.__name__) # pylint: disable-msg=W0104
        for (k,v) in self.options.items():
            self.dbg << "  %20s : %s\n" % (k,repr(v)) # pylint: disable-msg=W0104
        #---------------------
        
     

        ## A dictionary to store the enum values of the error codes of the SDH firmware
        #  \internal
        #   In the SDH firmware these enums are of type DSA_STAT
        self.eErrorCode = dict( E_SUCCESS = 0,
                                E_NOT_AVAILABLE = 1,
                                E_NOT_INITIALIZED = 2,
                                E_ALREADY_RUNNING = 3,
                                E_FEATURE_NOT_SUPPORTED = 4,
                                E_INCONSISTENT_DATA = 5,
                                E_TIMEOUT = 6,
                                E_READ_ERROR = 7,
                                E_WRITE_ERROR = 8,
                                E_INSUFFICIENT_RESOURCES = 9,
                                E_CHECKSUM_ERROR = 10,
                                E_NOT_ENOUGH_PARAMS = 11 ,
                                E_NO_PARAMS_EXPECTED = 12,
                                E_CMD_UNKNOWN = 13,
                                E_CMD_FORMAT_ERROR = 14,
                                E_ACCESS_DENIED = 15,
                                E_ALREADY_OPEN = 16,
                                E_CMD_FAILED = 17,
                                E_CMD_ABORTED = 18,
                                E_INVALID_HANDLE = 19,
                                E_DEVICE_NOT_FOUND = 20,
                                E_DEVICE_NOT_OPENED = 21,
                                E_IO_ERROR = 22,
                                E_INVALID_PARAMETER = 23,
                                E_RANGE_ERROR = 24,
                                E_NO_DATAPIPE = 25,
                                E_INDEX_OUT_OF_BOUNDS = 26,
                                E_HOMING_ERROR = 27,
                                E_AXIS_DISABLED = 28,
                                E_OVER_TEMPERATURE = 29,
                                E_MAX_COMMANDS_EXCEEDED = 30,
                                E_INVALID_PASSWORD = 31,
                                E_MAX_COMMANDLINE_EXCEEDED = 32,
                                E_CRC_ERROR = 33,
                                E_NO_COMMAND = 34,

                                E_INTERNAL = 35,
                                E_UNKNOWN_ERROR = 36,
                                )

        ## A dictinary to map error codes to human readable error messages
        self.firmware_error_codes = {
            self.eErrorCode[ "E_SUCCESS" ] :  "E_SUCCESS: No error",
            self.eErrorCode[ "E_NOT_AVAILABLE" ] :  "E_NOT_AVAILABLE: Service or data is not available",
            self.eErrorCode[ "E_NOT_INITIALIZED" ] :  "E_NOT_INITIALIZED: The device is not initialized",
            self.eErrorCode[ "E_ALREADY_RUNNING" ] :  "E_ALREADY_RUNNING: Data acquisition: the acquisition loop is already running",
            self.eErrorCode[ "E_FEATURE_NOT_SUPPORTED" ] :  "E_FEATURE_NOT_SUPPORTED: The asked feature is not supported",
            self.eErrorCode[ "E_INCONSISTENT_DATA" ] :  "E_INCONSISTENT_DATA: One or more dependent parameters mismatch",
            self.eErrorCode[ "E_TIMEOUT" ] :  "E_TIMEOUT: Timeout error",
            self.eErrorCode[ "E_READ_ERROR" ] :  "E_READ_ERROR: Error while reading from a device",
            self.eErrorCode[ "E_WRITE_ERROR" ] :  "E_WRITE_ERROR: Error while writing to a device",
            self.eErrorCode[ "E_INSUFFICIENT_RESOURCES" ] :  "E_INSUFFICIENT_RESOURCES: No memory available",
            self.eErrorCode[ "E_CHECKSUM_ERROR" ] :  "E_CHECKSUM_ERROR: Checksum error",
            self.eErrorCode[ "E_NOT_ENOUGH_PARAMS" ] :  "E_NOT_ENOUGH_PARAMS: Not enough parameters",
            self.eErrorCode[ "E_NO_PARAMS_EXPECTED" ] :  "E_NO_PARAMS_EXPECTED: No parameters expected",
            self.eErrorCode[ "E_CMD_UNKNOWN" ] :  "E_CMD_UNKNOWN: Unknown command",
            self.eErrorCode[ "E_CMD_FORMAT_ERROR" ] :  "E_CMD_FORMAT_ERROR: Command format error",
            self.eErrorCode[ "E_ACCESS_DENIED" ] :  "E_ACCESS_DENIED: Access denied",
            self.eErrorCode[ "E_ALREADY_OPEN" ] :  "E_ALREADY_OPEN: Interface already open",
            self.eErrorCode[ "E_CMD_FAILED" ] :  "E_CMD_FAILED: Command failed",
            self.eErrorCode[ "E_CMD_ABORTED" ] :  "E_CMD_ABORTED: Command aborted",
            self.eErrorCode[ "E_INVALID_HANDLE" ] :  "E_INVALID_HANDLE: Invalid handle", 
            self.eErrorCode[ "E_DEVICE_NOT_FOUND" ] :  "E_DEVICE_NOT_FOUND: Device not found",  
            self.eErrorCode[ "E_DEVICE_NOT_OPENED" ] :  "E_DEVICE_NOT_OPENED: Device not open",   
            self.eErrorCode[ "E_IO_ERROR" ] :  "E_IO_ERROR: General I/O-Error",          
            self.eErrorCode[ "E_INVALID_PARAMETER" ] :  "E_INVALID_PARAMETER: Invalid parameter",  
            self.eErrorCode[ "E_RANGE_ERROR" ] :  "E_RANGE_ERROR: Range error",
            self.eErrorCode[ "E_NO_DATAPIPE" ] :  "E_NO_DATAPIPE: No datapipe was found to open the specified device path",
            self.eErrorCode[ "E_INDEX_OUT_OF_BOUNDS" ] :  "E_INDEX_OUT_OF_BOUNDS: The passed index is out of bounds",
            self.eErrorCode[ "E_HOMING_ERROR" ] :  "E_HOMING_ERROR: Error while homing",
            self.eErrorCode[ "E_AXIS_DISABLED" ] :  "E_AXIS_DISABLED: The selected axis is disabled",
            self.eErrorCode[ "E_OVER_TEMPERATURE" ] :  "E_OVER_TEMPERATURE: Over-temperature",
            self.eErrorCode[ "E_MAX_COMMANDS_EXCEEDED" ] :  "E_MAX_COMMANDS_EXCEEDED: cannot add more than CI_MAX_COMMANDS to interpreter / POSCON_MAX_OSCILLOSCOPE parameters to oscilloscope",
            self.eErrorCode[ "E_INVALID_PASSWORD" ] :  "E_INVALID_PASSWORD: invalid password given for change user command",
            self.eErrorCode[ "E_MAX_COMMANDLINE_EXCEEDED" ] :  "E_COMMANDLINE_EXCEEDED: the command line given is too long",
            self.eErrorCode[ "E_CRC_ERROR" ] :  "E_CRC_ERROR: Cyclic Redundancy Code error",
            self.eErrorCode[ "E_NO_COMMAND" ] :  "E_NO_COMMAND: No command available",
            self.eErrorCode[ "E_INTERNAL" ] :       "E_INTERNAL: internal error",
            self.eErrorCode[ "E_UNKNOWN_ERROR" ] :  "E_UNKNOWN_ERROR: unknown error",
            }

        ## \brief A lightweight object to store the enum values of the known grasps
        #  \internal
        #    In the SDH firmware these enums are of type TGRIP
        self.eGraspId = dict( GRIP_INVALID = -1,
                              GRIP_CENTRICAL = 0,
                              GRIP_PARALLEL = 1,
                              GRIP_CYLINDRICAL = 2,
                              GRIP_SPHERICAL = 3,
                              NUMBER_OF_GRIPS = 4 )
                              
        ## The number of valid grips
        self.NUMBER_OF_GRIPS = len( self.eGraspId ) -1  # (-1 for the GRIP_INVALID)

        ## A dictionary to store the enum values of the controller types
        self.eControllerType = dict( eCT_POSE = 0,
                                     eCT_VELOCITY = 1,
                                     eCT_VELOCITY_ACCELERATION = 2 )
                                     
                                     # TODO: not implemented yet:
                                     #eCT_POSITION = 3 )

        ## A dictionary to store the enum values of the velocity profile types of the SDH firmware
        self.eVelocityProfile = dict( eVP_SIN_SQUARE = 0,
                                      eVP_RAMP = 1 )

        ## A dictionary to store the enum values of the axis states of the SDH firmware
        self.eAxisState = dict( eAS_IDLE = 0,                # axis is idle
                                eAS_POSITIONING = 1,         # the goal position has not been reached yet
                                eAS_SPEED_MODE = 2,          # axis is in speed mode and is moving
                                eAS_NOT_INITIALIZED = 3,     # axis is not initialized or doesn't exist
                                eAS_CW_BLOCKED = 4,          # axis is blocked in counterwise direction
                                eAS_CCW_BLOCKED = 5,         # axis is blocked is blocked in against counterwise direction
                                eAS_DISABLED = 6,            # axis is disabled
                                eAS_LIMITS_REACHED = 7 )     # position limits reached and axis stopped
                                
        ## The number of axes
        self.NUMBER_OF_AXES = 7

        ## The number of fingers
        self.NUMBER_OF_FINGERS = 3

        ## The number of temperature sensors
        self.NUMBER_OF_TEMPERATURE_SENSORS = 9

        ## A list with all axis indices [0,1,...,NUMBER_OF_AXES-1]
        self.all_axes = range( 0, self.NUMBER_OF_AXES )

        ## A list with all finger indices [0,1,...,NUMBER_OF_FINGERS-1]
        self.all_fingers = range( 0, self.NUMBER_OF_FINGERS )

        ## the last known state of the SDH firmware
        self.firmware_state = self.eErrorCode[ "E_SUCCESS" ]

        ## number of remaining reply lines of a previous (non sequential) command
        self.nb_lines_to_ignore = 0

        ## regular expression to extract the duration of a command from its reply
        self.re_get_T = re.compile(r'.*=([0-9.]+)')

        ## \brief epsilon value (max absolute deviation of reported values from actual hardware values)
        ## (needed since firmware limits number of digits reported)
        self.eps = 0.5 # !!!

        ## array of 7 epsilon values
        self.eps_a   = array.array( "d",  [ self.eps ]*len(self.all_axes) )

        ## array of 7 0 values
        self.zeros_a = array.array( "d",  [ 0.0 ]*len(self.all_axes) )

        ## array of 7 1 values
        self.ones_a  = array.array( "d",  [ 1.0 ]*len(self.all_axes) )

        ## Minimum allowed axis angles (in internal units (degrees))
        self.min_angle_a = array.array( "d",  ( 0.0, -90.0, -90.0, -90.0, -90.0, -90.0, -90.0) )

        ## Maximum allowed axis angles (in internal units (degrees))
        self.max_angle_a = array.array( "d",  (90.0,  90.0,  90.0,  90.0,  90.0,  90.0,  90.0) )

        ## Maximum allowed axis angular velocities (in internal units (degrees/s))
        #  these are overwritten later when connected to the real hand by reading the actual limits from the SDH firmware 
        self.max_angular_velocity_a = array.array( "d",  (80.0,  100.0,  100.0,  100.0,  100.0,  100.0,  100.0) )

        ## Minimum allowed axis angular velocities (in internal units (degrees/s))
        #  these are overwritten later when connected to the real hand by reading the actual limits from the SDH firmware 
        self.min_angular_velocity_a = array.array( "d",  [ -v for v in self.max_angular_velocity_a ] )

        ## Maximum allowed axis angular accelerations (in internal units (degrees/(s*s)))
        self.max_angular_acceleration_a = array.array( "d",  (5000.0, 400.0, 1500.0, 400.0, 1500.0, 400.0, 1500.0) )

        ## Minimum allowed axis angular accelerations (in internal units (degrees/(s*s)))
        self.min_angular_acceleration_a = array.array( "d", [ 0.0 for a in self.max_angular_acceleration_a ] ) 

        ## array of 7 MIN_FLOAT values
        self.MIN_FLOATS = array.array( "d", [ MIN_FLOAT ]*len(self.all_axes) )

        ## array of 7 MAX_FLOAT values
        self.MAX_FLOATS = array.array( "d", [ MAX_FLOAT ]*len(self.all_axes) )

        ## \brief A list with all vector-like types that are accepted as parameters.
        #  
        #  Most methods of cSDHBase and derivatives accept not only
        #  single numbers, but vectors of several numbers as
        #  parameters, These types are herein refered to as \b "vector".
        #
        #  TODO: This should be made more general, e.g. to work with derived classes.
        #        What we acutally need to know if the parameter is iterable,
        #        see e.g. http://bytes.com/topic/python/answers/514838-how-test-if-object-sequence-iterable
        self.vector_types = [ list, tuple, type( self.ones_a) ]

    #-----------------------------------------------------------------
    ## Check if \a index is in [0 .. \a maxindex-1] or All. Raise a cSDHErrorInvalidParameter exception if not.
    def CheckIndex( self, index, maxindex, name="" ):
        if (index < 0  or  maxindex <= index):
            raise cSDHErrorInvalidParameter( "Invalid %s index '%s' (not in range [0..%d[)" % (name, repr(index), maxindex) )

    #-----------------------------------------------------------------
    ## Check if \a value is in [\a minvalue .. \a maxvalue]. Raise a cSDHErrorInvalidParameter exception if not.
    def CheckRange( self, value, minvalue, maxvalue, name="" ):
        if (type(value) in self.vector_types):
            for (v_i,min_i,max_i,i) in zip( value, minvalue, maxvalue, range(0,len(value)) ):
                if (not InRange(v_i,min_i,max_i)):
                    raise cSDHErrorInvalidParameter( "Invalid %s value in vector '%s' (value[%d]='%s' not in range [%d..%d])" % (name, repr(value), i, repr(v_i), min_i, max_i) )
        else:
            if not InRange(value, minvalue, maxvalue):
                raise cSDHErrorInvalidParameter( "Invalid %s value ('%s' not in range [%d..%d])" % (name, repr(value), minvalue, maxvalue) )


# end of class cSDHBase
#=====================================================================

