package Servers;

import java.util.*;

public class KawasakiSocketServer extends SocketServer {
    private boolean flgInPosition = false;
    private int rotations[] = new int[6];
    private int positions[] = new int[6];
    private int errors[] = new int[6];
    private int uregs[] = new int[6];

    public void setState(int[] state) {
        this.state = state;
    }

    public int[] getState() {
        return state;
    }
    private int[] state = new int[6];

    // что сделать, окгда кавасаки встанет в заданную точку

    Runnable lastRunnable;
    ForceSensor sensor;

    public void setSensor(ForceSensor sensor) {
        this.sensor = sensor;
    }
    public KawasakiSocketServer(String name) {
        super(name,9);
    }

    @Override
    void sendDefaultCommand() {
        int arrS[] = sensor.getRVals();
        Integer [] arr  = {0,Constants.C_SENSOR_VALS,0,-arrS[0]/100, arrS[1]/100, -arrS[2]/100, arrS[3]/100, arrS[4]/100, arrS[5]/100};
        sendValsi(arr);
    }

    public void sendChangeGravity(){
        Integer [] arr  = {0,Constants.C_CHANGE_GRAVITY_MODE,0,0,0,0,0,0,0};
        sendValsi(arr);
    }

    @Override
    void processIncomingCommand() {
        switch (lst[1]) {
            case Constants.C_GetPositionAxis:
                System.arraycopy(lst, 3, rotations, 0, 6);
                sensor.setJ(rotations);
                break;
            case Constants.C_GetPosition:
                System.arraycopy(lst, 3, positions, 0, 6);
                break;
            case Constants.C_ERR:
                switch (lst[2]) {
                    case Constants.ERR_NOT_INRANGE:
                        System.out.println("Заданная точка находится вне досягаемости");
                        break;
                }
                break;
            case Constants.C_U_REGULATOR:
                System.arraycopy(lst, 3, uregs, 0, 6);
                break;
            case Constants.C_ERR_REGULATOR:
                System.arraycopy(lst, 3, errors, 0, 6);
                break;
            case Constants.C_IN_POS:
                if(lastRunnable!=null){
                    lastRunnable.run();
                    lastRunnable = null;
                }
                break;
            case Constants.A_DELTA_STATE:
                System.arraycopy(lst, 3, state, 0, 6);
                break;
            default:
                System.out.println(lst[1]+"пришло от кавасаки, не получилось расшифровать");
        }
    }

    public int[] getRotations() {
        return Arrays.copyOf(rotations, 6);
    }
    public int[] getPositions() {
        return Arrays.copyOf(positions, 6);
    }

    public void runInPointD(int x, int y, int z, int o, int a, int t, int speed,Runnable runnable) {
        int[] arr = {0, Constants.C_D_POINT, speed, x, y, z, o, a, t};
        addToComFifo(arr);
        lastRunnable = runnable;
    }

    public void runInPointA(int j1, int j2, int j3, int j4, int j5, int j6, int speed,Runnable runnable) {
        int[] arr = {0, Constants.C_J_POINT, speed, j1, j2, j3, j4, j5, j6};
        addToComFifo(arr);
        lastRunnable = runnable;
    }

    public void home1(Runnable runnable) {
        int[] arr = {0, Constants.C_HOME1, 0, 0, 0, 0, 0, 0, 0};
        addToComFifo(arr);
        lastRunnable = runnable;
    }

    public void home2(Runnable runnable) {
        int[] arr = {0, Constants.C_HOME2, 0, 0, 0, 0, 0, 0, 0};
        addToComFifo(arr);
        lastRunnable = runnable;
    }


}
