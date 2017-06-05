import java.util.ArrayList;

public class JPoints {
	final static String ABSOLUTE="abs";
	private ArrayList <JPoint> pointList = new ArrayList<JPoint>();
	
	public class JPoint{
		int j1;
		int j2;
		int j3;
		int j4;
		int j5;
		int j6;
		String type;
		int speed;
		public JPoint() {
				this.j1 = 0;
				this.j2 = 0;
				this.j3 = 0;
				this.j4 = 0;
				this.j5 = 0;
				this.j6 = 0;
				this.speed = 1;
				this.type = ABSOLUTE;
		}
		public JPoint(int j1,int j2,int j3,int j4,int j5,int j6,String type,int speed){
			this.j1 = j1;
			this.j2 = j2;
			this.j3 = j3;
			this.j4 = j4;
			this.j5 = j5;
			this.j6 = j6;
			this.speed = speed;
			this.type = type;
		}
	}

	public void add(int j1,int j2,int j3,int j4,int j5,int j6,String type,int speed){
		pointList.add(new JPoint(j1,j2,j3,j4,j5,j6,type,speed));
	}
	public ArrayList <String> getRequests(){
		if (pointList.size()!=0){
			ArrayList <String> lst = new ArrayList<String>();
			for (JPoint point:pointList){
				String s = "000000 000005";
				s +=" "+Custom.getVali(point.speed,6);
				s +=" "+Custom.getVali(point.j1,6);
				s += " "+Custom.getVali(point.j2,6);
				s += " "+Custom.getVali(point.j3,6);
				s += " "+Custom.getVali(point.j4,6);
				s += " "+Custom.getVali(point.j5,6);
				s += " "+Custom.getVali(point.j6,6);
				s += " ";
				//System.out.println("add: "+s);
				lst.add(s);
			}			
			return lst;
		}else{
			return null; 
		}		
	}
	public void clear() {
		pointList.clear();		
	}
}
