import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.net.Socket;
import java.nio.ByteBuffer;
import java.nio.IntBuffer;
import java.util.Timer;
import java.util.TimerTask;

public class Hand {
	Socket soc;
	DataOutputStream dout;
	DataInputStream din;
	DataInputStream in;
    DataOutputStream out;
	Timer time = new Timer();
	boolean flgOpenSocket = false;
	float [] powArr = new float[6];
	Hand(){
		
	}
	// ìåæäó ïàëüöàìè 0-90
	// îñòàëüíûå +90...-90
	// ñêîğîñòü 0...83		
	
	public void openSocket(){
		try {
			soc=new Socket("localhost",2005);
			dout=new DataOutputStream(soc.getOutputStream());
			din = new DataInputStream(soc.getInputStream());
			flgOpenSocket = true;
			in = new DataInputStream(din);
            out = new DataOutputStream(dout);
			time.schedule(new TimerTask() {
		        @Override
		        public void run() { //ÏÅĞÅÇÀÃĞÓÆÀÅÌ ÌÅÒÎÄ RUN Â ÊÎÒÎĞÎÌ ÄÅËÀÅÒÅ ÒÎ ×ÒÎ ÂÀÌ ÍÀÄÎ
		        	getChars();	
		        }
		     }, 100, 100);	
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} 		
		
	}	
	
	public void sendCommand(int com, int[] params){
		String s = " "+com;
		switch (com) {
		case 0:
			break;
		case 1:
			for (int i=0;i<7;i++)
				s+=" "+params[i];
			break;
		}	
		try {
			dout.writeUTF(s);
			dout.flush();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}		
	}
	float [] getPowers(){
		return powArr;
	}
	public void closeSocket(){
		int [] a={0};
		try {
			sendCommand(0,a);
			dout.close();
			soc.close();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}  
		
	}
	
	private void getChars(){
		try {
			String s = "";
			while(in.available()!=0){
				byte b  = in.readByte();  
				s += (char)b;				   
			}
			//System.out.println(s);
			//if (s.length()>0)
			//	System.out.println(s.charAt(0)+" "+s.charAt(1));
			if (s.length()>0 &&s.charAt(0)=='1') {
				s = s.substring(3,s.length());
				//while(s.indexOf("  ") >= 0) {
				//	   s.replace("  ", " ");
				//	}
				System.out.println(s);
				String sarr[] = s.split(":");
				for (int i=0;i<sarr.length;i++){
					powArr[i] = Float.parseFloat(sarr[i]);
				}
			}
			
			
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
    }
	
	

}
