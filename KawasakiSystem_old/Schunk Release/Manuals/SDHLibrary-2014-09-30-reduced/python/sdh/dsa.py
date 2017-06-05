#!/usr/bin/env python
# -*- coding: latin-1 -*-
# disable "line too long":
# pylint: disable-msg=C0301
#######################################################################
## \file
#  \section sdhlibrary_python_dsa_py_general General file information
#
#    \author   Dirk Osswald
#    \date     2007-05-04
#
#  \brief  
#    Implementation of the python import module #dsa, the interface to
#    the DSA tactile sensor controller of an SDH.
#
#  \section sdhlibrary_python_dsa_py_copyright Copyright
#
#  - Copyright (c) 2007 SCHUNK GmbH & Co. KG
#
#  <HR>
#  \internal
#
#    \subsection sdhlibrary_python_dsa_py_details SVN related, detailed file specific information:
#      $LastChangedBy: Osswald2 $
#      $LastChangedDate: 2013-06-18 18:28:14 +0200 (Di, 18 Jun 2013) $
#      \par SVN file revision:
#        $Id: dsa.py 10351 2013-06-18 16:28:14Z Osswald2 $
#
#  \subsection sdhlibrary_python_dsa_py_changelog Changelog of this file:
#      \include dsa.py.log
#
#######################################################################

#######################################################################
# 
## \package dsa
#
#  \brief  
#    Python module to control the tactile sensors of the SDH (SCHUNK Dexterous Hand).
#
#    \anchor sdhlibrary_python_dsa_py_package_overview This is a
#    python import module. It is meant to be imported by other modules
#    and scripts. It provides constants, functions and classes to
#    communicate with the \b DSACON32m, the tactile sensor controller of a SDH
#    (SCHUNK Dexterous Hand) device connected to a PC.
#    The main user interface is provided via the class sdh.dsa.cDSA 
#
#  \section sdhlibrary_python_dsa_py_dependencies Dependencies
#    The following standard python modules are used:
#    - struct, array, threading, time
#
#    The following non-standard python modules are used
#    - util, utils, dbg : common utilities, provided by SCHUNK
#    - serial    : the pySerial module from <a href="http://pyserial.sourceforge.net/">http://pyserial.sourceforge.net/</a>
#    - py.test   : unit testing framework from <a href="http://codespeak.net/py/current/doc/index.html">http://codespeak.net/py/current/doc/index.html</a>.
#
#
#  \section sdhlibrary_python_dsa_py_copyright Copyright
#
#  - Copyright (c) 2007 SCHUNK GmbH & Co. KG
#
#######################################################################


import sys, struct, array, threading, time

# pySerial module from http://pyserial.sourceforge.net/
import serial

# import modules from the package:
from . import sdh
from . import util
from . import utils
from . import auxiliary
from . import tcpserial
import socket

# special value to indicate "all fingers" or "all parts"
All = None
    
class cDSAError(sdh.cSDHError):
    '''
    DSA (tactile sensor of the SDH) related error occurred.
    '''
    def __init__(self, msg, error_code=-1):
        '''Constructor for cDSAError exceptions. 
        The parameteter error_code is stored as a member. 
        A positive value indicates an error code received from 
        the remote DSACON32m controller, see cDSA.error_codes.
        A negative value indicates (library) internal errors.
        '''
        sdh.cSDHError.__init__( self, msg )
        self.error_code = error_code
    

    
#-----------------------------------------------------------------
def LB( i ):
    '''
    return low byte of integer value i
    '''
    return i & 0xff


#-----------------------------------------------------------------
def HB( i ):
    '''
    return high byte of integer value i
    '''
    return (i>>8) & 0xff
#-----------------------------------------------------------------

def Boolify( v ):
    '''
    return True if v != 0, else False
    '''
    if (v!=0):
        return True
    else:
        return False
#-----------------------------------------------------------------

## The CRC table used by the DSACON32m controller
gCRCtbl = [ 0x0000, 0x1021, 0x2042, 0x3063, 0x4084, 0x50a5, 0x60c6, 0x70e7,
                  0x8108, 0x9129, 0xa14a, 0xb16b, 0xc18c, 0xd1ad, 0xe1ce, 0xf1ef,
                  0x1231, 0x0210, 0x3273, 0x2252, 0x52b5, 0x4294, 0x72f7, 0x62d6,
                  0x9339, 0x8318, 0xb37b, 0xa35a, 0xd3bd, 0xc39c, 0xf3ff, 0xe3de,
                  0x2462, 0x3443, 0x0420, 0x1401, 0x64e6, 0x74c7, 0x44a4, 0x5485,
                  0xa56a, 0xb54b, 0x8528, 0x9509, 0xe5ee, 0xf5cf, 0xc5ac, 0xd58d,
                  0x3653, 0x2672, 0x1611, 0x0630, 0x76d7, 0x66f6, 0x5695, 0x46b4,
                  0xb75b, 0xa77a, 0x9719, 0x8738, 0xf7df, 0xe7fe, 0xd79d, 0xc7bc,
                  0x48c4, 0x58e5, 0x6886, 0x78a7, 0x0840, 0x1861, 0x2802, 0x3823,
                  0xc9cc, 0xd9ed, 0xe98e, 0xf9af, 0x8948, 0x9969, 0xa90a, 0xb92b,
                  0x5af5, 0x4ad4, 0x7ab7, 0x6a96, 0x1a71, 0x0a50, 0x3a33, 0x2a12,
                  0xdbfd, 0xcbdc, 0xfbbf, 0xeb9e, 0x9b79, 0x8b58, 0xbb3b, 0xab1a,
                  0x6ca6, 0x7c87, 0x4ce4, 0x5cc5, 0x2c22, 0x3c03, 0x0c60, 0x1c41,
                  0xedae, 0xfd8f, 0xcdec, 0xddcd, 0xad2a, 0xbd0b, 0x8d68, 0x9d49,
                  0x7e97, 0x6eb6, 0x5ed5, 0x4ef4, 0x3e13, 0x2e32, 0x1e51, 0x0e70,
                  0xff9f, 0xefbe, 0xdfdd, 0xcffc, 0xbf1b, 0xaf3a, 0x9f59, 0x8f78,
                  0x9188, 0x81a9, 0xb1ca, 0xa1eb, 0xd10c, 0xc12d, 0xf14e, 0xe16f,
                  0x1080, 0x00a1, 0x30c2, 0x20e3, 0x5004, 0x4025, 0x7046, 0x6067,
                  0x83b9, 0x9398, 0xa3fb, 0xb3da, 0xc33d, 0xd31c, 0xe37f, 0xf35e,
                  0x02b1, 0x1290, 0x22f3, 0x32d2, 0x4235, 0x5214, 0x6277, 0x7256,
                  0xb5ea, 0xa5cb, 0x95a8, 0x8589, 0xf56e, 0xe54f, 0xd52c, 0xc50d,
                  0x34e2, 0x24c3, 0x14a0, 0x0481, 0x7466, 0x6447, 0x5424, 0x4405,
                  0xa7db, 0xb7fa, 0x8799, 0x97b8, 0xe75f, 0xf77e, 0xc71d, 0xd73c,
                  0x26d3, 0x36f2, 0x0691, 0x16b0, 0x6657, 0x7676, 0x4615, 0x5634,
                  0xd94c, 0xc96d, 0xf90e, 0xe92f, 0x99c8, 0x89e9, 0xb98a, 0xa9ab,
                  0x5844, 0x4865, 0x7806, 0x6827, 0x18c0, 0x08e1, 0x3882, 0x28a3,
                  0xcb7d, 0xdb5c, 0xeb3f, 0xfb1e, 0x8bf9, 0x9bd8, 0xabbb, 0xbb9a,
                  0x4a75, 0x5a54, 0x6a37, 0x7a16, 0x0af1, 0x1ad0, 0x2ab3, 0x3a92,
                  0xfd2e, 0xed0f, 0xdd6c, 0xcd4d, 0xbdaa, 0xad8b, 0x9de8, 0x8dc9,
                  0x7c26, 0x6c07, 0x5c64, 0x4c45, 0x3ca2, 0x2c83, 0x1ce0, 0x0cc1,
                  0xef1f, 0xff3e, 0xcf5d, 0xdf7c, 0xaf9b, 0xbfba, 0x8fd9, 0x9ff8,
                  0x6e17, 0x7e36, 0x4e55, 0x5e74, 0x2e93, 0x3eb2, 0x0ed1, 0x1ef0 ]

# DSACON32m controller uses this value as initial value of the checksum:
CRC_INIT_VALUE = 0xffff

def CRC16( crc, byte, crc_table ):
    '''Do cyclic redundancy check calculation. 
    Return the CRC for byte added to the current crc using the crc_table.  
    '''
    return ( (crc & 0xFF00) >> 8 ) ^ crc_table[ ( crc & 0x00FF ) ^ (byte & 0x00FF)] 

#-----------------------------------------------------------------
def UIntFromBytes( the_bytes ):
    '''
    Return an int from the bytes in list the_bytes (1,2,3,4,...,bytes) in little endian
    '''
    if not type( the_bytes ) in [ list, tuple ]:
        return int(the_bytes)
    the_sum = 0
    factor = 0
    for byte in the_bytes:
        the_sum += byte << (factor)
        factor += 8
    return the_sum

        
#-----------------------------------------------------------------
def FloatFromBytes( the_bytes ):
    '''
    Return a float from the list of the_bytes 
    '''
    fmt = "%c%c%c%c" % (the_bytes[0], the_bytes[1], the_bytes[2], the_bytes[3])
    value = struct.unpack( "f", fmt )[0]
    #self._dbg << "FloatFromBytes( %s ) = %f\n" % (the_bytes, value) # pylint: disable-msg=W0104
    return value
        

#-----------------------------------------------------------------
def FloatToBytes( the_float ):
    '''
    Return a list of bytes from the float \a the_float
    '''
    byte_string = struct.pack( "f", the_float )
    #self._dbg << "FloatToBytes( %f ) = %r \n" % (the_float, byte_string) # pylint: disable-msg=W0104
    return [ ord(b) for b in byte_string ]
        
#-----------------------------------------------------------------
def UInt16ToBytes( the_uint16 ):
    '''
    Return a list of bytes from the UInt16 \a the_uint16
    '''
    byte_string = struct.pack( "H", the_uint16 )
    #self._dbg << "UInt16ToBytes( %d ) = %r \n" % (the_uint16, byte_string) # pylint: disable-msg=W0104
    return [ ord(b) for b in byte_string ]
        

#-----------------------------------------------------------------
## \addtogroup sdh_library_python_primary_user_interface_classes_group
#  @{

class cDSA( object ):
    '''
    Interface class to access the DSACON32m, the tactile sensor controller of the SDH.
    
    \bug SCHUNK-internal bugzilla ID: Bug 983<br>
      With SDHLibrary-Python < 0.0.2.1 communication to the DSACON32m tactile sensor
      controller within the SDH was not established correctly in some cases. 
      The default baudrate of the RS232 port was not set correctly unless specified explicitly.
      <br><b>=> Resolved in SDHLibrary-Python 0.0.2.1</b>
    '''

    #----------------------------------------------------------------- 
    def __init__(self, debug_level=0, port=None, baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=1, xonxoff=0, rtscts=0, writeTimeout=None, dsrdtr=None, debug_output=sys.stderr ): # pylint: disable-msg=W0231
        '''Constructor of cDSA class.
        
        This constructs a cDSA object to communicate with
        the remote DSACON32m controller within the SDH.
    
        The connection is opened and established, and the sensor_info, controller_info and
        matrix_info[] is queried from the remote DSACON32m controller.
        This initialization may take up to 9 seconds, since the
        DSACON32m controller needs > 8 seconds for "booting". If the SDH is already powered
        for some time then this will be much quicker.
    
        \param self          - the instance of the class that this function operates on (the "object") 
        \param debug_level   - the level of debug messages to be printed:
                             - if > 0 (1,2,3...) then debug messages of cDSA itself are printed
                             - if > 1 (2,3,...) then debug messages of the low level communication interface object are printed too
        \param port          - the communication to use 
                               - a single number like 0 for an RS232 port (port 0 = ttyS0 = COM1, port 1 = ttyS1 = COM2, 
                               - or a device name like \"/dev/ttyUSB0\" for the corresponding RS232 port,
                               - or a IP_OR_HOSTNAME:PORT for a TCP connection to that numeric IPv4 address or hostname
        \param baudrate      - the baudrate to use. Leave this at the default 115200 bit/s. A value of 0 will use the default.
        \param bytesize      - the size in bits of one byte to transfer. Leave this at the default 8 bit / byte.
        \param parity        - the parity to use for transfer. Leave this at the default 'N' for no parity.
        \param stopbits      - the number of stop bits to use for transfer. Leave this at the default 1.
        \param timeout       - the timeout in seconds to use for transfer. 
        \param xonxoff       - the Xon/Xoff settung to use for transfer. Leave this at the default 0.
        \param rtscts        - the RTS/CTS setting to use for transfer. Leave this at the default 0.
        \param writeTimeout  - the write timeout to use for transfer. Leave this at the default None.
        \param dsrdtr        - the DSR/DTR setting to use for transfer. Leave this at the default None.
        \param debug_output  - a file like object where debug output is sent to, if enabled. Default is stderr. 
        '''
        self._dbg = sdh.dbg.tDBG( True, "blue" )
        self._dbg.SetFlag( debug_level > 0 )
        self._dbg.SetOutput( debug_output )

        if ( baudrate == 0 ):
            baudrate = 115200

        self.com = None
        self.port = port
        if ( type( port ) is int  or  "/" in port or (type( port ) is str  and  port[:3] == "COM") ):
            self._dbg << "Using RS232 on port %r for communication\n" % port
            self.com = serial.Serial( port=port, baudrate=baudrate, bytesize=bytesize, parity=parity, stopbits=stopbits, timeout=timeout, xonxoff=xonxoff, rtscts=rtscts, writeTimeout=writeTimeout, dsrdtr=dsrdtr )
            self.GetTimeout = self.GetTimeoutRS232
            self.SetTimeout = self.SetTimeoutRS232
        elif ":" in port:
            adr_port = port.split(":")
            tcp_adr = adr_port[0]
            dsa_tcp_port = int( adr_port[1] )
            self._dbg << "Using TCP on IP_OR_HOSTNAME %r, port %r for communication\n" % (tcp_adr,dsa_tcp_port)
            self.com = tcpserial.tTCPSerial( tcp_adr, dsa_tcp_port )
            self.GetTimeout = self.GetTimeoutTCP
            self.SetTimeout = self.SetTimeoutTCP
        else:
            raise cDSAError( "Invalid communication port specification %r" % port )

        self._dbg.var( "port baudrate bytesize parity stopbits timeout xonxoff rtscts writeTimeout dsrdtr")

        ## flag, true if user requested acquiring of a single frame. Needed for DSACON32m firmware-bug workaround.
        self.acquiring_single_frame = False 
        
        ## \brief A list with all vector-like types that are accepted as parameters.
        self._vector_types = [ list, tuple ]
        #  TODO: This should be made more general, e.g. to work with derived classes.
        #        What we acutally need to know if the parameter is iterable,
        #        see e.g. http://bytes.com/groups/python/514838-how-test-if-object-sequence-iterable
        
        #---------------------
        # Set framerate of remote DSACON32m to 0 first.
        #   This is necessary since the remote DSACON32m might still be sending frames
        #   from a previous command of another process.
        #   An exception may be thrown if the response for the command gets messed up
        #   with old sent frames, so ignore these.
        #   Additionally we have to ignore the "Detect terminal presence" codes sent by the
        #   DSACON32m after power up / reset. These codes ("\x1b[5n" = 0x1b 0x5b 0x35 0x6e)
        #   are sent 3 times within 0.82 seconds approximately 7 seconds after power up.
        #   The DSACON32m will accept commands only after this time (ca. 8 seconds).
        try:
            old_timeout = self.timeout
            ## The read timeout for accessing the interface in seconds. This is a property of the superclass serial.Serial. 
            self.timeout = 3 # 3000000us = 3s  => 4 retries a 3s = 12s > 8s = power up time of DSACON32m
            self.SetFramerateRetries( framerate=0, do_data_acquisition=False, retries=3, ignore_exceptions=False )
        finally:
            self.timeout = old_timeout
        #---------------------
    
        self.FlushInput( 1.0, 0.001 )
        self._framerate = 0

        ## A structure holding info about the remote DSACON32m controller     
        self.controller_info = self.QueryControllerInfo()
        
        ## A structure holding info about the remote DSACON32m sensor     
        self.sensor_info     = self.QuerySensorInfo()

        # read this from data ???
        self.sensor_info.bit_resolution = 12
        self.sensor_info.maxvalue = (1 << self.sensor_info.bit_resolution)-1


        ## A list of structures holding info about the remote tactile sensors connected to the DSACON32m
        self.matrix_info = []
        
        ## A list of texel offsets. For each sensor matrix the offset of the first texel of the matrix in the frame is stored. 
        self.texel_offset = []
        
        ## A structure containing the last tactile sensor frame read from the SDH
        self.frame = utils.Struct()
        self.frame.timestamp = 0
        nb_cells = 0
        
        for i in xrange( 0, self.sensor_info.nb_matrices ):
            self.texel_offset.append( nb_cells )
            self.matrix_info.append( self.QueryMatrixInfo( i ) )
            nb_cells += self.matrix_info[i].cells_x * self.matrix_info[i].cells_y

        self._dbg.var( "self.controller_info" )
        self._dbg.var( "self.sensor_info" )
        self._dbg.var( "self.matrix_info" )
        self._dbg.var( "nb_cells" )

        self.frame.data = array.array( 'H', [ 0 ]*nb_cells )
        self._start_pc = 0
        self._start_dsa = 0
        
        self._updater = None
        self._semaphore = None

        ## A list of all the finger indices of the SDH.        
        self.all_fingers = [ 0, 1, 2 ]
        
        ## A list of all the tactile sensor part indices of a finger of the SDH
        self.all_parts   = [ 0, 1 ]
        
        ## threshold of texel cell value for detecting contacts with GetContactArea
        self.contact_area_cell_threshold = 10

        ## threshold of texel cell value for detecting forces with GetContactForce
        self.contact_force_cell_threshold = 10

        ## additional calibration factor for forces in GetContactForce
        self.force_factor = 1.0

        ## For the voltage to pressure conversion in _VoltageToPressure()
        #  enter one pressure/voltage measurement here (from demo-dsa.py --calibration):
        self.calib_pressure = 0.000473    # N/(mm*mm)
        ## see calib_pressure
        self.calib_voltage  = 592.1       # "what the DSA reports:" ~mV
        
        ## flag, if True then the ReadFrame() function will read tactile sensor
        #  frames until a timeout occurs. This will ignore intermediate frames 
        #  as long as new ones are available. This was usefull some time in the
        #  past, or if you have a slow computer that cannot handle incoming
        #  frames fast enough. 
        #  If False then any completely read valid frame will be reported. With
        #  new computers and fast communication like via TCP this should remain
        #  at "False".
        self.read_another = False
        
    def read(self,n):
        try:
            return self.com.read(n)
        except socket.error,e:
            # TCP my throw socket.error: [Errno 11] Resource temporarily unavailable
            return ""
    
    def write(self,s):
        return self.com.write(s)

    @property
    def timeout(self):
        return self.GetTimeout()
    
    @timeout.setter
    def timeout(self, value):
        self.SetTimeout( value )
    
    def GetTimeoutRS232(self):
        return self.com.timeout
    def SetTimeoutRS232(self,v):
        self.com.timeout = v
    def GetTimeoutTCP(self):
        return self.com.GetTimeout()
    def SetTimeoutTCP(self,v):
        self._dbg << "SetTimeoutTCP(%r)\n" % v 
        self.com.SetTimeout(v)
        
    #-----------------------------------------------------------------
    def FlushInput( self, timeout_s_first, timeout_s_subsequent ):
        '''Cleanup communication line: read all available bytes
        with \a timeout_s_first timeout in s for first byte
        and \a timeout_s_subsequent timeoutin s for subsequent bytes
        
        @param timeout_s_first - timeout in s for first byte
        @param timeout_s_subsequent - timeout in s for subsequent bytes
        
        The push mode of the DSACON32m must be switched off on call since
        else the method will not return.
        '''
        #---------------------
        # clean up communication line
        bytes_read = 1        # to start the loop
        bytes_read_total = 0
        try:
            old_timeout = self.timeout
            self.timeout = timeout_s_first
            while bytes_read > 0:
                the_bytes = self.read( 1 )
                bytes_read = len( the_bytes )
                bytes_read_total += bytes_read
                self.timeout = timeout_s_subsequent
            
            self._dbg << "ignoring " << bytes_read_total << " old bytes of garbage from port " << self.port << "\n" # pylint: disable-msg=W0104
        except socket.timeout,e:
            # tcpserial.read really throws an exception on timeout
            pass
        finally:
            self.timeout = old_timeout
        #---------------------

    #-----------------------------------------------------------------
    ## A list of triples (error code (int), error code name (string), error code description (string))
    #  These are the error codes reported by the remote DSACON32m controller. These are contained
    #  as member \c response.error_code in the response structs returned by some member functions.
    #  The cDSAError exception that is thrown in case of an error contains this value as member
    #  error_code as well, if the error was reported by the remote DSACON32m controller.
    error_codes = [ 
                    (0, "E_SUCCESS", "No error occurred, operation was successful"),
                    (1, "E_NOT_AVAILABLE", "Function or data is not available"),
                    (2, "E_NO_SENSOR", "No measurement converter is connected"),
                    (3, "E_NOT_INITIALIZED", "Device was not initialized"),
                    (4, "E_ALREADY_RUNNING", "The data acquisition is already running"),
                    (5, "E_FEATURE_NOT_SUPPORTED", "The requested feature is currently not available"),
                    (6, "E_INCONSISTENT_DATA", "One or more parameters are inconsistent"),
                    (7, "E_TIMEOUT", "Timeout error"),
                    (8, "E_READ_ERROR", "Error while reading data"),
                    (9, "E_WRITE_ERROR", "Error while writing data"),
                    (10, "E_INSUFFICIENT_RESOURCES", "No more memory available"),
                    (11, "E_CHECKSUM_ERROR", "Checksum error"),
                    (12, "E_CMD_NOT_ENOUGH_PARAMS", "Not enough parameters for executing the command"),
                    (13, "E_CMD_UNKNOWN", "Unknown command"),
                    (14, "E_CMD_FORMAT_ERROR", "Command format error"),
                    (15, "E_ACCESS_DENIED", "Access denied"),
                    (16, "E_ALREADY_OPEN", "Interface is already open"),
                    (17, "E_CMD_FAILED", "Error while executing a command"),
                    (18, "E_CMD_ABORTED", "Command execution was aborted by the user"),
                    (19, "E_INVALID_HANDLE", "Invalid handle"),
                    (20, "E_DEVICE_NOT_FOUND", "Device not found"),
                    (21, "E_DEVICE_NOT_OPENED", "Device not opened"),
                    (22, "E_IO_ERROR", "Input/Output Error"),
                    (23, "E_INVALID_PARAMETER", "Wrong parameter"),
                    (24, "E_INDEX_OUT_OF_BOUNDS", "Index out of bounds"),
                    (25, "E_CMD_PENDING", "No error, but the command was not completed, yet. Another return message will follow including an error code, if the function was completed."),
                    (26, "E_OVERRUN", "Data overrun"),
                    (27, "E_RANGE_ERROR", "Range error")
                    ]

    #-----------------------------------------------------------------
    ## A dictionary of packet ID to number mappings
    eDSAPacketID = dict( eDSA_FULL_FRAME = 0x00,
                         eDSA_QUERY_CONTROLLER_CONFIGURATION = 0x01,
                         eDSA_QUERY_SENSOR_CONFIGURATION = 0x02,
                         eDSA_QUERY_MATRIX_CONFIGURATION = 0x0B,
                         eDSA_CONFIGURE_DATA_ACQUISITION = 0x03,
                         eDSA_QUERY_CONTROLLER_FEATURES = 0x10,
                         eDSA_READ_MATRIX_MASK = 0x04,
                         eDSA_SET_DYNAMIC_MASK = 0xAB,
                         eDSA_READ_DESCRIPTOR_STRING = 0x05,
                         eDSA_LOOP = 0x06,
                         eDSA_QUERY_CONTROLLER_STATE = 0x0a,
                         eDSA_SET_PROPERTIES_SAMPLE_RATE = 0x0c,
                         eDSA_SET_PROPERTIES_CONTROL_VECTOR_FOR_MATRIX = 0x0d,
                         eDSA_GET_PROPERTIES_CONTROL_VECTOR_OF_MATRIX = 0x0e,
                         eDSA_ADJUST_MATRIX_SENSITIVITY = 0x0f,
                         eDSA_GET_SENSITIVITY_ADJUSTMENT_INFO = 0x12,
                         eDSA_SET_MATRIX_THRESHOLD = 0x13,
                         eDSA_GET_MATRIX_THRESHOLD = 0x14
                        )

    #-----------------------------------------------------------------
    def CheckErrorCode(self, error_code, msg="" ):
        '''Check error_code \a error_code. Raise a cDSAError including \a msg in case of error
        '''
        if (error_code == 0): 
            return
        raise cDSAError( "Received error code %d = %s (%s) from tactile sensor controller DSACON32m for command %s" % (error_code, self.error_codes[error_code][1], self.error_codes[error_code][2], msg),
                         error_code=error_code ) 

    #-----------------------------------------------------------------
    def Close(self):
        '''Close connection to remote DSACON32m controller in the SDH.
        Tries to reset the framerate to 0 to stop the DSACON32m from sending before closing
        '''
        self.SetFramerateRetries( framerate=0, do_data_acquisition=False, retries=0, ignore_exceptions=True )
        self.com.close()


    #-----------------------------------------------------------------
    def CleanCommunicationLine(self):
        '''Clean up the communication line by reading up to 1000 bytes with 
        timeout 0, i.e. return at once ignoring anything that is available
        now.
        '''
        try:
            old_timeout = self.timeout
            self.timeout = 0
            self.read(1000)
            # pylint: disable-msg=W0104
            #self._dbg << "CCL took %fs\n" % (e-s) # pylint: disable-msg=W0104
        finally:
            self.timeout = old_timeout

        
    #-----------------------------------------------------------------
    def _WriteBytes( self, the_bytes ):
        '''Non public helper function: 
        Write the byte or bytes given as ints in the_bytes to the interface.
        '''
        if ( not type( the_bytes ) in [ tuple, list ]):
            the_bytes = [ the_bytes ]

        for b in the_bytes:
            if ( b < 0  or  b > 255 ):
                raise cDSAError( "Invalid byte value %d = 0x%x, not in [0.255]" % (b, b) )
            self.write( "%c" % b )

        self._dbg << "wrote bytes %s to port\n" % (repr(the_bytes)) # pylint: disable-msg=W0231

    #-----------------------------------------------------------------
    def _WriteCommandWithPayload( self, command, payload ):
        '''Non public helper function:
        Write a command with some payload to the remote DSACON32m controller. 
        '''
        checksum = CRC_INIT_VALUE
        if ( type(payload) not in (tuple, list) ):
            payload = [ payload ]
    
        lenp = len( payload )
        for b in [command, LB( lenp ), HB( lenp )] + payload:
            checksum = CRC16( checksum, b, gCRCtbl )
        self._WriteBytes( [0xaa, 0xaa, 0xaa, command, LB( lenp ), HB( lenp )] + payload + [ LB( checksum ), HB( checksum ) ] )

    #-----------------------------------------------------------------
    def SetFramerate( self, framerate, do_RLE=True, do_data_acquisition=True ):
        '''Set the \a framerate for querying full frames.
        
        @param self                - the instance of the class that this function operates on (the "object") 
        @param framerate           - rate of frames. 
        @param do_RLE              - flag, if true then use RLE (run length encoding) for sending frames
        @param do_data_acquisition - flag, enable or disable data acquisition. Must be true if you want to get new frames
        
        - Use \a framerate=0 and \a do_data_acquisition=false to make the remote DSACON32m in %SDH stop sending frames
        - Use \a framerate=0 and \a do_data_acquisition=true to read a single frame
        - Use \a framerate>0 and \a do_data_acquisition=true to make the remote DSACON32m in %SDH send frames at the
          highest possible rate (for now: 30 FPS (frames per second)).
     
        \bug SCHUNK-internal bugzilla ID: Bug 680<br>
        With DSACON32m firmware R276 and after and SDHLibrary-Python v0.0.1.19
        and before stopping of the sending did not work.
        <br><b>=> Resolved in SDHLibrary-Python v0.0.1.20</b>
        
        \bug SCHUNK-internal bugzilla ID: Bug 680<br>
        With DSACON32m firmware before R276 and SDHLibrary-Python v0.0.1.20
        and before acquiring of single frames did not work
        <br><b>=> Resolved in SDHLibrary-Python v0.0.1.21</b>

        \bug SCHUNK-internal bugzilla ID: Bug 703<br>
        With DSACON32m firmware R288 and before and SDHLibrary-Python v0.0.2.1 and before
        tactile sensor frames could not be read reliably in single frame mode.
        <br><b>=> Resolved in DSACON32m firmware 2.9.0.0</b>
        <br><b>=> Resolved in SDHLibrary-Python v0.0.2.1 with workaround for older DSACON32m firmwares</b>
        '''
        self._dbg << "Setting framerate to %d, do_data_acquisition=%r\n" % (framerate,do_data_acquisition) # pylint: disable-msg=W0104
        self._WriteCommand( self.eDSAPacketID[ "eDSA_CONFIGURE_DATA_ACQUISITION" ], 
                            framerate=framerate, 
                            do_data_acquisition=do_data_acquisition, 
                            do_single_shot=False, 
                            do_internal_trigger=True, 
                            do_level_trigger=False, 
                            do_rising_high=False, 
                            do_RLE=do_RLE, 
                            payload=None )
        # code above will already handle the response or raise an error for incorrect response
        
        if ( framerate==0  and  do_data_acquisition ):
            self.acquiring_single_frame = True
        else:
            self.acquiring_single_frame = False
        

    #-----------------------------------------------------------------


    def SetFramerateRetries( self, framerate, do_RLE=True, do_data_acquisition=True, retries=0, ignore_exceptions=False ):
        ''' Set the \a framerate for querying full frames.
        
        @param self                - the instance of the class that this function operates on (the "object") 
        @param framerate           - rate of frames
        @param do_RLE              - flag, if true then use RLE (run length encoding) for sending frames
        @param do_data_acquisition - flag, enable or disable data acquisition. Must be true if you want to get new frames
        @param retries             - number of times the sending will be retried in case of an error (like timeout while waiting for response)
        @param ignore_exceptions   - flag, if true then exceptions are ignored in case of error. After \a retries tries the function just returns even in case of an error

        - Use \a framerate=0 and \a do_data_acquisition=false to make the remote DSACON32m in %SDH stop sending frames
        - Use \a framerate=0 and \a do_data_acquisition=true to read a single frame
        - Use \a framerate>0 and \a do_data_acquisition=true to make the remote DSACON32m in %SDH send frames at the
          highest possible rate (for now: 30 FPS (frames per second)).
     
        \bug With DSACON32m firmware R276 and after and SDHLibrary-Python v0.0.1.19
        and before stopping of the sending did not work.
        <br><b>=> Resolved in SDHLibrary-Python v0.0.1.20</b>
        
        \bug With DSACON32m firmware before R276 and SDHLibrary-Python v0.0.1.20
        and before acquiring of single frames did not work
        <br><b>=> Resolved in SDHLibrary-C++ v0.0.1.21</b>
        '''
        while retries >= 0:
            try:
                self.SetFramerate( framerate=framerate, do_RLE=do_RLE, do_data_acquisition=do_data_acquisition )
                # in case of success we just return
                return
            except cDSAError, e:
                if ( retries <= 0  and  not ignore_exceptions ):
                    raise e # reraise in case of retries exceeded
                # catch and ignore exceptions which might result from an invalid response
                self._dbg << "ignoring Caught exception: " << str(e) << "\n" # pylint: disable-msg=W0104
            # retry: reopen the interface and try again:
            #self.com.close()
            #self.open()
            retries -= 1

    #-----------------------------------------------------------------
    # pylint: disable-msg=W0613
    def _WriteCommand( self, command, framerate=None, do_data_acquisition=True, do_single_shot=False, do_internal_trigger=True, do_level_trigger=False, do_rising_high=False, do_RLE=True, payload=None ):
        '''Non public helper function: 
        write a command to the remote DSACON32m controller.
        
        Raises a cDSAError in case of invalid responses from the remote DSACON32m controller.
        '''
        flags = 0
        if ( do_data_acquisition ):
            flags |= (1<<7)
            
        if ( do_single_shot ):
            flags |= (1<<6) 
                
        #if ( do_internal_trigger ):
        #    flags |= (1<<5)

        #if ( do_level_trigger ):
        #    flags |= (1<<4)
                        
        #if ( do_rising_high ):
        #    flags |= (1<<3)
                            
        if ( do_RLE ):
            flags |= (1<<0)
    
        if ( framerate is not None ):
            self._WriteCommandWithPayload( command, [ flags, LB( framerate ), HB( framerate ) ] )
            response = self._ReadResponse( command )
            if ( response.size != 2 ):
                raise cDSAError( "Invalid response from DSACON32m, expected 2 bytes but got %d" % response.size )
            response.error_code = UIntFromBytes( response.payload )
            self.CheckErrorCode(response.error_code, "Error response from DSACON32m for command 0x%02x" % command )
            self._dbg << "acknowledge ok\n" # pylint: disable-msg=W0104
        elif ( payload is not None):
            self._WriteCommandWithPayload( command, payload )
        else:
            # no payload => no checksum
            self._WriteBytes( [0xaa, 0xaa, 0xaa, command, 0x00, 0x00 ] )                
        return # everything ok, so return

            

    #-----------------------------------------------------------------
    def _ReadUInt8( self ):
        '''Non public helper function: 
        Read one byte from the interface and return the byte as 8 bit unsigned int
        '''
        retries = 3
        e = None
        while (retries>0):
            retries -= 1
            try:
                c = self.read( 1 )
                if c == "":
                    raise cDSAError( "Timeout while reading 1 byte from port %r " % (self.port) )
                b = ord( c )
                #self._dbg << "read UInt8 %d\n" % b  # pylint: disable-msg=W0104
                return b
            except OSError, e:
                pass
            except TypeError, e:
                # this seems to happen sometimes: TypeError: ord() expected a character, but string of length 4 found
                pass
        if (e is None):
            e = cDSAError( "Could not read 1 byte with 3 retries" )
        raise e # pylint: disable-msg=E0702
            

    #-----------------------------------------------------------------
    def _ReadUInt16( self ):
        '''Non public helper function: 
        Read two bytes from the interface and return the value as 16 bit unsigned int.
        '''
        bs = [ self._ReadUInt8(), self._ReadUInt8() ]
        v = bs[0] + (bs[1] << 8)
        #self._dbg << "read UInt16 %d\n" % v  # pylint: disable-msg=W0104
        return (v, bs)

    #-----------------------------------------------------------------
    def _ReadUInt32( self ):
        '''Non public helper function: 
        Read four bytes from the interface and return the value as 32 bit unsigned int.
        '''
        bs = [ self._ReadUInt8() for i in xrange(0, 4) ] # pylint: disable-msg=W0612
        v = bs[0] + (bs[1] << 8) + (bs[1] << 16) + (bs[1] << 24)
        #self._dbg << "read UInt32 %d\n" % v  # pylint: disable-msg=W0104
        return (v, bs)

    #-----------------------------------------------------------------
    def _ReadNextResponse( self ):
        '''Non public helper function: 
        Read and return the next response from the remote DSA
        '''
        # read  preamble 0xaa, 0xaa, 0xaa
        the_bytes = []
        response = utils.Struct()
        response.size = 0
        
        # scan for 3 preamble bytes
        nb_preamble_bytes = 0
        for i in xrange( 0, 1000): # pylint: disable-msg=W0612
            v = self._ReadUInt8()
            if ( v == 0xaa ):
                nb_preamble_bytes += 1
            else:
                nb_preamble_bytes = 0
                
            if (nb_preamble_bytes == 3):
                the_bytes.extend( [ 0xaa, 0xaa, 0xaa] )
                break
        if (nb_preamble_bytes != 3):
            raise cDSAError( "Could not find preamble 0xaa 0xaa 0xaa within 1000 bytes" )

        # read and check packet ID
        v = self._ReadUInt8() 
        the_bytes.append( v )
        response.packet_id = v
        

        # read size
        (v, bs) = self._ReadUInt16()
        the_bytes += bs
        response.size = v

        # read indicated rest
        response.payload = []
        # TODO: reading byte by byte could be slow!
        response.payload +=  [ self._ReadUInt8()  for i in xrange( 0, response.size ) ] # do not include checksum here any more  !!!new
        the_bytes += response.payload
        
        # read checksum
        (response.checksum, bs) = self._ReadUInt16() # chksum is now 2 bytes !!!new
        the_bytes += bs
        
        response.the_bytes = the_bytes
        self._dbg << "read %s\n" % repr( the_bytes ) # pylint: disable-msg=W0104

        # do CRC check
        checksum = CRC_INIT_VALUE
        for b in the_bytes[3:-2]:
            checksum = CRC16( checksum, b, gCRCtbl )
        if ( checksum != response.checksum ):
            raise cDSAError( "Checkusm Error, expected 0x%x but got 0x%x" % (checksum, response.checksum) )
        else:
            self._dbg << "Checksum OK\n" # pylint: disable-msg=W0104

        return response

    #-----------------------------------------------------------------
    def _ReadResponse( self, command_id ):
        '''Non public helper function: 
        Read any response from the remote DSACON32m, expect the \a command_id as command id
        '''
        retries_frames = 0
        while ( retries_frames < 5 ):
            retries_frames += 1
            
            response = self._ReadNextResponse()
            
            if ( response.packet_id == command_id ):
                return response
                
            # it is a common case that the answer is a normal "full-frame"
            # response from the DSACON32m, since it can send data
            # automatically in "push-mode". So just ignore such a response
            # and try to read the next response:
            if ( response.packet_id == self.eDSAPacketID[ "eDSA_FULL_FRAME" ] ):
                continue

            # else report an error
            raise cDSAError( "Unexpected response. Expected command_id 0x%02x, but got command_id 0x%02x with %d payload bytes" % (command_id, response.packet_id, response.size) )
        raise cDSAError( "Retried %d times but could not get expected response with command_id 0x%02x.", (retries_frames, command_id) )

    #-----------------------------------------------------------------
    def _ReadControllerInfo( self ):
        '''Non public helper function: 
        Read and parse a controller info response from the remote DSA
        
        Raises a cDSAError in case of invalid responses from the remote DSACON32m controller.
        '''
        response = self._ReadResponse( self.eDSAPacketID[ "eDSA_QUERY_CONTROLLER_CONFIGURATION" ] )

        response.error_code          = UIntFromBytes( response.payload[ 0:2 ] )
        self.CheckErrorCode( response.error_code, "_ReadControllerInfo" )
        response.serial_no           = UIntFromBytes( response.payload[ 2:6 ] )
        response.hw_version          = UIntFromBytes( response.payload[ 6 ] )   #??? BCD encoded !
        response.sw_version          = UIntFromBytes( response.payload[ 7:9 ] )
        response.status_flags        = UIntFromBytes( response.payload[ 9 ] )
        response.feature_flags       = UIntFromBytes( response.payload[ 10 ])
        response.senscon_type        = UIntFromBytes( response.payload[ 11 ])
        response.active_interface    = UIntFromBytes( response.payload[ 12 ])
        response.can_baudrate        = UIntFromBytes( response.payload[ 13:17 ])
        response.can_id              = UIntFromBytes( response.payload[ 17:19 ])

        ## !!! somehow the controller sends only 18 bytes although 19 are expected 
        ##if ( 19 != response.size ):
        ##    raise cDSAError( "Response with controllerinfo has unexpected size %d (expected %d)" % (response.size, 19) )
        if ( 18 != response.size ):
            raise cDSAError( "Response with controllerinfo has unexpected size %d (expected %d)" % (response.size, 18) )
        
        response.sensor_controller_operable = Boolify( response.status_flags &  (1<<7) )
        response.data_acquisition_running   = Boolify( response.status_flags &  (1<<6) )
        response.usb_available              = Boolify( response.feature_flags & (1<<6) )
        response.can_available              = Boolify( response.feature_flags & (1<<5) )
        response.rs232_available            = Boolify( response.feature_flags & (1<<4) )
        
        
        return response


    #-----------------------------------------------------------------
    def _ReadSensorInfo( self ):
        '''Non public helper function: 
        Read and parse a sensor info response from the remote DSA
        
        Raises a cDSAError in case of invalid responses from the remote DSACON32m controller.
        '''
        response = self._ReadResponse( self.eDSAPacketID[ "eDSA_QUERY_SENSOR_CONFIGURATION" ] )
        response.error_code          = UIntFromBytes( response.payload[ 0:2 ] )
        self.CheckErrorCode( response.error_code, "_ReadSensorInfo" )
        response.nb_matrices         = UIntFromBytes( response.payload[ 2:4 ] )
        response.generated_by        = UIntFromBytes( response.payload[ 4:6 ] )  
        response.hw_revision         = UIntFromBytes( response.payload[ 6 ] )
        response.serial_no           = UIntFromBytes( response.payload[ 7:11 ])  
        response.feature_flags       = UIntFromBytes( response.payload[ 11 ])  
        
        if ( 12 != response.size ):
            raise cDSAError( "Response with sensorinfo has unexpected size %d (expected %d)" % (response.size, 12) )

        response.discriptor_string_set = Boolify( response.feature_flags & (1<<0) )

        return response

    #-----------------------------------------------------------------
    def _ReadMatrixInfo( self ):
        '''Non public helper function: 
        Read and parse a matrix info response from the remote DSA
        
        Raises a cDSAError in case of invalid responses from the remote DSACON32m controller.
        '''
        response = self._ReadResponse( self.eDSAPacketID[ "eDSA_QUERY_MATRIX_CONFIGURATION" ] )
        i = 0
        # pylint: disable-msg=C0321
        response.error_code      = UIntFromBytes(   response.payload[ i:i+2 ] ); i += 2
        self.CheckErrorCode( response.error_code, "_ReadMatrixInfo" )
        response.texel_width     = FloatFromBytes( response.payload[ i:i+4 ] ); i += 4
        response.texel_height    = FloatFromBytes( response.payload[ i:i+4 ] ); i += 4
        response.cells_x         = UIntFromBytes(   response.payload[ i:i+2 ] ); i += 2 
        response.cells_y         = UIntFromBytes(   response.payload[ i:i+2 ] ); i += 2 
        response.uid             = UIntFromBytes(   response.payload[ i:i+6 ] ); i += 6
        i += 2 # 2 reserved bytes
        response.hw_revision     = UIntFromBytes(   response.payload[ i:i+1 ] ); i += 1

        response.matrix_center_x = FloatFromBytes( response.payload[ i:i+4 ] ); i += 4 
        response.matrix_center_y = FloatFromBytes( response.payload[ i:i+4 ] ); i += 4
        response.matrix_center_z = FloatFromBytes( response.payload[ i:i+4 ] ); i += 4

        response.matrix_theta_x  = FloatFromBytes( response.payload[ i:i+4 ] ); i += 4 
        response.matrix_theta_y  = FloatFromBytes( response.payload[ i:i+4 ] ); i += 4 
        response.matrix_theta_z  = FloatFromBytes( response.payload[ i:i+4 ] ); i += 4 
        response.fullscale       = UIntFromBytes(   response.payload[ i:i+4 ] ); i += 4
        response.feature_flags   = UIntFromBytes(   response.payload[ i:i+1 ] ); i += 1

        if ( i != response.size ):
            raise cDSAError( "Response with matrixinfo has unexpected size %d (expected %d)" % (response.size, i) )
        
        response.discriptor_string_set = Boolify( response.feature_flags & (1<<0) )
        return response
      
    #-----------------------------------------------------------------
    def ReadFrame( self ):
        '''
        read and parse a full frame response from remote DSA
        '''
        response = self._ReadResponse( self.eDSAPacketID[ "eDSA_FULL_FRAME" ] )

        #---------------------
        # since DSACON32m might send data in push mode there might be more frames
        # available in the input buffer of the OS. E.g. if the processor has a high load.
        # so we have to try to read all frames available and use the last one.
        #read_others_start = time.time()  # FIX ME: remove me
    
        try:
            old_timeout = self.timeout
            self.timeout = 0
        
            read_another = self.read_another
            while ( read_another ):
                try:
                    response = self._ReadResponse( self.eDSAPacketID[ "eDSA_FULL_FRAME" ] )
                    #sys.stderr.write( "Read another pending frame!\n" ) # FIX ME: remove me

                except cDSAError,e:
                    # timeout occured, so no more frames available
                    #sys.stderr.write( "Caught %r; No more frames available\n" % (e) ) # FIX ME: remove me
                    read_another = False

            #read_others_elapsed = time.time() - read_others_start  # FIX ME: remove me
            #sys.stderr.write( "Reading others took %fs\n" % (read_others_elapsed) ) # FIX ME: remove me
            #---------------------
        finally:
            self.timeout = old_timeout

        # DSACON32m firmware release up to and including 288 except 269
        # are not able to handle single frame acquisition. Instead they
        # start sending as fast as possible right away.
        #
        # So stop acquiring immediately after frame was received
        if ( self.acquiring_single_frame and self.controller_info.sw_version <= 288 and self.controller_info.sw_version != 269 ):
            self._dbg << "switching off acquiring single frames\n"
            self.SetFramerate( 0, True, False )
            self.FlushInput( 0.050, 0.001 ) # wait 50ms for first byte since hand sends with 30 fps => 33ms

        return self._ParseFrame( response )


    #-----------------------------------------------------------------
    def _ParseFrame( self, response ):
        '''
        Parse a full frame response from remote DSA
        '''
        i = 0 # index of next unparsed data byte in payload
        # pylint: disable-msg=C0321
        self.frame.timestamp = UIntFromBytes( response.payload[ i:i+4 ] ); i+=4
        self._dbg.var( "self.frame.timestamp" )

        self.frame.flags = UIntFromBytes( response.payload[ i:i+1 ] ); i+=1
        self._dbg.var( "self.frame.flags" )

        do_RLE = Boolify( self.frame.flags & (1<<0) )

        # for the first frame: record reported timestamp (time of DS) and now (time of pc)
        if self._start_pc == 0:
            self._start_pc  = int(time.time() * 1000.0 + 0.5)
            self._dbg << "Init start_pc  %d \n" % (self._start_pc ) # pylint: disable-msg=W0104
        if self._start_dsa == 0:
            self._start_dsa = self.frame.timestamp
            self._dbg << "Init start_dsa %d\n" % (self._start_dsa ) # pylint: disable-msg=W0104
        ####
        diff_pc = int(time.time() * 1000.0 + 0.5) - self._start_pc
        diff_dsa = self.frame.timestamp - self._start_dsa
        self._dbg << "_ParseFrame: elapsed ms pc,dsa = %6d,%6d  age %6d\n" % (diff_pc, diff_dsa, self.GetAgeOfFrame(self.frame)) # pylint: disable-msg=W0104
        ####

        #response.frame = array.array('H')

        j = 0   # counter for frame elements
        if do_RLE:
            self._dbg.var( "do_RLE" )
            while i+1 < response.size:
                b = UIntFromBytes( response.payload[ i:i+2 ] )
                v = b & 0x0fff
                n = b >> 12
                while n > 0:
                    #response.frame append( v )
                    self.frame.data[ j ] = v
                    n -= 1
                    j += 1
                i += 2
        
        else:
            while i+1 < response.size:
                #self._dbg.var( "response.size i j" )
                self.frame.data[ j ] = UIntFromBytes( response.payload[ i:i+2 ] )
                i += 2
                j += 1
        #self._dbg.var( "response" )
        response.frame = self.frame
        return response

    #-----------------------------------------------------------------
    def QueryControllerInfo( self ):
        '''
        Send command to respond controller info to remote DSA.
        Read and parse the response from the remote DSA.
        
        This is already done by the constructor and cached in self.controller_info
        '''
        self._WriteCommand( self.eDSAPacketID[ "eDSA_QUERY_CONTROLLER_CONFIGURATION" ] )
        return self._ReadControllerInfo()

    #-----------------------------------------------------------------
    def QuerySensorInfo( self ):
        '''
        Send command to respond sensor info to remote DSA.
        Read and parse the response from the remote DSA.
        
        This is already done by the constructor and cached in self.sensor_info
        '''
        self._WriteCommand( self.eDSAPacketID[ "eDSA_QUERY_SENSOR_CONFIGURATION" ] )
        return self._ReadSensorInfo()

    #-----------------------------------------------------------------
    def QueryMatrixInfo( self, matrix_no ):
        '''
        Send command to respond matrix info to remote DSA.
        Read and parse the response from the remote DSA.
        
        This is already done by the constructor and cached in the self.matrix_info list
        '''
        self._WriteCommand( self.eDSAPacketID[ "eDSA_QUERY_MATRIX_CONFIGURATION" ], payload=matrix_no )
        return self._ReadMatrixInfo()

    #-----------------------------------------------------------------
    def SetMatrixSensitivity( self, matrix_no, sensitivity, do_all_matrices=False, do_reset=False, do_persistent=False ):
        '''
        Send command to set matrix sensitivity to \a sensitivity as float [0.0 .. 1.0] (0.0 is minimum, 1.0 is maximum sensitivity).
        If \a do_all_matrices is True then the \a sensitivity is set for all matrices.
        If \a do_reset is True then the sensitivity is reset to the factory default.
        If \a do_persistent is True then the sensitivity is saved persistently to 
        configuration memory and will thus remain after the next power off/power on
        cycle and will become the new factory default value. If \a do_persistent is
        False (default) then the value will be reset to default on the next power
        off/power on cycle
        \warning PLEASE NOTE: the maximum write endurance of the configuration 
        memory is about 100.000 times!        
        
        Raises a cDSAError in case of invalid responses from the remote DSACON32m controller.

        \remark Setting the matrix sensitivity persistently is only possible if the DSACON32m firmware is R268 or above.
        '''
        flags = 0
        if ( do_all_matrices ):
            flags |= (1<<1)
        if ( do_reset ):
            flags |= (1<<0)
        if ( do_persistent ): 
            flags |= (1<<7)        
            
            
        self._WriteCommand( self.eDSAPacketID[ "eDSA_ADJUST_MATRIX_SENSITIVITY"], payload=[ flags, matrix_no ] + FloatToBytes( sensitivity )  )
        response = self._ReadResponse( self.eDSAPacketID[ "eDSA_ADJUST_MATRIX_SENSITIVITY" ] )
        response.error_code = UIntFromBytes( response.payload[ 0:2 ] )
        self.CheckErrorCode( response.error_code, "SetMatrixSensitivity" )
        return response
        
    #-----------------------------------------------------------------
    def GetMatrixSensitivity( self, matrix_no ):
        '''
        Send command to get matrix sensitivity. Returns sensitivities of matrix no \a matrix_no.
        
        A struct is returned containing the members
        \a error_code - see DSACON32 Command Set Reference Manual
        \a adj_flags  - see DSACON32 Command Set Reference Manual
        \a cur_sens   - the currently set sensitivity as float [0.0 .. 1.0] (0.0 is minimum, 1.0 is maximum sensitivity)
        \a fact_sens  - the factory sensitivity as float [0.0 .. 1.0] (0.0 is minimum, 1.0 is maximum sensitivity)
        
        Raises a cDSAError in case of invalid responses from the remote DSACON32m controller.
        
        \bug With DSACON32m firmware R218 and before this did not work, instead the factory default (0.5) was always reported
        <br><b>=> Resolved in DSACON32m firmware R268</b>
        '''
            
        self._WriteCommand( self.eDSAPacketID[ "eDSA_GET_SENSITIVITY_ADJUSTMENT_INFO" ], payload=matrix_no )
        response = self._ReadResponse( self.eDSAPacketID[ "eDSA_GET_SENSITIVITY_ADJUSTMENT_INFO" ] )
        response.error_code = UIntFromBytes(   response.payload[ 0:2 ] )
        self.CheckErrorCode( response.error_code, "GetMatrixSensitivity" )
        response.adj_flags  = UIntFromBytes(   response.payload[ 2:3 ] )
        response.cur_sens   = FloatFromBytes( response.payload[ 3:7 ] )
        response.fact_sens  = FloatFromBytes( response.payload[ 7:11 ] )

        return response

    #-----------------------------------------------------------------
    def SetMatrixThreshold( self, matrix_no, threshold, do_all_matrices=False, do_reset=False, do_persistent=False ):
        '''
        Send command to set matrix threshold to \a threshold as integer [0 .. 4095] (0 is minimum, 4095 is maximum threshold).
        If \a do_all_matrices is True then the \a threshold is set for all matrices.
        If \a do_reset is True then the threshold is reset to the factory default.        
        If \a do_persistent is True then the threshold is saved persistently to 
        configuration memory and will thus remain after the next power off/power on
        cycle and will become the new factory default value. If \a do_persistent is
        False (default) then the value will be reset to default on the next power
        off/power on cycle
        \warning PLEASE NOTE: the maximum write endurance of the configuration 
        memory is about 100.000 times!        
        
        Raises a cDSAError in case of invalid responses from the remote DSACON32m controller.
        
        \remark Getting the matrix threshold is only possible if the DSACON32m firmware is R268 or above.
        '''
        if ( self.controller_info.sw_version < 268 ):
            raise cDSAError( "Cannot adjust matrix threshold with current DSACON32m firmware (R%d)! Please update to R268 or above.)" % (self.controller_info.sw_version) )
            
        flags = 0
        if ( do_all_matrices ):
            flags |= (1<<1)
        if ( do_reset ):
            flags |= (1<<0)
        if ( do_persistent ):
            flags |= (1<<7)        
            
        self._WriteCommand( self.eDSAPacketID[ "eDSA_SET_MATRIX_THRESHOLD" ], payload=[ flags, matrix_no ] + UInt16ToBytes( threshold )  )
        response = self._ReadResponse( self.eDSAPacketID[ "eDSA_SET_MATRIX_THRESHOLD" ] )
        response.error_code = UIntFromBytes( response.payload[ 0:2 ] )
        self.CheckErrorCode( response.error_code, "SetMatrixThreshold" )
        return response
        
    #-----------------------------------------------------------------
    def GetMatrixThreshold( self, matrix_no ):
        '''
        Send command to get matrix threshold. Returns threshold of matrix no \a matrix_no.
        
        A struct is returned containing the members
        \a error_code - see DSACON32 Command Set Reference Manual
        \a threshold  - the currently set threshold as integer [0 .. 4095] (0 is minimum, 4095 is maximum threshold)
        
        Raises a cDSAError in case of invalid responses from the remote DSACON32m controller.
        
        \remark Getting the matrix threshold is only possible if the DSACON32m firmware is R268 or above.
        '''
        if ( self.controller_info.sw_version < 268 ):
            raise cDSAError( "Cannot read matrix threshold with current DSACON32m firmware (R%d)! Please update to R268 or above.)" % (self.controller_info.sw_version) )
            
        self._WriteCommand( self.eDSAPacketID[ "eDSA_GET_MATRIX_THRESHOLD" ], payload=matrix_no )
        response = self._ReadResponse( self.eDSAPacketID[ "eDSA_GET_MATRIX_THRESHOLD" ] )
        response.error_code = UIntFromBytes(   response.payload[ 0:2 ] )
        self.CheckErrorCode( response.error_code, "GetMatrixThreshold" )
        response.threshold  = UIntFromBytes(   response.payload[ 2:4 ] )

        return response

    #-----------------------------------------------------------------
    def GetTexel( self, m, x, y ):
        '''
        Return texel value at column x row y of frame
        '''
        #self._dbg.var( "m self.sensor_info.nb_matrices" )
        assert 0 <= m and m < self.sensor_info.nb_matrices
        assert x >= 0  and x < self.matrix_info[m].cells_x
        assert y >= 0  and y < self.matrix_info[m].cells_y

        return self.frame.data[ self.texel_offset[m] + y * self.matrix_info[m].cells_x + x ]
    
    #-----------------------------------------------------------------
    def PrintMessage( self, message ):
        '''
        Debug function: print bytes of message
        '''
        for (b, i) in util.Ziplen(message.the_bytes):
            print "%2d: %3d = 0x%02x = '%c'" % (i, b, b, b)

    #-----------------------------------------------------------------
    def PrintFrame( self ):
        '''
        Debug function: print frame 
        '''
        for m in xrange( 0, self.sensor_info.nb_matrices ):
            print "matrix %d:" % m
            for y in xrange( 0, self.matrix_info[m].cells_y ):
                print "%2d" % (y),
                for x in xrange( 0, self.matrix_info[m].cells_x ):
                    print "%4d" % (self.GetTexel( m, x, y )),
                print
            print

    #-----------------------------------------------------------------
    def StartUpdater( self, framerate, do_RLE = True  ):
        '''
        Make remote DSA send frames with framerate. Create a thread
        that updates self.frame continuously (guarded by self.semaphore).
        '''
        self._framerate = framerate
        self._WriteCommand( self.eDSAPacketID[ "eDSA_CONFIGURE_DATA_ACQUISITION" ], framerate=framerate, do_RLE = do_RLE )
        # read and forget first response
        self._ReadNextResponse()

        # is there already an _Updater thread running ?
        if self._updater is None:
            # no, so start one
            self._dbg << "Starting new updater thread\n" # pylint: disable-msg=W0104
            self._semaphore = threading.Semaphore()
            self._updater = threading.Thread( target = self._Updater, name = "cDSA._Updater", args = (self._semaphore,) )
            self._updater.setDaemon( True )
            self._updater.start()

    #-----------------------------------------------------------------
    def _Updater( self, semaphore ):
        '''
        run function of updater thread
        '''
        try:
            while True:
                #self._dbg << "_Updater: self.framerate = %d\n" % self.framerate # pylint: disable-msg=W0104
                if self._framerate > 0:
                    response = self._ReadResponse( self.eDSAPacketID[ "eDSA_FULL_FRAME" ] )
        
                    #self._dbg << "_Updater: read\n" # pylint: disable-msg=W0104
                    
                    self._dbg << "_Updater: updating\n" # pylint: disable-msg=W0104
                    semaphore.acquire()
                    self._ParseFrame( response )
                    semaphore.release()
                else:
                    # framerate was (re)set to 0: retry periodically
                    time.sleep( 1 )
        except cDSAError,e:
            # ignore errors like checksum errors and retry next time
            self._dbg << "_Updater: ignoring %s\n" % str(e) # pylint: disable-msg=W0104
        except KeyboardInterrupt:
            print "_Updater thread: caught KeyboardInterrupt"
        except Exception,e:
            print "_Updater thread: caught exception %s" % str(e)
        finally:
            self._dbg << "_Updater thread in finally!\n" # pylint: disable-msg=W0104
            sys.exit() #raiese SystemExit()

    #-----------------------------------------------------------------
    def _CheckIndex( self, index, maxindex, name="" ):
        ''' Check if \a index is in [0 .. \a maxindex-1] or All. Raise a cDSAError exception if not.
        '''
        if (index < 0  or  maxindex <= index):
            raise cDSAError( "Invalid %s index '%s' (not in range [0..%d[)" % (name, repr(index), maxindex) )

    #-----------------------------------------------------------------
    def _CheckRange( self, value, minvalue, maxvalue, name="" ):
        '''Check if \a value is in [\a minvalue .. \a maxvalue]. Raise a cDSAError exception if not.
        '''
        if (type(value) in self._vector_types):
            for (v_i, min_i, max_i, i) in zip( value, minvalue, maxvalue, range(0, len(value)) ):
                if (not auxiliary.InRange(v_i, min_i, max_i)):
                    raise cDSAError( "Invalid %s value in vector '%s' (value[%d]='%s' not in range [%d..%d])" % (name, repr(value), i, repr(v_i), min_i, max_i) )
        else:
            if not auxiliary.InRange(value, minvalue, maxvalue):
                raise cDSAError( "Invalid %s value ('%s' not in range [%d..%d])" % (name, repr(value), minvalue, maxvalue) )

    #-----------------------------------------------------------------
    def _ToIndexList( self, index, all_replacement, maxindex, name="" ):
        '''Non public helper function: 
        Return a new list of checked indices according to index.
        '''
        if (index == All):
            return all_replacement
        elif (type( index ) in self._vector_types):
            for i in index:
                self._CheckIndex( i, maxindex, name )
            self._CheckRange( len( index ), 1, maxindex, "number of %ss" % name )
            return list(index)
        else:
            self._CheckIndex( index, maxindex, name )
            return [index]


    #-----------------------------------------------------------------
    def GetMatrixIndex( self, fi, part ):
        '''
        return the index of the sensor matrix attached to finger with index fi [1..3] and part [0,1] = [proximal,distal]
        '''
        return fi * 2 + part

    #-----------------------------------------------------------------
    def GetAgeOfFrame( self, frame = None ):
        '''
        return age of frame in ms (time in ms from frame sampling until now)
        '''
        if frame is None:
            frame = self.frame
        now_ms = int(time.time() * 1000.0 +0.5)
        return now_ms - self._start_pc - (frame.timestamp - self._start_dsa)

      
    #-----------------------------------------------------------------
    def GetContactArea( self, fi = All, part = All, frame = None ):
        '''
        Return contact area in mm*mm for finger(s) fi and sensor part(s) part
        '''
        fingers = self._ToIndexList( fi, self.all_fingers, 2, "finger" )
        parts   = self._ToIndexList( part, self.all_parts, 1, "tactile sensor part" )
        if frame is None:
            frame = self.frame

        area = 0.0
        for fi in fingers: 
            for part in parts:
                m = self.GetMatrixIndex( fi, part )
                apc  = self.matrix_info[m].texel_width * self.matrix_info[m].texel_height  # area per cell

                for y in xrange( 0, self.matrix_info[m].cells_y ):
                    for x in xrange( 0, self.matrix_info[m].cells_x ):
                        if self.GetTexel( m, x, y ) > self.contact_area_cell_threshold:
                            area += apc
        return area


    #-----------------------------------------------------------------
    def _VoltageToPressure( self, voltage ):
        '''
        Return a pressure in for cell voltage.
        pressure is in N/(mm*mm)
        '''
        # !!! for now use linear scale anyway

        # N/(mm*mm)  <-> Pascal    (from units.exe):
        #   You have: N/(mm*mm)
        #   You want: pascal
        #             * 1000000
        #             / 1e-06
        # => 1 N/(mm*mm) = 1e6 Pascal
        
        return voltage * self.calib_pressure / self.calib_voltage

    
    #-----------------------------------------------------------------
    def GetContactForce( self, fi, part, frame = None ):
        '''
        Return a tuple (force,cog_x,cog_y,area) of contact force and
        center of gravity and contact area of that force for finger
        fi and sensor part.
        force is in N, cog_x,cog_ in mm, area in mm*mm.
        '''
        assert 0 <= fi  and  fi < 3
        assert 0 <= part and part < 2
        if frame is None:
            frame = self.frame


        sum_pressures = 0.0
        sum_x = 0.0
        sum_y = 0.0
        nbcells = 0

        m = self.GetMatrixIndex( fi, part )

        for y in xrange( 0, self.matrix_info[m].cells_y ):
            for x in xrange( 0, self.matrix_info[m].cells_x ):
                v = self.GetTexel( m, x, y )

                if ( v > self.contact_force_cell_threshold ):

                    # \attention we cannot just sum up the voltages delivered by the tactile sensor since the 
                    # correlation between voltage and pressure might be non linear
                    # so let calibration_data.VoltageToPressure() handle that
                    p = self._VoltageToPressure( v )
                    sum_pressures += p
                    sum_x += float(x) * p
                    sum_y += float(y) * p
                    nbcells += 1

        area = self.matrix_info[m].texel_width * self.matrix_info[m].texel_height * float(nbcells)

        force = self.force_factor * sum_pressures * area
        if ( sum_pressures != 0.0 ):
            cog_x = self.matrix_info[m].texel_width  * sum_x / sum_pressures
            cog_y = self.matrix_info[m].texel_height * sum_y / sum_pressures
        else:
            cog_x = 0.0
            cog_y = 0.0

        return (force, cog_x, cog_y, area)
    
# end of class cDSA
######################################################################

##
#  @}



######################################################################
# some usefull editing settings for emacs:
#
#;;; Local Variables: ***
#;;; mode:python ***
#;;; End: ***
#
######################################################################
