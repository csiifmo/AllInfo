/*
 * NetFTRDTPacket.java
 *
 * Created on February 8, 2006, 2:36 PM
 *
 * 
 */

package com.atiia.automation.sensors;

/**Represents an F/T record received from the Net F/T via RDT.
 *
 * @author Sam Skuce (ATI Industrial Automation)
 */
public class NetFTRDTPacket {
    
    private int m_uiRDTSequence; /*the number of the packet. increments by 
                                      *1 each RDT packet.  actually unsigned.*/
        private int m_uiFTSequence; /*the internal sequence number of the f/t 
                             *data in the RDT packet.  Updated at the internal 
                             *FX rate of the Net F/T.  actually unsigned.*/
        private int m_uiStatus; /*bitmapped status code from the RDT packet.*/
        private int m_iFx; /*the force in the x-axis, in engineering units*/
        private int m_iFy; /*the force in the y-axis, in engineering units*/
        private int m_iFz; /*the force in the z-axis, in engineering units*/
        private int m_iTx; /*the torque in the x-axis, in engineering units*/
        private int m_iTy; /*the torque in the y-axis, in engineering units*/
        private int m_iTz; /*the torque in the z-axis, in engineering units*/
        
        /**Get the RDT sequence number of this packet.  The RDT sequence number
         *increases by one for each packet that is sent, and thus can be used to
         *determine the total number of packets that have been sent by the
         *sensor.
         * @return  RDT sequence number of this packet.
         */
        public long getRDTSequence(){
            return (long)m_uiRDTSequence & 0xffffffffL;
        }
        
        /**Get the FT sequence number of this packet.  The F/T sequence number
         *increases at the internal FX rate of the Net F/T sensor, and thus
         *can be used to time-stamp the data.
         *@return FT sequence number of this packet.
         */
        public long getFTSequence(){
            return (long)m_uiFTSequence & 0xffffffffL;
        }
        
        /**Get the bit-mapped status code of this packet.
         *@return The bit-mapped int status code.
         */
        public int getStatus() {
            return m_uiStatus;
        }
        
        /**Get the force in the x-axis
         *@return The force in the x-axis, in engineering units.
         */
        public int getFx(){
            return m_iFx;
        }
        
        /**Get the force in the y-axis.
         *@return The force in the y-axis, in engineering units.
         */
        public int getFy(){
            return m_iFy;
        }
        
        /**Get the force in the z-axis.
         *@return The force in the z-axis, in engineering units.
         */
        public int getFz(){
            return m_iFz;
        }
        
        /**Get the torque in the x-axis.
         *@return The torque in the x-axis, in engineering units.
         */
        public int getTx(){
            return m_iTx;
        }
        
        /**Get the torque in the y-axis.
         *@return The torque in the y-axis, in engineering units.
         */
        public int getTy(){
            return m_iTy;
        }
        
        /**Get the torque in the z-axis.
         *@return the torque in the z-axis, in engineering units.
         */
        public int getTz(){
            return m_iTz;
        }
        
        /**Get the F/T data in an array of ints.
         *@return A int[] which contains the force and torque data in the
         *order Fx, Fy, Fz, Tx, Ty, Tz.  Data is in engineering units ("counts").
         */
        public int[] getFTArray()
        {
            return new int[] { m_iFx, m_iFy, m_iFz, m_iTx, m_iTy, m_iTz };
        }
        
        /**Create a new NetFTRDTPacket object.
         *@param setRDTSequence     The RDT sequence of this packet.
         *@param setFTSequence      The F/T sequence of this packet.
         *@param setStatus          The bit-mapped status code of this packet.
         *@param setFx              The force in the x-axis, in engineering
         *units.
         *@param setFy              The force in the y-axis, in engineering
         *units.
         *@param setFz              The force in the z-axis, in engineering
         *units.
         *@param setTx              The torque in the x-axis, in engineering
         *units.
         *@param setTy              The torque in the y-axis, in engineering
         *units.
         *@param setTz              The torque in the z-axis, in engineering
         *units.
         */
        public NetFTRDTPacket( int setRDTSequence, int setFTSequence,
                int setStatus, int setFx, int setFy, int setFz, int setTx,
                int setTy, int setTz ){
            
            setRDTPacketValues( setRDTSequence, setFTSequence, setStatus,
                    setFx, setFy, setFz, setTx, setTy, setTz );
        }
        
        /**Set the values of the packet data members
         *@param setRDTSequence     The RDT sequence of this packet.
         *@param setFTSequence      The F/T sequence of this packet.
         *@param setStatus          The bit-mapped status code of this packet.
         *@param setFx              The force in the x-axis, in engineering
         *units.
         *@param setFy              The force in the y-axis, in engineering
         *units.
         *@param setFz              The force in the z-axis, in engineering
         *units.
         *@param setTx              The torque in the x-axis, in engineering
         *units.
         *@param setTy              The torque in the y-axis, in engineering
         *units.
         *@param setTz              The torque in the z-axis, in engineering
         *units.
         */
        private void setRDTPacketValues( int setRDTSequence, int setFTSequence,
                int setStatus, int setFx, int setFy, int setFz, int setTx,
                int setTy, int setTz ){
            m_uiRDTSequence = setRDTSequence;
            m_uiFTSequence = setFTSequence;
            m_uiStatus = setStatus;
            m_iFx = setFx;
            m_iFy = setFy;
            m_iFz = setFz;
            m_iTx = setTx;
            m_iTy = setTy;
            m_iTz = setTz;
        }
        
        /**Create a new NetFTRDTPacket object
         *@param fields     The fields of the RDT data packet, in the order
         *RDTSequence, FTSequence, Status, Fx, Fy, Fz, Tx, Ty, Tz
         */
        public NetFTRDTPacket( int[] fields ){
            setRDTPacketValues( fields[0], fields[1], fields[2], fields[3],
                    fields[4], fields[5], fields[6], fields[7], fields[8]);
        }       
        
    
}
