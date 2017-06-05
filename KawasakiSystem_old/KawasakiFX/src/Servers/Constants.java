package Servers;

/**
 * Created by Алексей on 06.12.2016.
 */
public class Constants {
    final static int C_STOP = 4;// остановка
    final static int C_J = 5; //управление конкретным джоиндом
    final static int C_GetPositionAxis = 6; //получить положение оси
    final static int C_GetPosition = 7; //получить положение координаты
    final static int C_J_POINT = 8; //управление по осям
    final static int C_D_POINT = 9; //управление по окординатам
    final static int C_HOME1 = 10; //выход в домашнюю зону 1
    final static int C_HOME2 = 11;// выход в домашнюю зону 2
    final static int C_ERR = 12; // ошибка
    final static int С_DRAW = 13; //смещение
    final static int C_SET_POS = 14; //задание по почте
    final static int C_SET_DELTA_POS = 15;  // задание по смещению
    final static int C_DELTA_POS_ENABLE = 16; // разрешаем смещение на условную единицу
    final static int C_DELTA_POS_DISABLE = 17; // запрещаем смещение на условную единицу
    final static int C_SENSOR_VALS = 18; // значения с сенсора
    final static int C_START_GRAVITY_PROGRAM = 19; // программа гравитации
    final static int C_GRAVITY_PROGRAM_OFF = 20; // программа гравитации
    final static int C_U_REGULATOR = 21; // выход компонент регулятора
    final static int C_ERR_REGULATOR = 22; // ошибки: интегральная и пропорциональная
    final static int C_CHANGE_GRAVITY_MODE = 25; // изменения режима гравити контролла
    final static int ERR_INRANGE_J1 = 1; //до джоинта 1 не достать
    final static int ERR_INRANGE_J2 = 2; //до джоинта 2 не достать
    final static int ERR_INRANGE_J3 = 4; //до джоинта 3 не достать
    final static int ERR_INRANGE_J4 = 8; //до джоинта 4 не достать
    final static int ERR_INRANGE_J5 = 16; //до джоинта 5 не достать
    final static int ERR_INRANGE_J6 = 32; //до джоинта 6 не достать
    final static int ERR_NOT_INRANGE = 32786; //вне досягаемости
    final static int C_SET_PARAMS = 23; // параметры гравитации
    final static int C_IN_POS = 24; // дошёл до позиции

    final static int C_POWER_LOG = 26; // лог управления по силам
    final static int A_DELTA_STATE = 27; // смещения от андроида


    final static int X_COORD = 0;
    final static int Y_COORD = 1;
    final static int Z_COORD = 2;
    final static int O_COORD = 3;
    final static int A_COORD = 4;
    final static int T_COORD = 5;

    double d1 = 430;
    double d2 = 450;
    double d3 = 450;
    double d4 = 100;
    double d5 = 10;

    final static int[] ULIMIMT = { 160,  140,  120,  270,  145,  360};
    final static int[] LLIMIMT = {-160, -105, -155, -270, -145, -360};

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
}
