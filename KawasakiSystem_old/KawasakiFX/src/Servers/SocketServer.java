package Servers;

import java.io.*;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.*;

abstract public class SocketServer {
    // имя сервера
    private String name;
    // список команд на отправку
    private LinkedList<ArrayList<Integer>> comFifo;
    // флаг того, что сокет открыт
    public boolean flgOpenSocket = false;
    // серверный сокет
    private ServerSocket serverSocket;
    // сокет подключённого клиента
    private Socket socket;
    // поток для чтения из сокета
    private DataInputStream in;
    // поток для записи в сокет
    private DataOutputStream out;
    // таймер
    private Timer time;
    // строка для хранения данных, полученных из сокета
    private String inStr = "";
    // флаг того, что предыдущий символ был пробелом
    private boolean flgSpace = false;
    // флаг того,что мы не встретили ещё ни одного пробела
    private boolean flgFirstSpace = true;
    // массив чисел команды, полученной по сокету
    int[] lst = new int[9];
    // номер текущего считываемого элемента массива
    private int pos = 0;
    // длина пакета
    private int packageSize;

    // открываем сокет
    public void openSocket(int port) {
        try {
            // создаем сокет сервера и привязываем его к вышеуказанному порту
            serverSocket = new ServerSocket(port);
            System.out.println("Waiting for a client...");
            /* эта строка закоменчена, т.к. она задаёт максимальное время, которое будет
             ждать сервер, пока не подключится клиент
             его можно использовать, но тогда надо динамически вызывать openSocket.
             его надо бы использовать, т.к. программа при клике по крестику в окне,
             не останавливается, а ждёт, пока подключится клиент, это нестрашно,
             если было уже хотя бы одно подключение */
            //serverSocket.setSoTimeout(1000);

            // заставляем сервер ждать подключений
            socket = serverSocket.accept();
            // выводим сообщение когда кто-то связался с сервером
            System.out.println("Got a client: " + socket.getInetAddress());

            // Берем входной и выходной потоки сокета, теперь можем
            // получать и отсылать данные клиенту.
            InputStream sin = socket.getInputStream();
            OutputStream sout = socket.getOutputStream();

            // Конвертируем потоки в другой тип,
            // чтоб легче обрабатывать текстовые сообщения.
            in = new DataInputStream(sin);
            out = new DataOutputStream(sout);
            // говорим, что сокет открыт
            flgOpenSocket = true;
        } catch (Exception e) {
            // если возникли ошибки, выводим соотв. сообщение
            System.out.println(name + ".openSocket: " + e);
        }
    }

    // остановка сервера
    public void close() {
        // останавливаем сокет
        closeSocket();
        // останавливаем таймер
        time.cancel();
    }

    // конструктор
    SocketServer(String name,int packageSize) {
        this.name = name;
        comFifo = new LinkedList<>();
        time = new Timer();
        this.packageSize = packageSize;
        // запускаем таймер с задержкой в 200мс и с интервалом 200мс
        time.schedule(new TimerTask() {
            @Override
            public void run() {
                // если клиент отключился
                if (socket != null && !socket.isConnected()) {
                    System.out.println("Client disconnected");
                    // закрываем сокет
                    closeSocket();
                }
                // если сокет открыт
                if (flgOpenSocket) {
                    // получаем символы от клиента
                    getChars();
                    // отправляем команды из очереди
                    sendCommands();
                }
            }
        }, 200, 200);
    }

    // отправление команд
    private void sendCommands() {
        // флаг, была ли отправлена хоть одна команда
        boolean flgCommand = false;
        while (comFifo.size() > 0) {
            ArrayList<Integer> lst = comFifo.remove();
            Integer arr[] = lst.toArray(new Integer[lst.size()]);
            sendValsi(arr);
            flgCommand = true;
        }
        // если ни одной команды не отправлено, посылаем показания сенсора
        if (!flgCommand) {
            // отправляем команду по умолчанию
            sendDefaultCommand();
        }
    }

    // отправить команду по умолчанию
    abstract void sendDefaultCommand();

    //добавить команду в очередь
    void addToComFifo(int[] arr) {
        ArrayList<Integer> ar = new ArrayList<>();
        for (int a : arr) {
            ar.add(a);
        }
        comFifo.add(ar);
    }

    // обработка входящей команды, лежащей в lst
    abstract void processIncomingCommand();

    // получить символы от сокета
    void getChars() {
        try {
            // пока есть символы для чтения
            while (in.available() != -0) {
                // читаем символ
                char c = (char) in.readByte();
                //System.out.print(c);
                // если это пробел
                if (c == ' ') {
                    // если до этого был не пробел и считан хотя бы один непробельный символ
                    if (!flgSpace && !flgFirstSpace) {
                        // переходим к следующему элементу массива команды
                        pos++;
                        // сохраняем число, лежащее в построенной строке
                        lst[pos - 1] = Integer.parseInt(inStr);
                        // обнуляем эту строку
                        inStr = "";
                        // если считали 9 элементов, можно обработать команду и считывать заново
                        if (pos >= packageSize) {
                            pos = 0;
                            processIncomingCommand();
                        }
                    }
                    flgSpace = true;
                } else {
                    inStr += c;
                    flgSpace = false;
                    flgFirstSpace = false;
                }
            }
        } catch (IOException e) {
            System.out.println(name + ".getChar: " + e);
        }
    }

    // отправляем целочисленную команду
    void sendValsi(Integer[] iVals) {
        if (flgOpenSocket) {
            String s = "";
            for (int i = 0; i < 9; i++)
                s += Constants.getVali(iVals[i], 6) + " ";
            //s+="/"
            sendPackage(s);
        }
    }

    // отправляем пакет
    void sendPackage(String s) {
        try {
            for (int i = 0; i < s.length(); i++) {
                out.writeByte((byte) s.charAt(i));
            }
        } catch (IOException e) {
            System.out.println(name + ".sendPackage" + e);
        }
    }

    // закрытие сокета
    public void closeSocket() {
        // отправляем команду остановки
        int[] arr = {0, Constants.C_STOP, 0, 0, 0, 0, 0, 0, 0};
        addToComFifo(arr);
        try {
            if (in != null) in.close();
            if (out != null) out.close();
            if (socket != null) socket.close();
            if (serverSocket != null) serverSocket.close();
        } catch (IOException e) {
            System.out.println("closeSocket: " + e);
        }
        flgOpenSocket = false;
        System.out.println("Socket closed");
    }

}
