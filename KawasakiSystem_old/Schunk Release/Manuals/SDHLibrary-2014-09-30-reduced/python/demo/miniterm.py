#!/usr/bin/env python
# -*- coding: latin-1 -*-
#######################################################################
#
## \file
#  \section miniterm_py_general General file information
#
#    \author   Dirk Osswald
#    \date     2007-01-29
#
#  \brief  
#     Very simple serial terminal
#
#     Source: pyserial the system independent serial port access module
#     An input line is read with readline and sent to the serial port on
#     return.  Commands can be edited with the cursor, delete, backspace,
#     insert keys. Previous commands, even from a previous session can be
#     reached with cursor up or CTRL-R. A history of lines is saved
#     in ~/.minitermhist and reread on the next invocation.
#
#     Input characters are sent
#     directly (only LF -> CR/LF/CRLF translation is done, if desired), received
#     characters are displayed as is (or as trough pythons repr, useful
#     for debug purposes) Baudrate and echo configuartion is done through
#     globals
#
#     As communication channels the following are available:
#     -  "normal" RS232 ports 
#     -  jtag_uart via the nios2-terminal program (if the jtagserial module is available). 
#     -  CAN where data is sent on one ID and received on another (if the canserial module is available and an ESD CAN card, native Windows only)
#
#     Start the script with \c "-h" or \c "--help" command line option
#     to see the online help.
#
#  \section miniterm_py_copyright Copyright
#
#     (C)2002-2004 Chris Liechti <cliecht@gmx.net>
#     (c)2007      Copyright (c) 2007 SCHUNK GmbH & Co. KG
#
#  <HR>
#  \internal
#
#    \subsection miniterm_py_details SVN related, detailed file specific information:
#      $LastChangedBy: Osswald2 $
#      $LastChangedDate: 2014-09-30 09:44:33 +0200 (Tue, 30 Sep 2014) $
#      \par SVN file revision:
#        $Id: miniterm.py 12281 2014-09-30 07:44:33Z Osswald2 $
#
#  \subsection miniterm_py_changelog Changelog of this file:
#      \include miniterm.py.log
#
#######################################################################
#

# Try to import sdh.canserial: Will only work: 
# - if using native windows python (not cygwin)
# - if using ESD CAN
# - if the ESD python wrapper is installed
try:
    import sdh.canserial
except ImportError:
    print "Info: Importing python module 'sdh.canserial' failed,"
    print "   CAN communication will not be available."
    print "   (Currently CAN support is only available in the "
    print "    native windows python environment. Try e.g.:"
    print "   /cygdrive/d/Programme/python2.5/python.exe ~/bin/miniterm.py )"
    print
    
try: 
    from sdh.jtagserial import cJTAGSerial
except ImportError:
    print "Info: Importing python module 'jtagserial' failed,"
    print "   JTAG communication will not be available."
    print
    
import atexit
import os
import select


try:
    # FIXed: this line below outputs 8 bytes 1b 5b 3f 31 30 33 34 68 which confuse latex
    # cannot be fixed internally (redirecting stdout does not help)
    # see also https://bugzilla.redhat.com/show_bug.cgi?id=593799
    # => workaround use "export TERM=dumb" in Makefile when generating online help
    import readline  
    
    # native windows might not have a HOME environment variable
    if   ( "HOME" in os.environ ):
        d = os.environ["HOME"]
    elif ( "APPDATA" in os.environ ):
        d = os.environ["APPDATA"]
        
    histfile = os.path.join(d, ".minitermhist")
    try:
        readline.read_history_file(histfile)
    except IOError:
        pass
    
    atexit.register(readline.write_history_file, histfile)
    del histfile
except ImportError:
    print "Info: Importing python module 'readline' failed,"
    print "   command line history will not be available."
    print 
import sys
import serial
import threading
import getopt
import string
import time
import subprocess
#import util
import os

######################################################################
# 
def GetColor(c):
    '''return a string that when printed sets the color to c, where c must be in
    normal, bold, red, green, yellow, blue, magenta, cyan, white, black, for normal color or
    black_back, red_back, green_back, yellow_back, blue_back, cyan_back, magenta_back, white_back for reverse color
    If the environment variable "TERM" is set to "eclipse" then no color string is returned.
    If the environment variable "SDH_NO_COLOR" is set then "" is returned.
    If the environment variable "OS" is WIN* or Win* and "OSTYPE" is not "cygwin"
    then "" is returned. (to prevent color output on windows consoles which cannot handle it).
    If the color is not found in the list of known colors then the string "" is returned.
    '''
    # no coloring when run within a non color aware console like windows
    if ( ('TERM' in os.environ.keys() and os.environ['TERM'] == "eclipse") or
         ('SDH_NO_COLOR' in os.environ.keys()) or
         ('OS' in os.environ.keys() and ('WIN' in os.environ['OS'] or 'Win' in os.environ['OS']) and (not 'OSTYPE' in os.environ.keys() or not 'cygwin' in os.environ['OSTYPE'] )) ):
        return ""
        
    colors={ "normal" : "\x1b[0m",
             "bold" : "\x1b[1m",
             "red" : "\x1b[31m",
             "green" : "\x1b[32m",
             "yellow" : "\x1b[33m",
             "blue" : "\x1b[34m",
             "magenta" : "\x1b[35m",
             "cyan" : "\x1b[36m",
             "white" : "\x1b[37m",
             "black" : "\x1b[39m",
             "black_back" : "\x1b[40m",
             "red_back" : "\x1b[41m",
             "green_back" : "\x1b[42m",
             "yellow_back" : "\x1b[43m",
             "blue_back" : "\x1b[44m",
             "cyan_back" : "\x1b[45m",
             "magenta_back" : "\x1b[46m",
             "white_back" : "\x1b[47m" }
    return colors[c]
#
######################################################################

prefix_keyboard = GetColor("blue")
suffix_keyboard = GetColor("normal")
prefix_serialin = GetColor("normal")
suffix_serialin = GetColor("normal")
prefix_message = GetColor("green")
suffix_message = GetColor("normal")
prefix_error = GetColor("red")
suffix_error = GetColor("normal")
prefix_warning = GetColor("magenta")
suffix_warning = GetColor("normal")
VT100_CLR_SCREEN = "\x1b[2J"

EXITCHARACTER = '\x04'   #ctrl+D


CONVERT_CRLF = 2
CONVERT_CR   = 1
CONVERT_LF   = 0

eModeAscii      = 0
eModeNumeric    = 1
eModeHexNumeric = 2


mode = eModeAscii
additional_ascii = False
numeric_length = 8
prompt = None

input_log_file = None
inputfilename = None

g_exiting = False
g_reader_thread = None
serialport = None

def GetPrompt():
    global usecan, usejtag, port, id_read, jtag_processor
    if usecan:
        return prefix_message + "CAN 0x%03x< " % (id_read) + prefix_keyboard
    elif usejtag:
        return prefix_message + "JTAG%s< " % (jtag_processor) + prefix_keyboard
    else:
        if ( type(port) == int ):
            return prefix_message + "COM%d< " % (port+1) + prefix_keyboard
        else:
            return prefix_message + "%s< " % (port) + prefix_keyboard

def hex2( n ):
    """Return the hexadecimal representation of an integer or long integer with 2 digits (hex2(5)->0x05)
    """
    return "0x%02x" % n

def cls():
    """Clear screen. Needed in windows console since that does not understand VT100 commands
    """
    os.system( "cls" )

def reader():
    """loop forever and copy serial->console
    """
    try:
        global mode, additional_ascii, prompt, input_log_file, serialport
        did_print = False
    
    
        # To catch ctrl sequences like VT100 "test presence":
        #
        #  according to http://www-user.tu-chemnitz.de/~heha/hs_freeware/terminal/terminal.htm#3
        #     query:  ESC [ 5 n     (test presence)
        #     answer: ESC [ 0 n
        #
        #   sent by dsacon32m on reset/startup:
        #     "\x1b\x5b\x35\x6e\x1b\x5b\x35\x6e\x1b\x5b\x35\x6e\x1b\x5b\x35\x6e"
        #   replied by hyperterminal:
        #     0x1b 0x5b 0x30 0x6e 0x1b 0x5b 0x30 0x6e
    
        #auto_reply = [ ("\x1b[5n\x1b[5n","\x1b[\x30\x1b[\x30") ]
        auto_reply = [ ("\x1b[5n","\x1b[0n") ]
        line = ""
        starttime = time.time()
        time.sleep(1)
        #print "starttime, time() = %f, %f" % (starttime,time.time())
        while 1:
            try:
                #data = serialport.read( numeric_length )
                data = serialport.readline() # this is much less CPU intensive than above
            except IOError,e:
                sys.stdout.write( prefix_error + "Error while reading (ignored): " + str(e) + suffix_error + "\r\n" )
                sys.stdout.flush()
                time.sleep( 0.1 )
                continue
            except select.error,e:
                # happens when resizing the terminal window that we run in, so ignore it and start over
                continue

    
            if ( len( data ) < 1 ):
                if ( did_print ):
                    sys.stdout.write( prompt )
                    sys.stdout.flush()
                    did_print = False
                continue
    
            #print "data =<", repr(data),"> type=", type(data)
    
            if ( not did_print ):
                sys.stdout.write( "\r\n" )
                sys.stdout.flush()
    
            did_print = True
    
    
            #print "caught %d bytes \r\n" % len(data)
            # collect date in lines, because since SDH firmware release 0.0.1.10
            # the test presence query from the SDH is split into several data packets
            line += data
            lines = line.split( "\r\n" )
            line = lines[-1]
            for (query,reply) in auto_reply:
                for l in lines:
                    if (query in l):
                        #sys.stderr.write( "tds received at %f\n" % (time.time()-starttime) ) # FIX ME: removeme
                        #continue
                        sys.stderr.write( prefix_warning + "autoreplying '%s' for '%s'\r\n" % (repr(reply), repr(query)) + suffix_warning )
                        serialport.write( reply )
                        serialport.flush()
                        line = "".join( line.split( query, 1 )) # remove query from line
                        continue
                        
            # try to handle VT100 command to clear screen specially in
            # windows console which does not understand VT100 commands
            # (unfortunatily this does not work...)
            #if ( VT100_CLR_SCREEN in line and  "win32" in sys.platform ):
            #    cls()
            #print "not autoreplying for data= %s" % repr(data)
    
            
            if repr_mode:
                sys.stdout.write( prefix_serialin + repr(data)[1:-1] + suffix_serialin )
                sys.stdout.flush()
            else:
                if mode == eModeAscii:
                    sys.stdout.write( prefix_serialin + data  + suffix_serialin )
                    sys.stdout.flush()
                    if ( input_log_file ):
                        input_log_file.write( data )
                else:
                    # one of the numeric modes
    
                    text = ""
                    # separate data into lines of length numeric_length
                    for l in [ data[ i : i+numeric_length ] for i in range( 0, len(data), numeric_length ) ]:
                        
                        if mode == eModeNumeric:
                            text = " ".join( map( str, map( ord, l ) ) )
                        if mode == eModeHexNumeric:
                            text = " ".join( map( hex2, map( ord, data ) ) )
    
                        if additional_ascii:
                            text = text.ljust( numeric_length*5 + 3 )
                            for c in l:
                                text += repr( c )[1:-1] + " "
                    text += "\r\n"
                        
                    sys.stdout.write( prefix_serialin + text + suffix_serialin )
                    sys.stdout.flush()
                    if ( input_log_file ):
                        input_log_file.write( text )
            sys.stdout.flush()
    except Exception,e:
        global g_exiting
        time.sleep(0.5)
        if (not g_exiting):
            print "reader: caught e=",e
            raise #reraise
        # when exiting e is ignored
        
online_help = prefix_message + """
miniterm onlinehelp:
F1 + RETURN: Show this help.
F2 + RETURN: Activate text mode:
             For "47 0x11" as input 8-9 bytes will be sent, the chars
             of the string plus linefeed chars.
F3 + RETURN: Activate numeric mode:
             For "47 0x11" as input 2 bytes will be sent, 42 and 17.
             For "256 65536" as input 5 bytes will be sent, 0,1, 0,0,1.
             I.E. little endian encoding with the fewest bytes necessary.
F4 + RETURN: Activate hex numeric mode
             For "47 11" as input 2 bytes will be sent, 71 and 17.
F5 + RETURN: Toggle additional ascii display in numeric mode
F6 + RETURN: Toggle prompt
F7 FILENAME + RETURN: save received data to file FILENAME
F7 + RETURN:          close a previously opened file
F8 FILENAME + RETURN: send data from file FILENAME
""" + suffix_message

def StringToInt( s, base=10 ):
    """return int of string s, e.g. 10 for "10" or "0xa"
    """
    if ( s[0:2] in [ "0x", "0X" ] ):
        return int( s, 16 )
    return int( s, base )


def HexStringToInt( s ):
    return StringToInt( s, 16 )


def SendFromFile( filename ):
    """send data from file filename to serial port.
    Data is sent as is with the following exceptions:
    - an empty line (2 consecutive newlines) make the sending pause until the RETURN key is pressed
    """
    try: 
        input_data_file = file( filename, "r" )
    except IOError,e:
        sys.stderr.write( "Could not open file %s: %s" % (filename, str(e) ) )
        sys.stdout.flush()

    lines = input_data_file.readlines()
    input_data_file.close()
    
    for l in lines:
        if ( l == "\n"  or l == "\r\n" ):
            time.sleep( 1.0 ) # give sdh2 time to answer previous command
            raw_input( prefix_warning + "Press RETURN to continue sending recorded commands" + suffix_warning )
        sys.stdout.write( prompt + l )
        sys.stdout.flush()
        serialport.write( l )
        
    time.sleep( 2.0 )
    sys.stdout.write( prefix_warning + "Sending of data from file '%s' finished" % filename + suffix_warning ) 
    sys.stdout.flush()

def writer():
    """loop and copy console->serial until EOF character is found
    """
    global mode, additional_ascii, convert_outgoing, convert_outgoing_last, prompt, input_log_file, serialport, inputfilename

    if ( inputfilename ):
        inputfile = file( inputfilename, "r" )
    def GetInput( prompt ):
        if ( inputfilename ):
            return inputfile.readline()[:-1]
        else:
            return raw_input(prompt)
    
    while 1:
        l = GetInput(prompt)
        if ( inputfilename and l == "" ):
            # end of file reached in inputfile
            inputfile.close()
            inputfilename = None
            
        if ( l == "1~" ):
            sys.stdout.write( online_help )
            sys.stdout.flush()
            continue
        if ( l == "2~" ):
            mode = eModeAscii
            convert_outgoing = convert_outgoing_last
            sys.stdout.write( prefix_message + "Text mode activated\r\n" + suffix_message )
            sys.stdout.flush()
            continue
        if ( l == "3~" ):
            mode = eModeNumeric
            convert_outgoing_last = convert_outgoing
            convert_outgoing = None
            sys.stdout.write( prefix_message + "Numeric mode activated\r\n" + suffix_message )
            sys.stdout.flush()
            continue
        if ( l == "4~" ):
            mode = eModeHexNumeric
            convert_outgoing_last = convert_outgoing
            convert_outgoing = None
            sys.stdout.write( prefix_message + "Hex numeric mode activated\r\n" + suffix_message )
            sys.stdout.flush()
            continue
        if ( l == "5~" ):
            additional_ascii = not additional_ascii
            sys.stdout.write( prefix_message + "Additional ASCII display is %s\r\n" % str(additional_ascii) + suffix_message )
            sys.stdout.flush()
            continue
        if ( l == "7~" ):  # yes! F6 is "7~" !!! Thats windows for you...
            if (prompt==""):
                prompt = GetPrompt()
                sys.stdout.write( prefix_message + "prompt is now on\r\n" )
                sys.stdout.flush()
            else:
                prompt = ""
                sys.stdout.write( prefix_message + "prompt is now off\r\n" )
                sys.stdout.flush()
            continue
        if ( l[0:2] == "8~" ):  # yes! F7 is "8~" !!! Thats windows for you...
            ll = string.split( l )
            if ( len( ll ) == 1 ):
                if ( input_log_file ):
                    input_log_file.close()
                    input_log_file = None
            else:
                input_log_file = file( ll[1], "w" )
            continue

        if ( l[0:2] == "9~" ):  # yes! F8 is "9~" !!! Thats windows for you...
            ll = string.split( l )
            SendFromFile( ll[1] )
            continue
        if echo:
            sys.stdout.write( prefix_keyboard + l + suffix_keyboard + "\r\n" )
            sys.stdout.flush()
            
        try:
            if mode == eModeNumeric:
                values = map( StringToInt, string.split( l ) )

            if mode == eModeHexNumeric:
                values = map( HexStringToInt, string.split( l ) )

            if mode in [ eModeNumeric, eModeHexNumeric ]:
                bytes = []
                for v in values:
                    while v > 255:
                        bytes.append( v & 255 ) #lowbyte
                        v = v >> 8
                    bytes.append( v )
                l = "".join( map( chr, bytes ) )
        except ValueError,e:
            sys.stdout.write( prefix_error + "invalid numeric input: %s" % str(e) + suffix_error + "\r\n" )
            sys.stdout.flush()
            continue
            
        sys.stderr.write( 'sending string %s\r\n' % repr( l ) )

        try:
            if convert_outgoing == CONVERT_CRLF:
                serialport.write(l+'\r\n')         #make it a CR+LF
            elif convert_outgoing == CONVERT_CR:
                serialport.write(l+'\r')           #make it a CR
            elif convert_outgoing == CONVERT_LF:
                serialport.write(l+'\n')           #make it a LF
            else:
                serialport.write( l )
        except IOError,e:
            sys.stderr.write( prefix_error + "IOError:" + repr( e ) + suffix_error + "\r\n" )
                
        continue
        
        c = getkey()
        if c == EXITCHARACTER: 
            break                       #exit app
        elif c == '\n':
            if convert_outgoing == CONVERT_CRLF:
                serialport.write('\r\n')         #make it a CR+LF
            elif convert_outgoing == CONVERT_CR:
                serialport.write('\r')           #make it a CR
            elif convert_outgoing == CONVERT_LF:
                serialport.write('\n')           #make it a LF
        else:
            serialport.write(c)                  #send character


#print a short help message
def usage():
    
    can_options  = ""
    jtag_options = ""

    if ( "sdh.canserial" in sys.modules ):
        can_options = """--can:               use the (ESD) CAN interface instead of RS232 serial port
    --net=NET            use the ESD CAN net number NET 
    --id_read=ID_READ:   use CAN ID ID_READ for receiving CAN messages (default: 43)
    --id_write=ID_WRITE: use CAN ID ID_WRITE for writing CAN messages (default: 42)"""

    if ( "sdh.jtagserial" in sys.modules ):
        jtag_options = """-j, --jtag:          use jtag_uart via nios2-terminal instead of RS232 serial port
    -i, --instance=ID:   use ID as jtag instance (see nios2-terminal --help)
    --cable=ID:          use ID as jtag cable (see nios2-terminal --help)
    --device=ID:         use ID as jtag device (see nios2-terminal --help)"""

    sys.stdout.write("""USAGE: %s [options]
    Miniterm - A simple terminal program for the serial port.

    options:
    -p, --port=PORT: RS232 port to use for communication
                     either a number, default = 0 (=COM1 / /dev/ttyS0)
                     or a device name like \"/dev/ttyUSB0\"
    -b, --baud=BAUD: baudrate, default 115200 for RS232, 1MBit for CAN
    -r, --rtscts:    enable RTS/CTS flow control (default off)
    -e, --echo:      enable local echo (default off)
    -D, --debug:     debug received data (escape nonprintable chars)
    -n, --numeric:       enable numeric mode, see online help (F1+RETURN)
    -x, --hexnumeric:    enable hex numeric mode, see online help (F1+RETURN)
    -a, --additional_ascii enable additional ascii display, see online help (F1+RETURN)
    -c, --cr:        do not send CR+LF, send CR only
    -t, --timeout=TIMEOUT: use timeout of TIMEOUT seconds, default is 0.1
    --xonxoff:   enable software flow control (default off)
    --newline:   do not send CR+LF, send LF only
    --input=FILE: send data from FILE instead of from keyboard
    --nonewline: do not add newlines, mainly usefull when using --input and --numeric or --hexnumeric
    --nocolor: do not use colored output
    %s
    %s
""" % (sys.argv[0], can_options, jtag_options ))


convert_outgoing = CONVERT_CRLF

#-----------------------------------------------------------------
## \brief A Frame widget class, used to select the communication interface to the SDH
#
#  - creates the widgets
#  <hr>
try:
    import Tkinter
    
    class cTkSDHInterfaceSelectorFrame(Tkinter.Frame):
        '''A toplevel widget class, used to interactively select the communication interface of the miniterm.py app on start. 
        '''
        #-----------------------------------------------------------------
        ## Constructor of cTkSDHInterfaceSelectorFrame
        def __init__(self, master=None ):
            Tkinter.Frame.__init__(self, master=master, class_="cTkSDHInterfaceSelectorFrame" )
    
            # create all subwidgets
            self.CreateWidgets()
    
        #-----------------------------------------------------------------
        def RS232Callback(self ):
            global port, usecan
            port = self.available_ports[self.p.get()][0]
            usecan = False
            
        def CANCallback(self ):
            global port, usecan
            usecan = True
            
        def OKCallback(self):
            self.quit()
            
        #-----------------------------------------------------------------
        ## Create the GUI widgets: 
        def CreateWidgets(self):
            Tkinter.Label( self, text="Please select the communication interface to the SDH:\n" ).pack(anchor=Tkinter.N)
            #---------------------
            self.p = Tkinter.IntVar( 0 )
            self.available_ports = sdh.GetAvailablePorts()
            print "available_ports =", self.available_ports
            i = 0                                            
            for (device_name,occupied) in self.available_ports:
                if (occupied):
                    state = Tkinter.DISABLED
                    hint = "  (used by another application / insufficient rights)"
                else:
                    state = Tkinter.NORMAL
                    hint = ""
                Tkinter.Radiobutton(self, state=state, text="RS232 Port %r%s" % (device_name,hint), variable=self.p, value=i, command=self.RS232Callback).pack(anchor=Tkinter.W)
                i += 1
            if ( "sdh.canserial" in sys.modules ):
                Tkinter.Radiobutton(self, text="CAN", variable=self.p, value=1000, command=self.CANCallback).pack(anchor=Tkinter.W)
    
            #---------------------
            Tkinter.Label( self, text=" " ).pack(anchor=Tkinter.W)
            Tkinter.Button( self, text="  OK  ", command=self.OKCallback).pack(anchor=Tkinter.S)
except ImportError:
    pass


def Exit( val=1, wait_for_key=("win32" in sys.platform) ):
    '''if wait_for_key is False then just call exit. If True tehn loop until a key is pressed then exit.
    On cygwin/linux wait_for_key defaults to False, on windows it defaults to True.
    (This is usefull to be able to view error messages of python when called on windows)
    '''
    global g_exiting, g_reader_thread, serialport
    g_exiting = True
    if ( not g_reader_thread is None ):
        serialport.close() # needed to terminate subprocesses (like nios-terminal for JTAG communication)
        #sys.stderr.write("closed\r\n")
        time.sleep(0.1)
        if ( g_reader_thread.isAlive() ):
            g_reader_thread.join(1.0)
            #sys.stderr.write("joined\r\n")
        #else:
        #    sys.stderr.write("already dead\r\n")
        #if ( g_reader_thread.isAlive() ):
        #    sys.stderr.write("still alive!\r\n")
        #else:
        #    sys.stderr.write("really dead!\r\n")
            
        
    if ( wait_for_key ):
        print "\nThis program can now be savely closed (CTRL-C)\n"
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            # catch CTRL-C, so no error msg & stacktrace is shown
            pass
    sys.exit(val)


def main():
    #initialize with defaults
    port  = 0
    baudrate_rs232 = 115200
    baudrate_can   = 1000000
    baudrate       = None
    echo = 0
    rtscts = 0
    xonxoff = 0
    repr_mode = 0
    timeout   = 0.1  # 0.5 is too long to make "terminal presence detection" work for DSACON32, since we are now using readline() instead of read()
    usecan = False
    id_read = 43
    id_write = 42
    net = 0
    usejtag = False
    jtag_options = []
    jtag_processor = ""
    channel_set_by_user = False
    
    #parse command line options
    try:
        can_short_options  = ""
        can_long_options   = [ "can", "id_read=", "id_write=", "net=" ]
        jtag_short_options = "ji:"
        jtag_long_options  = [ "jtag", "instance=", "cable=", "device=" ]
        opts, args = getopt.getopt(sys.argv[1:],
                                   "hp:b:reDnxact:o" + can_short_options + jtag_short_options,
                                   ["help", "port=", "baud=", "rtscts", "echo",
                                    "debug", "numeric", "hexnumeric", "additional_ascii",
                                    "cr", "timeout=", "noprompt", "xonxoff", "newline", "input=", "nonewline", "nocolor"  ] 
                                    + can_long_options
                                    + jtag_long_options 
                                   )
    except getopt.GetoptError:
        # print help information and exit:
        usage()
        Exit(2)
    
    for o, a in opts:
        if o in ["-h", "--help"]:       #help text
            usage()
            Exit(0)
        elif o in ["-p", "--port"]:     #specified port
            try:
                port = int(a)
            except ValueError:
                port = a
            channel_set_by_user = True
        elif o in ["-b", "--baud"]:     #specified baudrate
            try:
                baudrate = int(a)
            except ValueError:
                raise ValueError, "Baudrate must be a integer number, not %r" % a
        elif o in ["-r", "--rtscts"]:
            rtscts = 1
        elif o in ["--xonxoff"]:
            xonxoff = 1
        elif o in ["-e", "--echo"]:
            echo = 1
        elif o in ["-c", "--cr"]:
            convert_outgoing = CONVERT_CR
        elif o in ["--newline"]:
            convert_outgoing = CONVERT_LF
        elif o in ["-D", "--debug"]:
            repr_mode = 1
        elif o in ["-n", "--numeric"]:
            print "mode = -n"
            mode = eModeNumeric
        elif o in ["-x", "--hexnumeric"]:
            mode = eModeHexNumeric
        elif o in ["-a", "--additional_ascii" ]:
            additional_ascii = True
        elif o in ["-t", "--timeout" ]:
            timeout = float(a)
        elif o in ["-o", "--noprompt" ]:
            prompt=""
        elif o in ["--input" ]:
            inputfilename = a
        elif o in ["--nonewline" ]:
            convert_outgoing = None
        elif ("sdh.canserial" in sys.modules  and  o in ["--can"]):
            usecan = True
            channel_set_by_user = True
        elif ("sdh.canserial" in sys.modules  and   o in ["--net"]):
            net = eval(a)
        elif ("sdh.canserial" in sys.modules  and   o in ["--id_read"]):
            id_read = eval(a)
        elif ("sdh.canserial" in sys.modules  and  o in ["--id_write"]):
            id_write = eval(a)
        elif ("sdh.jtagserial" in sys.modules  and   o in ["-j", "--jtag"]):
            usejtag = True
            channel_set_by_user = True
        elif ("sdh.jtagserial" in sys.modules  and  o in ["-i", "--instance"]):
            jtag_options.append( "--instance=" + a ) 
            if ( a in [ 0, "0" ] ):
                jtag_processor = "-LLC"
            elif ( a in [ 1, "1" ] ):
                jtag_processor = "-HLC"
            else:
                jtag_processor = "-?"
        elif ("sdh.jtagserial" in sys.modules  and   o in ["--device"]):
            jtag_options.append( "--device=" + a ) 
        elif ("sdh.jtagserial" in sys.modules  and   o in ["--cable"]):
            jtag_options.append( "--cable=" + a )
        elif ( o in "--nocolor" ):
            prefix_keyboard=suffix_keyboard=prefix_serialin=suffix_serialin=prefix_message=suffix_message=prefix_error=suffix_error=prefix_warning=suffix_warning = ""
            
    convert_outgoing_last = convert_outgoing

    if ( not channel_set_by_user ):
        if "Tkinter" in sys.modules:
            try:
                import sdh
    
                root = Tkinter.Tk()
                ##try:
                ##    root.wm_iconbitmap(GetIconPath())
                ##except tkinter.TclError,e:
                ##    dbg << "Ignoring tkinter.TclError %r\n" % e
                ##    pass # ignore error
                app = cTkSDHInterfaceSelectorFrame( master=root )
                app.master.title("miniterm interface selector" )
                app.pack()
                #app.mainloop()
                root.mainloop()
                root.destroy()
                channel_set_by_user = True
            except ImportError:
                sys.stderr.write( "Could not import module sdh => no interactive interface selection available.\n" )
            finally:
                pass
        else:       
            sys.stderr.write( "Std. Python module Tkinter not available, no interactive interface selection available.\n" )
            
        if ( not channel_set_by_user ):
            sys.stderr.write( "  You can specifiy the interface to use with command line options.\n" )
            sys.stderr.write( "  Use -h or --help to see the online help.\n" )
            sys.stderr.write( "  Using default (RS232, port 0 = COM1).\n\n" )
            
    if ( prompt is None ):
        prompt = GetPrompt()

    #open the port
    try:
        if ( usecan ):
            if ( baudrate is None ):
                baudrate = baudrate_can
            serialport = sdh.canserial.tCANSerial( id_read, id_write, baudrate, net )
            serialport._return_on_less = True
            print "Using ESD CAN net %d, id_read = 0x%03x, id_write = 0x%03x, baudrate = %d" % (net, id_read, id_write, baudrate)
            sys.stdout.flush()
        elif ( usejtag ):
            serialport = cJTAGSerial( jtag_options )
        else:
            if ( baudrate is None ):
                baudrate = baudrate_rs232
            serialport = serial.Serial(port, baudrate, rtscts=rtscts, xonxoff=xonxoff, timeout=timeout)
    except Exception,e:
        sys.stderr.write("Could not open port\r\n")
        sys.stderr.write("  Exception: %s\r\n" % str(e) )
        raise
        Exit(1)
    sys.stderr.write("--- Miniterm --- type Ctrl-D to quit\r\n")
    sys.stderr.flush()
            

    #start serial->console thread
    g_reader_thread = threading.Thread(target=reader)
    g_reader_thread.setDaemon(1)
    g_reader_thread.start()
    #and enter console->serial loop
    try:
        writer()
    except EOFError:
        pass
    except KeyboardInterrupt:
        pass
    sys.stderr.write("\r\n--- exit ---\r\n")

if __name__ == '__main__':
    main()
Exit(0)
