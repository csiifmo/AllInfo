# -*- coding: latin-1 -*-
#######################################################################
#
## \file
#  \section sdhlibrary_python_auxiliary_py_general General file information
#
#    \author   Dirk Osswald
#    \date     2007-06-13
#
#  \brief  
#    Implementation of auxiliary variables, functions, classes.
#
#  \section sdhlibrary_python_auxiliary_py_copyright Copyright
#
#  Copyright (c) 2007 SCHUNK GmbH & Co. KG
#
#  <HR>
#  \internal
#
#    \subsection sdhlibrary_python_auxiliary_py_details SVN related, detailed file specific information:
#      $LastChangedBy: Osswald2 $
#      $LastChangedDate: 2014-09-30 09:44:33 +0200 (Tue, 30 Sep 2014) $
#      \par SVN file revision:
#        $Id: auxiliary.py 12281 2014-09-30 07:44:33Z Osswald2 $
#
#  \subsection sdhlibrary_python_auxiliary_py_changelog Changelog of this file:
#      \include auxiliary.py.log
#
#######################################################################

import sys, os, array, math, re

#######################################################################
## \anchor sdhlibrary_python_auxiliary_py_python_vars
#  \name   Python specific variables
#  
#  Some definitions that describe the module for python.
#
#  @{

# pylint: disable-msg=W0622
__doc__       = "Auxiliary variables, functions, classes for sdh package"
__author__    = "Dirk Osswald: dirk.osswald@de.schunk.com"
__url__       = "http://www.schunk.com"
__version__   = "$Id: auxiliary.py 12281 2014-09-30 07:44:33Z Osswald2 $"
__copyright__ = "Copyright (c) 2007 SCHUNK GmbH & Co. KG"

#  end of doxygen name group sdhlibrary_python_auxiliary_py_python_vars
#  @}
######################################################################


#######################################################################
## \anchor sdhlibrary_python_auxiliary_py_auxiliary
#  \name   Auxiliary variables, functions, classes
#
#  @{

######################################################################
# Auxiliary variables:

## \brief Flag, if True then this hand has a DSA, i.e. a tactile sensor controller
has_dsa = True

#
######################################################################


######################################################################
# Auxiliary functions:

#-----------------------------------------------------------------
def InIndex( v, max_v ):
    '''
    Return True if v is in range [0 .. max_v[
    '''
    return 0 <= v  and  v < max_v


#-----------------------------------------------------------------
def InRange( v, min_v, max_v ):
    '''
    Return True if v is in range [min_v .. max_v]
    '''
    return min_v <= v  and  v <= max_v


#-----------------------------------------------------------------
def ToRange( v, min_v, max_v ):
    '''
    Return v limited to range [min_v .. max_v]. I.e. if v is < min_v then
    min_v is returned, or if v > max_v then max_v is returned, else v is
    returned
    '''
    if v < min_v: return min_v
    if v > max_v: return max_v
    return v


#-----------------------------------------------------------------
def Approx( a, b, eps ):
    '''
    Return True if a is approximately the same as b. I.E. |a-b| < eps
    '''
    return abs( a - b ) < eps


#-----------------------------------------------------------------
def InRange_a( v, min_v, max_v ):
    '''
    Return True if in list/tuple/array v=(v1,v2,...)  each
    v_i is in range [min_v_i..max_v_i] with
    min_v = (min_v1, min_v2,...) max_v = (max_v1, max_v2, ..)
    '''
    for (v_i, min_v_i, max_v_i) in zip( v, min_v, max_v ):
        if (not InRange( v_i, min_v_i, max_v_i )):
            return False
    return True


#-----------------------------------------------------------------
def ToRange_a( v, min_v, max_v ):
    '''
    Return list/tuple/array v=(v1,v2,...) where each
    v_i is limited to range [min_v_i..max_v_i] with
    min_v = (min_v1, min_v2,...) max_v = (max_v1, max_v2, ..)

    I.e. if v_i is < min_v_i then min_v_i is part of the result
    list/tuple/array, or if v_i > max_v_i then max_v_i is part of the
    result list/tuple/array, else v_i is part of the result
    list/tuple/array
    '''
    res = tuple()
    for (v_i, min_v_i, max_v_i) in zip( v, min_v, max_v ):
        res += (ToRange( v_i, min_v_i, max_v_i ),)

    if type( v ) == type(array.array("d")):
        return array.array( "d", res )
    if type( v ) == list:
        return list(res)
    return res


#-----------------------------------------------------------------
def Approx_a( a, b, eps ):
    '''
    Return True if list/tuple/array a=(a1,a2,...) is approximately
    the same as b=(b1,b2,...). I.E. |a_i-b_i| < eps[i]
    '''
    for (a_i, b_i, eps_i) in zip( a, b, eps ):
        if (not Approx( a_i, b_i, eps_i )): 
            return False
    return True


#-----------------------------------------------------------------
def DegToRad( d ):
    '''
    Return d in deg converted to rad
    '''
    return d*math.pi/180.0


#-----------------------------------------------------------------
def RadToDeg( r ):
    '''
    Return r in rad converted to deg
    '''
    return r*180.0/math.pi


#-----------------------------------------------------------------
def Square(v):
    """
    Return v squared (i.e. v*v)
    """
    return v*v
#---------------------------------------------------------------------

def Alltrue( v ):
    '''
    Return True if all elements of v (tuple, list, array.array).
    '''
    for vi in v:
        if not vi:
            return False
    return True
#-----------------------------------------------------------------

def Allmin( v, w ):
    '''
    Return list of min elements of v and w (tuple, list, array.array).
    '''
    return map( min, zip( v, w ) ) # pylint: disable-msg=W0141
#-----------------------------------------------------------------

def Allmax( v, w ):
    '''
    Return list of max elements of v and w (tuple, list, array.array).
    '''
    return map( max, zip( v, w ) ) # pylint: disable-msg=W0141

MIN_FLOAT = -3.40E+38 # http://de.wikipedia.org/wiki/IEEE_754
MAX_FLOAT = +3.40E+38

#-----------------------------------------------------------------
 
def AsStruct( dict_or_struct ):
    '''
    return dict_or_struct as struct
    '''
    if ( type( dict_or_struct ) == dict ):
        # pylint: disable-msg=F0401
        from . import utils
        ret = utils.Struct()
        ret.__dict__.update(dict_or_struct)
        return ret
    else:
        return dict_or_struct  
 
def GetVersionInfo( script_name, script_release, options, hand=None, dsa_obj=None ):
    ''' 
    Return a string with all the version info:
    - name and release of the calling script (PC),
    - name and release of the library (PC),
    - name of the platform (PC),
    - name and release of the Python executable (PC),
    - release and date of firmware (SDH),
    - release and date of SoC (SDH),
    - id and serial number of the SDH,
    - hardware and software versions and serial numbers for:
      - the tactile controller DSACON32m (SDH),
      - the tactile sensors (SDH)
    '''
    # pylint: disable-msg=F0401
    from . import release
    from . import sdh
    
    options = AsStruct( options )
    _dbg = sdh.dbg.tDBG( options.debug_level>0 )
    _dbg << PrettyStruct( "GetVersionInfo: using options", options )
    ret  = "PC-side:\n"
    ret += "  Script name:                  %s\n" % script_name
    ret += "  Script release:               %s\n" % script_release
    ret += "  SDHLibrary-python release:    %s\n" % (release.PROJECT_RELEASE)
    ret += "  SDHLibrary-python date:       %s\n" % (release.PROJECT_DATE)
    ret += "  Recommended firmware release: %s\n" % (sdh.cSDH.GetFirmwareReleaseRecommended())

    # pylint: disable-msg=E1103
    if ( options.debug_level > 0 ):
        ret += "  Platform:                     %s\n" % sys.platform  
        ret += "  Python executable:            %s\n" % sys.executable
        ret += "  Python version:               %s\n" % sys.version.replace("\n", "\n" + 29*" " )

    nc = "? (not connected?)" # ANOTE: Could include a hint to the interface tried (RS232 port, CAN, Ethernet,...)
    ver = nc
    ver_date = nc
    soc = nc
    soc_date = nc
    sid = nc
    sn = nc
    do_close = False
    _dbg << "GetVersionInfo: Trying to connect to joint controller of SDH for retrieving version info...\n" # pylint: disable-msg=W0104
    try:
        options.debug_level -= 1
        if not hand:
            hand = sdh.cSDH( options=options.__dict__ )
        if ( not hand.IsOpen() ):
            hand.Open()
            do_close = True
        ver      = hand.GetInfo( "release-firmware" )
        ver_date = hand.GetInfo( "date-firmware" )
        soc      = hand.GetInfo( "release-soc" )
        soc_date = hand.GetInfo( "date-soc" )
        sid      = hand.GetInfo( "id-sdh" )
        sn       = hand.GetInfo( "sn-sdh" )
    except IndexError:
        # ignore this, happens if hand is not connected
        pass
    except sdh.cSDHErrorTimeout:
        # ignore this, happens if hand is not connected
        pass
    except sdh.cSDHErrorCommunication:
        # ignore this, happens if hand is not connected
        pass
    finally:
        if hand  and do_close:
            hand.Close()
        
    ret += "SDH-side:\n"
    ret += "  Joint Controller:\n"
    ret += "    SDH firmware release:       %s\n" % (ver)
    ret += "    SDH firmware date:          %s\n" % (ver_date)
    ret += "    SDH SoC ID:                 %s\n" % (soc)
    ret += "    SDH SoC date:               %s\n" % (soc_date)
    ret += "    SDH ID:                     %s\n" % (sid)
    ret += "    SDH Serial Number:          %s\n" % (sn)

    if (sdh.has_dsa):
        _dbg << "GetVersionInfo: Trying to connect to tactile sensor controller of SDH for\n" # pylint: disable-msg=W0104
        _dbg << "  retrieving version info. This may take up to 8 seconds...\n" # pylint: disable-msg=W0104
        
        from . import dsa  # pylint: disable-msg=E0611,F0401
        nc = "? (not connected?)" # ANOTE: Could include a hint to the interface tried (RS232 port, CAN, Ethernet,...)
        dsa_controller_hw_version = nc
        dsa_controller_sw_version = nc
        dsa_controller_serial_no = nc
        dsa_sensor_hw_revision = nc
        dsa_sensor_serial_no = nc
        dsa_matrix_info = nc
        do_close = dsa_obj is None
        try:
            if dsa_obj is None:
                dsa_obj = dsa.cDSA( port=options.dsaport, 
                                    debug_level=options.debug_level-1, 
                                    baudrate=115200, # fixed for now 
                                    timeout=1,       # fixed for now
                                    debug_output=options.debug_output )
            dsa_controller_hw_version = str( dsa_obj.controller_info.hw_version )
            dsa_controller_sw_version = str( dsa_obj.controller_info.sw_version )
            if ( dsa_obj.controller_info.sw_version >= 0x1000 ):
                # version numbering has changed, see bug 996
                new_version_string = ""
                sep = ""
                for i in range(4):
                    new_version_string = str((dsa_obj.controller_info.sw_version >> (i*4)) & 0x0f) + sep + new_version_string
                    sep = "." 
                dsa_controller_sw_version += " (" + (new_version_string) + ")"
            dsa_controller_serial_no = str( dsa_obj.controller_info.serial_no )
            dsa_sensor_hw_revision = str( dsa_obj.sensor_info.hw_revision )
            dsa_sensor_serial_no = str( dsa_obj.sensor_info.serial_no )
            dsa_matrix_info = ""
            sep = ""
            for m in dsa_obj.matrix_info:
                dsa_matrix_info += sep + str( m.hw_revision )
                sep = ", "
        except IndexError:
            # ignore this, happens if hand is not connected
            pass
        except sdh.cSDHErrorTimeout:
            # ignore this, happens if hand is not connected
            pass
        except sdh.serial.SerialException:
            # ignore this, happens if hand is not connected
            pass
        except dsa.cDSAError:
            pass
        finally:
            if dsa_obj and do_close:
                dsa_obj.Close()
    
        ret += "  Tactile sensor system:\n"
        ret += "    Controller HW version:   %s\n" % (dsa_controller_hw_version)
        ret += "    Controller SW version:   %s\n" % (dsa_controller_sw_version)
        ret += "    Controller SN:           %s\n" % (dsa_controller_serial_no)
        ret += "    Sensor HW revision:      %s\n" % (dsa_sensor_hw_revision)
        ret += "    Sensor SN:               %s\n" % (dsa_sensor_serial_no)
        ret += "    Matrix HW revisions:     %s"   % (dsa_matrix_info)

    return ret

#
######################################################################

######################################################################
# Auxiliary classes:

from optparse import OptionParser, OptionValueError

    

## \brief Customized OptionParser with some SDH specific options already set.
#
#  The following common options are already set
#  -  -p | --port PORT   : use com port PORT instead of the default 0 (sets options.port)
#  -  -d | --debug LEVEL : turn on debug (sets options.debug_level to LEVEL)
#  -  -R | --radians     : Use radians and radians per second for angles and angular
#                          velocities instead of default degrees and degrees per second
#                          (sets options.use_radians)
#  -  -F | --fahrenheit  : Use degrees fahrenheit to report temperatures instead of
#                          default degrees celsius"
#                          (sets options.use_fahrenheit)
#  -  -v | --version     : print version and exit
#  -  -T | --timeout     : Timeout used to wait for answers from SDH
#                          (The default is None which means wait for ever)
#
#  An object of this class can be used by scripts that access the SDH.
#  Such scripts can of course add further script specific options.
#  For example uses see the demo-*.py scripts
#
#  \par example
#  \code
#    # Command line option handling
#
#    # Create an option parser object to parse common command line options
#    parser = sdh.cSDHOptionParser( usage    =  __doc__ + "\nusage: %prog [options]",
#                                   revision = __version__ )
#
#    Parse (and handle, if possible) the command line options of the script
#    (options, args) = parser.parse_args()
#  
#    # The parsed command line arguments are now stored in the options
#    # object. E.g. options.port is the communication port to use, either
#    # the default one or the one read from the -p | --port command line
#    # argument:
#    print "The serial port %d will be used" % (options.port)
#  
#    # For even more comfort the parsed options can be forwarded directly
#    # to a cSDH constructor, like in:
#    hand = sdh.cSDH( options=options.__dict__ )
#
#  \endcode
#
#  <hr>
class cSDHOptionParser(OptionParser):
    '''Customized OptionParser with some SDH specific options already set. See html/pdf documentation for details.
    '''
    default_sdh_port = 0
    default_dsa_port = 4
    default_tcp_adr  = "192.168.1.42"
    default_tcp_port = 23
    default_dsa_tcp_port = 13000
    
    #-----------------------------------------------------------------
    def CBDebugLog( self, option, opt_str, value, parser, *args, **kwarg ):
        '''Callback for the -l | --debuglog option
        '''
        if ( value == "stderr" ):
            debug_output = sys.stderr
        elif ( value == "stdout" ):
            debug_output = sys.stdout
        else:
            mode = "w"
            if ( value[0] == "+" ):
                mode = "a"
                value = value[1:]
            try:
                debug_output = file( name=value, mode=mode, buffering=1 )
            except IOError,e:
                raise OptionValueError( "Could not open debug logfile '%s': %s" % (value, str(e)) )
                 
        setattr( parser.values, option.dest, debug_output )
         
         
    def CBTCP( self, option, opt_str, value, parser, *args, **kwarg ):
        '''Callback for the --tcp option
        '''
        from . import sdh
        _dbg = sdh.dbg.tDBG( parser.values.debug_level > 0, "blue" )
        #_dbg.var( "option opt_str value args kwarg")
        setattr( parser.values, option.dest, True )

        tcp_adr  = getattr( parser.values, "tcp_adr", self.default_tcp_adr )
        tcp_port = self.default_tcp_port
        
        if ( ":" in value ):
            adr_port = value.split(":")
            if ( adr_port[0] != "" ):
                tcp_adr = adr_port[0]
            tcp_port = int( adr_port[1] )
        elif ( value != "" ):
            tcp_adr = value
            
        _dbg.var( "tcp_adr" )
        _dbg.var( "tcp_port" )
        setattr( parser.values, "tcp_adr",  tcp_adr )
        setattr( parser.values, "tcp_port", tcp_port )

        #>demo-GetAxisActualAngle.py -d 5 --tcp= -h
        #option = <Option at 0x7fe531ac: --tcp>, opt_str = '--tcp', value = '', args = (), kwarg = {}
        #>demo-GetAxisActualAngle.py -d 5 --tcp -h
        #option = <Option at 0x7fe531ac: --tcp>, opt_str = '--tcp', value = '-h', args = (), kwarg = {}
        #>demo-GetAxisActualAngle.py -d 5 --tcp=$ipsdh
        #option = <Option at 0x7fe9ff6c: --tcp>, opt_str = '--tcp', value = '192.168.101.106', args = (), kwarg = {}
        #>demo-GetAxisActualAngle.py -d 5 --tcp=:40   
        #option = <Option at 0x7fe9ff6c: --tcp>, opt_str = '--tcp', value = ':40', args = (), kwarg = {}
         
    def CBDSATCP( self, option, opt_str, value, parser, *args, **kwarg ):
        '''Callback for the --dsa_tcp option
        '''
        from . import sdh
        _dbg = sdh.dbg.tDBG( parser.values.debug_level > 0, "blue" )
        #_dbg.var( "option opt_str value args kwarg")
        setattr( parser.values, option.dest, True )

        tcp_adr  = getattr( parser.values, "tcp_adr", self.default_tcp_adr )
        dsa_tcp_port = self.default_dsa_tcp_port
        
        if ( ":" in value ):
            adr_port = value.split(":")
            if ( adr_port[0] != "" ):
                tcp_adr = adr_port[0]
            dsa_tcp_port = int( adr_port[1] )
        elif ( value != "" ):
            tcp_adr = value
            
        _dbg.var( "tcp_adr" )
        _dbg.var( "dsa_tcp_port" )
        setattr( parser.values, "tcp_adr",  tcp_adr )
        setattr( parser.values, "dsa_tcp_port", dsa_tcp_port )
        setattr( parser.values, "dsaport", "%s:%d" %(tcp_adr,dsa_tcp_port) )
         
    def parse_args(self, args=None, values=None):
        '''overloaded version of the optparse.OptionParser.parse_args() method
        parse the args and perform some actions if requested (like reading version info from SDH)
        '''
        # call method of parent class
        (options,args) = OptionParser.parse_args( self, args, values )

        if ( options.port is None  and  options.sdh_rs_device is None ):
            options.port_set_by_user = False
        else:
            options.port_set_by_user = True

        if ( options.dsaport is None  and  options.dsa_rs_device is None):
            options.dsaport_set_by_user = False
        else:
            options.dsaport_set_by_user = True


        if ( options.port is None ):
            options.port = self.default_sdh_port

        if ( options.dsaport is None ):
            options.dsaport = self.default_dsa_port

        
        if ( options.sdh_rs_device is None ):
            options.sdh_rs_device = GetDevicePatterns()[0]

        if ( options.dsa_rs_device is None ):
            options.dsa_rs_device = GetDevicePatterns()[0]
            
            
        if ( "%" in options.sdh_rs_device  and  type(options.port) == int ):
            if ( options.port == -1 ):
                options.sdh_rs_device = -1
            else:
                if ( options.sdh_rs_device[0:3] == "COM" ):
                    options.port = (options.sdh_rs_device % (options.port+1)) # port 0 is COM1 on windows
                else:
                    options.port = (options.sdh_rs_device % (options.port))
        else:
            options.port = options.sdh_rs_device
        
        if ( "%" in options.dsa_rs_device  and  type(options.dsaport) == int ):
            if ( options.dsa_rs_device[0:3] == "COM" ):
                options.dsaport = (options.dsa_rs_device % (options.dsaport+1))
            else:
                options.dsaport = (options.dsa_rs_device % (options.dsaport))
        elif ( ":" in options.dsaport ):
            # dsaport is a IP_OR_HOSTNAME:PORT, leave it alone
            pass
        else:
            options.dsaport = options.dsa_rs_device
        
        # do final actions, if requested
        if (options.do_check_version):
            from . import sdh
            
            options = AsStruct( options )
            options.debug_level -= 1
            hand = sdh.cSDH( options=options.__dict__ )
            hand.Open()
            if ( hand.CheckFirmwareRelease() ):
                print "The firmware release of the connected SDH is the one recommended by"
                print "this SDHLibrary. Good."
            else:
                print "The firmware release of the connected SDH is NOT the one recommended"
                print "by this SDHLibrary:"
                print "  Actual SDH firmware release:     ", hand.GetFirmwareRelease()
                print "  Recommended SDH firmware release:", hand.GetFirmwareReleaseRecommended()
                print "  => Communication with the SDH might not work as expected!"
            if hand:
                hand.Close()
            
        if (options.do_show_version):
            print GetVersionInfo( os.path.basename(sys.argv[0]), self.revision, options, None, None )
            sys.exit(0)
            
        # return parsing results   
        return (options,args)
        
        
    #-----------------------------------------------------------------
    ## Create a cSDHOptionParser instance
    #
    #  \param self     - reference to the object itself
    #  \param usage    - A string describing the purpose of the calling script
    #  \param revision - A string describing the revision of the calling script
    def __init__(self, usage = "", revision = "" ):
        '''
        Create a cSDHOptionParser instance. See html/pdf documentation for details.
        '''
        OptionParser.__init__( self, usage )
        self.revision = revision
        
        # add common options:
        self.add_option( "-p", "--port",
                         dest="port", type=int,
                         help="use serial communication port PORT to connect to SDH instead of default %d='COM%d'='/dev/ttyS%d'." % (self.default_sdh_port,self.default_sdh_port+1,self.default_sdh_port),
                         metavar="PORT" )
        self.add_option( "--sdh_rs_device",
                         dest="sdh_rs_device", type=str,
                         help="Use DEVICE_FORMAT_STRING instead of the default \"%s\". Useful on Linux, e.g. to use USB to RS232 converters available via \"/dev/ttyUSB%%d\". If the DEVICE_FORMAT_STRING contains '%%d' then the PORT must also be provided. If not then the DEVICE_FORMAT_STRING is the full device name." % (GetDevicePatterns()[0]),
                         metavar="DEVICE_FORMAT_STRING" )
        self.add_option( "-d", "--debug",
                         dest="debug_level", default=0, type=int, metavar="LEVEL",
                         help="Print debug messages of level LEVEL or lower while processing the python script. Level 0 (default): No messages,\r 1: Script-level messages, 2: cSDH-level messages, 3: cSDHSerial-level messages" )
        self.add_option( "-l", "--debuglog",
                         dest="debug_output", default=sys.stderr, type=str, metavar="LOGFILE",
                         action="callback", callback=self.CBDebugLog,
                         help="Redirect the printed debug messages to LOGFILE instead of standard error (default). If LOGFILE starts with '+' then the output will be appended to the file (without the leading '+'), else the file will be rewritten." )
        self.add_option( "-R", "--radians",
                         dest="use_radians", default=False, action="store_true",
                         help="Use radians and radians per second for angles and angular velocities instead of default degrees and degrees per second" )
        self.add_option( "-F", "--fahrenheit",
                         dest="use_fahrenheit", default=False, action="store_true",
                         help="Use degrees fahrenheit to report temperatures instead of default degrees celsius" )
        self.add_option( "-v", "--version",
                         dest="do_show_version", default=False, action="store_true", 
                         help="Print the version (revision/release names) of script, library, python interpreter (PC-side) and firmware release, date (SDH-side) then exit.")
        self.add_option( "-V", "--version_check",
                         dest="do_check_version", default=False, action="store_true", 
                         help="Check the firmware release of the connected SDH if it is the one recommended by this library. A message will be printed accordingly.")
        self.add_option( "-T", "--timeout",
                         dest="timeout", default=None, type=float, metavar="TIMEOUT",
                         help="Timeout in seconds (float accepted) used to wait for answers from SDH (default is None = wait for ever)." )
        self.add_option( "-c", "--can",
                         dest="usecan", default=False, action="store_true",
                         help="use the (ESD) CAN interface instead of RS232. (Requires the windows python.exe not the cygwin one)" )
        self.add_option( "-n", "--net",
                         dest="net", default=0, type=int, metavar="NET",
                         help="use the ESD CAN net number NET" )
        self.add_option( "--id_read",
                         dest="id_read", default=43, type=int, metavar="ID_READ",
                         help="use the CAN ID ID_READ for receiving messages from the SDH. Default is 43." )
        self.add_option( "--id_write",
                         dest="id_write", default=42, type=int, metavar="ID_WRITE",
                         help="use the CAN ID ID_WRITE for sending messages to the SDH. Default is 42." )
        self.add_option( "--baudrate", "--baud",
                         dest="baudrate", default=0, type=int, metavar="BAUDRATE",
                         help="use the BAUDRATE for communication. Default is 115200 Bit/s for RS232 and 1 MBit/s for CAN." )
        self.add_option( "--tcp", 
                         action="callback", callback=self.CBTCP,
                         dest="usetcp", default=False, type=str, metavar="[IP_OR_HOSTNAME][:PORT]",
                         help="use TCP for communication with the SDH. The SDH can be reached via TCP/IP on port PORT at IP_OR_HOSTNAME, which can be a numeric IPv4 address or a hostname. The default is %s:%d (to use the default you have to specify '--tcp='). When using --tcp and --dsa_tcp then only the last set IP_OR_HOSTNAME is used for both. (This feature requires at least SDH firmware 0.0.3.1)" % (self.default_tcp_adr, self.default_tcp_port) )

        global has_dsa
        if has_dsa:
            # Add an option to set the extra serial port used by the DSA
            self.add_option( "--dsaport",
                             dest="dsaport", type=int,
                             help="use serial communication port PORT to connect to DSA (tactile sensor of SDH) instead of default %d='COM%d'='/dev/ttyS%d'." % (self.default_dsa_port,self.default_dsa_port+1,self.default_dsa_port),
                             metavar="PORT" )
            self.add_option( "--dsa_rs_device",
                             dest="dsa_rs_device", type=str,
                             help="Use DEVICE_FORMAT_STRING instead of the default \"%s\". Useful on Linux, e.g. to use USB to RS232 converters available via \"/dev/ttyUSB%%d\". If the DEVICE_FORMAT_STRING contains '%%d' then the PORT must also be provided. If not then the DEVICE_FORMAT_STRING is the full device name." % (GetDevicePatterns()[0]),
                             metavar="DEVICE_FORMAT_STRING" )
            self.add_option( "--dsa_tcp",
                             action="callback", callback=self.CBDSATCP,
                             dest="usedsatcp", default=False, type=str, metavar="[IP_OR_HOSTNAME][:PORT]",
                             help="use TCP for communication with the DSA (tactile sensor of SDH). The DSA can be reached via TCP/IP on port PORT at IP_OR_HOSTNAME, which can be a numeric IPv4 address or a hostname. The default is %s:%d (to use the default you have to specify '--dsa_tcp='). When using --tcp and --dsa_tcp then only the last set IP_OR_HOSTNAME is used for both. (This feature requires at least SDH firmware 0.0.3.2)" % (self.default_tcp_adr, self.default_dsa_tcp_port) )
            self.add_option( "--dsa_tcp_port",
                             dest="dsa_tcp_port", default=self.default_dsa_tcp_port, type=int, metavar="PORT",
                             help="use TCP port PORT for communication with the DSA (tactile sensor of SDH). The default is %d. (This feature requires at least SDH firmware 0.0.3.2)" % (self.default_dsa_tcp_port) )
            # Add an option to set the rate of acquiring frames from DSA
            self.add_option( "-r", "--framerate",
                             dest="framerate", default=0, type=int,
                             help="Framerate for acquiring full tactile sensor frames. Default value 0 means 'acquire a single frame only'. Any value > 0 will make the DSACON32m controller in the SDH send data at the highest possible rate (ca. 30 FPS (frames per second))." )
            # Add an option to disable RLE (Run Length Encoding) for acquiring full frames
            self.add_option( "--no_rle",
                             dest="do_RLE", default=True, action="store_false",
                             help="Disable RLE (Run Length Encoding) for acquiring full frames." )
  
  
def GetCommunicationInterfaceName( options, dsa=False):
    '''\return the name of the selected communication interface according to \a options as a human readable string.
    If \a dsa is False then then interface for SDH is returned. If True then the interface for DSA is returned.
    '''    
    if ( dsa ):
        return "RS232 (%s)" %(options["dsaport"]) 
        
    if ( options["usecan"] ):
        return "CAN bus (ESD net %d)" % (options["net"])
    if ( options["usetcp"] ):
        return "TCP/IP (%s:%d)" %(options["tcp_adr"], options["tcp_port"]) 
    return "RS232 (%s)" %(options["port"]) 
                             
#
######################################################################

class cSphere:
    """
    A class to represent sphere objects. Used for simple internal collision check.
    """
    def __init__( self, x, y, z, r ):
        """
        Constructor, store coordinates x,y,z and radius r of spehre
        """
        self.x, self.y, self.z = x, y, z
        self.r = r
        #-------------------------
    

    def Distance( self, other ):
        """
        Calculates the distance between self and other sphere.
        If the returned result is zero then the spheres touch each other,
        If it is negative the spheres intersect each other.
        """
        # small speed up:
        # - do not use Square()
        # - access sqrt directly
        dx = other.x - self.x
        dy = other.y - self.y
        dz = other.z - self.z
        
        dist_centers = math.sqrt( dx*dx + dy*dy + dz*dz )
        #dist_centers = math.sqrt( dx*dx + dy*dy + dz*dz )
        #dist_centers = math.sqrt( Square( other.x - self.x ) +
        #                                  Square( other.y - self.y ) +
        #                                  Square( other.z - self.z )   )
        #print "Distance %f, %f, %f,  -  %f, %f, %f = %f" % (other.x, other.y, other.z, self.x, self.y, self.z, dist_centers)
        return dist_centers - self.r - other.r
        #-------------------------

    def Toiv( self ):
        """
        Return a string of this sphere as an OpenInventor iv description
        """
        return """Separator {
    Transform { translation %f %f %f }
    Material { diffuseColor 1 1 1 }
    Sphere { radius %f }
}
""" % (self.x, self.y, self.z, self.r )
#---------------------------------------------------------------------


def WriteIVFile( filename, objects ):
    """
    Generate an OpenInventor iv file of all the objects by calling o.Toiv()
    """
    f = file( filename, "w" )

    f.write( "#Inventor V2.0 ascii\n" )
    
    f.write( "Separator {\n" )

    for o in objects:
        if type(o) in [list, tuple]:
            for oi in o:
                f.write( oi.Toiv() )
        else:
            f.write( o.Toiv() )
    
    f.write( "}\n" )
    f.close()
#---------------------------------------------------------------------

def GetDevicePatterns():
    '''Return a list of RS232 device name patterns corresponding to the current platform
    '''
    if ('linux' in sys.platform):
        return ["/dev/ttyS%d","/dev/ttyUSB%d"]
    if ( sys.platform == 'cygwin' ):
        return ["/dev/ttyS%d"]
    return ["COM%d"]
    
    
def GetAvailablePorts( maxport=32, Print=lambda msg: None, device_patterns=GetDevicePatterns(), exclude=[] ):
    '''Return a list of tuples (p,occupied), where p is device name of a serial port 
    of the computer and occupied is True if the port is occupied by another 
    application or the port is inaccessible. The ports up to maxport are tested.
    If hints like "port is occupied" or "insufficient rights" should printed then
    Print should be a function that is able to print messages given as parameter.  
    The device_patterns is a list of device name patterns like ["/dev/ttyS%d", "/dev/ttyUSB%d"]
    to search for.
    \param exclude - a list of ports or devicenames that should be excluded from probing
                     (required on Linux where searching for a port A that is already in use by
                     the application makes a running select call on that port A block).
                     The excluded ports will be contained as (name,True) in the return list.
                     
    \bug
       SCHUNK-internal bugzilla ID: Bug 1013<br>
       On Linux the probing for available ports seems to disturb communication to
       already opened ports. This inhibits demo-gui.py from working. 
       <br><b>=> Resolved in SDHLibrary-Python 0.0.2.2</b> 
    '''
    import serial
    os_cygwin = sys.platform == 'cygwin'
    os_win32  = sys.platform == 'win32'
    os_linux  = 'linux' in sys.platform
    # regular expression to parse the error number from pyserial exception.
    # Sadly this is VERY system specific...
    # !!!
    # ANOTE: dont forget to forward updates below to sdhflash/sdhflash.py as well !!!
    # !!!
    get_errno_re = re.compile( "(Could not open port: \[Errno (\d+)|"     # group(2): cygwin python 2.5.1  pyserial 2.2, SuSE Linux python 2.5.2
                              + "could not open port: \((\d+)|"             # group(3): Windows python 2.5.1 pyserial 2.2
                              + "could not open port '?[^:]+'?: \[Errno (\d+)|"  # group(4): cygwin python 2.5.1/2.6 pyserial 2.4    
                              + "could not open port '?[^:]+'?: \((\d+)|"      # group(5): Windows python 2.6   pyserial 2.4
                              + "Could not configure port: \((\d+)|"         # group(6): Ubuntu Linux python 2.5
                              + "could not open port '?[^:]+'?: \[Error (\d+)|" # group(7): Windows python 2.6   pyserial 2.6
                              + "could not open port '?[^:]+'?: WindowsError\((\d+)|" # group(8): Windows python 2.7   pyserial 2.7
                              + "could not open port '?[^:]+'?: \((\d+))" # group(9): Windows python ?   pyserial ?
                              ) 
    available_ports=[]
    for device_pattern in device_patterns:
        for port in range(0,maxport):
            s = None
            try:
                portname = device_pattern % port
                ignore = False
                for ex in exclude:
                    if ( ((type( ex ) == int) and (ex == port)) or (ex == portname ) ):
                        ignore = True
                        break
                if ( ignore ):
                    available_ports.append( (portname,True) )
                    continue
 
                s = serial.Serial( port=portname )
            except ValueError,e:
                sys.stderr.write( "Error: Could not access port %d, ignored!\n  Exception was '%s'.\n  Please send a screenshot to dirk.osswald@de.schunk.com to get this fixed!" % (port,str(e)) )
                continue
                
            except serial.serialutil.SerialException, e:
                get_errno_mo = get_errno_re.match( str(e) )
                errno = None
                if ( get_errno_mo is not None ):
                    for g in get_errno_mo.groups()[1:]:
                        if (g is not None):
                            errno = int(g)
                #print "caught except e=", e, " errno=", errno, "os_cygwin=", os_cygwin, "os_win32=", os_win32, "os_linux=", os_linux
                if ( errno is None ):
                    #raise Exception( "Error: Could not parse pyserial exception while accessing port %d, giving up!\n  Exception was '%s'" % (port,str(e)) )
                    # Instead of raising an Exception just inform the user und ignore the error.
                    # In most cases something usefull can still be done. 
                    sys.stderr.write( "Error: Could not parse pyserial exception while accessing port %d, ignored!\n  Exception was '%s'.\n  Please send a screenshot to dirk.osswald@de.schunk.com to get this fixed!" % (port,str(e)) )
                    continue
                if ( ((os_cygwin or os_win32) and errno == 2)   or
                     (os_linux and errno == 5) ):
                    # errno 2 is "No such file or directory" or "'Das System kann die angegebene Datei nicht finden.' on cygwin and windows
                    # errno 5 is "Could not configure port" on linux / ubuntu / suse"
                    # these indicate that the port does not exist 
                    continue
                if ( os_linux and errno in [2,6] ):
                    # errno 2 is "could not open port / No such file or directory" on linux
                    # errno 6 is "could not open port / No such device or address" on linux
                    # these indicate that the port does not exist 
                    continue
                if ( (os_cygwin and errno == 13) or
                     (os_win32  and errno == 5) ):
                    # any other errno indicates that the port does exist but is not available
                    # errno 5/13 is "Permission denied" on windows/cygwin, 
                    # which indicates that the port is used by another application,
                    # So warn user about that, and do not try to use that port
                    Print( "\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" )
                    Print( "! Another application is using port %d = COM%d !" % (port,port+1) )
                    Print( "! A SDH connected there cannot be detected     !" )
                    Print( "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n" )
                    available_ports.append( (portname,True) )
                    continue
                if ( (os_linux and errno == 13) ):
                    # errno 13 is "Permission denied" on Linux,
                    # which indicates that the user does not have sufficient rights to access the port
                    # So warn user about that, and do not try to use that port
                    Print( "\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" )
                    Print( "! You do not have sufficient rights to access " )
                    Print( "! port %s !" % ((device_pattern % port)) )
                    Print( "! A SDH connected there cannot be detected     !" )
                    Print( "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n" )
                    available_ports.append( (portname,True) )
                    continue
                sys.stderr.write( "Error: Could not handle pyserial exception while accessing port %d, ignored!\n  Exception was '%s'.\n  Please send a screenshot to dirk.osswald@de.schunk.com to get this fixed!" % (port,str(e)) )
                continue
            if (s):
                s.close()
            available_ports.append( (portname,False) )
    return available_ports
#----------------------------------------------------------------------

def GetIconPath( icon_dir=None, icon_base_name="schunk" ):
    """Return a path to an appropriate icon for this application and OS.
    
    \param icon_dir - a directory where the icon(s) are stored. 
           The default None makes this function use the directory of the current application.
    \param icon_base_name - the base name of the icon without path prefix or file type suffix.
    
    \return
    - For windows "icon_dir\icon_base_name.ico" will be returned if it exists.
    - For linux  "@icon_dir\icon_base_name.xbm" will be returned if it exists.
    If the file does not exist then None is returned.
    This way the result can be given directly to wm_iconbitmap(sdh.GetIconPath()) from Tkinter.Tk()
    In recent (ca since spring 2012) tkinter on cygwin icons do not work any more. Background: X11 
    is needed (native windows tkinter does not work any more from python.  
    """        
    if ( icon_dir is None ):
        icon_dir = os.path.split( sys.argv[0] )[0]
    if ( "linux" in sys.platform ):
        icon_path = os.path.join( icon_dir, icon_base_name + ".xbm" )
        icon = "@" + icon_path
    else:
        icon_path = os.path.join( icon_dir, icon_base_name + ".ico" )
        icon = icon_path
    if os.path.exists(icon_path):
        return icon
    return None

#---------------------------------------------------------------------
def PrettyStruct( name, s, exclude=None ):
    '''Return a string containing the name and the content of the structure s.
    s must be a struct or dictionary like object. For every element in s
    the key name and the value of the element is printed on one line,
    except for elements listed in list \a exclude.   
    '''    
    result = "%s:\n" % name
    if ( exclude is None ):
        exclude = []
    for (k, v) in vars(s).items():
        if ( k not in exclude ):
            result += "%20s = %s\n" % (k, str(v))
    return result
#---------------------------------------------------------------------

def NumerifyRelease( rev ):
    '''return a list of integer numbers for a release string \a 
    \param rev release string like "0.0.1.11-a"
    \return a list of integer numbers like [0,0,1,11,1]
    '''
    # remove stuff that does not carry numerical information
    if ( "-dev" in rev   or  "-2fo" in rev ):
        rev = rev[:-4]
        
    # translate "-a", "-b", ... in ".1", ".2", ... 
    rev=rev.replace("-",".")
    nums=[]
    for r in rev.split('.'):
        if r.isalpha() and r.islower:
            nums.append( (ord(r) - ord('a')+1) )
        elif r.isalpha() and r.isupper:
            nums.append( (ord(r) - ord('A')+1) )
        else:
            nums.append( int(r) )
    return nums

def CompareReleases( rev1, rev2 ):
    '''compare release strings \a rev1 and \a rev2.
    \return -1,0, or 1 if \a rev1 is older, equal or newer than \a rev2
    
    \param rev1 - a release string like "0.0.1.5" or "0.0.1.11-a
    \param rev2 - another release string
    
    Example: 
    - CompareReleases( "0.0.1.5", "0.0.1.5" )   ==>  0
    - CompareReleases( "0.0.1.5", "0.0.1.4" )   ==>  1
    - CompareReleases( "0.0.1.5", "0.0.2.1" )   ==> -1 
    - CompareReleases( "0.0.1.5", "0.0.1.5-a" ) ==> -1 
    '''
    nums1 = NumerifyRelease( rev1)
    nums2 = NumerifyRelease( rev2 )
    for (n1,n2) in zip(nums1,nums2 ):
        if ( n1 < n2 ):
            return -1
        elif ( n1 > n2 ):
            return 1
    
    # elements existing in both lists are all the same
    if ( len(nums1) < len(nums2) ):
        return -1
    if ( len(nums1) > len(nums2) ):
        return 1
    return 0
           
#---------------------------------------------------------------------
    
#
######################################################################

#  end of doxygen name group sdhlibrary_python_auxiliary_py_auxiliary
## @}
