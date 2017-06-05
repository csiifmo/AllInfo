import java.awt.Color;

import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Event;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.events.ControlEvent;
import org.eclipse.swt.events.ControlListener;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.widgets.ProgressBar;
import org.eclipse.swt.widgets.Text;
import org.ejml.simple.SimpleMatrix;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Listener;
import org.eclipse.swt.widgets.Menu;
import org.eclipse.swt.widgets.MenuItem;
import org.eclipse.swt.widgets.Spinner;
import org.eclipse.swt.widgets.Slider;
import org.eclipse.swt.widgets.Group;

public class MainWindow {
	
	Runnable timer;
	Display display;
	ClientSocket client; 	
	boolean flgFirstRotGet = true;
	boolean flgFirstPosGet = true;
	boolean flgUseMatrix = true;
	CamSocket camSocket;
	Hand hand;
	
	int testPos = 0;
	public void onTime(){
		setSensorProgress();
		setSensorText();		
		setAngleText();
		setRotations();
		setDekart();
		setMatrix4x4();
		setVectorVals();
		setCam();
		setVectors();
		setHandPowers();
		if (client.getInPosition()){
			setSliders();
		}
		int pos [] = client.getPositions();
		client.sensor.setAngles(pos[3], pos[4], pos[5]);
	}
	
	public void setVectors(){
		SimpleMatrix m [] = client.sensor.getVecs();
		textVArr1x.setText(Math.floor(m[0].get(0,0))+"");
		textVArr1y.setText(Math.floor(m[0].get(1,0))+"");
		textVArr1z.setText(Math.floor(m[0].get(2,0))+"");
		
		textVArr2x.setText(Math.floor(m[1].get(0,0))+"");
		textVArr2y.setText(Math.floor(m[1].get(1,0))+"");
		textVArr2z.setText(Math.floor(m[1].get(2,0))+"");
		
		textVArr3x.setText(Math.floor(m[2].get(0,0))+"");
		textVArr3y.setText(Math.floor(m[2].get(1,0))+"");
		textVArr3z.setText(Math.floor(m[2].get(2,0))+"");
		
		textVArr4x.setText(Math.floor(m[3].get(0,0))+"");
		textVArr4y.setText(Math.floor(m[3].get(1,0))+"");
		textVArr4z.setText(Math.floor(m[3].get(2,0))+"");
	}
	
	public void init(){
		 
		 final int time = 100;
		 timer = new Runnable() {
			 public void run() {
				 onTime();
		         display.timerExec(time, this);
		         
		     }
		 };
		 display.timerExec(time, timer);
		 client = new ClientSocket();
		 camSocket = new CamSocket();
		 hand = new Hand();
		 hand.openSocket();
		// client.openSocket("192.168.1.0","40000");
		 //camSocket.openSocket("192.168.1.101",5005);
		 int pos [] = client.getPositions();
		 
		 
		 
		 sliderDX.setSelection(pos[0]+1000);
		 sliderDY.setSelection(pos[1]+1000);
		 sliderDZ.setSelection(pos[2]+1000);
		 sliderDO.setSelection(pos[3]+1000);
		 sliderDA.setSelection(pos[4]+1000);
		 sliderDT.setSelection(pos[5]+1000);
		 
		 
		 
		 sliderDX.addListener(SWT.Selection, new Listener() {	
			@Override
			public void handleEvent(Event arg0) {
				// TODO Auto-generated method stub
				textDSx.setText((sliderDX.getSelection()-1000)+"");
			}
		 });
		 sliderDY.addListener(SWT.Selection, new Listener() {	
				@Override
				public void handleEvent(Event arg0) {
					// TODO Auto-generated method stub
					textDSy.setText((sliderDY.getSelection()-1000)+"");
				}
			 });
		 sliderDZ.addListener(SWT.Selection, new Listener() {	
				@Override
				public void handleEvent(Event arg0) {
					// TODO Auto-generated method stub
					textDSz.setText((sliderDZ.getSelection()-1000)+"");
				}
			 });
		 sliderDO.addListener(SWT.Selection, new Listener() {	
				@Override
				public void handleEvent(Event arg0) {
					// TODO Auto-generated method stub
					textDSo.setText((sliderDO.getSelection()-1000)+"");
				}
			 });
		 sliderDA.addListener(SWT.Selection, new Listener() {	
				@Override
				public void handleEvent(Event arg0) {
					// TODO Auto-generated method stub
					textDSa.setText((sliderDA.getSelection()-1000)+"");
				}
			 });
		 sliderDT.addListener(SWT.Selection, new Listener() {	
				@Override
				public void handleEvent(Event arg0) {
					// TODO Auto-generated method stub
					textDSt.setText((sliderDT.getSelection()-1000)+"");
				}
			 });
		 sliderJx.addListener(SWT.Selection, new Listener() {	
				@Override
				public void handleEvent(Event arg0) {
					// TODO Auto-generated method stub
					textJSx.setText((sliderJx.getSelection()-160)+"");
				}
			 });
		 sliderJy.addListener(SWT.Selection, new Listener() {	
				@Override
				public void handleEvent(Event arg0) {
					// TODO Auto-generated method stub
					textJSy.setText((sliderJy.getSelection()-105)+"");
				}
			 });
		 sliderJz.addListener(SWT.Selection, new Listener() {	
				@Override
				public void handleEvent(Event arg0) {
					// TODO Auto-generated method stub
					textJSz.setText((sliderJz.getSelection()-155)+"");
				}
			 });
		 sliderJo.addListener(SWT.Selection, new Listener() {	
				@Override
				public void handleEvent(Event arg0) {
					// TODO Auto-generated method stub
					textJSo.setText((sliderJo.getSelection()-270)+"");
				}
			 });
		 sliderJa.addListener(SWT.Selection, new Listener() {	
				@Override
				public void handleEvent(Event arg0) {
					// TODO Auto-generated method stub
					textJSa.setText((sliderJa.getSelection()-145)+"");
				}
			 });
		 sliderJt.addListener(SWT.Selection, new Listener() {	
				@Override
				public void handleEvent(Event arg0) {
					// TODO Auto-generated method stub
					textJSt.setText((sliderJt.getSelection()-360)+"");
				}
			 }); 
		 sliderDJ1.addListener(SWT.Selection, new Listener() {	
				@Override
				public void handleEvent(Event arg0) {
					// TODO Auto-generated method stub
					textDJ1.setText((sliderDJ1.getSelection()-360)+"");
				}
			 }); 
		 sliderDJ2.addListener(SWT.Selection, new Listener() {	
				@Override
				public void handleEvent(Event arg0) {
					// TODO Auto-generated method stub
					textDJ2.setText((sliderDJ2.getSelection()-360)+"");
				}
			 }); 
		 sliderDJ3.addListener(SWT.Selection, new Listener() {	
				@Override
				public void handleEvent(Event arg0) {
					// TODO Auto-generated method stub
					textDJ3.setText((sliderDJ3.getSelection()-360)+"");
				}
			 }); 
		 sliderDJ4.addListener(SWT.Selection, new Listener() {	
				@Override
				public void handleEvent(Event arg0) {
					// TODO Auto-generated method stub
					textDJ4.setText((sliderDJ4.getSelection()-360)+"");
				}
			 }); 
		 sliderDJ5.addListener(SWT.Selection, new Listener() {	
				@Override
				public void handleEvent(Event arg0) {
					// TODO Auto-generated method stub
					textDJ5.setText((sliderDJ5.getSelection()-360)+"");
				}
			 }); 
		 sliderDJ6.addListener(SWT.Selection, new Listener() {	
				@Override
				public void handleEvent(Event arg0) {
					// TODO Auto-generated method stub
					textDJ6.setText((sliderDJ6.getSelection()-360)+"");
				}
			 }); 
		 client.setParams(Integer.parseInt(textAccel.getText()),
			     Integer.parseInt(textDecel.getText()),
			     Integer.parseInt(textSpeed.getText()),
			     Integer.parseInt(textMMPS.getText()),
			     10,
			     10);
		 
		 setSliders();
		 setRotations();
		 setDekart();
	}
	public void setSliders(){
		int rot [] = client.getRotations();
		sliderJx.setSelection(rot[0]+160);
		sliderJy.setSelection(rot[1]+105);
		sliderJz.setSelection(rot[2]+155);
		sliderJo.setSelection(rot[3]+270);
		sliderJa.setSelection(rot[4]+145);
		sliderJt.setSelection(rot[5]+360);
		textJSx.setText(rot[0]+"");
		textJSy.setText(rot[1]+"");
		textJSz.setText(rot[2]+"");
		textJSo.setText(rot[3]+"");
	 	textJSa.setText(rot[4]+"");
	 	textJSt.setText(rot[5]+"");
		
		int pos [] = client.getPositions();
		sliderDX.setSelection(pos[0]+1000);
		sliderDY.setSelection(pos[1]+1000);
		sliderDZ.setSelection(pos[2]+1000);
		sliderDO.setSelection(pos[3]+1000);
		sliderDA.setSelection(pos[4]+1000);
		sliderDT.setSelection(pos[5]+1000);
		textDSx.setText(pos[0]+"");
		textDSy.setText(pos[1]+"");
		textDSz.setText(pos[2]+"");
		textDSo.setText(pos[3]+"");
	 	textDSa.setText(pos[4]+"");
	 	textDSt.setText(pos[5]+"");
	 	
	 	sliderDJ1.setSelection(360);
	 	sliderDJ2.setSelection(360);
	 	sliderDJ3.setSelection(360);
	 	sliderDJ4.setSelection(360);
	 	sliderDJ5.setSelection(360);
	 	sliderDJ6.setSelection(360);
	 	
	 	textDJ1.setText("0");
	 	textDJ2.setText("0");
	 	textDJ3.setText("0");
	 	textDJ4.setText("0");
	 	textDJ5.setText("0");
	 	textDJ6.setText("0");
	 	
	 	
	 	
	}
	/**
	 * Launch the application.
	 * @param args
	 */
	public static void main(String[] args) {
		try {
			MainWindow window = new MainWindow();
			window.open();
		} catch (Exception e) {
			e.printStackTrace();
		}
	}

	/**
	 * Open the window.
	 */
	
	
	public void open() {
		display = Display.getDefault();
		createContents();
		textJo.open();
		textJo.layout();		
		init();
		
		while (!textJo.isDisposed()) {
			if (!display.readAndDispatch()) {	
				display.sleep();
			}
		}
		onDestroy();
	}
	public void onDestroy(){
		client.closeSocket();
		client.close();
		hand.closeSocket();
		camSocket.closeSocket();
		System.out.println("Destroyed");
	}	
	/**
	 * Create contents of the window.
	 */
	protected void createContents() {
		textJo = new Shell();
		textJo.setSize(984, 737);
		textJo.setText("SWT Application");
		
		progressBarX = new ProgressBar(textJo, SWT.NONE);
		progressBarX.setMaximum(200000);
		progressBarX.setBounds(37, 14, 182, 17);
		
		progressBarY = new ProgressBar(textJo, SWT.NONE);
		progressBarY.setMaximum(200000);
		progressBarY.setBounds(37, 37, 182, 17);
		
		progressBarZ = new ProgressBar(textJo, SWT.NONE);
		progressBarZ.setMaximum(200000);
		progressBarZ.setBounds(37, 60, 182, 17);
		
		progressBarMx = new ProgressBar(textJo, SWT.NONE);
		progressBarMx.setMaximum(200000);
		progressBarMx.setBounds(37, 83, 182, 17);
		
		progressBarMy = new ProgressBar(textJo, SWT.NONE);
		progressBarMy.setMaximum(200000);
		progressBarMy.setBounds(37, 106, 182, 17);
		
		progressBarMz = new ProgressBar(textJo, SWT.NONE);
		progressBarMz.setMaximum(200000);
		progressBarMz.setBounds(37, 129, 182, 17);
		
		progressBarRx = new ProgressBar(textJo, SWT.NONE);
		progressBarRx.setMaximum(200000);
		progressBarRx.setBounds(370, 14, 182, 17);
		
		progressBarRy = new ProgressBar(textJo, SWT.NONE);
		progressBarRy.setMaximum(200000);
		progressBarRy.setBounds(370, 37, 182, 17);
		
		progressBarRz = new ProgressBar(textJo, SWT.NONE);
		progressBarRz.setMaximum(200000);
		progressBarRz.setBounds(370, 60, 182, 17);
		
		progressBarRMx = new ProgressBar(textJo, SWT.NONE);
		progressBarRMx.setMaximum(20000);
		progressBarRMx.setBounds(370, 83, 182, 17);
		
		progressBarRMy = new ProgressBar(textJo, SWT.NONE);
		progressBarRMy.setMaximum(20000);
		progressBarRMy.setBounds(370, 106, 182, 17);
		
		progressBarRMz = new ProgressBar(textJo, SWT.NONE);
		progressBarRMz.setMaximum(20000);
		progressBarRMz.setBounds(370, 129, 182, 17);
		
		textX = new Text(textJo, SWT.BORDER);
		textX.setBounds(225, 14, 76, 17);
		
		textY = new Text(textJo, SWT.BORDER);
		textY.setBounds(225, 37, 76, 17);
		
		textZ = new Text(textJo, SWT.BORDER);
		textZ.setBounds(225, 60, 76, 17);
		
		textMx = new Text(textJo, SWT.BORDER);
		textMx.setBounds(225, 83, 76, 17);
		
		textMy = new Text(textJo, SWT.BORDER);
		textMy.setBounds(225, 106, 76, 17);
		
		textMz = new Text(textJo, SWT.BORDER);
		textMz.setBounds(225, 129, 76, 17);
		
		textRx = new Text(textJo, SWT.BORDER);
		textRx.setBounds(558, 14, 76, 17);
		
		textRy = new Text(textJo, SWT.BORDER);
		textRy.setBounds(558, 37, 76, 17);
		
		textRz = new Text(textJo, SWT.BORDER);
		textRz.setBounds(558, 60, 76, 17);
		
		textRMx = new Text(textJo, SWT.BORDER);
		textRMx.setBounds(558, 83, 76, 17);
		
		textRMy = new Text(textJo, SWT.BORDER);
		textRMy.setBounds(558, 106, 76, 17);
		
		textRMz = new Text(textJo, SWT.BORDER);
		textRMz.setBounds(558, 129, 76, 17);
		
		Label lblRx = new Label(textJo, SWT.NONE);
		lblRx.setBounds(344, 14, 20, 15);
		lblRx.setText("Rx");
		
		Label lblRy = new Label(textJo, SWT.NONE);
		lblRy.setBounds(344, 37, 20, 15);
		lblRy.setText("Ry");
		
		Label lblRz = new Label(textJo, SWT.NONE);
		lblRz.setBounds(344, 60, 20, 15);
		lblRz.setText("Rz");
		
		Label lblRmx = new Label(textJo, SWT.NONE);
		lblRmx.setBounds(331, 83, 28, 15);
		lblRmx.setText("RMx");
		
		Label lblRmy = new Label(textJo, SWT.NONE);
		lblRmy.setBounds(331, 106, 28, 15);
		lblRmy.setText("RMy");
		
		Menu menu = new Menu(textJo, SWT.BAR);
		textJo.setMenuBar(menu);
		
		MenuItem mntmFirst = new MenuItem(menu, SWT.NONE);
		mntmFirst.setText("First");
		
		MenuItem mntmSecond = new MenuItem(menu, SWT.NONE);
		mntmSecond.setText("Second");
		
		Label lblRmz = new Label(textJo, SWT.NONE);
		lblRmz.setBounds(331, 131, 28, 15);
		lblRmz.setText("RMz");
		
		Label lblX = new Label(textJo, SWT.NONE);
		lblX.setBounds(26, 16, 5, 15);
		lblX.setText("x");
		
		Label lblY = new Label(textJo, SWT.NONE);
		lblY.setBounds(26, 37, 5, 15);
		lblY.setText("y");
		
		Label lblMx = new Label(textJo, SWT.NONE);
		lblMx.setBounds(11, 83, 20, 15);
		lblMx.setText("Mx");
		
		Label lblMy = new Label(textJo, SWT.NONE);
		lblMy.setBounds(11, 106, 20, 15);
		lblMy.setText("My");
		
		Label lblMz = new Label(textJo, SWT.NONE);
		lblMz.setBounds(11, 129, 20, 15);
		lblMz.setText("Mz");
		
		Label lblZ = new Label(textJo, SWT.NONE);
		lblZ.setBounds(26, 60, 5, 15);
		lblZ.setText("z");
		
		textO = new Text(textJo, SWT.BORDER);
		textO.setBounds(686, 129, 34, 18);
		
		textA = new Text(textJo, SWT.BORDER);
		textA.setBounds(733, 129, 34, 17);
		
		textT = new Text(textJo, SWT.BORDER);
		textT.setBounds(781, 129, 34, 17);
		
		Label lblO = new Label(textJo, SWT.NONE);
		lblO.setBounds(698, 106, 9, 15);
		lblO.setText("O");
		
		lblA = new Label(textJo, SWT.NONE);
		lblA.setText("A");
		lblA.setBounds(747, 106, 20, 15);
		
		lblT = new Label(textJo, SWT.NONE);
		lblT.setText("T");
		lblT.setBounds(795, 106, 20, 15);
		
		sliderDX = new Slider(textJo, SWT.NONE);
		sliderDX.setMaximum(2000);
		sliderDX.setBounds(370, 185, 170, 17);
		
		sliderDY = new Slider(textJo, SWT.NONE);
		sliderDY.setMaximum(2000);
		sliderDY.setBounds(370, 208, 170, 17);
		
		sliderDZ = new Slider(textJo, SWT.NONE);
		sliderDZ.setMaximum(2000);
		sliderDZ.setBounds(370, 231, 170, 17);
		
		sliderDO = new Slider(textJo, SWT.NONE);
		sliderDO.setMaximum(2000);
		sliderDO.setBounds(370, 254, 170, 17);
		
		sliderDA = new Slider(textJo, SWT.NONE);
		sliderDA.setMaximum(2000);
		sliderDA.setBounds(370, 277, 170, 17);
		
		sliderDT = new Slider(textJo, SWT.NONE);
		sliderDT.setMaximum(2000);
		sliderDT.setBounds(370, 300, 170, 17);
		
		textDSx = new Text(textJo, SWT.BORDER);
		textDSx.setBounds(558, 185, 47, 17);
		
		textDSy = new Text(textJo, SWT.BORDER);
		textDSy.setBounds(558, 208, 47, 17);
		
		textDSz = new Text(textJo, SWT.BORDER);
		textDSz.setBounds(558, 231, 47, 17);
		
		textDSo = new Text(textJo, SWT.BORDER);
		textDSo.setBounds(558, 254, 47, 17);
		
		textDSa = new Text(textJo, SWT.BORDER);
		textDSa.setBounds(558, 277, 47, 17);
		
		textDSt = new Text(textJo, SWT.BORDER);
		textDSt.setBounds(558, 300, 47, 17);
		
		Button btnHome = new Button(textJo, SWT.NONE);
		btnHome.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent arg0) {
				client.home1();
			}
		});
		btnHome.setBounds(146, 407, 75, 25);
		btnHome.setText("Home");
		
		Button btnHome_1 = new Button(textJo, SWT.NONE);
		btnHome_1.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent arg0) {
				client.home2();
			}
		});
		btnHome_1.setBounds(146, 376, 75, 25);
		btnHome_1.setText("Home2");
		
		lblX_1 = new Label(textJo, SWT.NONE);
		lblX_1.setText("X");
		lblX_1.setBounds(344, 187, 20, 15);
		
		lblY_1 = new Label(textJo, SWT.NONE);
		lblY_1.setText("Y");
		lblY_1.setBounds(344, 208, 20, 15);
		
		lblZ_1 = new Label(textJo, SWT.NONE);
		lblZ_1.setText("Z");
		lblZ_1.setBounds(344, 231, 20, 15);
		
		lblO_1 = new Label(textJo, SWT.NONE);
		lblO_1.setText("O");
		lblO_1.setBounds(344, 254, 20, 15);
		
		lblA_1 = new Label(textJo, SWT.NONE);
		lblA_1.setText("A");
		lblA_1.setBounds(344, 277, 20, 15);
		
		lblT_1 = new Label(textJo, SWT.NONE);
		lblT_1.setText("T");
		lblT_1.setBounds(344, 300, 20, 15);
		
		textDx = new Label(textJo, SWT.NONE);
		textDx.setText("0");
		textDx.setBounds(611, 187, 28, 15);
		
		textDy = new Label(textJo, SWT.NONE);
		textDy.setText("0");
		textDy.setBounds(611, 210, 28, 15);
		
		textDz = new Label(textJo, SWT.NONE);
		textDz.setText("0");
		textDz.setBounds(611, 233, 28, 15);
		
		textDo = new Label(textJo, SWT.NONE);
		textDo.setText("0");
		textDo.setBounds(611, 254, 28, 15);
		
		textDa = new Label(textJo, SWT.NONE);
		textDa.setText("0");
		textDa.setBounds(611, 279, 28, 15);
		
		textDt = new Label(textJo, SWT.NONE);
		textDt.setText("0");
		textDt.setBounds(611, 300, 28, 15);
		
		lblJ = new Label(textJo, SWT.NONE);
		lblJ.setText("J1");
		lblJ.setBounds(662, 187, 20, 15);
		
		lblJ_1 = new Label(textJo, SWT.NONE);
		lblJ_1.setText("J2");
		lblJ_1.setBounds(662, 210, 20, 15);
		
		lblJ_2 = new Label(textJo, SWT.NONE);
		lblJ_2.setText("J3");
		lblJ_2.setBounds(662, 233, 20, 15);
		
		lblJ_3 = new Label(textJo, SWT.NONE);
		lblJ_3.setText("J4");
		lblJ_3.setBounds(662, 256, 20, 15);
		
		lblJ_4 = new Label(textJo, SWT.NONE);
		lblJ_4.setText("J5");
		lblJ_4.setBounds(662, 279, 20, 15);
		
		lblJ_5 = new Label(textJo, SWT.NONE);
		lblJ_5.setText("J6");
		lblJ_5.setBounds(662, 302, 20, 15);
		
		sliderJx = new Slider(textJo, SWT.NONE);
		sliderJx.setMaximum(320);
		sliderJx.setSelection(0);
		sliderJx.setBounds(688, 185, 170, 17);
		
		sliderJy = new Slider(textJo, SWT.NONE);
		sliderJy.setMaximum(245);
		sliderJy.setSelection(0);
		sliderJy.setBounds(688, 208, 170, 17);
		
		sliderJz = new Slider(textJo, SWT.NONE);
		sliderJz.setMaximum(275);
		sliderJz.setSelection(0);
		sliderJz.setBounds(688, 231, 170, 17);
		
		sliderJo = new Slider(textJo, SWT.NONE);
		sliderJo.setMaximum(540);
		sliderJo.setSelection(0);
		sliderJo.setBounds(688, 254, 170, 17);
		
		sliderJa = new Slider(textJo, SWT.NONE);
		sliderJa.setMaximum(290);
		sliderJa.setSelection(0);
		sliderJa.setBounds(688, 277, 170, 17);
		
		sliderJt = new Slider(textJo, SWT.NONE);
		sliderJt.setMaximum(720);
		sliderJt.setSelection(0);
		sliderJt.setBounds(688, 300, 170, 17);
		
		textJSx = new Text(textJo, SWT.BORDER);
		textJSx.setText("0");
		textJSx.setBounds(864, 185, 47, 17);
		
		textJSy = new Text(textJo, SWT.BORDER);
		textJSy.setText("0");
		textJSy.setBounds(864, 208, 47, 17);
		
		textJSz = new Text(textJo, SWT.BORDER);
		textJSz.setText("0");
		textJSz.setBounds(864, 231, 47, 17);
		
		textJSo = new Text(textJo, SWT.BORDER);
		textJSo.setText("0");
		textJSo.setBounds(864, 254, 47, 17);
		
		textJSa = new Text(textJo, SWT.BORDER);
		textJSa.setText("0");
		textJSa.setBounds(864, 277, 47, 17);
		
		textJSt = new Text(textJo, SWT.BORDER);
		textJSt.setText("0");
		textJSt.setBounds(864, 300, 47, 17);
		
		textJx = new Label(textJo, SWT.NONE);
		textJx.setText("0");
		textJx.setBounds(917, 187, 20, 15);
		
		textJy = new Label(textJo, SWT.NONE);
		textJy.setText("0");
		textJy.setBounds(917, 210, 20, 15);
		
		textJz = new Label(textJo, SWT.NONE);
		textJz.setText("0");
		textJz.setBounds(917, 231, 20, 15);
		
		label_3 = new Label(textJo, SWT.NONE);
		label_3.setText("0");
		label_3.setBounds(917, 254, 20, 15);
		
		textJa = new Label(textJo, SWT.NONE);
		textJa.setText("0");
		textJa.setBounds(917, 279, 20, 15);
		
		textJt = new Label(textJo, SWT.NONE);
		textJt.setText("0");
		textJt.setBounds(917, 300, 20, 15);
		
		Button btnSendD = new Button(textJo, SWT.NONE);
		btnSendD.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent arg0) {
				if (btnD.getSelection())
				client.runInPointD(sliderDX.getSelection()-1000,
								   sliderDY.getSelection()-1000,
								   sliderDZ.getSelection()-1000,
								   sliderDO.getSelection()-1000,
								   sliderDA.getSelection()-1000,
								   sliderDT.getSelection()-1000,10);
				if (btnJ.getSelection())
					client.runInPointA(sliderJx.getSelection()-160,
									   sliderJy.getSelection()-105,
									   sliderJz.getSelection()-155,
									   sliderJo.getSelection()-270,
									   sliderJa.getSelection()-145,
									   sliderJt.getSelection()-360,10);
				if (btnDJ.getSelection()){
					client.runInDeltaPointA(sliderDJ1.getSelection()-360,
											sliderDJ2.getSelection()-360,
											sliderDJ3.getSelection()-360,
											sliderDJ4.getSelection()-360,
											sliderDJ5.getSelection()-360,
											sliderDJ6.getSelection()-360,10);
				}
				
			}
		});
		btnSendD.setBounds(475, 346, 75, 25);
		btnSendD.setText("Send");
		
		textM11 = new Text(textJo, SWT.BORDER);
		textM11.setBounds(688, 14, 53, 17);
		
		textM21 = new Text(textJo, SWT.BORDER);
		textM21.setBounds(688, 37, 53, 17);
		
		textM31 = new Text(textJo, SWT.BORDER);
		textM31.setBounds(688, 60, 53, 17);
		
		textM41 = new Text(textJo, SWT.BORDER);
		textM41.setBounds(688, 83, 53, 17);
		
		textM12 = new Text(textJo, SWT.BORDER);
		textM12.setBounds(747, 14, 53, 17);
		
		textM22 = new Text(textJo, SWT.BORDER);
		textM22.setBounds(747, 37, 53, 17);
		
		textM32 = new Text(textJo, SWT.BORDER);
		textM32.setBounds(747, 60, 53, 17);
		
		textM42 = new Text(textJo, SWT.BORDER);
		textM42.setBounds(747, 83, 53, 17);
		
		textM13 = new Text(textJo, SWT.BORDER);
		textM13.setBounds(805, 14, 53, 17);
		
		textM23 = new Text(textJo, SWT.BORDER);
		textM23.setBounds(805, 37, 53, 17);
		
		textM33 = new Text(textJo, SWT.BORDER);
		textM33.setBounds(805, 60, 53, 17);
		
		textM43 = new Text(textJo, SWT.BORDER);
		textM43.setBounds(806, 83, 53, 17);
		
		textM14 = new Text(textJo, SWT.BORDER);
		textM14.setBounds(864, 14, 53, 17);
		
		textM24 = new Text(textJo, SWT.BORDER);
		textM24.setBounds(864, 37, 53, 17);
		
		textM34 = new Text(textJo, SWT.BORDER);
		textM34.setBounds(864, 60, 53, 17);
		
		textM44 = new Text(textJo, SWT.BORDER);
		textM44.setBounds(864, 83, 53, 17);
		
		Label lblCam = new Label(textJo, SWT.NONE);
		lblCam.setBounds(21, 381, 55, 15);
		lblCam.setText("Cam:");
		
		text = new Text(textJo, SWT.BORDER);
		text.setBounds(11, 414, 28, -1);
		
		textCam1 = new Text(textJo, SWT.BORDER);
		textCam1.setBounds(11, 402, 65, 21);
		
		textCam2 = new Text(textJo, SWT.BORDER);
		textCam2.setBounds(11, 430, 65, 21);
		
		textCam3 = new Text(textJo, SWT.BORDER);
		textCam3.setBounds(11, 457, 65, 21);
		
		textCam4 = new Text(textJo, SWT.BORDER);
		textCam4.setBounds(11, 485, 65, 21);
		
		textCam5 = new Text(textJo, SWT.BORDER);
		textCam5.setBounds(11, 512, 65, 21);
		
		textCam6 = new Text(textJo, SWT.BORDER);
		textCam6.setBounds(11, 539, 65, 21);
		
		sliderDJ1= new Slider(textJo, SWT.NONE);
		sliderDJ1.setMaximum(720);
		sliderDJ1.setSelection(360);
		sliderDJ1.setBounds(51, 185, 170, 17);
		
		sliderDJ2 = new Slider(textJo, SWT.NONE);
		sliderDJ2.setMaximum(720);
		sliderDJ2.setSelection(360);
		sliderDJ2.setBounds(49, 208, 170, 17);
		
		sliderDJ3 = new Slider(textJo, SWT.NONE);
		sliderDJ3.setMaximum(720);
		sliderDJ3.setSelection(360);
		sliderDJ3.setBounds(51, 231, 170, 17);
		
		sliderDJ4 = new Slider(textJo, SWT.NONE);
		sliderDJ4.setMaximum(720);
		sliderDJ4.setSelection(360);
		sliderDJ4.setBounds(51, 254, 170, 17);
		
		sliderDJ5 = new Slider(textJo, SWT.NONE);
		sliderDJ5.setMaximum(720);
		sliderDJ5.setSelection(360);
		sliderDJ5.setBounds(51, 277, 170, 17);
		
		sliderDJ6 = new Slider(textJo, SWT.NONE);
		sliderDJ6.setMaximum(720);
		sliderDJ6.setSelection(360);
		sliderDJ6.setBounds(49, 300, 170, 17);
		
		textDJ1 = new Text(textJo, SWT.BORDER);
		textDJ1.setText("0");
		textDJ1.setBounds(225, 185, 47, 17);
		
		textDJ2 = new Text(textJo, SWT.BORDER);
		textDJ2.setText("0");
		textDJ2.setBounds(225, 208, 47, 17);
		
		textDJ3 = new Text(textJo, SWT.BORDER);
		textDJ3.setText("0");
		textDJ3.setBounds(225, 231, 47, 17);
		
		textDJ4 = new Text(textJo, SWT.BORDER);
		textDJ4.setText("0");
		textDJ4.setBounds(225, 254, 47, 17);
		
		textDJ5 = new Text(textJo, SWT.BORDER);
		textDJ5.setText("0");
		textDJ5.setBounds(225, 277, 47, 17);
		
		textDJ6 = new Text(textJo, SWT.BORDER);
		textDJ6.setText("0");
		textDJ6.setBounds(225, 300, 47, 17);
		
		lblJ_7 = new Label(textJo, SWT.NONE);
		lblJ_7.setText("J3");
		lblJ_7.setBounds(26, 233, 28, 15);
		
		label = new Label(textJo, SWT.NONE);
		label.setText("J1");
		label.setBounds(26, 187, 20, 15);
		
		lblJ_6 = new Label(textJo, SWT.NONE);
		lblJ_6.setText("J2");
		lblJ_6.setBounds(26, 208, 20, 15);
		
		lblJ_8 = new Label(textJo, SWT.NONE);
		lblJ_8.setText("J4");
		lblJ_8.setBounds(26, 256, 20, 15);
		
		lblJ_9 = new Label(textJo, SWT.NONE);
		lblJ_9.setText("J5");
		lblJ_9.setBounds(25, 277, 20, 15);
		
		lblJ_10 = new Label(textJo, SWT.NONE);
		lblJ_10.setText("J6");
		lblJ_10.setBounds(26, 300, 20, 15);
		
		textAccel = new Text(textJo, SWT.BORDER);
		textAccel.setText("10");
		textAccel.setBounds(146, 438, 65, 21);
		
		textDecel = new Text(textJo, SWT.BORDER);
		textDecel.setText("10");
		textDecel.setBounds(146, 465, 65, 21);
		
		textSpeed = new Text(textJo, SWT.BORDER);
		textSpeed.setText("5");
		textSpeed.setBounds(146, 492, 65, 21);
		
		textMMPS = new Text(textJo, SWT.BORDER);
		textMMPS.setText("100");
		textMMPS.setBounds(146, 520, 65, 21);
		
		Button btnSetparams = new Button(textJo, SWT.NONE);
		btnSetparams.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent arg0) {
				client.setParams(Integer.parseInt(textAccel.getText()),
							     Integer.parseInt(textDecel.getText()),
							     Integer.parseInt(textSpeed.getText()),
							     Integer.parseInt(textMMPS.getText()),
							     10,
							     10);
			}
		});
		btnSetparams.setBounds(225, 481, 75, 25);
		btnSetparams.setText("SetParams");
		
		Button btnRefresh = new Button(textJo, SWT.NONE);
		btnRefresh.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent arg0) {
				setSliders();
			}
		});
		btnRefresh.setBounds(381, 346, 75, 25);
		btnRefresh.setText("Refresh");
		
	    btnDJ = new Button(textJo, SWT.RADIO);
		btnDJ.setBounds(380, 323, 34, 16);
		btnDJ.setText("DJ");
		
		btnD = new Button(textJo, SWT.RADIO);
		btnD.setText("D");
		btnD.setBounds(447, 323, 34, 16);
		
		btnJ = new Button(textJo, SWT.RADIO);
		btnJ.setText("J");
		btnJ.setBounds(518, 323, 34, 16);
		
		lblAccel = new Label(textJo, SWT.NONE);
		lblAccel.setText("Accel");
		lblAccel.setBounds(106, 441, 34, 15);
		
		lblDecel = new Label(textJo, SWT.NONE);
		lblDecel.setText("Decel");
		lblDecel.setBounds(106, 468, 34, 15);
		
		lblSpeed = new Label(textJo, SWT.NONE);
		lblSpeed.setText("Speed");
		lblSpeed.setBounds(106, 498, 34, 15);
		
		lblSpeedMmps = new Label(textJo, SWT.NONE);
		lblSpeedMmps.setText(" MMPS");
		lblSpeedMmps.setBounds(98, 523, 47, 15);
		
		textKP = new Text(textJo, SWT.BORDER);
		textKP.setText("5");
		textKP.setBounds(611, 409, 47, 17);
		
		textKI = new Text(textJo, SWT.BORDER);
		textKI.setText("5");
		textKI.setBounds(611, 430, 47, 17);
		
		Button btnStartGravity = new Button(textJo, SWT.NONE);
		btnStartGravity.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent arg0) {
				int p =  Integer.parseInt(textSMin.getText());
				if (!btnForces.getSelection()) p = -p;
				client.startGravityProgram(Integer.parseInt(textKP.getText()),
						   				   Integer.parseInt(textKI.getText()),
						   				   p);
			}
		});
		btnStartGravity.setBounds(662, 407, 75, 25);
		btnStartGravity.setText("Start Gravity");
		
		Button btnStopGravity = new Button(textJo, SWT.NONE);
		btnStopGravity.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent arg0) {
				client.stopGravityProgram();
			}
		});
		btnStopGravity.setBounds(664, 436, 75, 25);
		btnStopGravity.setText("Stop Gravity");
		
		Label lblKp = new Label(textJo, SWT.NONE);
		lblKp.setText("Kp");
		lblKp.setBounds(592, 407, 20, 15);
		
		Label lblKi = new Label(textJo, SWT.NONE);
		lblKi.setText("Ki");
		lblKi.setBounds(592, 433, 20, 15);
		
		textSMin = new Text(textJo, SWT.BORDER);
		textSMin.setText("65");
		textSMin.setBounds(611, 457, 47, 17);
		
		Label lblSmin = new Label(textJo, SWT.NONE);
		lblSmin.setText("Smin");
		lblSmin.setBounds(576, 460, 34, 15);
		
		textVx = new Text(textJo, SWT.BORDER);
		textVx.setBounds(824, 129, 34, 17);
		
		textVy = new Text(textJo, SWT.BORDER);
		textVy.setBounds(866, 129, 34, 17);
		
		textVz = new Text(textJo, SWT.BORDER);
		textVz.setBounds(906, 129, 34, 17);
		
		lblX_2 = new Label(textJo, SWT.NONE);
		lblX_2.setText("X");
		lblX_2.setBounds(834, 106, 20, 15);
		
		lblY_2 = new Label(textJo, SWT.NONE);
		lblY_2.setText("Y");
		lblY_2.setBounds(874, 106, 20, 15);
		
		lblZ_2 = new Label(textJo, SWT.NONE);
		lblZ_2.setText("Z");
		lblZ_2.setBounds(917, 106, 20, 15);
		
		progressBarRM2 = new ProgressBar(textJo, SWT.NONE);
		progressBarRM2.setMaximum(20000);
		progressBarRM2.setBounds(370, 152, 182, 17);
		
		textVArr1x = new Text(textJo, SWT.BORDER);
		textVArr1x.setBounds(317, 430, 76, 21);
		
		textVArr1y = new Text(textJo, SWT.BORDER);
		textVArr1y.setBounds(399, 430, 76, 21);
		
		textVArr1z = new Text(textJo, SWT.BORDER);
		textVArr1z.setBounds(481, 430, 76, 21);
		
		textVArr2x = new Text(textJo, SWT.BORDER);
		textVArr2x.setBounds(317, 457, 76, 21);
		
		textVArr2y = new Text(textJo, SWT.BORDER);
		textVArr2y.setBounds(399, 457, 76, 21);
		
		textVArr2z = new Text(textJo, SWT.BORDER);
		textVArr2z.setBounds(481, 457, 76, 21);
		
		textVArr3x = new Text(textJo, SWT.BORDER);
		textVArr3x.setBounds(317, 485, 76, 21);
		
		textVArr3y = new Text(textJo, SWT.BORDER);
		textVArr3y.setBounds(399, 485, 76, 21);
		
		textVArr3z = new Text(textJo, SWT.BORDER);
		textVArr3z.setBounds(481, 485, 76, 21);
		
		textVArr4x = new Text(textJo, SWT.BORDER);
		textVArr4x.setBounds(317, 512, 76, 21);
		
		textVArr4y = new Text(textJo, SWT.BORDER);
		textVArr4y.setBounds(399, 512, 76, 21);
		
		textVArr4z = new Text(textJo, SWT.BORDER);
		textVArr4z.setBounds(481, 512, 76, 21);
		
		Group grpGravity = new Group(textJo, SWT.NONE);
		grpGravity.setText("Graviti");
		grpGravity.setBounds(749, 407, 191, 82);
		
		btnForces = new Button(grpGravity, SWT.RADIO);
		btnForces.setBounds(10, 24, 90, 16);
		btnForces.setText("Forces");
		
		Button btnMomments = new Button(grpGravity, SWT.RADIO);
		btnMomments.setBounds(10, 46, 90, 16);
		btnMomments.setText("Momments");
		
		Button btnTest = new Button(textJo, SWT.NONE);
		btnTest.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent arg0) {
				client.processTest(testPos);
				testPos++;
				if(testPos>2) testPos=0;
			}
		});
		btnTest.setBounds(725, 346, 75, 25);
		btnTest.setText("Test");
		
		Button btnTest_1 = new Button(textJo, SWT.NONE);
		btnTest_1.setBounds(824, 346, 75, 25);
		btnTest_1.setText("Test 2");
		
		hCoordEdit2 = new Text(textJo, SWT.BORDER);
		hCoordEdit2.setText("0");
		hCoordEdit2.setBounds(625, 512, 53, 17);
		
		hCoordEdit3 = new Text(textJo, SWT.BORDER);
		hCoordEdit3.setText("0");
		hCoordEdit3.setBounds(625, 539, 53, 17);
		
		hCoordEdit4 = new Text(textJo, SWT.BORDER);
		hCoordEdit4.setText("0");
		hCoordEdit4.setBounds(625, 562, 53, 17);
		
		hCoordEdit5 = new Text(textJo, SWT.BORDER);
		hCoordEdit5.setText("0");
		hCoordEdit5.setBounds(625, 588, 53, 17);
		
		hCoordEdit6 = new Text(textJo, SWT.BORDER);
		hCoordEdit6.setText("0");
		hCoordEdit6.setBounds(625, 615, 53, 17);
		
		hCoordEdit1 = new Text(textJo, SWT.BORDER);
		hCoordEdit1.setText("0");
		hCoordEdit1.setBounds(625, 485, 53, 17);
		
		hCoordEdit7 = new Text(textJo, SWT.BORDER);
		hCoordEdit7.setText("0");
		hCoordEdit7.setBounds(625, 638, 53, 17);
		
		Button button = new Button(textJo, SWT.NONE);
		button.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent arg0) {
				int [] params = {
					Integer.parseInt(hCoordEdit1.getText()),
					Integer.parseInt(hCoordEdit2.getText()),
					Integer.parseInt(hCoordEdit3.getText()),
					Integer.parseInt(hCoordEdit4.getText()),
					Integer.parseInt(hCoordEdit5.getText()),
					Integer.parseInt(hCoordEdit6.getText()),
					Integer.parseInt(hCoordEdit7.getText()),
				};
				hand.sendCommand(1, params);
			}
		});
		button.setBounds(740, 510, 75, 25);
		button.setText("\u0412 \u0442\u043E\u0447\u043A\u0443");
		
		Label hCoordLable1 = new Label(textJo, SWT.NONE);
		hCoordLable1.setBounds(686, 485, 55, 15);
		hCoordLable1.setText("0");
		
		Label hCoordLable2 = new Label(textJo, SWT.NONE);
		hCoordLable2.setText("0");
		hCoordLable2.setBounds(686, 512, 28, 15);
		
		Label hCoordLable3 = new Label(textJo, SWT.NONE);
		hCoordLable3.setText("0");
		hCoordLable3.setBounds(686, 539, 55, 15);
		
		Label hCoordLable4 = new Label(textJo, SWT.NONE);
		hCoordLable4.setText("0");
		hCoordLable4.setBounds(684, 564, 55, 15);
		
		Label hCoordLable5 = new Label(textJo, SWT.NONE);
		hCoordLable5.setText("0");
		hCoordLable5.setBounds(684, 590, 55, 15);
		
		Label hCoordLable6 = new Label(textJo, SWT.NONE);
		hCoordLable6.setText("0");
		hCoordLable6.setBounds(684, 617, 55, 15);
		
		Label hCoordLable7 = new Label(textJo, SWT.NONE);
		hCoordLable7.setText("0");
		hCoordLable7.setBounds(686, 641, 55, 15);
		
		hPow1 = new Label(textJo, SWT.NONE);
		hPow1.setText("0");
		hPow1.setBounds(578, 512, 41, 15);
		
		hPow2 = new Label(textJo, SWT.NONE);
		hPow2.setText("0");
		hPow2.setBounds(576, 539, 41, 15);
		
		hPow3 = new Label(textJo, SWT.NONE);
		hPow3.setText("0");
		hPow3.setBounds(578, 564, 41, 15);
		
		hPow4 = new Label(textJo, SWT.NONE);
		hPow4.setText("0");
		hPow4.setBounds(576, 588, 41, 15);
		
		hPow5 = new Label(textJo, SWT.NONE);
		hPow5.setText("0");
		hPow5.setBounds(576, 615, 41, 15);
		
		hPow6 = new Label(textJo, SWT.NONE);
		hPow6.setText("0");
		hPow6.setBounds(576, 638, 41, 15);
		

	}
	public void setRotations(){
		int rot [] = client.getRotations();
		textJx.setText(rot[0]+"");
		textJy.setText(rot[1]+"");
		textJz.setText(rot[2]+"");
		textJo.setText(rot[3]+"");
		textJa.setText(rot[4]+"");
		textJt.setText(rot[5]+"");		
	}
	public void setDekart(){
		int pos [] = client.getPositions();
		textDx.setText(pos[0]+"");
		textDy.setText(pos[1]+"");
		textDz.setText(pos[2]+"");
		textDo.setText(pos[3]+"");
		textDa.setText(pos[4]+"");
		textDt.setText(pos[5]+"");		
	}
	
	public void setCam(){
		int vals[] = camSocket.getVals();
		textCam1.setText(vals[0]+"");
		textCam2.setText(vals[1]+"");
		textCam3.setText(vals[2]+"");
		textCam4.setText(vals[3]+"");
		textCam5.setText(vals[4]+"");
		textCam6.setText(vals[5]+"");
	}
	
	public void setHandPowers(){
		float[] powers = hand.getPowers();
		hPow1.setText(powers[0]+"");
		hPow2.setText(powers[1]+"");
		hPow3.setText(powers[2]+"");		
		hPow4.setText(powers[3]+"");
		hPow5.setText(powers[4]+"");
		hPow6.setText(powers[5]+"");
	}
	
	public void setSensorText(){
		int vals[] = client.getSensorVals();
		
		int p[] = client.getPositions();
		SimpleMatrix V = KawasakiMatrix.modifyVector3m(false,flgUseMatrix,
														p[3],p[4],p[5],
														vals[0],vals[1],vals[2]);
		double [] angles = {(double)p[3],(double)p[4],(double)p[5]};
		double m[]= KawasakiMatrix.ZYZtoXYZ(angles);
		//textO.setText(m[0]+"");
		//textA.setText(m[1]+"");
		//textT.setText(m[2]+"");
	
    	int rVals[] = client.sensor.getRVals();	
    	
		textX.setText(vals[0]+"");
		textY.setText(vals[1]+"");
		textZ.setText(vals[2]+"");
		textMx.setText(vals[3]+"");
		textMy.setText(vals[4]+"");
		textMz.setText(vals[5]+"");
		
		textRx.setText(rVals[0]+"");
		textRy.setText(rVals[1]+"");
		textRz.setText(rVals[2]+"");
		textRMx.setText(rVals[3]+"");
		textRMy.setText(rVals[4]+"");
		textRMz.setText(rVals[5]+"");
		
	}
	public void setSensorProgress(){
		int vals[] = client.getSensorVals();	
    	int rVals[] = client.sensor.getRVals();	
		if ( vals[0] < 0)
			progressBarX.setState(SWT.PAUSED); 
		else
        	progressBarX.setState(SWT.NORMAL); 
		if ( vals[1] < 0)
			progressBarY.setState(SWT.PAUSED); 
		else
        	progressBarY.setState(SWT.NORMAL); 
		if ( vals[2] < 0)
			progressBarZ.setState(SWT.PAUSED); 
		else
        	progressBarZ.setState(SWT.NORMAL); 
		if ( vals[3] < 0)
			progressBarMx.setState(SWT.PAUSED); 
		else
        	progressBarMx.setState(SWT.NORMAL); 
		if ( vals[4] < 0)
			progressBarMy.setState(SWT.PAUSED); 
		else
			progressBarMy.setState(SWT.NORMAL); 
		if ( vals[5] < 0)
			progressBarMz.setState(SWT.PAUSED); 
		else
        	progressBarMz.setState(SWT.NORMAL); 
		
		if ( rVals[0] < 0)
			progressBarRx.setState(SWT.PAUSED); 
		else
        	progressBarRx.setState(SWT.NORMAL); 
		if ( rVals[1]< 0)
			progressBarRy.setState(SWT.PAUSED); 
		else
        	progressBarRy.setState(SWT.NORMAL); 
		if ( rVals[2] < 0)
			progressBarRz.setState(SWT.PAUSED); 
		else
        	progressBarRz.setState(SWT.NORMAL); 
		if ( rVals[3] < 0)
			progressBarRMx.setState(SWT.PAUSED); 
		else
        	progressBarRMx.setState(SWT.NORMAL); 
		if ( rVals[4] < 0)
			progressBarRMy.setState(SWT.PAUSED); 
		else
			progressBarRMy.setState(SWT.NORMAL); 
		if ( rVals[5] < 0)
			progressBarRMz.setState(SWT.PAUSED); 
		else
        	progressBarRMz.setState(SWT.NORMAL); 
		
		if ( rVals[6] < 0)
			progressBarRM2.setState(SWT.PAUSED); 
		else
			progressBarRM2.setState(SWT.NORMAL); 
		
		
		progressBarX.setSelection(Math.abs(vals[0]));
		progressBarY.setSelection(Math.abs(vals[1]));
		progressBarZ.setSelection(Math.abs(vals[2]));
		progressBarMx.setSelection(Math.abs(vals[3]));
		progressBarMy.setSelection(Math.abs(vals[4]));
		progressBarMz.setSelection(Math.abs(vals[5]));
		
		progressBarRx.setSelection(Math.abs(rVals[0]));
		progressBarRy.setSelection(Math.abs(rVals[1]));
		progressBarRz.setSelection(Math.abs(rVals[2]));
		progressBarRMx.setSelection(Math.abs(rVals[3]));
		progressBarRMy.setSelection(Math.abs(rVals[4]));
		progressBarRMz.setSelection(Math.abs(rVals[5]));
		progressBarRM2.setSelection(Math.abs(rVals[6]));
	}
	public void setAngleText(){
		
	}
	public void setVectorVals(){
		int [] r = client.getRotations();
		SimpleMatrix M = KawasakiMatrix.getDHM(r);
		
		textVx.setText((int)(M.get(0,3)*1000)+"");
		textVy.setText((int)(M.get(1,3)*1000)+"");
		textVz.setText((int)(M.get(2,3)*1000)+"");
		int a [] = KawasakiMatrix.parceMatrixXYZm(M);
		
		textO.setText(a[0]+"");
		textA.setText(a[1]+"");
		textT.setText(a[2]+"");
		
		textM11.setText(M.get(0,0)+"");
		textM12.setText(M.get(0,1)+"");
		textM13.setText(M.get(0,2)+"");
		textM14.setText(M.get(0,3)+"");
		
		textM21.setText(M.get(1,0)+"");
		textM22.setText(M.get(1,1)+"");
		textM23.setText(M.get(1,2)+"");
		textM24.setText(M.get(1,3)+"");
		
		textM31.setText(M.get(2,0)+"");
		textM32.setText(M.get(2,1)+"");
		textM33.setText(M.get(2,2)+"");
		textM34.setText(M.get(2,3)+"");
		
		textM41.setText(M.get(3,0)+"");
		textM42.setText(M.get(3,1)+"");
		textM43.setText(M.get(3,2)+"");
		textM44.setText(M.get(3,3)+"");
		
	}
	public void setMatrix4x4(){
		int [] pos = client.getPositions();
	    SimpleMatrix M  = KawasakiMatrix.getMatrix3x3ZYZm(false,pos[3],pos[4],pos[5]);
		//System.out.println(M);
	/*	
		textM11.setText(M.get(0,0)+"");
		textM12.setText(M.get(0,1)+"");
		textM13.setText(M.get(0,2)+"");
		//textM14.setText(M.get(0,3)+"");
		
		textM21.setText(M.get(1,0)+"");
		textM22.setText(M.get(1,1)+"");
		textM23.setText(M.get(1,2)+"");
		//textM24.setText(M.get(1,3)+"");
		
		textM31.setText(M.get(2,0)+"");
		textM32.setText(M.get(2,1)+"");
		textM33.setText(M.get(2,2)+"");
		//textM34.setText(M.get(2,3)+"");
	/*	
		textM41.setText(M.get(3,0)+"");
		textM42.setText(M.get(3,1)+"");
		textM43.setText(M.get(3,2)+"");
		textM44.setText(M.get(3,3)+"");*/
	}
	
	Button btnForces;
	protected Shell textJo;
	private Text textX;
	private Text textY;
	private Text textZ;
	private Text textMx;
	private Text textMy;
	private Text textMz;
	private Text textRx;
	private Text textRy;
	private Text textRz;
	private Text textRMx;
	private Text textRMy;
	private Text textRMz;
	ProgressBar progressBarX;	
	ProgressBar progressBarY;	
	ProgressBar progressBarZ;	
	ProgressBar progressBarMx;	
	ProgressBar progressBarMy;	
	ProgressBar progressBarMz;	
	ProgressBar progressBarRx;	
	ProgressBar progressBarRy;	
	ProgressBar progressBarRz;	
	ProgressBar progressBarRMx;
	ProgressBar progressBarRMy;	
	ProgressBar progressBarRMz;
	private Text textO;
	private Text textA;
	private Text textT;
	private Label lblA;
	private Label lblT;
	private Text textDSx;
	private Text textDSy;
	private Text textDSz;
	private Text textDSo;
	private Text textDSa;
	private Text textDSt;
	private Label lblX_1;
	private Label lblY_1;
	private Label lblZ_1;
	private Label lblO_1;
	private Label lblA_1;
	private Label lblT_1;
	Slider sliderDX;	
	Slider sliderDY;	
	Slider sliderDZ;	
	Slider sliderDO;	
	Slider sliderDA;	
	Slider sliderDT;
	
	private Label textDx;
	private Label textDy;
	private Label textDz;
	private Label textDo;
	private Label textDa;
	private Label textDt;
	private Label lblJ;
	private Label lblJ_1;
	private Label lblJ_2;
	private Label lblJ_3;
	private Label lblJ_4;
	private Label lblJ_5;
	private Slider sliderJx;
	private Slider sliderJy;
	private Slider sliderJz;
	private Slider sliderJo;
	private Slider sliderJa;
	private Slider sliderJt;
	private Text textJSx;
	private Text textJSy;
	private Text textJSz;
	private Text textJSo;
	private Text textJSa;
	private Text textJSt;
	private Label textJx;
	private Label textJy;
	private Label textJz;
	private Label label_3;
	private Label textJa;
	private Label textJt;
	private Text textM11;
	private Text textM21;
	private Text textM31;
	private Text textM41;
	private Text textM12;
	private Text textM22;
	private Text textM32;
	private Text textM42;
	private Text textM13;
	private Text textM23;
	private Text textM33;
	private Text textM43;
	private Text textM14;
	private Text textM24;
	private Text textM34;
	private Text textM44;
	private Text text;
	private Text textCam1;
	private Text textCam2;
	private Text textCam3;
	private Text textCam4;
	private Text textCam5;
	private Text textCam6;
	private Slider sliderDJ2;
	private Slider sliderDJ3;
	private Slider sliderDJ4;
	private Slider sliderDJ5;
	private Slider sliderDJ6;
	private Text textDJ1;
	private Text textDJ2;
	private Text textDJ3;
	private Text textDJ4;
	private Text textDJ5;
	private Text textDJ6;
	private Label lblJ_7;
	private Label label;
	private Label lblJ_6;
	private Label lblJ_8;
	private Label lblJ_9;
	private Label lblJ_10;
	private Text textAccel;
	private Text textDecel;
	private Text textSpeed;
	private Text textMMPS;
	private Slider sliderDJ1;
	private Button btnDJ;
	private Button btnD;
	private Button btnJ;
	private Label lblAccel;
	private Label lblDecel;
	private Label lblSpeed;
	private Label lblSpeedMmps;
	private Text textKP;
	private Text textKI;
	private Text textSMin;
	private Text textVx;
	private Text textVy;
	private Text textVz;
	private Label lblX_2;
	private Label lblY_2;
	private Label lblZ_2;
	private ProgressBar progressBarRM2;
	private Text textVArr1x;
	private Text textVArr1y;
	private Text textVArr1z;
	private Text textVArr2x;
	private Text textVArr2y;
	private Text textVArr2z;
	private Text textVArr3x;
	private Text textVArr3y;
	private Text textVArr3z;
	private Text textVArr4x;
	private Text textVArr4y;
	private Text textVArr4z;
	private Text hCoordEdit2;
	private Text hCoordEdit3;
	private Text hCoordEdit4;
	private Text hCoordEdit5;
	private Text hCoordEdit6;
	private Text hCoordEdit1;
	private Text hCoordEdit7;
	private Label hPow1;
	private Label hPow2;
	private Label hPow3;
	private Label hPow4;
	private Label hPow5;
	private Label hPow6;
}
