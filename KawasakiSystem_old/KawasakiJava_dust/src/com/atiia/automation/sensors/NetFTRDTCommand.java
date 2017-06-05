/*
 * NetFTRDTCommand.java
 *
 * Created on February 8, 2006, 2:38 PM
 *
 * 
 */

package com.atiia.automation.sensors;

/**Represents an RDT request command from the host to the Net F/T sensor.
 *
 * @author Sam Skuce (ATI Industrial Automation)
 */
public class NetFTRDTCommand {
    
    /*all these items should be thought of as unsigned, even though Java doesn't
     *include built-in unsigned types (grumble, grumble)*/
        private final short m_fusHeader = 0x1234; /*header message*/
        private short m_usCommand = 1; /*nonzero = start in specified mode, 
         0 = stop*/
        private int m_uiCount = 0; /*number of packets to output (0 = infinite).
         *don't forget to think of it as unsigned*/
        
        /**Gets the header of the RDT command packet
         *@return The header of the RDT packet.  This is always 0x1234
         */
        public int getHeader(){
            return (int)m_fusHeader & 0xffff;
        }
        
        /**sets the command mode of the rdt command
         * @param newCommand    the int command to set (1 = main-loop-driven,
         * 2 = interrupt-driven, 0 = stop)
         */
        public void setCommand( int newCommand ){
            m_usCommand = (short)(newCommand & 0xffff); /*remember, the data 
             *packet uses unsigned data, which is why we had to use an int for 
             *the newCommand argument*/
        }
        
        /**get the mode of the RDT command
         *@return 0 = stop command, 1= loop driven output (default), 2 =
         *interrupt driven output.  Returns int even though underlying data 
         *member is a short, because the command is actually unsigned integer 
         *from the Net F/T's perspective.
         */
        public int getCommand(){
            return (int)m_usCommand & 0xffff;
        }
        
        /**Set the number of RDT packets to output
         * @param  newCount the long number of RDT packets to output (0 = 
         * infinite). Cannot be greater then largest unsigned four-byte 
         * integer.
         */
        public void setCount( long newCount ){
            m_uiCount = (int)(newCount & 0xffffffffL);
        }
        
        /**Get the number of RDT samples to output
         *@return Number of samples to output.  0 = infinite (default). 
         */
        public long getCount(){
            return (long)m_uiCount & 0xffffffffL;
        } 
        
        /**Create a new NetFTRDTPacket with default field values.  The mode will
         *be 1 (loop-driven output), and the count will be 0 (infinite samples)
         */
        public NetFTRDTCommand(){
            /*do nothing, defaults already set.*/
        }
        
        /**Create a new NetFTRDTCommand with specific field values.
         *@param command    The mode to set.  0 = stop, 1 = loop-driven output
         * (good for requesting single packets), 2 = interrupt-driven output
         * (good for requesting a lot of data at high speed)
         *@param count      The number of samples to output.  A value of 0 will
         *cause the Net F/T to output samples until it is sent another command
         *with the mode field set to 0 (stop mode).  This value is sent to the
         *Net F/T as an unsigned four-byte integer, so the largest possible
         *value is 4294967296 ( 2 ^ 32 ).
         */
        public NetFTRDTCommand( int command, long count ){
            setCommand( command );
            setCount( count );
        }
    
}
