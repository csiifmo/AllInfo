import java.awt.List;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.PrintWriter;
import java.net.InetAddress;
import java.net.Socket;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Deque;
import java.util.HashSet;
import java.util.LinkedList;
import java.util.Timer;
import java.util.TimerTask;
import java.util.Vector;

import javax.naming.ldap.HasControls;
import javax.sound.midi.ShortMessage;
import javax.swing.JOptionPane;

import org.ejml.simple.SimpleMatrix;

public class ClientSocket {
	final static int C_STOP = 4;// ���������
	final static int C_J = 5; //���������� ���������� ��������
	final static int C_GetPositionAxis = 6; //�������� ��������� ���
	final static int C_GetPosition = 7; //�������� ��������� ����������
	final static int C_J_POINT = 8; //���������� �� ����
	final static int C_D_POINT = 9; //���������� �� �����������
	final static int C_HOME1 = 10; //����� � �������� ���� 1
	final static int C_HOME2 = 11;// ����� � �������� ���� 2
	final static int C_ERR = 12; // ������
	final static int C_DRAW = 13; //��������
	final static int C_SET_POS = 14; //������� �� �����
	final static int C_SET_DELTA_POS = 15;  // ������� �� ��������
	final static int C_DELTA_POS_ENABLE = 16; // ��������� �������� �� �������� �������
	final static int C_DELTA_POS_DISABLE = 17; // ��������� �������� �� �������� �������
	final static int C_SENSOR_VALS = 18; // �������� � �������
	final static int C_START_GRAVITY_PROGRAM = 19; // ��������� ����������
	final static int C_GRAVITY_PROGRAM_OFF = 20; // ��������� ����������
	final static int C_U_REGULATOR = 21; // ����� ��������� ����������
	final static int C_ERR_REGULATOR = 22; // ������: ������������ � ����������������
	final static int C_CHANGE_GRAVITY_MODE = 25; // ��������� ������ ������� ���������
	final static int ERR_INRANGE_J1 = 1; //�� ������� 1 �� �������
	final static int ERR_INRANGE_J2 = 2; //�� ������� 2 �� �������
	final static int ERR_INRANGE_J3 = 4; //�� ������� 3 �� �������
	final static int ERR_INRANGE_J4 = 8; //�� ������� 4 �� �������
	final static int ERR_INRANGE_J5 = 16; //�� ������� 5 �� �������
	final static int ERR_INRANGE_J6 = 32; //�� ������� 6 �� �������
	final static int ERR_NOT_INRANGE = 32786; //��� ������������
	final static int C_SET_PARAMS = 23; // ��������� ����������
	final static int C_IN_POS = 24; // ����� �� �������
	final static int C_POWER_LOG = 26; // ��� ���������� �� �����
	
	final static int X_COORD = 0;
	final static int Y_COORD = 1;
	final static int Z_COORD = 2;
	final static int O_COORD = 3;
	final static int A_COORD = 4;
	final static int T_COORD = 5;
	
	double d1 = 430;
	double d2 = 450;
	double d3 = 450;
	double d4 = 100;
	double d5 = 10;
	FileWriter outF;
	
	final static int[] ULIMIMT = { 160,  140,  120,  270,  145,  360};
	final static int[] LLIMIMT = {-160, -105, -155, -270, -145, -360};
	
	int port=40000;
	final Timer time = new Timer();
	final Timer sensorTime = new Timer();
	
	boolean flgOpenSocket = false;
	
	
    Socket socket;
	Sensor sensor;
    InputStream sin;
    OutputStream sout;
    DataInputStream in;
    DataOutputStream out;
    
    String inStr = "";
    int coordArr[] = new int[6];
    JPoints jp= new JPoints();
    LinkedList<String> fifo = new LinkedList<String>();
    public void flush(){
    	try {
			out.flush();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
    }
    int pos = 0;
    boolean flgInPosition = false;
    boolean flgSpace = false;
    boolean flgFirstSpace = true;
    int [] lst = new int[9];
    int rotations[] = new int [6];
    int positions[] = new int [6];
    int rVals[] = new int[6];
    int vals[] = new int[6];
    
    int errors[] = new int[6];
    int uregs[] = new int[6];
    
    PrintWriter writer;
    boolean flgOpenLog = false;
    
    public void processTest(int testPos){
    	switch(testPos){
    	case 0:
    		setParams(10,10,15,100,10,10);
    		runInPointA(-27, 20, -73, 181, 77, -10, 0);    		
    		break;    			
    	case 1:
    		setParams(10,10,3,100,10,10);
    		runInPointA(-135, 20, -73, 181, 77, -10, 0);
    		setParams(10,10,5,100,10,10);
    		runInPointA(-135, 82, -14, 181, 77, -10, 0);
    		break;    		
    	case 2:
    		setParams(10,10,10,100,10,10);    		
    		runInPointA(-135, 18, -36, 181, 77, -10, 0);
    		runInPointA(40, 40, -36, 181, 77, -10, 0);
    		runInPointA(40, 81, -19, 181, 77, -10, 0);  
    		break;
    	
    	}
    }
    public void openLog(String path){
    	try{
    		writer = new PrintWriter(new File(path));
    		flgOpenLog = true;
    		writer.println("x y z o a t kEx kEy kEz iEx iEy iEz kUx kUy kUz iUx iUy iUz");
    	}catch (IOException e ){
    		e.printStackTrace();
    	}
    }
    public void closeLog(){
    	writer.close();
    	flgOpenLog = false;
    }
    public void setParams(int accel,int deccel,int speed,int mmps,int delta,int maxDeltaPos){
    	int [] arr  = {0,C_SET_PARAMS,0,accel,deccel,speed,mmps,delta,maxDeltaPos};   
    	sendVals2(arr);  
    }
    private void writeStatsToLog(){
    		for (int i=0;i<6;i++){
    			writer.print(positions[i]+" ");
    		}
    		writer.print(' ');
    		for (int i=0;i<6;i++){
    			writer.print(errors[i]+" ");
    		}
    		writer.print(' ');
    		for (int i=0;i<6;i++){
    			writer.write(uregs[i]+" ");
    		}
    		writer.println();
    }
    
    public int [] getRotations(){
    	return Arrays.copyOf(rotations,6);
    }
    public int [] getPositions(){
    	return Arrays.copyOf(positions,6);
    }
    public void processRVals(){	
		//double arrayV[][] = {{vals[0],vals[1],vals[2]}}; 
		//SimpleMatrix V = new SimpleMatrix(arrayV);
		//SimpleMatrix Vn = V.mult(getMatrix3x3M());
		//rVals[0] =  (int)Vn.get(0,0);
		//rVals[1]  = (int)Vn.get(0,1);
		//rVals[2]  = (int)Vn.get(0,2);
    }
   
    
  
    
    public void runInPointD(int j1,int j2,int j3,int j4,int j5,int j6,int speed){
    	int [] arr  = {0,C_D_POINT,speed,j1,j2,j3,j4,j5,j6};   
    	sendVals2(arr);
    }
    public void runInPointD(int[] arrIn,String type,int speed){
    	int [] arr  = {0,C_D_POINT,speed,arrIn[0],arrIn[1],arrIn[2],arrIn[3],arrIn[4],arrIn[5]};   
    	sendVals2(arr);
    }
    public void drawPointD(int[] arrIn,String type,int speed){
    	int [] arr  = {0,�_DRAW,speed,arrIn[0],arrIn[1],arrIn[2],arrIn[3],arrIn[4],arrIn[5]};   
    	sendVals2(arr);
    }
    
    public void runInPointA(int j1,int j2,int j3,int j4,int j5,int j6,int speed){
    	int [] arr  = {0,C_J_POINT,speed,j1,j2,j3,j4,j5,j6};   
    	sendVals2(arr);
    }
    
    public void runInDeltaPointA(int j1,int j2,int j3,int j4,int j5,int j6,int speed){
    	int [] arr  = {0,C_J,speed,j1,j2,j3,j4,j5,j6};   
    	sendVals2(arr);
    }
     
    public void setPoint(int [] coords, int speed){
    	int [] arr  = {0,C_SET_POS,speed,coords[0],coords[1],coords[2],coords[3],coords[4],coords[5]};   
    	sendVals2(arr);    	
    }
    public void setDelta(int [] coords, int speed){
    	int [] arr  = {0,C_SET_DELTA_POS,speed,coords[0],coords[1],coords[2],coords[3],coords[4],coords[5]};   
    	sendVals2(arr);    	
    }
    public void home1(){
    	int [] arr  = {0,C_HOME1,0,0,0,0,0,0,0};
		sendVals2(arr);
    }
    
    public void enableDelta(){
    	int [] arr  = {0,C_DELTA_POS_ENABLE,1,2,0,0,0,0,0};   
    	sendVals2(arr);  
    }
    public void disableDelta(){
    	int [] arr  = {0,C_DELTA_POS_DISABLE,1,2,0,0,0,0,0};   
    	sendVals2(arr);  
    }
    
    public void home2(){
    	int [] arr  = {0,C_HOME2,0,0,0,0,0,0,0};
		sendVals2(arr);
    }
    public int[] getSensorVals(){
    	return sensor.getVals();
    }
    public int[] getSensorRVals(){
    	return rVals;
    }
    public void getChars(){
    	if (flgOpenSocket){ 	        		
      	   if (!socket.isConnected()){
      		   Custom.showMessage("Client disconnected");
      		   closeSocket();
      	   }else
      	   try {
      		   if(flgOpenSocket){ 	        			  
      			   while(in.available()!=0){	
      				 
      				   char c = (char)in.readByte();      				   
      				   if (c==' '){
      					   if (!flgSpace&&!flgFirstSpace){
      						   pos++;
      						   lst[pos-1] = Integer.parseInt(inStr);
      						   inStr = "";
      						   if (pos>=9){
      							   switch(lst[1]){
      							   		case  C_GetPositionAxis:
      							   			for (int i=0;i<6;i++)
      							   				rotations[i]=lst[i+3];
      							   			sensor.setJ(rotations);
      							   		break;
      							   		case  C_GetPosition:
      							   			for (int i=0;i<6;i++)
      							   				positions[i]=lst[i+3];
  							   			break;
      							   		case C_ERR:
      							   			switch (lst[2]){
      							   				case ERR_NOT_INRANGE:
      							   					Custom.showMessage("�������� ����� ��������� ��� ������������");		
      							   				break;
      							   			}
      							   		break;
      							   		case C_U_REGULATOR:
      							   			for (int i=0;i<6;i++){
      							   				uregs[i]=lst[i+3];
      							   			}
      							   			break;
      							   		case C_ERR_REGULATOR:
      							   			for (int i=0;i<6;i++){
      							   				errors[i]=lst[i+3];
      							   			}
      							   			if (flgOpenLog)writeStatsToLog();
      							   			break;
      							   		case C_IN_POS:
      							   			flgInPosition = true;
      							   			break;
      							   			
      							   		case C_POWER_LOG:
      							   			switch (lst[2]){ 
      							   				case 0:
      							   					for (int i=0;i<5;i++)
      							   						outF.write(lst[i+2]+" ");      					          
      							   					break;
      							   				case 1:			
      							   					for (int i=0;i<5;i++)
      							   						outF.write(lst[i+2]+" ");     					          
      							   					break;
      							   				case 2:
      							   					for (int i=0;i<5;i++)
      							   						outF.write(lst[i+2]+" ");     					          
      							   					outF.append('\n');      						            
      							   					outF.flush();
      							   					break;
      							   			}
      						                break;      						         
      							   }
      							   pos = 0;
      						   }
      					   }
      					   flgSpace = true;      					   
      				   }else{
      					   inStr += c;
      					   flgSpace = false; 
      					   flgFirstSpace = false;
      				   }
      				
      			   }
      		   }
      	   } catch (IOException e) {
      		   e.printStackTrace();
      	   }
    	}
    }
    public boolean getInPosition(){
    	if (flgInPosition){
    		flgInPosition = false;
    		return true;
    	}else{
    		return false;
    	}
    }
    boolean flgCom = false;
    int cntEnabled = 0;
    final int MAX_POWER_VAL = 10000;
    public ClientSocket() {
    	sensor = new Sensor();
    	sensor.start(100);
    	 time.schedule(new TimerTask() {
 	        @Override
 	        public void run() { //������������� ����� RUN � ������� ������� �� ��� ��� ����
 	        		getChars();	
 	        }
 	    }, 200, 200); //(4000 - ��������� ����� ������� � �������, ���������� 4 ������� (1 ��� = 1000 �������))
    	sensorTime.schedule(new TimerTask() {
  	        @Override
  	        public void run() { //������������� ����� RUN � ������� ������� �� ��� ��� ����
  	        	int arrS[] = sensor.getRVals();
  	        	for (int i=0;i<6;i++){
  	        		vals[i]=arrS[i];
  	        	}
  	        	processRVals();
  	        	int max = 3;
  	        	for (int i=4;i<7;i++){
  	        		if (Math.abs(arrS[i])>Math.abs(arrS[max]))
  	        			max = i;       			
  	        	}
  	        	//for (int i=3;i<7;i++){
  	        	//	if(i!=max) arrS[i] = 0;
  	        	//}  	    
  	        	boolean flgE = false;
  	        	for (int i=0;i<3;i++){
  	        		if (arrS[i]>MAX_POWER_VAL)
  	        			flgE = true;
  	        	}
  	        	if (flgE){
  	        		cntEnabled++;  	        		
  	        	}else{
  	        		if (cntEnabled<6&&cntEnabled>0){
  	        			System.out.println(arrS[0]+" "+arrS[1]+" "+arrS[2]);
  	        			//sendChangeGravity();
  	        		}
  	        		cntEnabled = 0;
  	        	}
  	        	int [] arr  = {0,C_SENSOR_VALS,0, -arrS[0]/100, arrS[1]/100, -arrS[2]/100, arrS[3]/100, arrS[4]/100, arrS[5]/100};   
  	        	sendVals2(arr);
  	        }
  	    }, 0, 50);
    	try {
			outF = new FileWriter("C:\\Programming\\Kawasaki\\log\\notes3.txt", false);
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
         
	}
	
	void sendChangeGravity(){
		int [] arr  = {0,C_CHANGE_GRAVITY_MODE,0,0,0,0,0,0,0};
		sendVals2(arr);
	}
    void close(){
    	sensor.stop();
    }
    void moveD(int[] arr){   
    	System.out.println("arr:"+ arr[0]+" "+arr[1]+" "+arr[2]);
    	int [] positionsN = Arrays.copyOf(positions, 6);
    	boolean flgMove = false;
    	for (int i=0;i<3;i++){
    		positionsN[i] = positions[i]+arr[i];
    		runInPointD(positionsN[0], positionsN[1], positionsN[2], 
    					positionsN[3], positionsN[4], positionsN[5], 10);
    	}
    }
    
    void startGravityProgram(int[]minVals){
    	int [] arr  = {0,C_START_GRAVITY_PROGRAM,0,minVals[0],minVals[1],minVals[2],minVals[3],minVals[4],minVals[5]};
		sendVals2(arr);
    }
    void startGravityProgram(int k, int i,int min){
    	int [] arr  = {0,C_START_GRAVITY_PROGRAM,min,k,k,k,i,i,i};
		sendVals2(arr);
    }
    
    void stopGravityProgram(){
    	int [] arr  = {0,C_GRAVITY_PROGRAM_OFF,0,0,0,0,0,0,0};
    	sendVals2(arr);
    }
   
    void stopSensor(){
    	sensor.stop();
    }
    void startSensor(){
    	sensor.start(100);
    }
	void sendVals(int []iVal, double []fVal){
		if(flgOpenSocket){
			String s=Custom.getVali(iVal[0],6)+" "+Custom.getVali(iVal[1],3)+" "+Custom.getVali(iVal[2],4)+" ";
			for (double a:fVal){
				s = s+Custom.getVald(a)+" ";
			}
			s = s.substring(0,s.length()-1);
			sendPackage(s);
		}
	}
	void sendVals(int []iVal){
		if(flgOpenSocket){
			String s="";
			for(int i=0;i<9;i++)
				s+=(char)((byte)'a'+i)+Custom.getVali(iVal[i],6);			
			s+="/";
			sendPackage(s);
		}
	}
	
	void sendVals2(int []iVal){
		if(flgOpenSocket){
			String s="";
			for(int i=0;i<9;i++)
				s+=Custom.getVali(iVal[i],6)+" ";			
			//s+="/"
			sendPackage(s);
		}
	}
	String prevRec = "";
	void sendPackage(String s){
		
		try {
			prevRec = s;
			//System.out.println(s.length()+"");
			//System.out.println(s);
			for (int i=0;i<s.length();i++){
				out.writeByte((byte)s.charAt(i));	
			}		
			
			//out.writeUTF(s);
			//if(!s.contains("000000 000018 000001"))
			//System.out.println("sended:"+s);
		} catch (IOException e) {
			System.out.println("IO Error");
			e.printStackTrace();
		} 
	}
	void openSocket(String adress,String port){
	    try {
	    	InetAddress ipAddress = InetAddress.getByName(adress); // ������� ������ ������� ���������� ������������� IP-�����.
            socket = new Socket(ipAddress, Integer.parseInt(port)); // ������� ����� ��������� IP-����� � ���� �������.
            // ����� ������� � �������� ������ ������, ������ ����� �������� � �������� ������ ��������. 
            sin = socket.getInputStream();
            sout = socket.getOutputStream();
            // ������������ ������ � ������ ���, ���� ����� ������������ ��������� ���������.
            in = new DataInputStream(sin);
            out = new DataOutputStream(sout);
	        flgOpenSocket = true;
	        Custom.showMessage("Socket connected");
	      } catch(Exception x) { 
	    	  x.printStackTrace(); 
	    	  Custom.showMessage("Socket open error");  
	     }
	}	
	void closeSocket(){
		int [] arr  = {0,C_STOP,0,0,0,0,0,0,0};
		//getChars();
		sendVals2(arr);
		if (flgOpenSocket)
		try {	
			in.close();
			sin.close();
			out.close();
			sout.close();
			socket.close();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		flgOpenSocket = false;
		Custom.showMessage("Socket closed");
		try {
			outF.close();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}		
	}
	public void addJPoint(int j1,int j2,int j3,int j4,int j5,int j6,String type,int speed){
		if (speed<=0) speed = 1;
		jp.add(j1,j2,j3,j4,j5,j6,type,speed);
	}
	public void sendJPoints(){
		ArrayList<String> lst = jp.getRequests();
		if (lst!=null){
			for (String s:lst){
				sendPackage(s);
			}
		}else{
			Custom.showMessage("��� �� ����� ����� �� ��������");
		}
	}
	public void clearJPoints(){
		jp.clear();
	}
	public void test(){
		if(flgOpenSocket)
			System.out.println("Test Operation");
		else
			System.out.println("Socket is closed");	
	}

}
