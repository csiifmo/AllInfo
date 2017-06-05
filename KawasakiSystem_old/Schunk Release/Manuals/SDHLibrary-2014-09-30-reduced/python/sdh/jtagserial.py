# -*- moding: latin-1 -*-
#######################################################################
#
## \file
#  \section sdhlibrary_python_jtagserial_py_general General file information
#
#    \author   Dirk Osswald
#    \date     2008-07-13
#
#  \brief  
#    Implementation of class to access the jtag_uart 
#
#  \section sdhlibrary_python_jtagserial_py_copyright Copyright
#
#  Copyright (c) 2008 SCHUNK GmbH & Co. KG
#
#  <HR>
#  \internal
#
#    \subsection sdhlibrary_python_jtagserial_py_details SVN related, detailed file specific information:
#      $LastChangedBy: Osswald2 $
#      $LastChangedDate: 2009-06-09 12:53:56 +0200 (Tue, 09 Jun 2009) $
#      \par SVN file revision:
#        $Id: jtagserial.py 4574 2009-06-09 10:53:56Z Osswald2 $
#
#  \subsection sdhlibrary_python_jtagserial_py_changelog Changelog of this file:
#      \include sdhserial.py.log
#
#######################################################################

import os, sys, time, subprocess
from . import util
from . import utils

def GetPath( cygpath ):
    '''translat cygwin path in cygpath to a windows path if this is a native windows python interpreter
    ''' 
    if ( "win" in sys.platform ):
        # translate cygwin to windows path
        result = ""
        for p in cygpath.split(":"):
            result += subprocess.Popen([os.environ["CYGWIN_ROOT"]+"\\bin\\"+"cygpath", "-w", p ], stdout=subprocess.PIPE).communicate()[0]
        return result
    return cygpath


class cJTAGSerial( object ):
    '''A class that emulates a communication channel that can be read and written.
    The data is sent to / read from a nios2-terminal process which in turn 
    communicates e.g. with a nios processor via a jtag_uart device
    '''
    def __init__( self, options = [] ):
        """Create a tJTAGSerial object for communicating via jtag uart
        options is a list of strings with the individual options
        """
        self.options = options
        self.restart()

    def restart( self ):
        if ("win" in sys.platform ):        
            args = [ "d:\\Programme\\Altera\\7.2\\nios2eds\\bin\\nios2-terminal.exe" ] + self.options
        else:
            args = [ "nios2-terminal" ] + self.options
        env = os.environ
        env["PATH"] = GetPath("/cygdrive/d/Programme/Altera/7.2/nios2eds/bin:/cygdrive/d/Programme/Altera/7.2/nios2eds/bin/nios2-gnutools/H-i686-pc-cygwin/bin:/cygdrive/d/Programme/Altera/7.2/nios2eds/sdk2/bin:/cygdrive/d/Programme/Altera/7.2/nios2eds/bin/fs2/bin:/cygdrive/d/Programme/Altera/7.2/quartus/bin/cygwin/bin:/cygdrive/d/Programme/Altera/7.2/quartus/bin/cygwin/usr/bin:/cygdrive/d/Programme/Altera/7.2/quartus/bin:/cygdrive/d/Programme/Altera/7.2/quartus/bin/perl/bin:/cygdrive/d/Programme/Altera/7.2/quartus/bin/gnu:/cygdrive/d/Programme/Altera/7.2/quartus/sopc_builder/bin:/cygdrive/c/WINDOWS/system32:/cygdrive/c/WINDOWS:/cygdrive/c/WINDOWS/system32/wbem:/cygdrive/c/WINDOWS/system32/nls:/cygdrive/c/WINDOWS/system32/nls/ENGLISH:/bin:/usr/bin")
        #print "calling subprocess.Popen( args=%s, ... ) " % (repr(args))
        if ("win" in sys.platform ):
            self.jtag = utils.Struct()
            self.jtag.stdout = None     
            self.jtag.stdin = None
            import popen2
            sep = ""
            cmdline = ""
            for a in args:
                cmdline += sep + a
                sep = " " 
            (self.jtag.stdout, self.jtag.stdin) = popen2.popen2( "d:\\Programme\\Altera\\7.2\\nios2eds\\bin\\nios2-terminal.exe -i 0" )#, mode="w", bufsize=1 ) #cmdline )     
            #(self.jtag.stdin, self.jtag.stdout) = os.popen2( "d:\\Programme\\Altera\\7.2\\nios2eds\\bin\\nios2-terminal.exe -i 0" , "t" )#cmdline )     
        else:
            self.jtag = subprocess.Popen( args = args,
                                          bufsize = 1,    # 0 = no buffering, 1=use line buffering
                                                        # 1 is needed to make readline work!
                                          stdin  = subprocess.PIPE,
                                          stdout = subprocess.PIPE,
                                          stderr = None,  # reuse our stderr
                                          universal_newlines = True,
                                          env = env 
                                          )

    def read( self, length ):
        b = self.jtag.stdout.read( 1 )
        # try to detect if the nios2-terminal has gone mad.
        # this happens if the remote processore is reset. 
        # the nios2-terminal then continuously sends 0xff
        # TODO: we react on the very first 0xff which might not be adequate...
        if ( len(b) == 0 ):
            sys.stderr.write( util.GetColor("red") + "\nCould not read 1 byte from jtag! (SDH switched off?)\n  I will wait a little and try to reconnect" + util.GetColor("normal") + "\n"  )
            try:
                os.kill( self.jtag.pid, 15 )
                self.jtag.wait()
            except AttributeError:
                pass # no os.kill on windows
            except OSError:
                # process was already gone...
                pass 
            time.sleep( 5 )
            self.restart()
            b = ""

        elif ( ord( b ) == 0xff ):
            sys.stderr.write( util.GetColor("red") + "\nMad nios2-terminal detected, restarting it!\n\n" + util.GetColor("normal") + "\n"  )
            os.kill( self.jtag.pid, 15 )
            self.jtag.wait()
            time.sleep( 0.3 )
            self.restart()
            b = ""
            
        return b
        
        # does not work at all:
#        try:
#            return self.jtag.stdout.next()
#        except StopIteration:
#            return ""

    def write( self, s ):
        self.jtag.stdin.write( s )

    def flush( self ):
        self.jtag.stdin.flush()
        
    def readline( self ):
        l = ""
        while ( "\n" not in l ):
            l += self.read( 0 )
        return l

    def close(self):
        os.kill( self.jtag.pid, 15 )
        self.jtag.wait()
        self.jtag = None
        
#===============================================================================
# end of class tJTAGSerial        
#===============================================================================

