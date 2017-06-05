/*  TODO:
 *  1) кнопка остановки выполнения программы роботом
 * 
 * 
 */

import java.awt.*;
import java.awt.event.*;
import java.io.BufferedReader;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.InetAddress;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.UnknownHostException;
import java.util.Timer;
import java.util.TimerTask;


import javax.security.auth.Subject;
import javax.swing.*;
import javax.swing.event.ChangeEvent;
import javax.swing.event.ChangeListener;
import javax.swing.text.AbstractDocument.LeafElement;



public class ClientGui extends JFrame {

	ClientSocket client;
	KeyListener keyListener;

	final Timer time = new Timer();
	final Timer timeSendC = new Timer();
	int dCoordArr[] = new int[6];
    public void clearInputs(){
    	for (int j=0;j<inputsCnt;j++)
			inputs[j].setText("");
    }
    boolean isKeyDown[] = new boolean[5000];
    int curPositions[] = new int [6];
    boolean flgFirstGet = true;
    boolean flgFirstDeltaPos = false;
    JPanel content;
    // создаём страницу для работы с пакетами
    public void createPackagePage(){
    	Container packagePage = new JPanel();
    	packagePage.setLayout(null);
  	    tabbedPane.addTab("Пакеты" , packagePage);
  	    Insets insets = packagePage.getInsets();
  	    // поля ввода
	    for (int i=0;i<inputsCnt;i++){
	    	inputs[i] = new JTextField("", 5);
	    	packagePage.add(inputs[i]);
	    	Dimension size = inputs[i].getPreferredSize(); 
	    	inputs[i].setBounds(10 + (i%9)*70 + insets.left, 80+(i/9)*30 + insets.top, 
	                     size.width, size.height); 
	    }
	    // поле ввода с адресом сервера
	    packagePage.add(adressSocket);
    	Dimension size = adressSocket.getPreferredSize(); 
    	adressSocket.setBounds(130 + insets.left, 40 + insets.top, 
    							size.width, size.height);
    	// поле ввода порта сокета
    	packagePage.add(portSocet);
    	size = portSocet.getPreferredSize(); 
    	portSocet.setBounds(130 + insets.left, 15 + insets.top, 
                     size.width, size.height);
    	// кнопка открытия сокета
    	packagePage.add(btnOpenSocket);
	    size = btnOpenSocket.getPreferredSize(); 
	    btnOpenSocket.setBounds(15 + insets.left, 10 + insets.top, 
                     	 size.width, size.height); 
	    btnOpenSocket.addActionListener(new ActionListener(){
			@Override
			public void actionPerformed(ActionEvent arg0) {
				client.openSocket(adressSocket.getText(),portSocet.getText());
			}	    	
	    });
	    // кнопка тест
    	packagePage.add(btnTest);
	    size = btnTest.getPreferredSize(); 
	    btnTest.setBounds(485+ insets.left, 40 + insets.top, 
                     	 size.width, size.height); 
	    btnTest.addActionListener(new ActionListener(){
			@Override
			public void actionPerformed(ActionEvent arg0) {
				client.test();
			}	    	
	    });
	    
	    // кнопка отправки пакета
	    packagePage.add(btnSendPackage);
	    size = btnSendPackage.getPreferredSize(); 
	    btnSendPackage.setBounds(360 + insets.left, 40 + insets.top, 
                     	 size.width, size.height); 
	    btnSendPackage.addActionListener(new ActionListener(){
			@Override
			public void actionPerformed(ActionEvent arg0) {
				defPackage();
			}	    	
	    });
	    // кнопка очистки полей ввода
	    packagePage.add(btnClearInputs);
	    size = btnClearInputs.getPreferredSize(); 
	    btnClearInputs.setBounds(250 + insets.left, 40 + insets.top, 
                     	 size.width, size.height); 
	    btnClearInputs.addActionListener(new ActionListener(){
			@Override
			public void actionPerformed(ActionEvent arg0) {
				clearInputs();
			}	    	
	    });	    
	    // IP Адрес
		try {
			InetAddress IP = InetAddress.getLocalHost();
			ipLabel.setText(IP.getHostAddress());
			packagePage.add(ipLabel);
		    size = ipLabel.getPreferredSize(); 
		    ipLabel.setBounds(300 + insets.left, 10 + insets.top, 
	                     	 size.width, size.height); 
		} catch (UnknownHostException e) {
			e.printStackTrace();
			Custom.showMessage("Не получилось определить IP");	
		}
		  // кнопка очистки полей ввода
	    packagePage.add(setFocusB);
	    size = setFocusB.getPreferredSize(); 
	    setFocusB.setBounds(470 + insets.left, 9 + insets.top, 
                     	 size.width, size.height); 
	    setFocusB.addActionListener(new ActionListener(){
			@Override
			public void actionPerformed(ActionEvent arg0) {
			      content.setFocusable(true);
		          content.requestFocusInWindow();
			}	    	
	    });	    
	    // поле положения
	    packagePage.add(deltaSp);
        size = deltaSp.getPreferredSize(); 
    	deltaSp.setBounds(380 + insets.left, 10 + insets.top, 
    							size.width, size.height);
    	// поле скорости
	    packagePage.add(deltaPos);
    	size = deltaPos.getPreferredSize(); 
    	deltaPos.setBounds(430 + insets.left, 10 + insets.top, 
    							 size.width, size.height);
		
    }
    public void createJoindPage(){    
    	Container joindPage = new JPanel();
    	joindPage.setLayout(null);
    	Insets insets = joindPage.getInsets();
    	tabbedPane.addTab("Джоинды" ,joindPage);
    	 // кнопка отправки точек на контроллер
    	joindPage.add(btnSendJPoinst);
    	Dimension size = btnSendJPoinst.getPreferredSize(); 
	    btnSendJPoinst.setBounds(460 + insets.left, 50 + insets.top, 
	    					     100, size.height); 
	    btnSendJPoinst.addActionListener(new ActionListener(){
			@Override
			public void actionPerformed(ActionEvent arg0) {
				client.sendJPoints();
			}	    	
	    });
	    // кнопка удаления всех точек
	    joindPage.add(btnClearJPoinst);
	    size = btnClearJPoinst.getPreferredSize(); 
	    btnClearJPoinst.setBounds(460 + insets.left, 110 + insets.top, 
	    					   100, size.height); 
	    btnClearJPoinst.addActionListener(new ActionListener(){
			@Override
			public void actionPerformed(ActionEvent arg0) {
				client.clearJPoints();
			}	    	
	    });
	    // кнопка добавления точек поворота
	    joindPage.add(btnAddJPoint);
	    size = btnAddJPoint.getPreferredSize(); 
	    btnAddJPoint.setBounds(460 + insets.left, 80 + insets.top, 
                     	 	   100, size.height); 
	    btnAddJPoint.addActionListener(new ActionListener(){
			@Override
			public void actionPerformed(ActionEvent arg0) {
				client.addJPoint(sliders[0].getValue(),
							     sliders[1].getValue(),
							     sliders[2].getValue(),
							     sliders[3].getValue(),
							     sliders[4].getValue(),
							     sliders[5].getValue(),JPoints.ABSOLUTE,Integer.parseInt(jSpeedInput.getText()));
			}	    	
	    });	  
	    size = jSpeedInput.getPreferredSize(); 
	    jSpeedInput.setBounds(460 + insets.left, 140 + insets.top, 
      	 	   100, size.height); 
    	joindPage.add(jSpeedInput);
	    // слайдеры
	    for (int i=0;i<6;i++){
	    	sliders[i] = new JSlider(-360, 360, 0);
	    	joindPage.add(sliders[i]);
	    	sliders[i].setMajorTickSpacing(120);
	    	sliders[i].setMinorTickSpacing(30);
	    	sliders[i].setPaintLabels(true);
	    	sliders[i].setPaintTicks(true);
	    	sliders[i].setPaintTrack(true);
	    	sliders[i].setAutoscrolls(true);
	    	size = sliders[i].getPreferredSize(); 
	    	sliders[i].setBounds(30 + insets.left, 40+i*50 + insets.top, 
                     	 230, size.height);
	    	final int pos = i;
	    	sliders[pos].addChangeListener(new ChangeListener() {				
				@Override
				public void stateChanged(ChangeEvent arg0) {
					// TODO Auto-generated method stub
					sliderVals[pos].setText(sliders[pos].getValue()+"");
				}
			});
	    	slederLables[i] = new JLabel("j"+i);
	    	size = slederLables[i].getPreferredSize(); 
	    	slederLables[i].setBounds(10 + insets.left, 40+i*50 + insets.top, 
                	 230, size.height);
	    	joindPage.add(slederLables[i]);
	    	sliderVals[i] = new JLabel("0");
	    	size = sliderVals[i].getPreferredSize(); 
	    	sliderVals[i].setBounds(280 + insets.left, 40+i*50 + insets.top, 
                	 230, size.height);
	    	joindPage.add(sliderVals[i]);	    	
	    }
	    // монитор положений
	    for (int i=0;i<6;i++){
	    	jPosLables[i] = new JLabel("0");
	    	size = jPosLables[i].getPreferredSize(); 
	    	jPosLables[i].setBounds(320 + insets.left, 40+i*50 + insets.top, 
                	 230, size.height);
	    	joindPage.add(jPosLables[i]);
	    	limitLables[i] = new JLabel("["+ClientSocket.ULIMIMT[i]+":"+ClientSocket.LLIMIMT[i]+"]");
	    	size = limitLables[i].getPreferredSize(); 
	    	limitLables[i].setBounds(360 + insets.left, 40+i*50 + insets.top, 
                	 230, size.height);
	    	joindPage.add(limitLables[i]);
	    }  	    
    }
    
    
    public void createPositionPage(){    
    	Container positionPage = new JPanel();
    	positionPage.setLayout(null);
    	Insets insets = positionPage.getInsets();
    	tabbedPane.addTab("Декард" ,positionPage);
    	 // кнопка отправки точек на контроллер
    	positionPage.add(btnSendPosition);
    	Dimension size = btnSendPosition.getPreferredSize(); 
    	btnSendPosition.setBounds(460 + insets.left, 50 + insets.top, 
    								size.width, size.height); 
    	btnSendPosition.addActionListener(new ActionListener(){
			@Override
			public void actionPerformed(ActionEvent arg0) {
				client.runInPointD(slidersPos[0].getValue(),
								   slidersPos[1].getValue(),
								   slidersPos[2].getValue(),
								   slidersPos[3].getValue(),
								   slidersPos[4].getValue(),
								   slidersPos[5].getValue(),Integer.parseInt(dSpeedInput.getText()));
			}	    	
	    });	
    	size = dSpeedInput.getPreferredSize(); 
    	dSpeedInput.setBounds(460 + insets.left, 80 + insets.top, 
      	 	   100, size.height); 
    	positionPage.add(dSpeedInput);
  
    	
    	positionPage.add(btnHome1);
    	size = btnHome1.getPreferredSize(); 
    	btnHome1.setBounds(20 + insets.left, 350 + insets.top, 
    								size.width, size.height); 
    	btnHome1.addActionListener(new ActionListener(){
			@Override
			public void actionPerformed(ActionEvent arg0) {
				client.home1();
			}	    	
	    });	
    	
    	
    	positionPage.add(btnHome2);
    	size = btnHome2.getPreferredSize(); 
    	btnHome2.setBounds(100 + insets.left, 350 + insets.top, 
    								size.width, size.height); 
    	btnHome2.addActionListener(new ActionListener(){
			@Override
			public void actionPerformed(ActionEvent arg0) {
				client.home2();
			}	    	
	    });	
    	
    	
    	sledersPosLables[0] = new JLabel("x");
    	sledersPosLables[1] = new JLabel("y");
    	sledersPosLables[2] = new JLabel("z");
    	sledersPosLables[3] = new JLabel("a");
    	sledersPosLables[4] = new JLabel("o");
    	sledersPosLables[5] = new JLabel("t");
	    // слайдеры
	    for (int i=0;i<6;i++){
	    	slidersPos[i] = new JSlider(-1000, 1000, 0);
	    	positionPage.add(slidersPos[i]);
	    	slidersPos[i].setMajorTickSpacing(500);
	    	slidersPos[i].setMinorTickSpacing(250);
	    	slidersPos[i].setPaintLabels(true);
	    	slidersPos[i].setPaintTicks(true);
	    	slidersPos[i].setPaintTrack(true);
	    	slidersPos[i].setAutoscrolls(true);
	    	size = slidersPos[i].getPreferredSize(); 
	    	slidersPos[i].setBounds(30 + insets.left, 15+i*50 + insets.top, 
                     	 230, size.height);
	    	size = sledersPosLables[i].getPreferredSize(); 
	    	sledersPosLables[i].setBounds(10 + insets.left, 15+i*50 + insets.top, 
	            	 230, size.height);
	    	positionPage.add(sledersPosLables[i]);
	    	final int pos = i;
	    	slidersPos[pos].addChangeListener(new ChangeListener() {				
				@Override
				public void stateChanged(ChangeEvent arg0) {
					// TODO Auto-generated method stub
					slierDekartVals[pos].setText(slidersPos[pos].getValue()+"");
				}
			});
	    	slierDekartVals[i] = new JLabel("0");
	    	size = slierDekartVals[i].getPreferredSize(); 
	    	slierDekartVals[i].setBounds(280 + insets.left, 15+i*50 + insets.top, 
	            	 230, size.height);
	    	positionPage.add(slierDekartVals[i]);
	    	slierDekartPoss[i] = new JLabel("0");
	    	size = slierDekartPoss[i].getPreferredSize(); 
	    	slierDekartPoss[i].setBounds(310 + insets.left, 15+i*50 + insets.top, 
	            	 230, size.height);
	    	positionPage.add(slierDekartPoss[i]);
	    }	
    }    
   

    public void createAnglesPage(){    
    	Container anglesPage = new JPanel();
    	anglesPage.setLayout(null);
    	Insets insets = anglesPage.getInsets();
    	tabbedPane.addTab("Углы" ,anglesPage);
    	 // кнопка отправки точек на контроллер
    	anglesPage.add(btnSendAngles);
    	Dimension size = btnSendAngles.getPreferredSize(); 
    	btnSendAngles.setBounds(460 + insets.left, 50 + insets.top, 
    								size.width, size.height); 
    	btnSendAngles.addActionListener(new ActionListener(){
			@Override
			public void actionPerformed(ActionEvent arg0) {
				client.runInPointA(slidersAngle[0].getValue(),
									slidersAngle[1].getValue(),
									slidersAngle[2].getValue(),
									slidersAngle[3].getValue(),
									slidersAngle[4].getValue(),
									slidersAngle[5].getValue(),Integer.parseInt(aSpeedInput.getText()));
			}	    	
	    });	
    	size = aSpeedInput.getPreferredSize(); 
    	aSpeedInput.setBounds(460 + insets.left, 80 + insets.top, 
      	 	   100, size.height); 
    	anglesPage.add(aSpeedInput);
	    // слайдеры
	    for (int i=0;i<6;i++){
	    	slidersAngle[i] = new JSlider(ClientSocket.LLIMIMT[i], ClientSocket.ULIMIMT[i], 0);
	    	anglesPage.add(slidersAngle[i]);
	    	int ln = ClientSocket.ULIMIMT[i]-ClientSocket.LLIMIMT[i];
	    	slidersAngle[i].setMajorTickSpacing(ln/4);
	    	slidersAngle[i].setMinorTickSpacing(ln/8);
	    	slidersAngle[i].setPaintLabels(true);
	    	slidersAngle[i].setPaintTicks(true);
	    	slidersAngle[i].setPaintTrack(true);
	    	slidersAngle[i].setAutoscrolls(true);
	    	size = slidersAngle[i].getPreferredSize(); 
	    	slidersAngle[i].setBounds(30 + insets.left, 15+i*50 + insets.top, 
                     	 230, size.height);
	    	sledersAngleLables[i] = new JLabel("j"+i);
	    	size = sledersAngleLables[i].getPreferredSize(); 
	    	sledersAngleLables[i].setBounds(10 + insets.left, 15+i*50 + insets.top, 
	            	 230, size.height);
	    	
	    	anglesPage.add(sledersAngleLables[i]);
	    	final int pos = i;
	    	slidersAngle[pos].addChangeListener(new ChangeListener() {				
				@Override
				public void stateChanged(ChangeEvent arg0) {
					// TODO Auto-generated method stub
					slierAngleVals[pos].setText(slidersAngle[pos].getValue()+"");
				}
			});
	    	slierAngleVals[i] = new JLabel("0");
	    	size = slierAngleVals[i].getPreferredSize(); 
	    	slierAngleVals[i].setBounds(280 + insets.left, 15+i*50 + insets.top, 
	            	 230, size.height);
	    	anglesPage.add(slierAngleVals[i]);
	    	slierAnglePoss[i] = new JLabel("0");
	    	size = slierAnglePoss[i].getPreferredSize(); 
	    	slierAnglePoss[i].setBounds(310 + insets.left, 15+i*50 + insets.top, 
	            	 230, size.height);
	    	anglesPage.add(slierAnglePoss[i]);
	    }	
    }    
    
    public void createSensorPage(){
    	Container sensorPage = new JPanel();
    	sensorPage.setLayout(null);
    	Insets insets = sensorPage.getInsets();
    	tabbedPane.addTab("Датчик" ,sensorPage);
    	 // кнопка отправки точек на контроллер
    	sensorPage.add(btnStartSensor);
    	Dimension size = btnStartSensor.getPreferredSize(); 
    	btnStartSensor.setBounds(20 + insets.left, 20 + insets.top, 
    								size.width, size.height); 
    	btnStartSensor.addActionListener(new ActionListener(){
			@Override
			public void actionPerformed(ActionEvent arg0) {
				client.startSensor();
			}	    	
	    });	
    	sensorPage.add(btnStopSensor);
    	size = btnStopSensor.getPreferredSize(); 
    	btnStopSensor.setBounds(20 + insets.left, 50 + insets.top, 
    								size.width, size.height); 
    	btnStopSensor.addActionListener(new ActionListener(){
			@Override
			public void actionPerformed(ActionEvent arg0) {
				client.stopSensor();
			}	    	
	    });	
    	
    	for (int i=0;i<6;i++){
    		sensorLables[i] = new JLabel();
    		sensorLables[i] = new JLabel("j"+i);
        	size = sensorLables[i].getPreferredSize(); 
        	sensorLables[i].setBounds(120 + insets.left, 15+i*30 + insets.top, 
                	 230, size.height);        	
        	sensorPage.add(sensorLables[i]);
        	sensorProgress[i]=new JProgressBar();
        	size = sensorProgress[i].getPreferredSize(); 
        	sensorProgress[i].setBounds(170 + insets.left, 15+i*30 + insets.top, 
                	                   230, size.height);  
        	sensorPage.add(sensorProgress[i]);
        	sensorProgress[i].setMaximum(500000);
        	sensorValLables[i] = new JTextField("0");
        	size = sensorValLables[i].getPreferredSize(); 
        	sensorValLables[i].setBounds(400 + insets.left, 15+i*30 + insets.top, 
                	                   80, size.height);  
        	sensorPage.add(sensorValLables[i]);
    	}
    	sensorLables[0].setText("Fx");
    	sensorLables[1].setText("Fy");
    	sensorLables[2].setText("Fz");
    	sensorLables[3].setText("Tx");
    	sensorLables[4].setText("Ty");
    	sensorLables[5].setText("Tz");    
    	
    	for (int i=0;i<6;i++){
    		sensorLables[i] = new JLabel();
    		sensorLables[i] = new JLabel("j"+i);
        	size = sensorLables[i].getPreferredSize(); 
        	sensorLables[i].setBounds(120 + insets.left, 15+i*30 + insets.top, 
                	 230, size.height);        	
        	sensorPage.add(sensorLables[i]);
        	sensorProgress[i]=new JProgressBar();
        	size = sensorProgress[i].getPreferredSize(); 
        	sensorProgress[i].setBounds(170 + insets.left, 15+i*30 + insets.top, 
                	                   230, size.height);  
        	sensorPage.add(sensorProgress[i]);
        	sensorProgress[i].setMaximum(500000);
        	sensorValLables[i] = new JTextField("0");
        	size = sensorValLables[i].getPreferredSize(); 
        	sensorValLables[i].setBounds(400 + insets.left, 15+i*30 + insets.top, 
                	                   80, size.height);  
        	sensorPage.add(sensorValLables[i]);
    	}
    	sensorLables[0].setText("Fx");
    	sensorLables[1].setText("Fy");
    	sensorLables[2].setText("Fz");
    	sensorLables[3].setText("Tx");
    	sensorLables[4].setText("Ty");
    	sensorLables[5].setText("Tz");    
    	
    	for (int i=6;i<12;i++){
    		sensorLables[i] = new JLabel();
    		sensorLables[i] = new JLabel("j"+i);
        	size = sensorLables[i].getPreferredSize(); 
        	sensorLables[i].setBounds(120 + insets.left, 50+i*30 + insets.top, 
                	 230, size.height);        	
        	sensorPage.add(sensorLables[i]);
        	sensorProgress[i]=new JProgressBar();
        	size = sensorProgress[i].getPreferredSize(); 
        	sensorProgress[i].setBounds(170 + insets.left, 50+i*30 + insets.top, 
                	                   230, size.height);  
        	sensorPage.add(sensorProgress[i]);
        	sensorProgress[i].setMaximum(500000);
        	sensorValLables[i] = new JTextField("0");
        	size = sensorValLables[i].getPreferredSize(); 
        	sensorValLables[i].setBounds(400 + insets.left, 50+i*30 + insets.top, 
                	                   80, size.height);  
        	sensorPage.add(sensorValLables[i]);
    	}
    	sensorLables[6].setText("FxR");
    	sensorLables[7].setText("FyR");
    	sensorLables[8].setText("FzR");
    	sensorLables[9].setText("TxR");
    	sensorLables[10].setText("TyR");
    	sensorLables[11].setText("TzR");    
    }
    
    public void createProgramPage(){    
    	Container programPage = new JPanel();
    	programPage.setLayout(null);
    	Insets insets = programPage.getInsets();
    	tabbedPane.addTab("Программы" ,programPage);
    	 // кнопка отправки точек на контроллер
    	Dimension size = btnStartGravity.getPreferredSize(); 
    	btnStartGravity.setBounds(460 + insets.left, 50 + insets.top, 
    								size.width, size.height); 
    	btnStartGravity.addActionListener(new ActionListener(){
			@Override
			public void actionPerformed(ActionEvent arg0) {
				client.setParams(Integer.parseInt(accelEdit.getText()),
						 Integer.parseInt(decelEdit.getText()),
						 Integer.parseInt(speedEdit.getText()),
						 Integer.parseInt(mmpsEdit.getText()),
						 Integer.parseInt(deltaEdit.getText()),
						 Integer.parseInt(maxDeltaEdit.getText()));
				/*client.startGravityProgram(Integer.parseInt(kPxEdit.getText()),
										   Integer.parseInt(kPyEdit.getText()),
										   Integer.parseInt(kPzEdit.getText()),
										   Integer.parseInt(kIxEdit.getText()),
										   Integer.parseInt(kIyEdit.getText()),
										   Integer.parseInt(kIzEdit.getText()));*/
				client.openLog("1.txt");
			}	    	
	    });	
    	size = btnStopGravity.getPreferredSize(); 
    	btnStopGravity.setBounds(460 + insets.left, 80 + insets.top, 
      	 	   100, size.height); 
    	
    	btnStopGravity.addActionListener(new ActionListener(){
			@Override
			public void actionPerformed(ActionEvent arg0) {
				client.stopGravityProgram();
				client.closeLog();
			}	    	
	    });	
    	size = kPx.getPreferredSize(); 
    	kPx.setBounds(15 + insets.left, 15+ insets.top, 
    			size.width, size.height);  
    	kPy.setBounds(15 + insets.left, 35+ insets.top, 
    			size.width, size.height); 
    	kPz.setBounds(15 + insets.left, 55+ insets.top, 
    			size.width, size.height); 
    	size = kPxEdit.getPreferredSize(); 
    	kPxEdit.setBounds(65 + insets.left, 15+ insets.top, 
    			40, size.height);  
    	kPyEdit.setBounds(65 + insets.left, 35+ insets.top, 
    			40, size.height);  
    	kPzEdit.setBounds(65 + insets.left, 55+ insets.top, 
    			40, size.height); 
    	
    	size = kIx.getPreferredSize(); 
    	kIx.setBounds(140 + insets.left, 15+ insets.top, 
    			size.width, size.height);  
    	kIy.setBounds(140 + insets.left, 35+ insets.top, 
    			size.width, size.height); 
    	kIz.setBounds(140 + insets.left, 55+ insets.top, 
    			size.width, size.height); 
    	size = kIxEdit.getPreferredSize(); 
    	kIxEdit.setBounds(185 + insets.left, 15+ insets.top, 
    			40, size.height);  
    	kIyEdit.setBounds(185 + insets.left, 35+ insets.top, 
    			40, size.height);  
    	kIzEdit.setBounds(185 + insets.left, 55+ insets.top, 
    			40, size.height);     	
    	
    	size = kPMx.getPreferredSize(); 
    	kPMx.setBounds(15 + insets.left, 95+ insets.top, 
    			size.width, size.height);  
    	kPMy.setBounds(15 + insets.left, 115+ insets.top, 
    			size.width, size.height); 
    	kPMz.setBounds(15 + insets.left, 135+ insets.top, 
    			size.width, size.height); 
    	size = kPMxEdit.getPreferredSize(); 
    	kPMxEdit.setBounds(65 + insets.left, 95+ insets.top, 
    			40, size.height);  
    	kPMyEdit.setBounds(65 + insets.left, 115+ insets.top, 
    			40, size.height);  
    	kPMzEdit.setBounds(65 + insets.left, 135+ insets.top, 
    			40, size.height); 
    	
    	size = kIMx.getPreferredSize(); 
    	kIMx.setBounds(140 + insets.left, 95+ insets.top, 
    			size.width, size.height);  
    	kIMy.setBounds(140 + insets.left, 115+ insets.top, 
    			size.width, size.height); 
    	kIMz.setBounds(140 + insets.left, 135+ insets.top, 
    			size.width, size.height); 
    	size = kIxEdit.getPreferredSize(); 
    	kIMxEdit.setBounds(185 + insets.left, 95+ insets.top, 
    			40, size.height);  
    	kIMyEdit.setBounds(185 + insets.left, 115+ insets.top, 
    			40, size.height);  
    	kIMzEdit.setBounds(185 + insets.left, 135+ insets.top, 
    			40, size.height);     	
    	
    	size = accelLabel.getPreferredSize(); 
    	accelLabel.setBounds(60 + insets.left, 180+ insets.top, 
    			size.width, size.height);  
    	size = decelLabel.getPreferredSize(); 
    	decelLabel.setBounds(60 + insets.left, 205+ insets.top, 
    			size.width, size.height);  
    	size = speedLabel.getPreferredSize(); 
    	speedLabel.setBounds(60 + insets.left, 230+ insets.top, 
    			size.width, size.height);  
    	
    	size = mmpsLabel.getPreferredSize(); 
    	mmpsLabel.setBounds(60 + insets.left, 255+ insets.top, 
    			size.width, size.height);  
    	size = deltaLabel.getPreferredSize(); 
    	deltaLabel.setBounds(60 + insets.left, 280+ insets.top, 
    			size.width, size.height);  
    	size = maxDeltaLabel.getPreferredSize(); 
    	maxDeltaLabel.setBounds(60 + insets.left, 305+ insets.top, 
    			size.width, size.height);  
    	
    	size = accelEdit.getPreferredSize(); 
    	accelEdit.setBounds(160 + insets.left, 180+ insets.top, 
    			size.width, size.height);  
    	size = decelEdit.getPreferredSize(); 
    	decelEdit.setBounds(160 + insets.left, 205+ insets.top, 
    			size.width, size.height);  
    	size = speedEdit.getPreferredSize(); 
    	speedEdit.setBounds(160 + insets.left, 230+ insets.top, 
    			size.width, size.height);  
    	size = mmpsEdit.getPreferredSize(); 
    	mmpsEdit.setBounds(160 + insets.left, 255+ insets.top, 
    			size.width, size.height);  
    	size = deltaEdit.getPreferredSize(); 
    	deltaEdit.setBounds(160 + insets.left, 280+ insets.top, 
    			size.width, size.height);  
    	size = maxDeltaEdit.getPreferredSize(); 
    	maxDeltaEdit.setBounds(160 + insets.left, 305+ insets.top, 
    			size.width, size.height);  
    	
    	size = btnSetParams.getPreferredSize(); 
    	btnSetParams.setBounds(300 + insets.left, 180 + insets.top, 
      	 	   100, size.height); 
    	
    	btnSetParams.addActionListener(new ActionListener(){
			@Override
			public void actionPerformed(ActionEvent arg0) {
				client.setParams(Integer.parseInt(accelEdit.getText()),
								 Integer.parseInt(decelEdit.getText()),
								 Integer.parseInt(speedEdit.getText()),
								 Integer.parseInt(mmpsEdit.getText()),
								 Integer.parseInt(deltaEdit.getText()),
								 Integer.parseInt(maxDeltaEdit.getText()));
			}	    	
	    });	
    	size = btnHomeP.getPreferredSize(); 
    	btnHomeP.setBounds(300 + insets.left, 210 + insets.top, 
       	 	   	100, size.height); 
    	btnHomeP.addActionListener(new ActionListener(){
 			@Override
 			public void actionPerformed(ActionEvent arg0) {
 				client.home1();
 			}	    	
 	    });	
     	size = btnHomeP2.getPreferredSize(); 
     	btnHomeP2.setBounds(300 + insets.left, 240 + insets.top, 
       	 	   				100, size.height); 
     	btnHomeP2.addActionListener(new ActionListener(){
 			@Override
 			public void actionPerformed(ActionEvent arg0) {
 				client.home2();
 			}	    	
 	    });	
     	programPage.add(maxDeltaEdit);
     	programPage.add(maxDeltaLabel);
    	programPage.add(btnHomeP);
    	programPage.add(btnHomeP2);
    	programPage.add(btnSetParams);
    	programPage.add(accelEdit);
    	programPage.add(decelEdit);
    	programPage.add(speedEdit);
    	programPage.add(deltaEdit);
    	programPage.add(mmpsEdit);
    	programPage.add(mmpsLabel);
    	programPage.add(accelLabel);
    	programPage.add(decelLabel);
    	programPage.add(speedLabel);
    	programPage.add(deltaLabel);
    	programPage.add(btnStopGravity);
    	programPage.add(btnStartGravity);
    	programPage.add(kPx);
    	programPage.add(kPy);
    	programPage.add(kPz);
    	programPage.add(kPxEdit);
    	programPage.add(kPyEdit);
    	programPage.add(kPzEdit);
    	programPage.add(kIx);
    	programPage.add(kIy);
    	programPage.add(kIz);
    	programPage.add(kIxEdit);
    	programPage.add(kIyEdit);
    	programPage.add(kIzEdit);
    	programPage.add(kPMx);
    	programPage.add(kPMy);
    	programPage.add(kPMz);
    	programPage.add(kPMxEdit);
    	programPage.add(kPMyEdit);
    	programPage.add(kPMzEdit);
    	programPage.add(kIMx);
    	programPage.add(kIMy);
    	programPage.add(kIMz);
    	programPage.add(kIMxEdit);
    	programPage.add(kIMyEdit);
    	programPage.add(kIMzEdit);
    	programPage.add(setFocusB);
    }    
    
	public ClientGui() {
		
	    super("Simple Example");
	    this.setBounds(100,100,660,480);
	    this.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
	keyListener = new KeyListener() {
			
			@Override
			public void keyTyped(KeyEvent arg0) {	
				if (flgFirstGet){	
					flgFirstGet = false;
					curPositions= client.getPositions();					
				}
				char c = arg0.getKeyChar();
				isKeyDown[(int)c] = true;				
			}
			
			@Override
			public void keyReleased(KeyEvent arg0) {
				char c = arg0.getKeyChar();	
				isKeyDown[(int)c] = false;				
			}
			
			@Override
			public void keyPressed(KeyEvent arg0) {
			}
		};
	    
	    // Контейнер        
        content = new JPanel();
        
        ChangeListener changeListener = new ChangeListener() {
            public void stateChanged(ChangeEvent changeEvent) {
              JTabbedPane sourceTabbedPane = (JTabbedPane) changeEvent.getSource();
              switch(sourceTabbedPane.getSelectedIndex()){
              case 2:
            	  	int [] arr = client.getPositions();
            		for (int i=0;i<6;i++){
            			slidersPos[i].setValue(arr[i]);
            		}
            		break;
              case 3:
            		int [] arr2 = client.getRotations();
    				for (int i=0;i<6;i++){
    					slidersAngle[i].setValue(arr2[i]);
    				}
            	  	break;
              }              
            }
          };
          tabbedPane.addChangeListener(changeListener);
          
          content.setFocusable(true);
          content.requestFocusInWindow();
        content.setLayout(new BorderLayout());
        content.addKeyListener(keyListener);
        getContentPane().add(content);
        content.add(tabbedPane);
        
  
        createPackagePage();
        createJoindPage();
        createPositionPage();
        createAnglesPage();
        createSensorPage();
        createProgramPage();
		
		this.addWindowListener(new WindowAdapter(){
            public void windowClosing(WindowEvent e){
            	if (client.flgOpenSocket)
            		client.closeSocket();
            	client.stopSensor();
            }
        });
		client = new ClientSocket();
		client.openSocket(adressSocket.getText(),portSocet.getText());
		timeSendC.schedule(new TimerTask() {
 	        @Override
 	        public void run() { //ПЕРЕЗАГРУЖАЕМ МЕТОД RUN В КОТОРОМ ДЕЛАЕТЕ ТО ЧТО ВАМ НАДО
 	        	dCoordArr = new int[6];
 	        	boolean flgCom = false;
 	        	int delta = Integer.parseInt(deltaEdit.getText());
 	        	if (isKeyDown[(int)'ц']||isKeyDown[(int)'w']){
 	        		dCoordArr[0]+=delta;
 	        		flgCom=true;
 	        	}
 	        	if (isKeyDown[(int)'ы']||isKeyDown[(int)'s']){
 	        		dCoordArr[0]-=delta;
 	        		flgCom=true;
 	        	}
 	        	if (isKeyDown[(int)'ф']||isKeyDown[(int)'a']){
 	        		dCoordArr[1]+=delta;
 	        		flgCom=true;
 	        	}
 	        	if (isKeyDown[(int)'в']||isKeyDown[(int)'d']){
 	        		dCoordArr[1]-=delta;
 	        		flgCom=true;
 	        	}
 	        	if (isKeyDown[(int)'й']||isKeyDown[(int)'q']){
 	        		dCoordArr[2]+=delta;
 	        		flgCom=true;
 	        	}
 	        	if (isKeyDown[(int)'у']||isKeyDown[(int)'e']){
 	        		dCoordArr[2]-=delta;
 	        		flgCom=true;
 	        	}	
 	        	if(flgCom){
 	        		if (flgFirstDeltaPos) {
 	               		client.enableDelta();
 	               		System.out.println("Delta Start works");
 	        		}
 	        		flgFirstDeltaPos = false;
 	        		client.setDelta(dCoordArr,15);
 	        	}else{
 	        		if (!flgFirstDeltaPos){
 	        			client.disableDelta();
 	        			System.out.println("Delta Stop works");
 	        		}
 	        		flgFirstDeltaPos = true;
 	        	}
 	        	
 	        	/*if (!flgFirstGet&&flgCom){
 	        		for(int i =0;i<3;i++){
 	        			curPositions[i]+=dCoordArr[i];
 	        		} 	        		
 	        		//System.out.println(curPositions[0]+"  "+curPositions[1]+"  "+curPositions[2]);
 	        	}*/
 	        }
 	    }, 0, 150); //(4000 - ПОДОЖДАТЬ ПЕРЕД НАЧАЛОМ В МИЛИСЕК, ПОВТОРЯТСЯ 4 СЕКУНДЫ (1 СЕК = 1000 МИЛИСЕК))

		time.schedule(new TimerTask() {
	 	        @Override
	 	        public void run() { //ПЕРЕЗАГРУЖАЕМ МЕТОД RUN В КОТОРОМ ДЕЛАЕТЕ ТО ЧТО ВАМ НАДО
	 	        	int [] paramsJ = client.getRotations();
	 	        	int [] paramsD = client.getPositions();
	 	        	int [] sensorVals = client.getSensorVals();
	 	        	int [] sensorRVals = client.getSensorRVals();
	 	        	
	 	        	for (int i=0;i<6;i++){
	 	        		jPosLables[i].setText(paramsJ[i]+"");
	 	        		slierDekartPoss[i].setText(paramsD[i]+"");
	 	        		if ( sensorVals[i] < 0)
	 	        			sensorProgress[i].setForeground( Color.blue );
	                    else
	                    	sensorProgress[i].setForeground( Color.green );
	 	        		sensorProgress[i].setValue(Math.abs(sensorVals[i]));
	 	        		sensorValLables[i].setText(sensorVals[i]+"");
	 	        	}
	 	        	for (int i=6;i<12;i++){	 	      
	 	        		if ( sensorRVals[i-6] < 0)
	 	        			sensorProgress[i].setForeground( Color.blue );
	                    else
	                    	sensorProgress[i].setForeground( Color.green );
	 	        		sensorProgress[i].setValue(Math.abs(sensorRVals[i-6]));
	 	        		sensorValLables[i].setText(sensorRVals[i-6]+"");
	 	        	}
	 	        	
	 	        }
	 	    }, 0, 100); //(4000 - ПОДОЖДАТЬ ПЕРЕД НАЧАЛОМ В МИЛИСЕК, ПОВТОРЯТСЯ 4 СЕКУНДЫ (1 СЕК = 1000 МИЛИСЕК))
	}    
	void defPackage(){
		//int iArr[] = {242,3423,5212};
		//double fArr[] = {123.7821,4234.0,123.12,23589.2,2344092.124879,532.129};
		int iArr[] = new int[9];
		double fArr[] = new double[6];
		client.flush();
		for (int i=0;i<inputsCnt/9;i++){
			boolean flgTyped = false;
			for (int j=0;j<9;j++)
				if(!inputs[i*9+j].getText().equals(""))
					flgTyped = true;
			if (flgTyped){
				for (int j=0;j<9;j++)
					if(inputs[i*9+j].getText().equals(""))
						iArr[j]=0;
					else{
						//System.out.println(inputs[i*9+j].getText());
						iArr[j]=Integer.parseInt(inputs[i*9+j].getText());
					}
				for (int j=3;j<9;j++)
					if(inputs[i*9+j].getText().equals(""))
						fArr[j-3]=0;
					else
						fArr[j-3]=Double.parseDouble(inputs[i*9+j].getText());
				//client.sendVals(iArr,fArr);
				client.sendVals2(iArr);
			}		
		}	
	}	
	
	public static void main(String[] args) {
		ClientGui app = new ClientGui();
		app.setVisible(true);
	}
	
	// элементы вкладки "пакеты
	private JButton btnOpenSocket = new JButton("OpenSocket");
	private JButton btnCloseSocket = new JButton("CloseSocket");
	private JButton btnClearInputs = new JButton("ClearInputs");
	private JButton btnSendPackage = new JButton("SendPackage");
	private JTextField portSocet = new JTextField("40000", 5);
	private JTextField adressSocket = new JTextField("192.168.1.0", 8);
	final static int inputsCnt = 99;	
	private JTextField [] inputs = new JTextField[inputsCnt];
	private JButton btnTest = new JButton("Test");
	private JLabel ipLabel = new JLabel();	
	private JTextField deltaSp  = new JTextField("10", 3);
	private JTextField deltaPos = new JTextField("5", 3);
	private JButton setFocusB = new JButton("SetFocus");
	// элементы вкладки джоиндов
	private JButton btnAddJPoint = new JButton("AddPoint");
	private JButton btnSendJPoinst = new JButton("SendJPoint");
	private JButton btnClearJPoinst = new JButton("ClearPoint");	

	private JButton [] buttons = new JButton[10];
	private JSlider [] sliders = new JSlider[6];
	private JLabel[] sliderVals = new JLabel[6];
	private JLabel[] slederLables = new JLabel[6];
	private JLabel[] limitLables = new JLabel[6];
	private JTextField jSpeedInput = new JTextField("10");
	// элементы вкладки позиций
	private JSlider [] slidersPos = new JSlider[6];
	private JLabel[] sledersPosLables = new JLabel[6];
	private JLabel[] slierDekartVals = new JLabel[6];
	private JLabel[] slierDekartPoss = new JLabel[6];
	private JButton btnHome1 = new JButton("Home1");
	private JButton btnHome2 = new JButton("Home2");
	private JTextField dSpeedInput = new JTextField("10");
	private JButton btnSendPosition = new JButton("SendPosition");
	// элементы вкладки углов
	private JSlider [] slidersAngle = new JSlider[6];
	private JLabel[] sledersAngleLables = new JLabel[6];
	private JLabel[] slierAngleVals = new JLabel[6];
	private JLabel[] slierAnglePoss = new JLabel[6];
	private JTextField aSpeedInput = new JTextField("10");
	private JButton btnSendAngles = new JButton("SendPosition");
	// элементы вкладки датчика
	private JButton btnStartSensor = new JButton("Start");
	private JButton btnStopSensor = new JButton("Stop");
	private JProgressBar [] sensorProgress = new JProgressBar[12];
	private JLabel[] sensorLables = new JLabel[12];
	private JTextField[] sensorValLables = new JTextField[12];
	// элементы обратной связи
	public JLabel [] jPosLables = new JLabel[6]; 
	
	final JTabbedPane tabbedPane = new JTabbedPane();
	
	private JButton btnStartGravity = new JButton("StartGravity");
	private JButton btnStopGravity  = new JButton("StopGravity");
	
	private JLabel kPx = new JLabel("kPx");
	private JLabel kPy = new JLabel("kPy");
	private JLabel kPz = new JLabel("kPz");
	
	private JTextField kPxEdit = new JTextField("1",2);
	private JTextField kPyEdit = new JTextField("1",2);
	private JTextField kPzEdit = new JTextField("1",2);

	private JLabel kIx = new JLabel("kIx");
	private JLabel kIy = new JLabel("kIy");
	private JLabel kIz = new JLabel("kIz");
	
	private JTextField kIxEdit = new JTextField("1",2);
	private JTextField kIyEdit = new JTextField("1",2);
	private JTextField kIzEdit = new JTextField("1",2);
	
	private JLabel kPMx = new JLabel("kPMx");
	private JLabel kPMy = new JLabel("kPMy");
	private JLabel kPMz = new JLabel("kPMz");
	
	private JTextField kPMxEdit = new JTextField("1",2);
	private JTextField kPMyEdit = new JTextField("1",2);
	private JTextField kPMzEdit = new JTextField("1",2);
	
	private JLabel kIMx = new JLabel("kIMx");
	private JLabel kIMy = new JLabel("kIMy");
	private JLabel kIMz = new JLabel("kIMz");
	
	private JTextField kIMxEdit = new JTextField("1",2);
	private JTextField kIMyEdit = new JTextField("1",2);
	private JTextField kIMzEdit = new JTextField("1",2);
	
	private JTextField accelEdit = new JTextField("100",3);
	private JTextField decelEdit = new JTextField("100",3);
	private JTextField speedEdit = new JTextField("10",3);
	private JTextField deltaEdit = new JTextField("1",3);
	private JTextField mmpsEdit = new JTextField("100",3);
	private JTextField maxDeltaEdit = new JTextField("20",3);
	
	private JLabel accelLabel = new JLabel("Accel");
	private JLabel decelLabel = new JLabel("Decel");
	private JLabel speedLabel = new JLabel("SpeedProc");
	private JLabel mmpsLabel = new JLabel("SpeedMMPS");
	private JLabel deltaLabel = new JLabel("delta");
	private JLabel maxDeltaLabel = new JLabel("maxDelta");
	
	private JButton btnSetParams = new JButton("SetParams");
	private JButton btnHomeP = new JButton("Home");
	private JButton btnHomeP2 = new JButton("Home2");
}