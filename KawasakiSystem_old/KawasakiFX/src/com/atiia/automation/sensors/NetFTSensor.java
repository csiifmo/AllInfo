/*
 * NetFTSensor.java
 *
 * Created on February 8, 2006, 2:32 PM
 *
 * History:
 * jun.1.2010       Sam Skuce (ATI Industrial Automation)
 *  Changed default timeout for high speed data collection to 1500 ms (You can
 *  set the 'high-speed' sample rate as low as 1 hz).
 */

package com.atiia.automation.sensors;

import java.io.IOException;
import java.net.*;

/**Represents an ATI Industrial Automation Net F/T force and torque load cell.
 *
 * @author Sam Skuce (ATI Industrial Automation)
 */
public class NetFTSensor {
    
        /** The version of the Net F/T interface. */
        private static final String VERSION = "1.0.2";
        
    
        private InetAddress m_iaNetFTAddress; /*the address of the Net F/T sensor*/   
        private final int RDTPORT = 49152; /*the port the Net F/T listens for                                             *
                                            *RDT requests on*/
        private final int NETFT_RDT_COMMAND_LENGTH = 8;
        private final int NETFT_RDT_DATA_LENGTH = 36;
        
        /**creates new Net F/T representation.
         *@param setAddress the address of the Net F/T sensor
         *@throws           UnkownHostException If setAddress is an 
         *unknown host.
         */
        public NetFTSensor( InetAddress setAddress ) throws 
                UnknownHostException
        {
            m_iaNetFTAddress = InetAddress.getByAddress( 
                    setAddress.getAddress() );
        }
        
        /**Request a single RDT F/T record from the Net F/T sensor.<br>
         *@return the RDT Packet from the sensor.
         *@throws SocketException If there is an error with the socket.
         *@throws IOException If there is an I/O error with the load cell.
         */
        public DatagramSocket initLowSpeedData() throws 
                SocketException, IOException {
            
            DatagramSocket netFTSocket = new DatagramSocket();
            final int SINGLE_RDT_TIMEOUT = 500; /*500 ms time-out when waiting
                                                 *for response*/
            netFTSocket.setSoTimeout( SINGLE_RDT_TIMEOUT );
            netFTSocket.connect( m_iaNetFTAddress, RDTPORT );
            
           return netFTSocket;
        }
        
        /**Start interrupt-driven (high-speed) data collection from Net F/T 
         *sensor.
         *@param iCount     The number of samples to collect.  A value of 0
         *means the Net F/T should keep outputting samples until it is sent
         *a stop command.  The stop command can be sent by calling 
         *stopDataCollection.
         *@return A DatagramSocket that you should pass to subsequent calls to
         *readHighSpeedData in order to read the samples sent back from the Net 
         *F/T.
         *@throws SocketException   A SocketException is thrown if there is 
         *a problem setting up the socket that is returned.
         *@throws IOException       An IOException is thrown if there is a
         *problem sending the start command to the Net F/T.
         */
        public DatagramSocket startHighSpeedDataCollection( int iCount ) throws
                SocketException, IOException {
            /*create a command with mode 2 for high-speed data acquisition,
             *to output the specified number of samples*/
            NetFTRDTCommand cNetFTCommand = new NetFTRDTCommand( 2, iCount );
            final int HIGH_SPEED_RDT_TIMEOUT = 1500; /*wait at most 1500 ms for
             *a high-speed FX*/
            DatagramSocket cNetFTSocket = new DatagramSocket();
            cNetFTSocket.setSoTimeout( HIGH_SPEED_RDT_TIMEOUT );
            cNetFTSocket.connect( m_iaNetFTAddress, RDTPORT );
            DatagramPacket cRDTCommandPacket = 
                    getDatagramPacketFromNetFTRDTCommand( cNetFTCommand );
            cNetFTSocket.send( cRDTCommandPacket );
            return cNetFTSocket;            
        }
        
        /** Tares the current load of the sensor.  
         *  @throws SocketException A SocketException is thrown if there is 
         *  trouble setting up the socket to send the tare command.
         *  @throws IOException An IOException is thrown if there is 
         *  trouble communicating with the sensor. */        
        public void tare() throws SocketException, IOException {
            /* Create a command with mode 0x0042 to tare, count is irrelevant.*/
            NetFTRDTCommand cNetFTCommand = new NetFTRDTCommand(0x0042, 1);
            DatagramSocket cNetFTSocket = new DatagramSocket();
            cNetFTSocket.connect( m_iaNetFTAddress, RDTPORT );
            DatagramPacket cRDTCommandPacket = getDatagramPacketFromNetFTRDTCommand(cNetFTCommand);
            cNetFTSocket.send( cRDTCommandPacket );
            cNetFTSocket.close();
        }
        
        /**Read high speed data from the Net F/T sensor.  This method is not 
         *thread-safe, so take care that you do not perform other operations on
         *the DatagramSocket while this function is executing, i.e. calling
         *stopDataCollection while this function is executing could cause a 
         *"socket is closed" error.
         *@param cNetFTSocket   The socket returned from 
         * startHighSpeedDataCollection.
         *@param iCount         The number of samples to read from the Net F/T
         *sensor.  This can be less than the total number of samples that the
         *Net F/T will output. I.e. you could call startHighSpeedDataCollection
         *with a count of 1000, then call this function 10 times, each time
         *reading 100 samples.
         *@return   An array of NetFTRDTPackets of length iCount, which 
         *represent the F/T records collected from the sensor.  
         *@throws IOException   An IOException will be thrown if there is an
         *error reading data from the Net F/T.
         */
        public NetFTRDTPacket[] readHighSpeedData( 
                DatagramSocket cNetFTSocket, int iCount ) throws IOException{
            
            /*the "raw" RDT packet received from the Net F/T.*/
            DatagramPacket cNetFTRDTPacket = new DatagramPacket( 
                    new byte[NETFT_RDT_DATA_LENGTH], NETFT_RDT_DATA_LENGTH );
            /*the RDT samples received from the Net F/T, and the return
             value*/
            NetFTRDTPacket[] caNetFTRDTPackets = new NetFTRDTPacket[iCount];
            int i; /*generic loop/array index*/
            /*precondition: caNetFTRDTPackets has iCount slots, cNetFTRDTPacket
             *has a byte array with at least NETFT_RDT_DATA_LENGTH slots.
             *postcondition: caNetFTRDTPackets == array of RDT samples received
             *from Net F/T.  i == iCount. cNetFTRDTPacket == the last RDT packet
             *received from the Net F/T.
             */
            for ( i = 0; i < iCount; i++ ){
                cNetFTSocket.receive( cNetFTRDTPacket );    
                caNetFTRDTPackets[i] = 
                        getNetFTRDTPacketFromDatagramPacket( cNetFTRDTPacket );
            }
            return caNetFTRDTPackets;
        }       
        
        public NetFTRDTPacket readLowSpeedData(DatagramSocket cNetFTSocket) throws
                IOException{
            NetFTRDTCommand netFTCommand = new NetFTRDTCommand();
            netFTCommand.setCount( 1 );
            DatagramPacket commandPacket = 
                    getDatagramPacketFromNetFTRDTCommand( netFTCommand );
            cNetFTSocket.send( commandPacket );
            DatagramPacket NetFTRDTDataPacket = new DatagramPacket( 
                    new byte[NETFT_RDT_DATA_LENGTH], NETFT_RDT_DATA_LENGTH );
            cNetFTSocket.receive( NetFTRDTDataPacket );
            
            return getNetFTRDTPacketFromDatagramPacket( NetFTRDTDataPacket );
                    
        }
        /**Stop the Net F/T from outputting any more RDT samples.
         *@param cNetFTSocket   The socket returned by 
         *startHighSpeedDataCollection.  This socket will be closed by this
         *function, so don't use it again!
         *@throws IOException   An IOException will be thrown if there is an
         *error sending the stop command to the Net F/T.
         */
        public void stopDataCollection( DatagramSocket cNetFTSocket ) 
                throws IOException{
            /*An RDT command with mode 0 (stop)*/
            NetFTRDTCommand cNetFTStopCommand = new NetFTRDTCommand(0 , 0);
            DatagramPacket cNetFTStopPacket = 
                    getDatagramPacketFromNetFTRDTCommand( cNetFTStopCommand );
            cNetFTSocket.send( cNetFTStopPacket );
            cNetFTSocket.close();
        }
        
        /**
         * Get the user-friendly NetFTRDTPacket structure from the data received
         * off the network.
         * @param NetFTRDTDataPacket   The DatagramPacket received from the Net
         * F/T sensor.
         * @return The filled NetFTRDTPacket structure
         */
        private NetFTRDTPacket getNetFTRDTPacketFromDatagramPacket( 
                DatagramPacket NetFTRDTDataPacket ){
            
            final int NUM_RDT_FIELDS = 9;
            int[] rdtFields = new int[NUM_RDT_FIELDS]; /*the 9 fields of an RDT
                                           *data packet*/
            byte[] dataBuf = NetFTRDTDataPacket.getData(); /*the received data*/
            
            int i, j; /*loop/array indices*/
            /*precondition: dataBuf has the data received from the network
             *postcondition: rdtFields has the fields of an rdt data packet,
             *in the order RDTSequence, FTSequence, Status, Fx, Fy, Fz, Tx, Ty,
             *and Tz. i = -1, j = 4.
             */
            for ( i = ( NUM_RDT_FIELDS - 1 ); i >= 0; i-- ){
                rdtFields[i] = (int)dataBuf[ (i * 4) ] & 0xff;
                for ( j = ( ( i * 4 ) + 1 ); j < ( ( i * 4 ) + 4 ); j++ )
                {
                    rdtFields[i] = ( rdtFields[i] << 8 ) | ( (int)dataBuf[j] & 
                            0xff );
                }
            }            
            
            return new NetFTRDTPacket( rdtFields );
        }
        
        /**
         * Get the network-sendable DatagramPacket from an RDT command
         * @param netFTCommand     The NetFTRDTCommand to send over the network.
         * @return The DatagramPacket to send to the Net F/T.
         */
        private DatagramPacket getDatagramPacketFromNetFTRDTCommand( 
                NetFTRDTCommand netFTCommand ){
            final int NUM_RDT_COMMAND_FIELDS = 3; /*the number of fields in
                                                   *an RDT command*/
            byte[] dataBuf = new byte[NETFT_RDT_COMMAND_LENGTH]; /*the data
                                                   *buffer of the datagram*/            
            
           dataBuf[0] = (byte)((netFTCommand.getHeader() >> 8) & 0xff);
           dataBuf[1] = (byte)(netFTCommand.getHeader() & 0xff);
           dataBuf[2] = (byte)((netFTCommand.getCommand() >> 8) & 0xff);
           dataBuf[3] = (byte)(netFTCommand.getCommand() & 0xff);
           dataBuf[4] = (byte)((netFTCommand.getCount() >> 24) & 0xff);
           dataBuf[5] = (byte)((netFTCommand.getCount() >> 16) & 0xff);
           dataBuf[6] = (byte)((netFTCommand.getCount() >> 8) & 0xff);
           dataBuf[7] = (byte)(netFTCommand.getCount() & 0xff);
           
           return new DatagramPacket( dataBuf, NETFT_RDT_COMMAND_LENGTH );
           
            
            
        }
        
        /** Get the version of the Net F/T interface.
         *  @return The version of the Net F/T interface.
         */
        public static String getVersion()
        {
            return VERSION;
        }
    
}
