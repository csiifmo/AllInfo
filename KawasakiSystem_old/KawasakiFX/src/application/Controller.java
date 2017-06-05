package application;

import Servers.AndroidServer;
import Servers.ForceSensor;
import Servers.RaspberryServer;
import javafx.concurrent.Task;
import javafx.fxml.FXML;
import javafx.scene.control.Button;
import javafx.scene.control.ProgressBar;
import javafx.scene.control.Slider;
import javafx.scene.control.TextField;
import javafx.scene.input.MouseEvent;
import Servers.KawasakiSocketServer;

import java.awt.*;
import java.lang.reflect.Array;
import java.util.Arrays;
import java.util.Timer;
import java.util.TimerTask;

public class Controller {

    private KawasakiSocketServer kServer;
    private RaspberryServer rServer;
    private AndroidServer aServer;
    private Timer mTimer;
    private ForceSensor forceSensor;


    // остановка контроллера
    public void close() {
        // останавливаем сервер кавасаки
        if (kServer != null) kServer.close();
        // останавливаем таймер контроллера
        if (mTimer != null) {
            mTimer.cancel();
            mTimer.purge();
        }
    }

    void setForceSensorVals() {
        int[] sensorVals = forceSensor.getVals();
        prValX.setProgress((double)Math.abs(sensorVals[0])/150000);
        prValY.setProgress((double)Math.abs(sensorVals[1])/150000);
        prValZ.setProgress((double)Math.abs(sensorVals[2])/150000);
        prValMX.setProgress((double)Math.abs(sensorVals[3])/1500);
        prValMY.setProgress((double)Math.abs(sensorVals[4])/1500);
        prValMZ.setProgress((double)Math.abs(sensorVals[5])/1500);

        if (sensorVals[0] < 0)
            setBarStyleClass(prValX, RED_BAR);
        else
            setBarStyleClass(prValX, GREEN_BAR);
        if (sensorVals[1] < 0)
            setBarStyleClass(prValY, RED_BAR);
        else
            setBarStyleClass(prValY, GREEN_BAR);
        if (sensorVals[2] < 0)
            setBarStyleClass(prValZ, RED_BAR);
        else
            setBarStyleClass(prValZ, GREEN_BAR);
        if (sensorVals[3] < 0)
            setBarStyleClass(prValMX, RED_BAR);
        else
            setBarStyleClass(prValMX, GREEN_BAR);

        if (sensorVals[4] < 0)
            setBarStyleClass(prValMY, RED_BAR);
        else
            setBarStyleClass(prValMY, GREEN_BAR);
        if (sensorVals[5] < 0)
            setBarStyleClass(prValMZ, RED_BAR);
        else
            setBarStyleClass(prValMZ, GREEN_BAR);
    }

    void setForceSensorRVals() {
        int[] sensorVals = forceSensor.getRVals();
        prRValX.setProgress((double)Math.abs(sensorVals[0])/150000);
        prRValY.setProgress((double)Math.abs(sensorVals[1])/150000);
        prRValZ.setProgress((double)Math.abs(sensorVals[2])/150000);
        prRValMX.setProgress((double)Math.abs(sensorVals[3])/1500);
        prRValMY.setProgress((double)Math.abs(sensorVals[4])/1500);
        prRValMZ.setProgress((double)Math.abs(sensorVals[5])/1500);

        if (sensorVals[0] < 0)
            setBarStyleClass(prRValX, RED_BAR);
        else
            setBarStyleClass(prRValX, GREEN_BAR);
        if (sensorVals[1] < 0)
            setBarStyleClass(prRValY, RED_BAR);
        else
            setBarStyleClass(prRValY, GREEN_BAR);
        if (sensorVals[2] < 0)
            setBarStyleClass(prRValZ, RED_BAR);
        else
            setBarStyleClass(prRValZ, GREEN_BAR);
        if (sensorVals[3] < 0)
            setBarStyleClass(prRValMX, RED_BAR);
        else
            setBarStyleClass(prRValMX, GREEN_BAR);

        if (sensorVals[4] < 0)
            setBarStyleClass(prRValMY, RED_BAR);
        else
            setBarStyleClass(prRValMY, GREEN_BAR);
        if (sensorVals[5] < 0)
            setBarStyleClass(prRValMZ, RED_BAR);
        else
            setBarStyleClass(prRValMZ, GREEN_BAR);
    }



    private void onTime() {
        // будет выполняться по таймеру
        setCameraVals();
        setForceSensorVals();
        setForceSensorRVals();
        System.out.println(Arrays.toString(forceSensor.getRVals()));
    }


    @FXML
    public void initialize() {
        kServer = new KawasakiSocketServer("Kawasaki");
        rServer = new RaspberryServer("Malina");
        aServer = new AndroidServer("Android");
        aServer.setkServer(kServer);

        forceSensor = new ForceSensor();
        forceSensor.start(100);
        kServer.setSensor(forceSensor);

        new Thread(() -> kServer.openSocket(40000)).start();    //Запуск потока
        new Thread(() -> rServer.openSocket(5005)).start();    //Запуск потока
        new Thread(() -> aServer.openSocket(30000)).start();    //Запуск потока
        try {
            Thread.sleep(1000);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        initTimer();
        addEvents();

    }

    // инициализация таймера
    private void initTimer() {
        int firstDelay = 1000; // задержка перед первым срабатыванием таймера
        int repeat = 500; // время между срабатываниями таймера
        mTimer = new Timer();
        // задержка 1000ms, repeat in 5000ms
        mTimer.schedule(new TimerTask() {
            @Override
            public void run() {
                onTime();
            }
        }, firstDelay, repeat);
    }

    // обработчики событий
    private void addEvents() {
        // нажатие на кнопку Home
        btnHome.addEventHandler(MouseEvent.MOUSE_CLICKED, mouseEvent -> kServer.home1(updateSlidersRunnable));
        // нажатие на кнопку Home2
        btnHome2.addEventHandler(MouseEvent.MOUSE_CLICKED, mouseEvent -> kServer.home2(updateSlidersRunnable));
        // нажатие на кнопку Совместить
        btnAccess.addEventHandler(MouseEvent.MOUSE_CLICKED, mouseEvent -> setSliders());
        // нажатие на кнопку двигаться по джоинтам
        jBtnMove.addEventHandler(MouseEvent.MOUSE_CLICKED, mouseEvent ->
                kServer.runInPointA((int) jPosScroll1.getValue(),
                        (int) jPosScroll2.getValue(),
                        (int) jPosScroll3.getValue(),
                        (int) jPosScroll4.getValue(),
                        (int) jPosScroll5.getValue(),
                        (int) jPosScroll6.getValue(), 20, updateSlidersRunnable));
        // нажатие на кнопку двигаться по декарту
        dBtnMove.addEventHandler(MouseEvent.MOUSE_CLICKED, mouseEvent ->
                kServer.runInPointD((int) dPosScroll1.getValue(),
                        (int) dPosScroll2.getValue(),
                        (int) dPosScroll3.getValue(),
                        (int) dPosScroll4.getValue(),
                        (int) dPosScroll5.getValue(),
                        (int) dPosScroll6.getValue(), 20, updateSlidersRunnable));
        gravityBtn.addEventHandler(MouseEvent.MOUSE_CLICKED, mouseEvent -> {
            kServer.sendChangeGravity();
        });
    }

    private void setCameraVals() {
        int[] data = rServer.getData();
        cameraX.setText((double) data[1] / 1000 + "");
        cameraY.setText((double) data[2] / 1000 + "");
        cameraR.setText((double) data[3] / 1000 + "");
    }

    // задаём значения слайдеров
    private void setSliders() {
        // если кавасаки не создан или нельзя получить от него данные
        if (kServer == null || !kServer.flgOpenSocket)
            // обрываем выполнение функции
            return;
        int rot[] = kServer.getRotations();
        int pos[] = kServer.getPositions();
        jPosScroll1.setValue(rot[0]);
        jPosScroll2.setValue(rot[1]);
        jPosScroll3.setValue(rot[2]);
        jPosScroll4.setValue(rot[3]);
        jPosScroll5.setValue(rot[4]);
        jPosScroll6.setValue(rot[5]);

        dPosScroll1.setValue(pos[0]);
        dPosScroll2.setValue(pos[1]);
        dPosScroll3.setValue(pos[2]);
        dPosScroll4.setValue(pos[3]);
        dPosScroll5.setValue(pos[4]);
        dPosScroll6.setValue(pos[5]);
    }

    /*
        Переменные, связывающие объекты в файле разметки и объекты на форме
     */
    @FXML
    TextField cameraX;
    @FXML
    TextField cameraY;
    @FXML
    TextField cameraR;
    @FXML
    Button btnHome;
    @FXML
    Button btnHome2;
    @FXML
    Button btnAccess;
    @FXML
    Slider jPosScroll1;
    @FXML
    Slider jPosScroll2;
    @FXML
    Slider jPosScroll3;
    @FXML
    Slider jPosScroll4;
    @FXML
    Slider jPosScroll5;
    @FXML
    Slider jPosScroll6;
    @FXML
    Button jBtnMove;
    @FXML
    Slider dPosScroll1;
    @FXML
    Slider dPosScroll2;
    @FXML
    Slider dPosScroll3;
    @FXML
    Slider dPosScroll4;
    @FXML
    Slider dPosScroll5;
    @FXML
    Slider dPosScroll6;
    @FXML
    Button dBtnMove;

    public ProgressBar prValX = new ProgressBar();
    public ProgressBar prValY = new ProgressBar();
    public ProgressBar prValZ = new ProgressBar();
    public ProgressBar prValMX = new ProgressBar();
    public ProgressBar prValMY = new ProgressBar();
    public ProgressBar prValMZ = new ProgressBar();
    public ProgressBar prRValX = new ProgressBar();
    public ProgressBar prRValY = new ProgressBar();
    public ProgressBar prRValZ = new ProgressBar();
    public ProgressBar prRValMX = new ProgressBar();
    public ProgressBar prRValMY = new ProgressBar();
    public ProgressBar prRValMZ = new ProgressBar();


    Runnable updateSlidersRunnable = new Runnable() {
        @Override
        public void run() {
            setSliders();
        }
    };

    private void setBarStyleClass(ProgressBar bar, String barStyleClass) {
        bar.getStyleClass().removeAll(barColorStyleClasses);
        bar.getStyleClass().add(barStyleClass);
    }


    public Button gravityBtn;
    private static final String RED_BAR = "red-bar";
    private static final String YELLOW_BAR = "yellow-bar";
    private static final String ORANGE_BAR = "orange-bar";
    private static final String GREEN_BAR = "green-bar";
    private static final String[] barColorStyleClasses = {RED_BAR, ORANGE_BAR, YELLOW_BAR, GREEN_BAR};


}
