import java.io.*;
import java.net.*;
import java.util.Timer;
import java.util.TimerTask;
 
class CamSocket {
	Socket socket;
	InputStream sin;
	OutputStream sout;
	DataInputStream in;
    DataOutputStream out;
	Timer time = new Timer();
	boolean flgOpenSocket = false;
	String address;
	int port;
	CamSocket(){
	   
	}
	public void openSocket(String address, int port){
		try{      
        	InetAddress ipAddress = InetAddress.getByName(address); // ������� ������ ������� ���������� ������������� IP-�����.
            socket = new Socket(ipAddress, port); // ������� ����� ��������� IP-����� � ���� �������.
            // ����� ������� � �������� ������ ������, ������ ����� �������� � �������� ������ ��������. 
            sin = socket.getInputStream();
            sout = socket.getOutputStream();
            in = new DataInputStream(sin);
            out = new DataOutputStream(sout);
	        Custom.showMessage("Socket connected");
	        flgOpenSocket = true;
	      } catch(Exception x) { 
	    	  x.printStackTrace(); 
	    	  Custom.showMessage("Socket open error");  
	     }
   	 	 time.schedule(new TimerTask() {
	        @Override
	        public void run() { //������������� ����� RUN � ������� ������� �� ��� ��� ����
	        		getChars();	
	        }
	     }, 100, 100);	
	}
	
	public void closeSocket(){			
		if (flgOpenSocket){
		System.out.println("Close Cam Socket");
		flgOpenSocket = false;
				
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
			Custom.showMessage("Socket closed");
			
		}
	}
	public int[] getVals(){
		return vals;
	}
    int pos = 0;
    int arr[]=new int[4];
    int valPos = 0;
    int [] vals= new int[6];
    
    private void getChars(){	    
    	if (flgOpenSocket){
      	   if (!socket.isConnected()){
      		   Custom.showMessage("Client disconnected");
      		 closeSocket();
      	   }else
      	   try {   
      		   while(in.available()!=0){
      			   byte b = in.readByte();
      			   arr[pos]= 0xFF & b;
      			   pos++;
      			   if (pos==4){
      				   pos = 0;
      				   int res = 0;
      				   for (int i=3;i>=0;i--){ 
      					   res=res*256+arr[i];
      				   } 
      				   vals[valPos]=res;
      				   valPos++;
      				   if(valPos>=6){
      					   valPos =0;
      					   System.out.print("vals: ");
      					   for (int i=0;i<6;i++)
      						  System.out.print(vals[i]+" ");
      					   System.out.println();
      				   }
      			   }
      		   }
      	   } catch (IOException e) {
      		   e.printStackTrace();
      	   }
    	}
    }
    
}