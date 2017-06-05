# -*- coding: latin-1 -*-
#######################################################################
## \file
#  \section sdhlibrary_python_tcpserial_py_general General file information
#
#    \author   Dirk Osswald
#    \date     2010-10-19
#
#  \brief  
#    Simple wrapper to access a TCP port like a serial port.
#
#  \section sdhlibrary_python_tcpserial_py_copyright Copyright
#
#  - Copyright (c) 2010 SCHUNK GmbH & Co. KG
#
#  <HR>
#  \internal
#
#    \subsection sdhlibrary_python_tcpserial_py_details SVN related, detailed file specific information:
#      $LastChangedBy: Osswald2 $
#      $LastChangedDate: 2010-12-03 12:46:13 +0100 (Fri, 03 Dec 2010) $
#      \par SVN file revision:
#        $Id: tcpserial.py 6269 2010-12-03 11:46:13Z Osswald2 $
#
#  \subsection sdhlibrary_python_tcpserial_py_changelog Changelog of this file:
#      \include tcpserial.py.log
#
#######################################################################


import time
import socket


# example: http://wiki.python.org/moin/TcpCommunication#Client
#
#import socket
#
#
#TCP_IP = '127.0.0.1'
#TCP_PORT = 5005
#BUFFER_SIZE = 1024
#MESSAGE="Hello, World!"
#
#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s.connect((TCP_IP, TCP_PORT))
#s.send(MESSAGE)
#data = s.recv(BUFFER_SIZE)
#s.close()
#
#print "received data:", data



class tTCPSerial( object ):
    """Simple wrapper class to access a TCP port like a serial port as a file like object
    """

    def __init__( self, tcp_adr="192.168.1.1", tcp_port=23, timeout=2.0 ):
        """Create a tTCPSerial object for communicating via TCP/IP
        \param self - the instance of the class that this function operates on (the "object") 
        \param tcp_adr - the TCP adress of the SDH as IPv4 numeric address or hostname
        \param tcp_port - the TCP port number of the SDH,
        \param timeout - timeout in seconds
               timeout==None => make read() / readline() wait for ever
               timeout==0.0  => make read() / readline() return immediately with whatever is available
               timeout==else => use the given timeout for read() and readline()
        """
        self._tcp_adr = tcp_adr
        self._tcp_port = tcp_port
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect( (self._tcp_adr, self._tcp_port) )
        self.SetTimeout( timeout )

    def GetTimeout(self):
        '''helper function to set property timeout
        '''
        return self._socket.gettimeout()


    def SetTimeout(self, value):
        '''helper function to get property timeout
        '''
        self._socket.settimeout(value)


    def read( self, length ):
        '''read \a length bytes from the TCP socket and return them as as string.
        The waiting time for that many bytes depends on the setting of timeout 
        '''
        return self._socket.recv( length )
        

    def write( self, s ):
        '''Write string \a s to TCP socket.
        '''
        self._socket.sendall(s)
           

    def flush( self ):
        '''This is a no-op for now. Just for compatibility with the file like interface.
        '''
        pass
        
    def close( self ):
        ''' close the CAN communication object
        '''
        self._socket.close()


    def _GetEndTime(self):
        '''helper function to return an end time according to self.timeout
        '''
        to = self.GetTimeout()
        if ( to is None):
            # timeout was None (=> wait for ever)
            # (use 24h)
            end = time.time() + (24 * 60 * 60)
        else:
            end = time.time() + to
        return end

        
    def readline( self, eol='\n' ):
        '''read a complete line (terminated by the \a eol character sequence) from CAN and return it as string.
        '''
        end = self._GetEndTime()
        buffer = ""
        goon = True
        while ( goon ):
            c = self.read(1)
            buffer += c
            goon = (c != eol) and  time.time() <= end
            
        return buffer

    timeout = property(GetTimeout, SetTimeout, None, "The timeout for reading in seconds. None == Wait for ever, 0.0 == return immediately.")

