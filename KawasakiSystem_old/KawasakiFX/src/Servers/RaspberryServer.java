package Servers;

/**
 * Created by Алексей on 18.01.2017.
 */
public class RaspberryServer extends SocketServer {

    public int[] getData() {
        return data;
    }

    int data [] = new int[4];

    public RaspberryServer(String name) {
        super(name,4);
    }

    @Override
    void sendDefaultCommand() {

    }

    @Override
    void processIncomingCommand() {
        System.arraycopy(lst,0,data,0,4);
      /*  for (int d:lst){
            System.out.print(d+" ");
        }
        System.out.println();*/
    }
}
