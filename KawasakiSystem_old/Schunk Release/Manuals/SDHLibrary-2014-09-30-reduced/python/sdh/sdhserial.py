# -*- coding: latin-1 -*-
#######################################################################
#
## \file
#  \section sdhlibrary_python_sdhserial_py_general General file information
#
#    \author   Dirk Osswald
#    \date     2007-06-13
#
#  \brief  
#    Implementation of class to access SDH via RS232
#
#  \section sdhlibrary_python_sdhserial_py_copyright Copyright
#
#  Copyright (c) 2007 SCHUNK GmbH & Co. KG
#
#  <HR>
#  \internal
#
#    \subsection sdhlibrary_python_sdhserial_py_details SVN related, detailed file specific information:
#      $LastChangedBy: Osswald2 $
#      $LastChangedDate: 2014-02-28 15:24:55 +0100 (Fri, 28 Feb 2014) $
#      \par SVN file revision:
#        $Id: sdhserial.py 11438 2014-02-28 14:24:55Z Osswald2 $
#
#  \subsection sdhlibrary_python_sdhserial_py_changelog Changelog of this file:
#      \include sdhserial.py.log
#
#######################################################################

import time, sys, re

# pySerial module from http://pyserial.sourceforge.net/
import serial

from sdhbase import *
import socket

# Try to import sdh.canserial: Will only work: 
# - if using native windows python (not cygwin)
# - if using ESD CAN
# - if the ESD python wrapper is installed
try:
    from . import canserial
except ImportError:
    pass
    
from . import tcpserial
    
#######################################################################
## \anchor sdhlibrary_python_sdhserial_py_python_vars
#  \name   Python specific variables
#  
#  Some definitions that describe the module for python.
#
#  @{

__doc__       = "Class to access SDH via RS232"
__author__    = "Dirk Osswald: dirk.osswald@de.schunk.com"
__url__       = "http://www.schunk.com"
__version__   = "$Id: sdhserial.py 11438 2014-02-28 14:24:55Z Osswald2 $"
__copyright__ = "Copyright (c) 2007 SCHUNK GmbH & Co. KG"

#  end of doxygen name group sdhlibrary_python_sdhserial_py_python_vars
#  @}
######################################################################

#-----------------------------------------------------------------
## \brief The class to communicate with a SDH via RS232.
#    
#  End-Users should \b NOT use this class directly! The interface
#  of cSDHSerial is subject to change in future releases. End users
#  should use the class cSDH instead, as that interface is considered
#  more stable.
#
#  <hr>
class cSDHSerial( cSDHBase ):
    '''
    The class to communicate with a SDH via RS232. See html/pdf documentation for details.
    
    \bug  SCHUNK-internal bugzilla ID: Bug 1517<br>
      With SDH firmware 0.0.3.x the first connection to a newly
      powered up SDH can yield an error especially when connecting via TCP.
      <br><b>=> Resolved in SDHLibrary-python 0.0.2.8</b>
    '''
    ##################################################################
    ## \anchor sdhlibrary_python_csdhserial_internal
    #  \name   Internal methods
    #  
    #  @{

    #-----------------------------------------------------------------
    ## \brief Constructor of cSDHSerial.
    #
    #  - Open the serial port
    #  - Check connection to SDH by querying the SDH firmware version
    #  
    # This may raise an exception on failure
    #
    #  \param self    - reference to the object itself
    #  \param options - a dictionary of additional settings,  like the
    #                   options.__dict__ returned from cSDHOptionParser.parse_args()
    #  - Settings used by the base class cSDHBase:
    #    - \c "debug_level" : if set, then it is used as debug level of
    #                         the created object, else a default of 0 is used
    #  - Settings used by this cSDHSerial class:                             
    #    - \c "port":         if set, then it is used as the port number or the device name of
    #                         the serial port to use. The default
    #                         value port=0 refers to 'COM1' in Windows and
    #                         to the corresponding '/dev/ttyS0' in Linux.
    #    - \c "timeout"     : the timeout to use:
    #                         - None : wait forever
    #                         - T    : wait for T seconds (float accepted)                   
    #  - (Superclasses of cSDHSerial use additional settings, see there.)
    #  - (Using classes of cSDHSerial like cSDH use additional settings, see there.)
    #
    #  <hr>                 
    def __init__( self, options=None ):
        '''
        Constructor of cSDHSerial. See html/pdf documentation for details.
        '''
        #---------------------
        # Option handling: 

        # Set class specific default options:
        default_options = dict( port=0, timeout=None )

        # Overwrite class specific defaults with settings from caller, if any:
        if ( options ):   default_options.update( options )
        #---------------------
                    
        # Call base class constructor using default + user options:
        cSDHBase.__init__( self, options=default_options )
        

        # use green as color for messages from cSDHSerial
        self.dbg.SetColor( "green" ) 
        self.dbg.PDM( "Debug messages of cSDHSerial are printed like this." )

        #---------------------
        # initialize additional member variables:
        
        ## \brief additional time in seconds to wait for sequential
        #  execution of "m"-command (as these are always executed
        #  non-sequentially by the SDH firmware)
        #  (no longer needed since WaitAxis() is used to ensure movement has ended)
        self.m_sequtime = 0.0

        ## String to use as "End Of Line" marker when sending to SDH
        self.EOL="\r\n"
        #---------------------
        
        #---------------------
        # open connection to SDH:

        self.com = None
        
        if (self.options[ "port" ] < 0):
            # "virtual" port for offline tests
            return

        try:
            dummy = self.options[ "usecan" ]
        except KeyError:
            self.options[ "usecan" ] = False
        try:
            dummy = self.options[ "baudrate" ]
        except KeyError:
            self.options[ "baudrate" ] = 0

        if (self.options[ "usecan" ]):
            # try using CAN via ESD
            if ( not "sdh.canserial" in sys.modules ):
                print "Importing sdh.canserial failed! Is this Winpython calling? If you want CAN try:"
                cmdline = ""
                for a in sys.argv:
                    cmdline += " " + a
                print "pythonwin %s" % cmdline
                print
                raise ImportError
                
            if ( self.options[ "baudrate" ] == 0 ):
                self.options[ "baudrate" ] = 1000000
            self.com = canserial.tCANSerial( self.options[ "id_read" ], self.options[ "id_write" ], self.options[ "baudrate" ], self.options[ "net" ], timeout=self.options[ "timeout" ] )
            self.dbg.PDM( "Using (ESD) CAN, id_read=0x%03x, id_write=0x%03x baudrate=%d timeout=%r" % (self.options[ "id_read" ], self.options[ "id_write" ], self.options[ "baudrate" ], self.options["timeout"]) )
            sys.stdout.flush()
        elif ( self.options[ "usetcp" ] ):
            self.dbg.PDM( "Using TCP/IP to %s:%d with timeout %r" % (self.options[ "tcp_adr" ], self.options[ "tcp_port" ], self.options["timeout"]) )
            self.com = tcpserial.tTCPSerial( self.options[ "tcp_adr" ], self.options[ "tcp_port" ] )
            sys.stdout.flush()
        else:
            if ( self.options[ "baudrate" ] == 0 ):
                self.options[ "baudrate" ] = 115200

            ## the RS232 connection to use for communication
            self.com = serial.Serial( port=self.options[ "port" ], baudrate=self.options[ "baudrate" ], rtscts=0, xonxoff=0, timeout=self.options[ "timeout" ] )
            # the above call will succeed even if the hand is connected but off

        # to make shure that the SDH is connected:
        # try to get the SDH firmware version with timeout
        old_timeout = self.com.timeout
        #print "cSDHSerial.__init__, modifying self.com.timeout"
        self.com.timeout = 1
        
        try:
            self.com.write( " " )  # empty command to terminate any potential partly received previous command
        except cSDHErrorCommunication, e:
            self.dbg << "caught <%s> (ignored while cleaning up communication 1)\n" % str(e);

        try:
            # Now try to read anything available.
            # This is only necessary if the SDH with a debug firmware (like
            # all v0.0.3.x releases) has been switched on recently and we are
            # communicating via TCP (since the TCP stack on the SDH buffers the
            # debug start messages forever).
            # In all other cases this does no harm other than a small delay.
            dummy = self.com.read( 1024 );
            self.dbg << "Read and ignored %d bytes \"%s\"\n" % (len(dummy),dummy)
            self.dbg.flush()
        except socket.timeout, e:
            self.dbg << "caught <%s> (ignored while cleaning up communication 2)\n" % str(e);
        except cSDHErrorCommunication, e:
            self.dbg << "caught <%s> (ignored while cleaning up communication 2)\n" % str(e);
    
        #---------------------
        
        try:
            #self.Send( "ver" )
            ver = self.ver()
            if ( ver == "" ):
                raise cSDHErrorCommunication( "Could not get version info from SDH. Either it is switched off or not connected to selected port." )
        except IndexError, e:
            if (self.options[ "usecan" ]):
                raise cSDHErrorTimeout( "Error while opening ESD CAN interface on net %d: %s" % (self.options[ "net" ], str(e)) )
            else:
                raise cSDHErrorTimeout( "Timeout while opening port %r" % self.options[ "port" ] )

        self.com.timeout = old_timeout
        #---------------------
        
        
    #-----------------------------------------------------------------
    def Close( self ):
        '''
        Close connection to serial interface.
        '''
        if self.com:
            self.com.close()
        self.com = None
    #-----------------------------------------------------------------

    def SendParse( self, s, re_obj ):
        '''
        Simplified parsing of 1 line commands.
        s is the command to send
        re_obj is a compiled regular expression object
        the reply for s from the SDH is matched against re_obj
        and the group 1 of the resulting match object is returned.
        In case of errors the procedure is repeated up to 3 times
        after syncing the output
        '''
        self.dbg << "Sendparse( %s, %s )\n" % (repr(s), repr(re_obj.pattern))  # pylint: disable-msg=W0104
        retries = 3 # retry sending at most this many times
        while retries > 0:
            reply=None
            try:
                reply = self.Send( s, 1 )
                mo = re_obj.match( reply[0] )
                if ( mo ):
                    return mo.group(1)
            except cSDHErrorCommunication,e:
                self.dbg << "Ignoring exception in SendParse: %r\n" % e # pylint: disable-msg=W0104
            retries -= 1
            if retries> 0:
                self.dbg << "reply %s from SDH does not match, syncing and retrying\n" % (repr(reply))  # pylint: disable-msg=W0104
            old_nb_lines_to_ignore = self.nb_lines_to_ignore
            self.nb_lines_to_ignore = 5
            self.Sync()
            self.nb_lines_to_ignore = old_nb_lines_to_ignore
                
        raise cSDHErrorCommunication( "Could not get matching reply in SendParse( '%s', '%s' )" % (s,re_obj.pattern) )
         

    #-----------------------------------------------------------------
    def Send( self, s, nb_lines=All, nb_lines_total=All ):
        '''
        Send command string s+EOL to self.com and read reply according to nb_lines.

        If nb_lines == All then reply lines are read until a line
        without "@" prefix is found.
        If nb_lines != All it is the number of lines to read.

        self.firmware_state is set according to reply (if read)
        nb_lines_total contains the total number of lines replied for
        the s command. If fewer lines are read then
        nb_lines_total-nb_lines will be remembered to be ignored
        before the next command can be sent.
        
        Return a list of all read lines of the reply from the SDH hardware.
        '''

        if (self.options[ "port" ] < 0):
            # "virtual" port for offline tests

            for (request,answer) in [ ("power=0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000", "POWER=0.0,0.0,0.0,0.0,0.0,0.0,0.0"),
                                      ("vp", ["@bla", "VP=0"]),
                                      ("p_max", ["P_MAX=90.0,90.0,90.0,90.0,90.0,90.0,90.0"]),
                                      ("p_min", ["P_MIN=0.0,-90.0,-90.0,-90.0,-90.0,-90.0,-90.0"]),
                                      ("vlim", ["VLIM=83,140,200,140,200,140,200"]),
                                      ("ver",  ["VER=0.0.0.0"]),
                                      ]:
                if (s == request):
                    self.dbg << "!!! Virtual COM port, faking reply '%s' for request '%s'\n" % (answer,request) # pylint: disable-msg=W0104
                    return answer
              
            self.dbg << "!!! Virtual COM port, ignoring '%s'\n" % s # pylint: disable-msg=W0104
            return []

        retries = 3 # retry sending at most this many times
        while retries > 0:
            try:
                #---------------------
                # first read all lines to ignore (replies of previous commands)
                while ( self.nb_lines_to_ignore > 0 ):
                    l = self.com.readline()
                    self.nb_lines_to_ignore -= 1
                    self.dbg.PDM( "ignoring line", l )
                #---------------------
                
                self.firmware_state = self.eErrorCode[ "E_SUCCESS" ]
                lines = []
                
                #---------------------
                # send new command to SDH
                self.dbg.PDM( "sending command "+repr(s+self.EOL)+" to SDH" )
                self.dbg.PDM( "nb_lines=", nb_lines, "  nb_lines_total=", nb_lines_total, "  self.nb_lines_to_ignore=", self.nb_lines_to_ignore )
                self.com.write(s+self.EOL)
                #---------------------
                
                #---------------------
                # read reply if requested
                while (nb_lines == All or nb_lines > 0):
                
                    #---------------------
                    # now read requested reply lines of current command
                    l = self.com.readline()
                    if (nb_lines != All):
                        nb_lines -= 1
                    if (nb_lines_total != All):
                        nb_lines_total -= 1
                
                    # append line l without beginning or trailing "\r\n" to lines list
                    start = 0
                    while (start < len(l)  and  l[start] in ('\r', '\n')):
                        start += 1
                
                    end = len(l)-1
                    while (end > 0         and  l[end] in ('\r', '\n')):
                        end -= 1
                    lines.append( l[start:end+1] )
                    self.dbg.PDM( "appended '%s' for l='%s'" %(lines[-1],l) )
                    if (len(lines[-1])>0 and lines[-1][0] != '@'): # ??? or better and (nb_lines != All and nb_lines <= 0)
                        break
                    if ( len(lines[-1]) == 0 ):
                        self.dbg << "breaking for empty line\n" # pylint: disable-msg=W0104
                        break  # !!! needed, but why????
                    self.dbg << "not breaking for line '%s'\n" % l # pylint: disable-msg=W0104
                    sys.stdout.flush()
                    sys.stderr.flush()
                    #---------------------
                sys.stdout.flush()
                sys.stderr.flush()
                
                #---------------------
                # remember if there are more lines to be ignored next time
                if (nb_lines_total != All):
                    self.nb_lines_to_ignore = nb_lines_total
                self.dbg.PDM( "%d lines remain to be ignored" % self.nb_lines_to_ignore )
                #---------------------
                
                #---------------------
                # set state if possible
                if (self.nb_lines_to_ignore == 0):
                    self.ExtractFirmwareState( lines )
                #---------------------

                # finished, so no more retries needed
                retries = 0
                
            except cSDHErrorCommunication, e:
                # some communication error occured, so retry:
                retries -= 1
                if (retries <= 0):
                    self.dbg << "Retried sending, but still got errors from SDH!\n" # pylint: disable-msg=W0104
                    # reraise e:
                    raise 
                
                self.dbg << "ignoring cSDHErrorCommunication:", e, "\n" # pylint: disable-msg=W0104

                # resync first:
                self.Sync()
                # now start over again

        self.dbg << "got reply:\n" # pylint: disable-msg=W0104
        self.dbg.SetColor( "blue" ) 
        for (i,l) in zip(range(0,len(lines)),lines):
            self.dbg << "%2d: " % i << repr( l ) << "\n" # pylint: disable-msg=W0104
        self.dbg.SetColor( "green" ) 
        return lines

    #-----------------------------------------------------------------
    def ExtractFirmwareState( self, lines ):
        '''
        Try to extract the state of the SDH firmware from the lines reply
        '''
        #---------------------
        # check first char of last line of lines
        if   (lines == []):
            raise cSDHErrorCommunication( "Cannot get SDH firmware state from empty lines" )
        elif (lines[-1] == ""):
            raise cSDHErrorCommunication( "Cannot get SDH firmware state from empty line" )
        elif (lines[-1][0] == 'E'):
            # it is an error message:
            self.firmware_state = int(lines[-1][1:])
            self.dbg.PDM( "got error reply '%s' = %d = %s" % (lines[-1], self.firmware_state, self.firmware_error_codes[self.firmware_state]) )
            raise cSDHErrorInvalidParameter( "SDH firmware reports error %d = %s" % (self.firmware_state, self.firmware_error_codes[self.firmware_state])  )

        elif (lines[-1][0] == '@'):
            # it is an debug message (should not happen):
            raise cSDHErrorCommunication( "Cannot get SDH firmware state from lines %r" % lines )

        else:
            # it is a normal "command completed" line:
            self.firmware_state = self.eErrorCode[ "E_SUCCESS" ]

    #-----------------------------------------------------------------
    def GetDuration( self, line ):
        '''
        Return duration of the execution of a SDH command as reported by line
        '''
        m = self.re_get_T.match( line )
        if (m is None):
            raise cSDHErrorCommunication( "Could not extract duration from lines '%s'" % (line) )
        
        return float( m.group(1) )
    
    #-----------------------------------------------------------------
    def Sync( self ):
        '''
        Read all pending lines from SDH to resync execution of PC and SDH.
        '''
        lines = []
        # read all lines to ignore (replies of previous commands)
        while ( self.nb_lines_to_ignore > 0 ):
            l = self.com.readline()
            
            self.nb_lines_to_ignore -= 1
            self.dbg.PDM( "syncing: ignoring line %r" % l )

            # append line l without trailing "\n\r" to lines list
            if (len(l) > 2):
                lines.append( l[:-2] )
        #---------------------
        if (lines != []):
            try:
                self.ExtractFirmwareState( lines )
            except cSDHErrorCommunication,e:
                self.dbg.PDM( "syncing: ignoring error from ExtractFirmwareState (%r)", e  )

    #-----------------------------------------------------------------
    def AxisCommand( self, command, axis=All, value=None ):
        '''
        Get/Set values.

        - If axis is All and value is None then a
          NUMBER_OF_AXES-list of the current values
          read from the SDH is returned
        - If axis is a single number and value is None then the
          current value for that axis is read from the SDH and is returned
        - If axis and value are single numbers then that value
          is set for that axis and returned.
        - If axis is All and value is a NUMBER_OF_AXES-vector then all axes
          values are set accordingly, a NUMBER_OF_AXES-list is returned.
        '''
        #cutoff  = len( command ) + 1
        #cutoff1 = len( command ) + 4
        cmd_answer = command.upper()
        retries = 3 # retry sending at most this many times
        while (retries > 0):
            try:

                if (type(axis) == int):
                    self.CheckIndex( axis, self.NUMBER_OF_AXES, "axis" )
                    if (value is None):
                        #reply = self.Send( "%s(%d)" % (command,axis) )
                        #return float( reply[-1][cutoff1:] )
                        answer = self.SendParse( "%s(%d)" % (command,axis), 
                                                re.compile("%s\(%d\)=([-+]?(\d+(\.\d*)?|\.\d+)?)" % (cmd_answer,axis)) )
                        return float( answer )
                    if (type(value) == int):
                        #reply = self.Send( "%s(%d)=%d" % (command,axis,value ) )
                        #return float( reply[-1][cutoff1:] )
                        answer = self.SendParse( "%s(%d)=%d" % (command,axis,value ),
                                                 re.compile("%s\(%d\)=([-+]?(\d+(\.\d*)?|\.\d+)?)" % (cmd_answer,axis)) )
                        return float( answer )
                    if (type(value) == float):
                        #reply = self.Send( "%s(%d)=%f" % (command,axis,value ) )
                        #return float( reply[-1][cutoff1:] )
                        answer = self.SendParse( "%s(%d)=%f" % (command,axis,value ),
                                                 re.compile("%s\(%d\)=([-+]?(\d+(\.\d*)?|\.\d+)?)" % (cmd_answer,axis)) )       
                        return float( answer )
                
                if (axis == All):
                    if ( value is None):
                        #reply = self.Send( command )
                        #return eval( "[" + reply[-1][cutoff:] + "]" ) # this will raise an TypeError exception if not enough data was read
                        answer = self.SendParse( command,
                                                 re.compile("%s=(.*)" % (cmd_answer)) )
                        return eval( "[" + answer + "]" ) # this will raise an TypeError exception if not enough data was read  
                
                    # if a single value was given for All axes then create a list of NUMBER_OF_AXES values first:
                    if (type(value) in [int, float]):
                        value = [ value  for ai in self.all_axes ]
                
                    if ( (type(value) in self.vector_types) and len(value) == self.NUMBER_OF_AXES):
                        #reply = self.Send( "%s=%f,%f,%f,%f,%f,%f,%f" % ((command,)+tuple(value)) )
                        #self.dbg.var( "command reply cutoff" )
                        #return eval( "[" + reply[-1][cutoff:] + "]" )
                        #self.dbg.var( "command reply cutoff" )
                        #return eval( "[" + reply[-1][cutoff:] + "]" )
                        answer = self.SendParse( "%s=%f,%f,%f,%f,%f,%f,%f" % ((command,)+tuple(value)),
                                                 re.compile( "%s=(.*)" % (cmd_answer)) )
                        self.dbg.var( "command answer cmd_answer" )
                        return eval( "[" + answer + "]" )
                
                raise cSDHErrorInvalidParameter( "Invalid parameter in call' %s(axis = %s, value = %s )'" % (command, repr(axis), repr(value) ) )
            
    	    # end of try
            except TypeError,e:
                # these errors seem to happen on linux only (not cygwin) where a reply can be partly received:
        
                # assume some communication error occured, so retry:
                retries -= 1
                if (retries > 0):
                    self.dbg << "ignoring TypeError: " << e << "\n" # pylint: disable-msg=W0104
                
                # resync first:
                self.Sync()
                #now start over again
            except SyntaxError,e:
                # these errors happen on windows if CAN is used, so a reply can be partly received:
        
                # assume some communication error occured, so retry:
                retries -= 1
                if (retries > 0):
                    self.dbg << "ignoring SyntaxError: " << e << "\n" # pylint: disable-msg=W0104
                
                # resync first:
                self.Sync()
                #now start over again
        
        
            # end of except
        
        # end of while (retries > 0) 
        
        self.dbg << "Retried sending, but still got errors from SDH!\n" # pylint: disable-msg=W0104
        # reraise e:
        raise 


    #  end of doxygen name group sdhlibrary_python_csdhserial_internal
    ## @}
    ##################################################################

    ##################################################################
    ## \anchor sdhlibrary_python_csdhserial_setup_commands
    #  \name   Setup and configuration methods
    #  @{

    #-----------------------------------------------------------------
    def pid( self, axis, p=None, i=None, d=None ):
        '''
        Get/Set PID controller parameters

        - axis must be a single number: the index of the axis to get/set
        - If p,i,d are None then a list of the currently
          set PID controller parameters of the axis is returned
        - If p,i,d are numbers then the PID controller parameters for
          that axis are set (and returned).

        \bug With SDH firmware 0.0.2.9 pid() might not respond
             pid values correctly in case these were changed before.
             With SDH firmwares 0.0.2.10 and newer this now works.
             <br><b>=> Resolved in SDH firmware 0.0.2.10</b>
        '''
        self.CheckIndex( axis, self.NUMBER_OF_AXES, "axis" )

        if (p is None and i is None and d is None):
            reply = self.Send( "pid(%d)" % (axis) )
            return eval( "[" + reply[0][7:] + "]" )
        if (type(p) in (int,float) and type(i) in (int,float) and type(d) in (int,float)):
            reply = self.Send( "pid(%d)=%f,%f,%f" % (axis,p,i,d) )
            return eval( "[" + reply[0][7:] + "]" )

        raise cSDHErrorInvalidParameter( "Invalid parameter in call' pid(axis=%s, p=%s, i=%s, d=%s )'" % (repr(axis), repr(p),repr(i), repr(d)) )

    #-----------------------------------------------------------------
    def kv( self, axis=All, kv=None ):
        '''
        Get/Set kv parameter 
        
        - If axis is All and kv is None then a
          NUMBER_OF_AXES-list of the currently set kv parameters is returned
        - If axis is a single number and kv is None then the
          kv parameter for that axis is returned.
        - If axis and kv are single numbers then the kv parameter
          for that axis is set (and returned).
        - If axis is All and kv is a NUMBER_OF_AXES-vector then all axes
          kv parameters are set accordingly, NUMBER_OF_AXES-list is returned.

        \bug With SDH firmware 0.0.2.9 kv() might not respond
             kv value correctly in case it was changed before.
             With SDH firmwares 0.0.2.10 and newer this now works.
             <br><b>=> Resolved in SDH firmware 0.0.2.10</b>
        '''

        if axis == All:
            # SDH firmware cannot handle setting / getting all values at once
            # so emulate that
            if kv is None:
                return [ self.AxisCommand( "kv", a, None )   for a in self.all_axes ]

            if (type( kv ) in self.vector_types and len(kv) == self.NUMBER_OF_AXES):
                return [ self.AxisCommand( "kv", a, kv[a] )   for a in self.all_axes ]

            raise cSDHErrorInvalidParameter( "Invalid parameter in call 'kv( axis=%s, kv=%s )'" % (repr(axis), repr(kv)) )
        else:
            return self.AxisCommand( "kv", axis, kv )

    #-----------------------------------------------------------------
    def ilim( self, axis=All, limit=None ):
        '''
        Get/Set current limit for m command
        
        - If axis is All and limit is None then a NUMBER_OF_AXES-list
          of the currently set current limits is returned
        - If axis is a single number and limit is None then the
          current limit for that axis is returned.
        - If axis and limit are single numbers then the current limit
          for that axis is set (and returned).
        - If axis is All and limit is a NUMBER_OF_AXES-vector then
          all axes current limits are set accordingly, the NUMBER_OF_AXES-list is returned.
        '''
        return self.AxisCommand( "ilim", axis, limit )

    #-----------------------------------------------------------------
    def power( self, axis=All, flag=None ):
        '''
        Get/Set current power state
        
        - If axis is All and flag is None then a NUMBER_OF_AXES-list
          of the currently set power states is returned
        - If axis is a single number and flag is None then the
          power state for that axis is returned.
        - If axis is a single number and flag is a single number or a
          boolean value then the power state
          for that axis is set (and returned).
        - If axis is All and flag is a NUMBER_OF_AXES-vector then all axes
          power states are set accordingly, the NUMBER_OF_AXES-list is returned.
        - If axis is All and flag is a a single number or a boolean
          value then all axes power states are set to that value, the
          NUMBER_OF_AXES-list is returned.
        '''
        # Actual input/output for the command looks like:
        #--
        # power=0,0,0,0,0,0,0
        # POWER=0,0,0,0,0,0,0

        if ( axis == All  and  type(flag) in (int, bool) ):
            if (flag):
                flag = [ 1   for i in self.all_axes ]
            else:
                flag = [ 0   for i in self.all_axes ]

        elif ( type(flag) in self.vector_types ):
            # make flag a vector of ints (not vector of bools)
            flag = map( int, flag )
        if ( type(flag) == bool ):
            # make flag an int (not bool)
            flag = int( flag )

        rc = self.AxisCommand( "power", axis, flag )
        if (type(axis) == int):
            return int( rc )
        return rc

    #  end of doxygen name group sdhlibrary_python_csdhserial_setup_commands
    ## @}
    ##################################################################


    ##################################################################
    ## \anchor sdhlibrary_python_csdhserial_misc_commands
    #  \name   Misc. methods
    #  @{

    #-----------------------------------------------------------------
    def demo( self, onoff ):
        '''
        Enable/disable SCHUNK demo
        '''
        return self.Send( "demo=%d" % onoff )

    #-----------------------------------------------------------------
    def property( self, propname, value ):
        '''
        Set named property

        Valid propnames are:
        - "user_errors"
        - "terminal"
        - "debug"
        '''

        reply = self.Send( "%s=%d" % (propname, value) )
        return int( reply[0][len(propname):] )

    #-----------------------------------------------------------------
    def user_errors( self, value ):
        '''
        '''
        return self.property( "user_errors", value )
                       
    #-----------------------------------------------------------------
    def terminal( self, value ):
        '''
        '''
        return self.property( "terminal", value )
                       
    #-----------------------------------------------------------------
    def debug( self, value ):
        '''
        '''
        return self.property( "debug", value )
                       
    
    #  end of doxygen name group sdhlibrary_python_csdhserial_misc_commands
    ## @}
    ##################################################################

    ##################################################################
    ## \anchor sdhlibrary_python_csdhserial_movement_commands
    #  \name   Movement methods
    #  @{

    #-----------------------------------------------------------------
    def v( self, axis=All, velocity=None ):
        '''
        Get/Set target velocity. (NOT the current velocity!)

        The default velocity set on power on is 40 deg/s.
        
        - If axis is All and velocity is None then a NUMBER_OF_AXES-list
          of the currently set target velocities is returned
        - If axis is a single number and velocity is None then the
          target velocity for that axis is returned.
        - If axis and velocity are single numbers then the target
          velocity for that axis is set (and returned).
        - If axis is All and velocity is a NUMBER_OF_AXES-vector
          then all axes target velocities are set accordingly, the NUMBER_OF_AXES-list
          is returned.

        Velocities are set/reported in degrees per second. 
        '''
        if (type( velocity ) in (int, float)):
            if axis == All:
                for a in self.all_axes:
                    self.CheckRange( velocity, self.min_angular_velocity_a[a], self.max_angular_velocity_a[a], "axis %s velocity" % (repr(a)) )
            else:               
                self.CheckRange( velocity, self.min_angular_velocity_a[axis], self.max_angular_velocity_a[axis], "axis %s velocity" % (repr(axis)) )

        elif (type( velocity ) in self.vector_types):
            self.CheckRange( velocity, self.min_angular_velocity_a, self.max_angular_velocity_a, "axis velocity" )
            
        return self.AxisCommand( "v", axis, velocity )


    #-----------------------------------------------------------------
    def vlim( self, axis=All ):
        '''
        Get velocity limits.

        - If axis is All then a NUMBER_OF_AXES-list
          of the velocity limits is returned
        - If axis is a single number then the
          velocity limit for that axis is returned.

        Velocity limits are reported in degrees per second. 
        '''
        return self.AxisCommand( "vlim", axis, None )


    #-----------------------------------------------------------------
    def alim( self, axis=All ):
        '''
        Get acceleration limits.

        - If axis is All then a NUMBER_OF_AXES-list
          of the acceleration limits is returned
        - If axis is a single number then the
          acceleration limit for that axis is returned.

        Acceleration limits are reported in degrees per (second*second). 
        '''
        return self.AxisCommand( "alim", axis, None )


    #-----------------------------------------------------------------
    def a( self, axis=All, acceleration=None ):
        '''
        Get/Set target acceleration. (NOT the current acceleration!)

        The default acceleration set on power on is 100 deg/(s*s).
        
        - If axis is All and acceleration is None then a NUMBER_OF_AXES-list
          of the currently set target accelerations is returned
        - If axis is a single number and acceleration is None then the
          target acceleration for that axis is returned.
        - If axis and acceleration are single numbers then the target
          acceleration for that axis is set (and returned).
        - If axis is All and acceleration is a NUMBER_OF_AXES-vector
          then all axes target accelerations are set accordingly, the NUMBER_OF_AXES-list
          is returned.

        Accelerations are set/reported in degrees per (second*second). 
        '''
        if (type( acceleration ) in (int, float)):
            if axis == All:
                for a in self.all_axes:
                    self.CheckRange( acceleration, self.min_angular_acceleration_a[a], self.max_angular_acceleration_a[a], "axis %s acceleration" % (repr(a)) )
            else:               
                self.CheckRange( acceleration, self.min_angular_acceleration_a[axis], self.max_angular_acceleration_a[axis], "axis %s acceleration" % (repr(axis)) )

        elif (type( acceleration ) in self.vector_types):
            self.CheckRange( acceleration, self.min_angular_acceleration_a, self.max_angular_acceleration_a, "axis acceleration" )
            
        return self.AxisCommand( "a", axis, acceleration )


    #-----------------------------------------------------------------
    def p( self, axis=All, angle=None ):
        '''
        Get/Set target angle for axis. (NOT the current angle!)

        - If axis is All and angle is None then a NUMBER_OF_AXES-list
          of the currently set target angles is returned
        - If axis is a single number and angle is None then the
          target angle for that axis is returned.
        - If axis and angle are single numbers then the target
          angle for that axis is set (and returned).
        - If axis is All and angle is a NUMBER_OF_AXES-vector
          then all axes target angles are set accordingly, the NUMBER_OF_AXES-list
          is returned.

        Angles are set/reported in degrees. 
        '''
        if (type( angle ) in (int, float)):
            if axis == All:
                for a in self.all_axes:
                    self.CheckRange( angle, self.min_angle_a[a], self.max_angle_a[a], "axis %s angle" % (repr(a)) )
            else:   
                self.CheckRange( angle, self.min_angle_a[axis], self.max_angle_a[axis], "axis %d angle" % axis )

        elif (type( angle ) in self.vector_types):
            self.CheckRange( angle, self.min_angle_a, self.max_angle_a, "axis angle" )
            
        return self.AxisCommand( "p", axis, angle )

    #-----------------------------------------------------------------
    def tpap( self, axis=All, angle=None ):
        '''
        Set target angle, get actual angle for axis. 

        - If axis is All and angle is None then a NUMBER_OF_AXES-list
          of the currently set target angles is returned
        - If axis is a single number and angle is None then the
          actual angle for that axis is returned.
        - If axis and angle are single numbers then the target
          angle for that axis is set (and actual angle returned).
        - If axis is All and angle is a NUMBER_OF_AXES-vector
          then all axes target angles are set accordingly, the NUMBER_OF_AXES-list
          of actual angles is returned.

        Angles are set/reported in degrees. 
        '''
        if (type( angle ) in (int, float)):
            if axis == All:
                for a in self.all_axes:
                    self.CheckRange( angle, self.min_angle_a[a], self.max_angle_a[a], "axis %s angle" % (repr(a)) )
            else:   
                self.CheckRange( angle, self.min_angle_a[axis], self.max_angle_a[axis], "axis %d angle" % axis )

        elif (type( angle ) in self.vector_types):
            self.CheckRange( angle, self.min_angle_a, self.max_angle_a, "axis angle" )
            
        return self.AxisCommand( "tpap", axis, angle )

    #-----------------------------------------------------------------
    def tvav( self, axis=All, velocity=None ):
        '''
        Set target velocity, get actual velocity for axis. 

        - If axis is All and velocity is None then a NUMBER_OF_AXES-list
          of the currently set target velocities is returned
        - If axis is a single number and velocity is None then the
          actual velocity for that axis is returned.
        - If axis and velocity are single numbers then the target
          velocity for that axis is set (and actual velocity returned).
        - If axis is All and velocity is a NUMBER_OF_AXES-vector
          then all axes target velocities are set accordingly, the NUMBER_OF_AXES-list
          of actual velocities is returned.

        Angles are set/reported in degrees. 
        '''
        if (type( velocity ) in (int, float)):
            if axis == All:
                for a in self.all_axes:
                    self.CheckRange( velocity, self.min_angular_velocity_a[a], self.max_angular_velocity_a[a], "axis %s velocity" % (repr(a)) )
            else:   
                self.CheckRange( velocity, self.min_angular_velocity_a[axis], self.max_angular_velocity_a[axis], "axis %d velocity" % axis )

        elif (type( velocity ) in self.vector_types):
            self.CheckRange( velocity, self.min_angular_velocity_a, self.max_angular_velocity_a, "axis velocity" )
            
        return self.AxisCommand( "tvav", axis, velocity )

    #-----------------------------------------------------------------
    def m( self, sequ ):
        '''
        Send move command. Moves all enabled axes to their previously
        set target angle. The movement duration is determined by
        that axis that takes longest with its currently set velocity.
        The actual velocity of all other axes is set so that all axes
        begin and end their movements synchronously.

        If sequ is True then wait until SDH hardware fully executed
        the command.  Else return immediately and do not wait until SDH
        hardware fully executed the command.

        return the expected duration of the execution of the command in seconds
        '''
        # Actual input/output for the command looks like:
        #--
        # m
        # M=4.51s
        #
        # Before firmware 0.0.3.1 actual input/output for the command looked like:
        #--
        # m
        # @Enabling all axis
        # @max distance=45.06, T=4.51s, num_points: 451
        # m

        #---------------------
        # settings for sequ/non-sequ:
        nb_lines_total = 1
        nb_lines = nb_lines_total
        #---------------------
        
        #---------------------
        # send command and parse reply    
        reply = self.Send( "m", nb_lines, nb_lines_total )


        T = self.GetDuration( reply[0] )
        #---------------------

        # the SDH firmware does NOT produce an output after the command has finished
        if sequ:
            time.sleep( T+self.m_sequtime )
            
        return T

    #-----------------------------------------------------------------
    def get_duration( self ):
        '''
        Send get_duration command. Returns the calculated duration of the 
        currently configured movement (target positions, velocities, 
        accelerations and velocity profile.

        return the expected duration of the execution of the command in seconds
        '''
        # Actual input/output for the command looks like:
        #--
        # get_duration
        # GET_DURATION=4.51
        #
        # Before firmware 0.0.3.1 actual input/output for the command looked like:
        #--
        # get_duration
        # @max distance=45.06, T=4.51s, num_points: 451
        # GET_DURATION=4.51

        #---------------------
        # settings for sequ/non-sequ:
        nb_lines_total = 1
        nb_lines = nb_lines_total
        #---------------------
        
        #---------------------
        # send command and parse reply    
        reply = self.Send( "get_duration", nb_lines, nb_lines_total )
        T = self.GetDuration( reply[0] )
        #---------------------

        return T

    #-----------------------------------------------------------------
    def stop( self ):
        '''
        Stop sdh.

        Will NOT interrupt a previous "selgrip" or "grip" command, only an "m" command!
        '''
        self.Send( "stop" )

    #-----------------------------------------------------------------
    def vp( self, velocity_profile=None ):
        '''
        Get/set velocity profile.

        If velocity_profile is None then the currently set velocity profile is
        read from the SDH firmware and returned. Else the given velocity_profile type
        is set in the SDH firmware if valid.
        '''
        if (type( velocity_profile  ) in (int, float)):
            self.CheckIndex( velocity_profile, len(self.eVelocityProfile), "velocity profile type" )
            reply = self.Send( "vp=%d" % (velocity_profile) )
            
        elif (velocity_profile is None):
            reply = self.Send( "vp" )
        else:
            raise cSDHErrorInvalidParameter( "Invalid paramter type %s for velocity_profile! (Not in [int, None])" % (type(velocity_profile)) )
        
        self.actual_vp = int( reply[-1][3:] )
        
        return self.actual_vp

    
    #-----------------------------------------------------------------
    def con( self, controller=None ):
        '''
        Get/set controller type.

        If controller is None then the currently set controller is
        read from the SDH firmware and returned. Else the given controller type
        is set in the SDH firmware if valid.
        '''
        if (type( controller  ) in (int, float)):
            self.CheckIndex( controller, len(self.eControllerType), "controller type" )
            reply = self.Send( "con=%d" % (controller) )
            
        elif (controller is None):
            reply = self.Send( "con" )
        else:
            raise cSDHErrorInvalidParameter( "Invalid paramter type %s for controller! (Not in [int, None])" % (type(controller)) )
        
        self.actual_con = int( reply[-1][4:] )
        
        return self.actual_con

    
    #  end of doxygen name group sdhlibrary_python_csdhserial_movement_commands
    ## @}
    ##################################################################

    ##################################################################
    ## \anchor sdhlibrary_python_csdhserial_diagnosis_commands
    #  \name   Diagnostic and identification methods
    #  @{
    
    #-----------------------------------------------------------------
    def pos( self, axis=All ):
        '''
        Get actual angle/s of axis/axes.

        - If axis is All then a NUMBER_OF_AXES-vector of the actual
          axis angles is returned
        - If axis is a single number then the
          actual angle of that axis is returned.

        Angles are reported in degrees. 
        '''
        return self.AxisCommand( "pos", axis )

    #-----------------------------------------------------------------
    def pos_save( self, axis=All, value=None ):
        '''
        Save actual angle/s to non volatile memory. (Usefull for axes that dont have an absolute encoder)

        - If value is None then an exception is thrown since
          this is NOT usefull if any axis has an absolute encoder that
          the LLC knows about since these positions will be invalidated at the next start
        - If axis and value are single numbers then that axis is saved.
        - If axis is All and value is a NUMBER_OF_AXES-vector
          then all axes are saved if the corresponding value is 1.
        - This will yield a E_RANGE_ERROR if any of the given values is not  0 or 1

        '''
        if ( value is None ):
            raise cSDHErrorInvalidParameter( "value may not be None for pos_save" )

        return self.AxisCommand( "pos_save", axis, value )

    #-----------------------------------------------------------------
    def ref( self, axis=All, value=None ):
        '''
        Do reference movements with selected axes. (Usefull for axes that dont have an absolute encoder)

        value must be either
        - 0 : do not reference
        - 1 : reference till mechanical block in positive direction
        - 2 : reference till mechanical block in negative direction

        - If value is None then an exception is thrown since
          this is NOT usefull here
        - If axis and value are single numbers then that axis is referenced as requested.
        - If axis is All and value is a NUMBER_OF_AXES-vector
          then all axes are referenced as requested.
        - This will yield a E_RANGE_ERROR if any of the given values is not  0 or 1 or 2

        '''
        if ( value is None ):
            raise cSDHErrorInvalidParameter( "value may not be None for ref" )
        return self.AxisCommand( "ref", axis, value )

    #-----------------------------------------------------------------
    def vel( self, axis=All ):
        '''
        Get actual angular velocity/ies of axis/axes.

        - If axis is All then a NUMBER_OF_AXES-vector of the actual
          angular velocity is returned
        - If axis is a single number then the
          actual angular velocity of that axis is returned.

        Angular velocities are reported in degrees per second. 
        '''
        return self.AxisCommand( "vel", axis )

    #-----------------------------------------------------------------
    def rvel( self, axis=All ):
        '''
        Get reference angular velocity/ies of axis/axes.

        - If axis is All then a NUMBER_OF_AXES-vector of the actual
          angular velocity is returned
        - If axis is a single number then the
          actual angular velocity of that axis is returned.

        Angular velocities are reported in degrees per second. 
        '''
        return self.AxisCommand( "rvel", axis )

    #-----------------------------------------------------------------
    def state( self, axis=All ):
        '''
        Get actual state/s of axis/axes. 

        state values are returned numerically, see eAxisState.

        - If axis is All then a NUMBER_OF_AXES-vector of the actual
          axis states is returned
        - If axis is a single number then the
          actual state of that axis is returned.
        '''
        return self.AxisCommand( "state", axis )

    #-----------------------------------------------------------------
    def temp( self ):
        '''
        Get actual temperatures of SDH. 

        Returns a list of the actual controller and driver temperature in degrees celsius.
        '''
        reply = self.Send( "temp" )
        return eval( "[" + reply[0][5:] + "]" )

    #-----------------------------------------------------------------
    def p_min( self, axis=All, angle=None ):
        '''
        Get/Set minimum allowed target angle for axis.

        - If axis is All and angle is None then a NUMBER_OF_AXES-list
          of the currently set minimum angles is returned
        - If axis is a single number and angle is None then the
          minimum angle for that axis is returned.
        - If axis and angle are single numbers then the minimum
          angle for that axis is set (and returned).
        - If axis is All and angle is a NUMBER_OF_AXES-vector
          then all axes minimum angles are set accordingly, the NUMBER_OF_AXES-list
          is returned.
        - This will yield a E_RANGE_ERROR if any of the new minimum positions
          to set is larger than the actual position or the current maximum
          position of the axis.

        Angles are set/reported in degrees. 
        '''
        if (type( angle ) in (int, float)):
            if axis == All:
                for a in self.all_axes:
                    self.CheckRange( angle, MIN_FLOAT,  min( self.pos( a ), self.p_max( a ) ), "axis %s angle" % (repr(a)) )
            else:
                self.CheckRange( angle, MIN_FLOAT, min( self.pos( axis ), self.p_max( axis ) ), "axis %d angle" % axis )

        elif (type( angle ) in self.vector_types):
            apos = self.pos( All )
            amax = self.p_max( All )
            self.CheckRange( angle, self.MIN_FLOATS, Allmin( apos, amax ), "axis angle" )
            
        return self.AxisCommand( "p_min", axis, angle )

    #-----------------------------------------------------------------
    def p_max( self, axis=All, angle=None ):
        '''
        Get/Set maximum allowed target angle for axis.

        - If axis is All and angle is None then a NUMBER_OF_AXES-list
          of the currently set maximum angles is returned
        - If axis is a single number and angle is None then the
          maximum angle for that axis is returned.
        - If axis and angle are single numbers then the maximum
          angle for that axis is set (and returned).
        - If axis is All and angle is a NUMBER_OF_AXES-vector
          then all axes maximum angles are set accordingly, the NUMBER_OF_AXES-list
          is returned.
        - This will yield a E_RANGE_ERROR if any of the new maximum positions
          to set is smaller than the actual position or the current minimum
          position of the axis.

        Angles are set/reported in degrees. 
        '''
        if (type( angle ) in (int, float)):
            if ( axis == All ):
                for a in self.all_axes:
                    self.CheckRange( angle, max( self.pos( a ), self.p_min( a ) ), MAX_FLOAT, "axis %s angle" % (repr(a)) )
            else:
                self.CheckRange( angle, max( self.pos( axis ), self.p_min( axis ) ), MAX_FLOAT, "axis %d angle" % axis )

        elif (type( angle ) in self.vector_types):
            apos = self.pos( All )
            amin = self.p_min( All )
            self.CheckRange( angle, self.MAX_FLOATS, Allmax( apos, amin ), "axis angle" )
            
        return self.AxisCommand( "p_max", axis, angle )

    #-----------------------------------------------------------------
    def p_offset( self, axis=All, angle=None ):
        '''
        Get/Set offset for axis.

        - If axis is All and angle is None then a NUMBER_OF_AXES-list
          of the currently set offset angles is returned
        - If axis is a single number and angle is None then the
          offset angle for that axis is returned.
        - If axis and angle are single numbers then the offset
          angle for that axis is set (and returned).
        - If axis is All and angle is a NUMBER_OF_AXES-vector
          then all axes offset angles are set accordingly, the NUMBER_OF_AXES-list
          is returned.

        Angles are set/reported in degrees. 
        '''
        #### ???? no range checking?
        return self.AxisCommand( "p_offset", axis, angle )

    #-----------------------------------------------------------------
    def ver( self ):
        '''
        Return version of SDH firmware
        '''
        reply = self.Send( "ver" )
        return reply[0][4:]

    def ver_date( self ):
        '''
        Return date of SDH firmware
        '''
        reply = self.Send( "ver_date" )
        return reply[0][9:]

    #-----------------------------------------------------------------
    def id( self ):
        '''
        Return id of SDH
        '''
        reply = self.Send( "id" )
        return reply[0][3:]

    #-----------------------------------------------------------------
    def sn( self ):
        '''
        Return sn of SDH
        '''
        reply = self.Send( "sn" )
        return reply[0][3:]

    #-----------------------------------------------------------------
    def soc( self ):
        '''
        Return soc of SDH
        '''
        reply = self.Send( "soc" )
        return reply[0][4:]

    #-----------------------------------------------------------------
    def soc_date( self ):
        '''
        Return soc of SDH
        '''
        reply = self.Send( "soc_date" )
        return reply[0][9:]

    #-----------------------------------------------------------------
    def numaxis( self ):
        '''
        Return number of axis of SDH
        '''
        reply = self.Send( "numaxis" )
        return int( reply[0][8:] )


    
    #  end of doxygen name group sdhlibrary_python_csdhserial_diagnosis_commands
    ## @}
    ##################################################################

    ##################################################################
    ## \anchor sdhlibrary_python_csdhserial_grip_commands
    #  \name   Grip methods
    #  @{

    #-----------------------------------------------------------------
    def igrip( self, axis=All, limit=None ):
        '''
        Get/Set motor current limits for grip commands
        
        - If axis is All and limit is None then a NUMBER_OF_AXES-list
          of the currently set current limits is returned
        - If axis is a single number and limit is None then the
          current limit for that axis is returned.
        - If axis and limit are single numbers then the current limit
          for that axis is set (and returned).
        - If axis is All and limit is a NUMBER_OF_AXES-vector then all axes
          current limits are set accordingly, the NUMBER_OF_AXES-list is returned.
        '''
        return self.AxisCommand( "igrip", axis, limit )

    #-----------------------------------------------------------------
    def ihold( self, axis=All, limit=None ):
        '''
        Get/Set motor current limits for hold commands
        
        - If axis is All and limit is None then a NUMBER_OF_AXES-list
          of the currently set current limits is returned
        - If axis is a single number and limit is None then the
          current limit for that axis is returned.
        - If axis and limit are single numbers then the current limit
          for that axis is set (and returned).
        - If axis is All and limit is a NUMBER_OF_AXES-vector then all axes
          current limits are set accordingly, the NUMBER_OF_AXES-list is returned.
        '''
        return self.AxisCommand( "ihold", axis, limit )

    #-----------------------------------------------------------------
    def selgrip( self, grip, sequ ):
        '''
        Send "selgrip grip" command to SDH. Where grip is in [0..self.NUMBER_OF_GRIPS-1]
        or one of the self.eGraspId enums.

        If sequ is True then wait until SDH hardware fully executed
        the command.  Else return immediately and do not wait until SDH
        hardware fully executed the command.

        return the expected duration of the execution of the command in seconds
        '''
        # Actual input/output for the command looks like:
        #--
        # selgrip=1
        # SELGRIP=0.0,1
        #
        # Before firmware 0.0.3.1 actual input/output for the command looked like:
        #--
        # selgrip=1
        # @Enabling all axis
        # @Setting current limit to @1.0 @0.5 @0.5 @0.5 @0.5 @0.5 @0.5 @
        # @max distance=0.00, T=0.00s, num_points: 1
        # @max distance=0.00, T=0.00s, num_points: 1
        # @Setting current limit to @0.1 @0.2 @0.2 @0.2 @0.2 @0.2 @0.2 @
        # @Disabling axis 0
        # SELGRIP=1

        self.CheckIndex( grip, self.NUMBER_OF_GRIPS, "grip" )

        #---------------------
        # settings for sequ/non-sequ:
        nb_lines_total = 1
        nb_lines = nb_lines_total
        #---------------------
        
        #---------------------
        # send command and parse reply    
        reply = self.Send( "selgrip=" + str(grip), nb_lines, nb_lines_total )

        T = self.GetDuration( reply[0] )
        #---------------------
        
        return T

    #-----------------------------------------------------------------
    def grip( self, close, velocity, sequ ):
        '''
        send "grip=close,velocity" command to SDH
        close    : [0.0 .. 1.0] where 0.0 is 'fully opened' and 1.0 is 'fully closed'
        velocity : ]0.0 .. 100.0] where 0.0 (not allowed) is very slow and 100.0 is very fast

        If sequ is True then wait until SDH hardware fully executed
        the command.  Else return immediately and do not wait until SDH
        hardware fully executed the command.

        This seems to work with sin square velocity profile only,
        so the velocity profile is switched to that if necessary.

        return the expected duration of the execution of the command in seconds
        '''
        # Actual input/output for the command looks like:
        #--
        # grip=0.1,40
        # GRIP=0.42,0.1
        #
        # Before firmware 0.0.3.1 actual input/output for the command looked like:
        #--
        # grip=0.1,40
        # @Enabling finger axis
        # @Setting current limit to @1.0 @0.5 @0.5 @0.5 @0.5 @0.5 @0.5 @
        # @max distance=8.31, T=0.42s, num_points: 42
        # @Setting current limit to @0.1 @0.2 @0.2 @0.2 @0.2 @0.2 @0.2 @
        # GRIP=0.1

        self.CheckRange( close, 0.0, 1.0, "close ratio" )
        self.CheckRange( velocity, 0.0+self.eps, 100.0, "velocity" )
        
        #---------------------
        # set velocity profile if wrong or unknown
        try:
            if  (self.actual_vp != 0 ):
                self.vp( 0 )
        except AttributeError:
            self.vp( 0 )
        #---------------------

        #---------------------
        # settings for sequ/non-sequ:
        nb_lines_total = 1
        nb_lines = nb_lines_total
        #---------------------
        
        #---------------------
        # send command and parse reply    
        reply = self.Send( "grip=" + str(close) + "," + str(velocity), nb_lines, nb_lines_total )

        T =  self.GetDuration( reply[0] )
        #---------------------
        
        return T
        


    #  end of doxygen name group sdhlibrary_python_csdhserial_grip_commands
    ## @}
    ##################################################################


# end of class cSDHSerial
#=====================================================================
