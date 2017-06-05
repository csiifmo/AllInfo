package Servers;

import com.atiia.automation.sensors.NetFTRDTPacket;
import com.atiia.automation.sensors.NetFTSensor;
import org.ejml.simple.SimpleMatrix;

import java.io.IOException;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.SocketException;
import java.net.UnknownHostException;


public class ForceSensor {
	String m_strSensorAddress;
    public NetFTSensor m_netFT; /*the Net F/T controller*/
    public NetFTReaderThread m_NetFTReaderThread = null; 
    private DatagramSocket m_cNetFTSlowSocket;
    
    int vals[] = new int[6];
    int rVals[] = new int[7];
    int timeToSleep;
    float o = 0;
    float a = 0;
    float t = 0;
    
    SimpleMatrix [] vArr = new SimpleMatrix[5];
    
    int [] q = new int[6];
    		
    public void setJ(int [] q){
    	System.arraycopy( q, 0, this.q, 0,6 );
    }

    public int [] getVals(){

    	int [] a = new int[6];    	
    	System.arraycopy( vals, 0, a, 0,6 );
    	return a;
    }
    
    public int [] getRVals(){
		processRVals();
    	int [] a = new int[7];    	
    	System.arraycopy( rVals, 0, a, 0,7 );
    	return a;
    }
    
    public void setAngles(float o,float a,float t){
    	this.o = o;
    	this.a = a;
    	this.t = t;
    }
    public void processRVals(){
    	//double mg = 12000;
    	double mg = 0;

    	//System.out.println("Works");
    	SimpleMatrix Ms = KawasakiMatrix.getBaseModification();
    	SimpleMatrix Mf = KawasakiMatrix.getDHM(q).extractMatrix(0, 3,0, 3);
    	//System.out.println(Mf);
    	//SimpleMatrix Mf = SimpleMatrix.identity(4);
    	// �������� �� ��������� ������� ���������� ���������� � ���� �������
    	System.arraycopy( vals, 0, rVals, 0,6 );
    	rVals[0] += 15500;
    	rVals[2] += 16000;


    	double v[][] = {{0},{0},{-mg}};
    	SimpleMatrix V = new SimpleMatrix(v);
    	SimpleMatrix M = Mf.invert();
    	V = M.mult(V);
    	V = Ms.invert().mult(V);
    	for (int i=0;i<3;i++)
    		rVals[i]-=V.get(i,0);
    	// ����������� ��������� �� ������� ������� � �������
    	double v2[][]= {{rVals[0]},{rVals[1]},{rVals[2]}};
    	SimpleMatrix V2 = new SimpleMatrix(v2);
    	V2 = Mf.mult(Ms).mult(V2);
    	for (int i=0;i<3;i++)
    		rVals[i]= (int)V2.get(i,0);
    	// �������
    	rVals[3] += 340;
    	rVals[4] += 180;
    	rVals[5] -= 521;
    	// ������ ������� ���� �������
    	double rg[][] = {{0},{0},{0.07}};
    	SimpleMatrix Rg = new SimpleMatrix(rg); 
    	SimpleMatrix M2 = KawasakiMatrix.getDHM(q).extractMatrix(0, 3, 0, 3);
    	Rg = M2.mult(Rg);    	
    	double vMg[][] = {
    			{mg*Rg.get(1,0) - 0*Rg.get(2,0)},
    			{0 *Rg.get(2,0) - mg*Rg.get(0,0)},
    		 	{0 *Rg.get(0,0) - 0 *Rg.get(1,0)}
    	};
    	SimpleMatrix M3 = KawasakiMatrix.getDHM(q).mult(KawasakiMatrix.getBaseModification4x4());
    	SimpleMatrix VMg = new SimpleMatrix(vMg);
    	VMg = M3.extractMatrix(0, 3, 0, 3).invert().mult(VMg);
    	for (int i=0;i<3;i++){
    		rVals[i+3]+= VMg.get(i,0);
    	}
    	double vecM[][] = {{rVals[3]},{rVals[4]},{rVals[5]}};
    	
    	SimpleMatrix VecM = new SimpleMatrix(vecM);
    	VecM = KawasakiMatrix.getBaseModification().mult(VecM);
    	VecM = KawasakiMatrix.getCurDHMbyQ(6, q[5]).extractMatrix(0, 3, 0, 3).mult(VecM);
    	for (int i=0;i<4;i++){
    		vArr[i] = new SimpleMatrix(VecM); 
    		rVals[3+i] = (int)VecM.get(2,0);
    		VecM.set(2, 0, 0);    		
    		VecM = KawasakiMatrix.getCurDHMbyQ(5-i, q[4-i]).extractMatrix(0, 3, 0, 3).mult(VecM);
    	}
    	//rVals[6] = -rVals[6];
    	
    	// ������������� �������� �� ��������
    	

    }
    
    public SimpleMatrix[] getVecs(){
    	return vArr;
    }
    // ����������� �� ���������   
	public ForceSensor(){
    	m_strSensorAddress = "192.168.1.1";
    }
    // ����������� �� ����������� ip
	ForceSensor(String ip){
    	m_strSensorAddress = ip;
    }
   
    public void start(int timeToSleep){
    	this.timeToSleep = timeToSleep;
    	 // ���� ������ ��� ���� ��������
    	 if ( null != m_NetFTReaderThread ){
    		 // ������������� ���
             m_NetFTReaderThread.stopReading();   
             m_NetFTReaderThread = null;
         }
         try{
        	 // ������������ � �������
             m_netFT = new NetFTSensor( InetAddress.getByName(
                                        m_strSensorAddress ) );
         } catch ( UnknownHostException uhex ){     
        	 System.out.println("������ ����������� � �������");
             return;
         }   
         try{
             m_cNetFTSlowSocket = m_netFT.initLowSpeedData();
         }catch ( SocketException sexc ){
        	 System.out.println("������ ����������� � ������");       
         }catch ( IOException iexc ){
        	 System.out.println("������ �����/������");
         }
         // ������ � ��������� ����� ������ ������ � �������
         m_NetFTReaderThread = new NetFTReaderThread( m_netFT);        
         m_NetFTReaderThread.start();
    }
    public void stop(){
    	// ���� ��� ������ �����
    	if(m_NetFTReaderThread!=null)
    		m_NetFTReaderThread.stopReading();
    	System.out.println("Sensor stopped");
    }
	
	
	public class NetFTReaderThread extends Thread{
	    
	    private NetFTSensor m_netFT;
	    private boolean m_bKeepGoing = true;
	    
	    public NetFTReaderThread( NetFTSensor setNetFT){
	        m_netFT = setNetFT;
	    }   
	    public void stopReading(){
	        m_bKeepGoing = false;
	        this.interrupt();
	    }
	    @Override
	    public void run(){
	        NetFTRDTPacket cRDTData; /*the latest f/t data from the Net F/T*/
	        while ( m_bKeepGoing ){                
	            try{
	                Thread.yield(); 
	                synchronized ( m_netFT ){	       
	                    cRDTData = m_netFT.readLowSpeedData(m_cNetFTSlowSocket);               
	                }
	                dispData( cRDTData );
	            }catch ( SocketException sexc ){
	            }catch ( IOException iexc ){
	                           
	            }
	            try{           
	                    Thread.sleep(timeToSleep);
	            }catch ( java.lang.InterruptedException iexc ){
	            }
	            
	        }
	    }
	    public SimpleMatrix calcRMatrix(int o,int a,int t){
	    	return new SimpleMatrix();
	    }
	    
	    public void dispData(NetFTRDTPacket displayRDT){
	    	vals[0] = displayRDT.getFx()/1000;
	    	vals[1] = displayRDT.getFy()/1000;
	    	vals[2] = displayRDT.getFz()/1000;
	    	vals[3] = displayRDT.getTx()/1000;
	    	vals[4] = displayRDT.getTy()/1000;
	    	vals[5] = displayRDT.getTz()/1000;
	    	processRVals();
	    }
	}
	

}
