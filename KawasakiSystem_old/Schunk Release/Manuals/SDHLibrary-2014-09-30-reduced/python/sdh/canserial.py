# -*- coding: latin-1 -*-
#######################################################################
## \file
#  \section sdhlibrary_python_canserial_py_general General file information
#
#    \author   Dirk Osswald
#    \date     2007-05-04
#
#  \brief  
#    Simple wrapper to access an ESD CAN port like a serial port.
#
#  \section sdhlibrary_python_canserial_py_copyright Copyright
#
#  - Copyright (c) 2007 SCHUNK GmbH & Co. KG
#
#  <HR>
#  \internal
#
#    \subsection sdhlibrary_python_canserial_py_details SVN related, detailed file specific information:
#      $LastChangedBy: Osswald2 $
#      $LastChangedDate: 2014-09-16 17:34:11 +0200 (Tue, 16 Sep 2014) $
#      \par SVN file revision:
#        $Id: canserial.py 12227 2014-09-16 15:34:11Z Osswald2 $
#
#  \subsection sdhlibrary_python_canserial_py_changelog Changelog of this file:
#      \include canserial.py.log
#
#######################################################################


import time
import sys

try:
    import ntcan
except ImportError:
    sys.stderr.write( "The python module ntcan is not available! Please install that first, then restart.\n" )    
    sys.stderr.write( "  (ntcan is a python wrapper module provided by ESD to access its CAN cards from python)\n" )
    raise  #reraise


class tCANSerial( object ):
    """Simple wrapper class to access an ESD CAN port like a serial port as a file like object
    """

    def __init__( self, id_read, id_write, baudrate, net, timeout=2.0 ):
        """Create a tCANSerial object for communicating via ESD card on CAN bus
        \param self - the instance of the class that this function operates on (the "object") 
        \param id_read will be used as the CAN ID to listen to,
        \param id_write will be used as the CAN ID to write to,
        \param baudrate is in bit/s
        \param net is the ESD CAN net number
        \param timeout - timeout in seconds
               timeout==None => make read() / readline() wait for ever
               timeout==0.0  => make read() / readline() return immediately with whatever is available
               timeout==else => use the given timeout for read() and readline()
        """
        self._cif = None
        self.SetTimeout( timeout )
        self._id_read = id_read
        self._id_write = id_write
        self._net = net
        # Open CAN Interface
        # ---> cif = ntcan.CIF( net, RxQueueSize, RxTimeOut, TxTimeOut, TxQueueSize, Flags?)
        self._RxQS=2000			           # RxQueueSize [0, ntcan.NTCAN_MAX_RX_QUEUESIZE=2047]
        self._TxQS=1					   # TxQueueSize [0, ntcan.NTCAN_MAX_TX_QUEUESIZE=2047]
        self._TxTO=1000				       # TxTimeOut in Millseconds
        #cifFlags=				           # Flags
        self._cif = ntcan.CIF(self._net,self._RxQS,self.RxTO,self._TxTO,self._TxQS)

        baudrate_codes = dict( [(1000000,0x0),  # see ESD API documentation page 51
                                (800000, 0xE),
                                (666600, 0x1),
                                (500000, 0x2),
                                (333300, 0x3),
                                (250000, 0x4),
                                (166000, 0x5),
                                (125000, 0x6),
                                (100000, 0x7),
                                (83300, 0x10),
                                (66600, 0x8),
                                (50000, 0x9),
                                (33300, 0xA),
                                (20000, 0xB),
                                (12500, 0xC),
                                (10000, 0xD) ] )
        self._cif.baudrate = baudrate_codes[ baudrate ]
        self._cif.canIdAdd( id_read )
        t = self._cif.timestamp  # required for CAN-USB/2, see ntcan.CIF.canIdAdd() @UnusedVariable
        self._rcmsg = ntcan.CMSG()
        self._wcmsg  =ntcan.CMSG()
        self._buffer  = ""
        self._return_on_less = False

    def GetTimeout(self):
        '''helper function to set property timeout
        '''
        return self.__timeout


    def SetTimeout(self, value):
        '''helper function to get property timeout
        '''
        self.__timeout = value
        
        if ( value is None ):
            # timeout was None (=> wait for ever), but the NTCAN API/driver wants 0 ms for "wait for ever", see file://C:/Programme/ESD/CAN/SDK/doc/de/CAN-API_Teil1_Funktionen_Handbuch.pdf#page=48
            self.RxTO = 0 
        elif (value == 0.0):
            # value was 0.0 (=> return immediately. We must use canTake() instead of canRead() then!)
            self.RxTO = 1
        else:
            self.RxTO = int(value*1000.0) # RxTimeOut in Millisconds
            
        # forward to sub object, if it already exists:
        if (self._cif is not None):
            self._cif.rx_timeout = self.RxTO


    def _GetEndTime(self):
        '''helper function to return an end time according to self.timeout
        '''
        if (self.__timeout is None):
            # timeout was None (=> wait for ever)
            # (use 24h)
            end = time.time() + (24 * 60 * 60)
        else:
            end = time.time() + self.timeout
        return end

        
    def read( self, length ):
        '''read \a length bytes from CAN and return them as as string.
        The waiting time for that many bytes depends on the setting of self.timeout and self._return_on_less
        '''
        read_bytes = 0
        result = []
        
        if ( self.__timeout == 0.0 ):
            # read non blocking => use canTake
            self._rcmsg.canTake( self._cif )
            if ( self._rcmsg.len == 0 ):
                # no data was available
                return ""
            result += self._rcmsg.data.c[0:self._rcmsg.len]
        else:
            # read with a real timeout (blocking read) => use canRead
            end = self._GetEndTime()
            while ( True ):
                try:
                    self._rcmsg.canRead( self._cif )
                except IOError,e:
                    # TODO: might not be too good to forget the already received bytes!
                    if ( read_bytes > 0 ):
                        # only report in case we really forget some data 
                        sys.stderr.write( "received only %d/%d bytes before timeout. Ignoring partial message. Exception was: %s\n" % (read_bytes,length,str(e)) )
                    return ""
                
                if ( self._rcmsg.len > 0 ):
                    result += self._rcmsg.data.c[0:self._rcmsg.len]
                    read_bytes += self._rcmsg.len
                    #print "added %d bytes, new result = '%s', len(result) = %d, read_bytes=%d" % (self.rcmsg.len, str(result), len(result), read_bytes)
                    if ( self._return_on_less  and  self._rcmsg.len < 8 ):
                        # break in case we should return on less data and the frame is not full
                        break
                    
                if ( read_bytes >= length  or  time.time() > end ):
                    break
                #else:
                    #print "read %d bytes, no timeout now = %f, end = %f" % (self.rcmsg.len, time.time(), end )
                
        #print "returning %d/%d bytes '%s'" % (read_bytes,length,repr(result))
        # return integer list cmsg.data.c as string:
        return "".join( map( chr, result ) )
        

    def write( self, s ):
        '''Write string \a s to CAN.
        '''
        for i in range( 0, len(s), 8 ):
            sub = map(ord, s[i:min(len(s),i+8)] )
            #print "sending bytes %s" % repr( sub )
            self._wcmsg.canWriteByte( self._cif, self._id_write, len(sub), *sub )
           

    def flush( self ):
        '''This is a no-op for now. Just for compatibility with the file like interface.
        '''
        pass
        
    def close( self ):
        ''' close the CAN communication object
        '''
        del self._cif

    def readline( self, eol='\n' ):
        '''read a complete line (terminated by the \a eol character sequence) from CAN and return it as string.
        '''
        old_return_on_less = self._return_on_less
        self._return_on_less = True
        end = self._GetEndTime()
        while ( not eol in self._buffer  and  time.time() <= end ):
            self._buffer += self.read( 8 )
        self._return_on_less = old_return_on_less
        if ( eol in self._buffer ):
            l = self._buffer.split( eol, 1 )
            self._buffer = l[1]
            return l[0] + eol
        return ""

    timeout = property(GetTimeout, SetTimeout, None, "The timeout for reading in seconds. None == Wait for ever, 0.0 == return immediately.")

