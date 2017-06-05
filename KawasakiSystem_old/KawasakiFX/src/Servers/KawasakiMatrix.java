package Servers;

import org.ejml.simple.SimpleMatrix;

import java.io.FileWriter;
import java.io.IOException;

public class KawasakiMatrix {
    static final double dx = -12000;
    static final double dy = 2000;
    static final double dz = -50000;



    static SimpleMatrix getCurDHM(double tetta, double d, double a, double alpha) {
        double dm[][] = {
                {Math.cos(tetta), -Math.sin(tetta) * Math.cos(alpha), Math.sin(tetta) * Math.sin(alpha), a * Math.cos(tetta)},
                {Math.sin(tetta), Math.cos(tetta) * Math.cos(alpha), -Math.cos(tetta) * Math.sin(alpha), a * Math.sin(tetta)},
                {0, Math.sin(alpha), Math.cos(alpha), d},
                {0, 0, 0, 1}
        };
        return new SimpleMatrix(dm);
    }

    static SimpleMatrix getCurDHMbyQ(int num, int q) {
        SimpleMatrix M = new SimpleMatrix();
        switch (num) {
            case 0:
                M = getCurDHM(0, 0, 0, Math.PI);
                break;
            case 1:
                M = getCurDHM(Math.toRadians(q) - Math.PI / 2, 0, 0.1, Math.PI / 2);
                break;
            case 2:
                M = getCurDHM(Math.toRadians(q) - Math.PI / 2, 0, 0.45, Math.PI);
                break;
            case 3:
                M = getCurDHM(Math.toRadians(q) + Math.PI / 2, 0, 0.04, Math.PI / 2);
                break;
            case 4:
                M = getCurDHM(Math.toRadians(q), 0.45, 0, -Math.PI / 2);
                break;
            case 5:
                M = getCurDHM(Math.toRadians(q), 0, 0, Math.PI / 2);
                break;
            case 6:
                M = getCurDHM(Math.toRadians(q) + Math.PI / 2, 0.1, 0, 0);
                break;
        }
        return M;
    }

    static SimpleMatrix getDHM(int q[]) {
        //System.out.println("Works");
        SimpleMatrix M0 = getCurDHM(0, 0, 0, Math.PI);
        SimpleMatrix M1 = getCurDHM(Math.toRadians(q[0]) - Math.PI / 2, 0, 0.1, Math.PI / 2);
        SimpleMatrix M2 = getCurDHM(Math.toRadians(q[1]) - Math.PI / 2, 0, 0.45, Math.PI);
        SimpleMatrix M3 = getCurDHM(Math.toRadians(q[2]) + Math.PI / 2, 0, 0.04, Math.PI / 2);
        SimpleMatrix M4 = getCurDHM(Math.toRadians(q[3]), 0.45, 0, -Math.PI / 2);
        SimpleMatrix M5 = getCurDHM(Math.toRadians(q[4]), 0, 0, Math.PI / 2);
        SimpleMatrix M6 = getCurDHM(Math.toRadians(q[5]) + Math.PI / 2, 0.1, 0, 0);
        return M0.mult(M1).mult(M2).mult(M3).mult(M4).mult(M5).mult(M6);

    }

    static double[] getInstrumentVector(float o, float a, float t) {
        SimpleMatrix M = getMatrix3x3ZYZm(false, o, a, t);
        double v[][] = {{0}, {0}, {1}};
        SimpleMatrix V = new SimpleMatrix(v);
        V = M.mult(V);
        double rv[] = {V.get(0, 0), V.get(1, 0), V.get(2, 0)};
        for (int i = 0; i < 3; i++)
            if (Math.abs(rv[i]) < 0.0001) rv[i] = 0;
        return rv;
    }

    static double[] parceMatrixXYZ(double[][] m) {
        double[] a = new double[3];
        //for (int i=0;i<3;i++)
        //for (int j=0;j<3;j++)
        //if (Math.abs(m[i][j])<0.01)
        //	m[i][j] = 0;


        a[1] = Math.atan2(Math.sqrt(m[0][2] * m[0][2]), m[0][2]) / Math.PI * 180;
        a[0] = Math.atan2(m[2][2], -m[1][2]) / Math.PI * 180;
        a[2] = Math.atan2(m[0][0], -m[0][1]) / Math.PI * 180;
        return a;
    }


    static int[] parceMatrixXYZm(SimpleMatrix m) {
        double thetaX, thetaY, thetaZ = 0.0;
        thetaX = Math.asin(m.get(2, 1));
        if (thetaX < (Math.PI / 2)) {
            if (thetaX > (-Math.PI / 2)) {
                thetaZ = Math.atan2(-m.get(0, 1), m.get(1, 1));
                thetaY = Math.atan2(-m.get(2, 0), m.get(2, 2));
            } else {
                thetaZ = -Math.atan2(-m.get(0, 2), m.get(0, 0));
                thetaY = 0;
            }
        } else {
            thetaZ = Math.atan2(m.get(0, 2), m.get(0, 0));
            thetaY = 0;
        }

        int a[] = {(int) (thetaX / Math.PI * 180),
                (int) (thetaY / Math.PI * 180),
                (int) (thetaZ / Math.PI * 180)
        };
        //int [] a = new int[3];
        //for (int i=0;i<3;i++)
        //for (int j=0;j<3;j++)
        //if (Math.abs(m[i][j])<0.01)
        //	m[i][j] = 0;
        //a[0] = (int)(Math.atan2(m.get(2,1),m.get(2,2))/Math.PI*180);
        //a[1] = (int)(Math.atan2(-m.get(2,0),Math.sqrt(m.get(2,1)*m.get(2,1)+m.get(2,2)*m.get(2,2)))/Math.PI*180);
        //a[2] = (int)(Math.atan2(m.get(1,0),m.get(0,0))/Math.PI*180);
        //for (int i=0;i<3;i++)
        //	if(a[i]<0) a[i]+=360;
        return a;
    }


    static double[] ZYZtoXYZ(double[] angles) {
        double[][] m = getMatrix3x3ZYZd(false, angles[0], angles[1], angles[2]);
        return parceMatrixXYZ(m);
    }

    static double[] XYZtoZYZ(double[] angles) {
        double res[] = new double[3];
        return res;
    }


    // ����� �������
    static final double mass = Math.sqrt(dx * dx + dy * dy + dz * dz);

    public static SimpleMatrix getMw() {

        // ��������� ������������
        double sM = (dx * 0 + dy * 0 + dz * mass);
        double cA = -sM / (mass * mass);
        double sA = Math.sqrt(1 - cA * cA);

        // ��������� ������������
        double tx = dz * 0 - dy * mass;
        double ty = dx * mass - dz * 0;
        double tz = dx * 0 - dy * 0;

        // ���������
        double l = Math.sqrt(tx * tx + ty * ty + tz * tz);
        double x = tx / l;
        double y = ty / l;
        double z = tz / l;
        double mat[][] = {
                {cA + (1 - cA) * x * x, (1 - cA) * x * y - sA * z, (1 - cA) * x * z + sA * y},
                {(1 - cA) * y * x + sA * z, cA + (1 - cA) * y * y, (1 - cA) * y * z - sA * x},
                {(1 - cA) * z * x - sA * y, (1 - cA) * z * y + sA * x, cA + (1 - cA) * z * z}
        };
        SimpleMatrix M = new SimpleMatrix(mat);
        return M;
    }

    public static SimpleMatrix getMatrix3x3XYZm(int[] a) {
        double s1 = Math.sin(a[0]);
        double c1 = Math.cos(a[0]);
        double s2 = Math.sin(a[1]);
        double c2 = Math.cos(a[1]);
        double s3 = Math.sin(a[2]);
        double c3 = Math.cos(a[2]);
        double[][] m = {
                {c2 * c3, -c2 * s3, s2},
                {c1 * s3 + c3 * s1 * s2, c1 * c3 - s1 * s2 * s3, -c2 * s1},
                {s1 * s3 - c1 * c3 * s2, c3 * s1 + c1 * s2 * s3, c1 * c2}
        };
        SimpleMatrix M = new SimpleMatrix(m);

        return M;
    }


    public static SimpleMatrix getBaseModification() {
        //double[][] d = {{0, -1, 0}, {1, 0, 0}, {0, 0, 1}};
        double[][] d = {{1, 0, 0}, {0, 1, 0}, {0, 0, 1}};
        return new SimpleMatrix(d);

    }

    public static SimpleMatrix getBaseModification4x4() {
        double[][] d = {{0, -1, 0, 0}, {1, 0, 0, 0}, {0, 0, 1, 0}, {0, 0, 0, 1}};
        return new SimpleMatrix(d);

    }

    public static double[][] getMatrix3x3ZYZd(boolean flgLog,
                                              double o, double a, double t) {
        return mToD(getMatrix3x3ZYZm(flgLog,
                o, a, t));
    }

    public static void calculateMw() {

    }

    public static SimpleMatrix modifyVector3m(boolean flgLog, boolean flgUseMass,
                                              double o, double a, double t,
                                              double x, double y, double z) {
        SimpleMatrix Mw = getMw();
        SimpleMatrix Mi = getMatrix3x3ZYZm(false, o, a, t);
        SimpleMatrix R = Mw.mult(Mi);
        //SimpleMatrix Rn = R.mult(getBaseModification());
        //System.out.println(getMassMatrix().toString());
        double v[][] = {{x}, {y}, {z}};
        SimpleMatrix V = new SimpleMatrix(v);
        SimpleMatrix Vn = R.mult(V);
        //������������ ���� �������
        //double massD[][]={{0},{0},{-mass}};
        //SimpleMatrix Mass = new SimpleMatrix(massD);
        //Mass = (getMatrix3x3ZYZm(false,o,a,t).invert()).mult(Mass);
        //System.out.println("LOG");
        //System.out.println(Mass);
        //System.out.println(Vn);
        //Vn = Vn.minus(Mass);
        //System.out.println(Vn);
        if (flgLog) {
            try (FileWriter writer = new FileWriter("c:\\Programming\\debug.txt", false)) {
                writer.write("     o=" + x + " a=" + y + " t=" + z + '\n');
                writer.write("new: o=" + Vn.get(0, 0) + " a=" + Vn.get(1, 0) + " t=" + Vn.get(2, 0) + '\n');
                writer.write("---------------------------------------------------------" + '\n');
                writer.write(R.toString());
                writer.write("---------------------------------------------------------" + '\n');
                writer.flush();
            } catch (IOException e) {
                // TODO Auto-generated catch block
                e.printStackTrace();
            }
        }
        return Vn;
    }

    public static SimpleMatrix getMatrix3x3ZYZm(boolean flgLog,
                                                double o, double a, double t) {
        double cO = Math.cos(Math.toRadians(o));
        double sO = Math.sin(Math.toRadians(o));
        double cA = Math.cos(Math.toRadians(a));
        double sA = Math.sin(Math.toRadians(a));
        double cT = Math.cos(Math.toRadians(t));
        double sT = Math.sin(Math.toRadians(t));

			/*if (Math.abs(sO)<0.0000001) cO = 0;
			if (Math.abs(sO)<0.0000001) sO = 0;
			if (Math.abs(cA)<0.0000001) cA = 0;
			if (Math.abs(sA)<0.0000001) sA = 0;
			if (Math.abs(cT)<0.0000001) cT = 0;
			if (Math.abs(sT)<0.0000001) sT = 0;*/


        //System.out.println("cA: "+cA+" | "+ Math.cos(Math.toRadians(a)));

        double[][] m = {
                {cO * cA * cT - sO * sT, -cO * cA * sT - sO * cT, cO * sA},
                {sO * cA * cT + cO * sT, -sO * cA * sT + cO * cT, sO * sA},
                {-sA * cT, sA * sT, cA}
        };
        SimpleMatrix M = new SimpleMatrix(m);
        if (flgLog) {
            try (FileWriter writer = new FileWriter("c:\\Programming\\debug.txt", false)) {
                double d1[][] = {
                        {cO, -sO, 0},
                        {sO, cO, 0},
                        {0, 0, 1}
                };
                SimpleMatrix R1 = new SimpleMatrix(d1);
                double d2[][] = {
                        {cA, 0, sA},
                        {0, 1, 0},
                        {-sA, 0, cA}
                };
                SimpleMatrix R2 = new SimpleMatrix(d2);
                double d3[][] = {
                        {cT, -sT, 0},
                        {sT, cT, 0},
                        {0, 0, 1}
                };
                SimpleMatrix R3 = new SimpleMatrix(d3);
                SimpleMatrix R = R1.mult(R2).mult(R3);
                writer.write("o=" + o + " a=" + a + " t=" + t + '\n');
                writer.write("---------------------------------------------------------" + '\n');
                writer.write(R1.toString() + '\n');
                writer.write(R2.toString() + '\n');
                writer.write(R3.toString() + '\n');
                writer.write("---------------------------------------------------------" + '\n');
                writer.write(R.toString() + '\n');
                writer.write("---------------------------------------------------------" + '\n');
                writer.write(M.toString() + '\n');
                writer.flush();
            } catch (IOException e) {
                // TODO Auto-generated catch block
                e.printStackTrace();
            }
        }
        return M;
    }

    public static double[][] mToD(SimpleMatrix M) {
        double[][] a = new double[3][3];
        for (int i = 0; i < 3; i++)
            for (int j = 0; j < 3; j++)
                a[i][j] = M.get(i, j);
        return a;
    }

    public static SimpleMatrix buildCurM4x4(double t, double alpha, double a, double d) {
        double arrayM[][] = {
                {Math.cos(t), -Math.cos(alpha) * Math.sin(t), Math.cos(alpha) * Math.sin(t), a * Math.cos(t)},
                {Math.sin(t), Math.cos(alpha) * Math.cos(t), -Math.sin(alpha) * Math.cos(t), a * Math.sin(t)},
                {0, Math.sin(alpha), Math.cos(alpha), d},
                {0, 0, 0, 1}
        };
        return new SimpleMatrix(arrayM);
    }

    public static double[][] getMatrix3x3(double o1, double a1, double t1) {
        double o = Math.toRadians(o1);
        double a = Math.toRadians(a1);
        double t = Math.toRadians(t1);

        double c1 = Math.cos(o);
        double s1 = Math.sin(o);
        double c2 = Math.cos(a);
        double s2 = Math.sin(a);
        double c3 = Math.cos(t);
        double s3 = Math.sin(t);

        double[][] M = {
                {c1 * c2 * c3 - s1 * s3, -c3 * s1 - c1 * c2 * s3, c1 * s2},
                {c1 * s3 + c2 * c3 * s1, c1 * c3 - c2 * s1 * s3, s1 * s2},
                {-c3 * s2, s2 * s3, c2}
        };
        return M;

    }

    public static SimpleMatrix getMatrix3x3M(double o1, double a1, double t1) {
        return new SimpleMatrix(getMatrix3x3(o1, a1, t1));

    }

    public static SimpleMatrix getMatrix4x4CJm(double r1, double r2, double r3, double r4, double r5, double r6,
                                               double d1, double d2, double d3, double d4, double d5) {
        // ������ ������
        double c1 = Math.cos(Math.toRadians(r1));
        double s1 = Math.sin(Math.toRadians(r1));
        double a1[][] = {{c1, -s1, 0, 0},
                {s1, c1, 0, 0},
                {0, 0, 1, 0},
                {0, 0, 0, 1}};
        SimpleMatrix A1 = new SimpleMatrix(a1);
        // ������ ������
        double c2 = Math.cos(Math.toRadians(r2));
        double s2 = Math.sin(Math.toRadians(r2));
        double a2[][] = {{c2, 0, -s2, 0},
                {0, 1, 0, 0},
                {-s2, 0, c2, d1},
                {0, 0, 0, 1}};
        SimpleMatrix A2 = new SimpleMatrix(a2);
        // ������ ������
        double c3 = Math.cos(Math.toRadians(r3));
        double s3 = Math.sin(Math.toRadians(r3));
        double a3[][] = {{c3, 0, s3, 0},
                {0, 1, 0, 0},
                {-s3, 0, c3, d2},
                {0, 0, 0, 1}};
        SimpleMatrix A3 = new SimpleMatrix(a3);
        // �������� ������
        double c4 = Math.cos(Math.toRadians(r4));
        double s4 = Math.sin(Math.toRadians(r4));
        double a4[][] = {{c4, -s4, 0, 0},
                {s4, c4, 0, 0},
                {0, 0, 1, d3},
                {0, 0, 0, 1}};
        SimpleMatrix A4 = new SimpleMatrix(a4);
        // ����� ������
        double c5 = Math.cos(Math.toRadians(r5));
        double s5 = Math.sin(Math.toRadians(r5));
        double a5[][] = {{c5, 0, s5, 0},
                {0, 1, 0, 0},
                {-s5, 0, c5, d4},
                {0, 0, 0, 1}};
        SimpleMatrix A5 = new SimpleMatrix(a5);
        // ������ ������
        double c6 = Math.cos(Math.toRadians(r6));
        double s6 = Math.sin(Math.toRadians(r6));
        double a6[][] = {{c6, -s6, 0, 0},
                {s6, c6, 0, 0},
                {0, 0, 1, d5},
                {0, 0, 0, 1}};
        SimpleMatrix A6 = new SimpleMatrix(a6);
        SimpleMatrix M = A1.mult(A2).mult(A3).mult(A4).mult(A5).mult(A6);
        return M;
    }

    public static double[][] getMatrix4x4Jd(boolean flgLog,
                                            double r1, double r2, double r3, double r4, double r5, double r6,
                                            double d1, double d2, double d3, double d4, double d5, double d6) {

        return mToD(getMatrix4x4Jm(flgLog,
                r1, r2, r3, r4, r5, r6,
                d1, d2, d3, d4, d5, d6));
    }

    public static SimpleMatrix getMatrix4x4Jm(boolean flgLog,
                                              double r1, double r2, double r3, double r4, double r5, double r6,
                                              double d1, double d2, double d3, double d4, double d5, double d6) {
        double[] t = {90 + r1, 0, 90, r4, 0, r6};
        double[] d = {430, 450, 450, 100, 70, 10};
        double[] alpha = {90, r2, -90 + r3, 90, -90 + r5, 0};
        double[] a = {0, 0, 0, 0, 0, 0};
        SimpleMatrix R = SimpleMatrix.identity(4);
        if (flgLog) {
            try (FileWriter writer = new FileWriter("c:\\Programming\\debug.txt", false)) {
                writer.write("I=" + R.toString());
                for (int i = 0; i < 6; i++) {
                    writer.write("---------------------------------------------------------" + '\n');
                    SimpleMatrix M = buildCurM4x4(Math.toRadians(t[i]), Math.toRadians(alpha[i]), a[i], d[i]);
                    writer.write("t=" + t[i] + " a=" + a[i] + " alpha=" + alpha[i] + " d=" + d[i] + '\n');
                    writer.write("A" + (i + 1) + "=" + M.toString() + '\n');
                    R = R.mult(M);
                }
                writer.write("R=" + R.toString() + '\n');
                writer.flush();
            } catch (IOException e) {
                // TODO Auto-generated catch block
                e.printStackTrace();
            }
        } else {
            for (int i = 0; i < 6; i++) {
                SimpleMatrix M = buildCurM4x4(Math.toRadians(t[i]), Math.toRadians(alpha[i]), a[i], d[i]);
                R = R.mult(M);
            }
        }
        return R;
    }


}
