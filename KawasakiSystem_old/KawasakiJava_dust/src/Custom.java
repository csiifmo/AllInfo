
import javax.swing.JOptionPane;

public class Custom {
	public static String getVali(int i,int ln){
			String s = Integer.toString(i);
			String minusS = "";
			if (i<0){
				s = s.substring(1,s.length());
				minusS = "-";
				ln--;
			}
				
			String tmpS = "";
			if (s.length()<ln){
				for (int j=s.length();j<ln;j++)
					tmpS = tmpS+"0";
				return minusS+tmpS+s;
			}else if( s.length()>ln){
				return minusS+s.substring(0, ln);
			}else return minusS+s;
		}
	  public static String getVald(double d){
			String s = Double.toString(d);
			boolean flgMinus = false;
			if (s.charAt(0)=='-'){
				flgMinus = true;
				s = s.substring(1);
			}
			int pos = s.indexOf('.');
			String afterS = "";
			int afterCnt = s.length()-pos-1;
			for (int i=0;i<3-(s.length()-pos-1);i++){
				afterS = afterS + "0";
			}
			if (afterCnt>3){
				s = s.substring(0,s.length()-afterCnt+3);
			}
			String beforeS = "";
			if (pos<5){
				for (int j=pos;j<5;j++)
					beforeS = beforeS+"0";
			}else if( s.length()>5){
				s = s.substring(pos-5,s.length());
			}
			if (flgMinus)
				return "-"+beforeS+s+afterS;
			else
				return beforeS+s+afterS;
		}
	  public static void showMessage(String message){
			JOptionPane.showMessageDialog(null,
		    		message,
		    		"Output",
		    	    JOptionPane.PLAIN_MESSAGE);	    
		}
}
