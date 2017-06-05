package Servers;

import java.util.Arrays;

/**
 * Created by Алексей on 18.01.2017.
 */
public class AndroidServer extends SocketServer {

    public int[] getData() {
        return data;
    }

    KawasakiSocketServer kServer;

    public void setkServer(KawasakiSocketServer kServer) {
        this.kServer = kServer;
    }

    int data [] = new int[9];

    public AndroidServer(String name) {
        super(name,9);
    }

    @Override
    void sendDefaultCommand() {

    }

    @Override
    void processIncomingCommand() {
        kServer.addToComFifo(lst);
        System.out.println(Arrays.toString(lst));
      /*  for (int d:lst){
            System.out.print(d+" ");
        }
        System.out.println();*/
    }
}
