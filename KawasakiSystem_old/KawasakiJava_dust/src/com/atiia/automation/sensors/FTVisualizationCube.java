/*
 * FTVisualizationCube.java
 *
 * Created on August 9, 2007, 9:47 AM
 *
 */

package com.atiia.automation.sensors;

import java.awt.event.*;
import java.awt.*;

/** The FTVisualizationCube provides a graphical display of the current
 * forces and torques acting on a sensor by plotting the force and torque as
 * lines in a 3-dimensional cube, the edges of which represent the maximum
 * ratings for each of the three axes.
 *
 * @author  Sam Skuce (ATI Industrial Automation)
 *
 * History:
 * aug.10.2007      Sam Skuce (ATI Industrial Automation)
 *  Started.
 */
public class FTVisualizationCube extends javax.swing.JPanel {
    
    private double m_dfocalLength = 2.5;
    
    /** Rotation about Y axis. */
    private double m_dPitch = 0;
    
    /** Rotation about X axis. */
    private double m_dRoll = 0;
    
    /** Rotation about Z axis. */
    private double m_dYaw = 0;
    
    private int m_iEdgeLength = 0; /* Length of cube edge. */
    
    private final double FILL_SCALE = 1.15; /* Percent of available area to fill with
     * the cube. */
    
    private double[][] m_adRotationMatrix; /* Rotation matrix for
     * current roll, pitch, and yaw. */
    
    /** Current force and torque values being displayed. */
    private double[] m_adFTValues = { 0, 0, 0, 0, 0, 0 };
    
    /** The maximum force. */
    private double m_dMaxForce = 100;
    
    /** The maximum torque. */
    private double m_dMaxTorque = 100;
    
    /** Handles mouse events. */
    private class MyMouseAdapter implements MouseListener, MouseMotionListener, MouseWheelListener{
        
        /** The point of the last drag event.  Used to calculate the
         * direction of movement during a drag to update the pitch and yaw. */
        private Point m_pLastPoint = null;
        
        /** The user can drag the mouse to change the pitch and roll. */
        public void mouseDragged(MouseEvent e) {
            if ( null != m_pLastPoint ) {
                /* Set up scaling so that dragging across the whole control
                 * causes one 360-degree turn. */
                double dRollChange = (e.getPoint().x - m_pLastPoint.x) * 360F /
                        getWidth(); /* Change in roll. */
                m_dRoll += dRollChange;
                /* It's easy for the user to get confused about which way to
                 * move the mouse if the cube is allowed to rotate without
                 * limits. */
                if ( 180 < m_dRoll ) {
                    m_dRoll = 180;
                }else if (-180 > m_dRoll) {
                    m_dRoll = -180;
                }
                double dPitchChange = (e.getPoint().y - m_pLastPoint.y) * 360F /
                        getHeight(); /* Change in pitch. */
                m_dPitch += dPitchChange;
                if ( 180 < m_dPitch ) {
                    m_dPitch = 180;
                }else if ( -180 > m_dPitch ) {
                    m_dPitch = -180;
                }
                updateRotationMatrix();
                update(getGraphics());
                
            }
            m_pLastPoint = e.getPoint();
            //System.out.println("mouseDragged Location: " + e.getPoint().toString());
            //System.out.println("New yaw = " + m_dYaw + ", new pitch = " + m_dPitch);
            
        }
        
        
        /** Initializes the start point of a drag. */
        public void mousePressed(MouseEvent e) {
            m_pLastPoint = e.getPoint();
            //System.out.println("mousePressed Location: " + e.getPoint().toString());
        }
        
        /** Mouse wheel changes yaw. */
        public void mouseWheelMoved(MouseWheelEvent e) {
            m_dYaw += e.getWheelRotation();
            /* It's easy for the user to get confused about which way to
             * move the mouse if the cube is allowed to rotate without
             * limits. */
            if ( 180 < m_dYaw ) {
                m_dYaw = 180;
            }else if ( -180 > m_dYaw ) {
                m_dYaw = -180;
            }
            updateRotationMatrix();
            update(getGraphics());
            //System.out.println("mouseWheelMoved rotation = " + e.getWheelRotation() + ", new roll = " + m_dRoll);
            
        }
        
        /** Does nothing. */
        public void mouseExited(MouseEvent e) {
        }
        
        /** Does nothing. */
        public void mouseEntered(MouseEvent e) {
        }
        
        /** Does nothing. */
        public void mouseReleased(MouseEvent e) {
        }
        
        /** Does nothing. */
        public void mouseClicked(MouseEvent e) {
        }
        
        /** Does nothing. */
        public void mouseMoved(MouseEvent e) {
        }
        
    }
    
    /** Creates new form FTVisualizationCube */
    public FTVisualizationCube() {
        updateRotationMatrix();
        initComponents();
        MyMouseAdapter mma = new MyMouseAdapter();
        addMouseMotionListener(mma);
        addMouseListener(mma);
        addMouseWheelListener(mma);
    }
    
    /** Sets the pitch.
     *  @param dPitch   The new pitch to set.
     */
    public void setPitch(double dPitch) {
        m_dPitch = dPitch;
        updateRotationMatrix();
        update(getGraphics());
    }
    
    /** Sets the yaw.
     *  @param dYaw     The new yaw to set.
     */
    public void setYaw(double dYaw) {
        m_dYaw = dYaw;
        updateRotationMatrix();
        update(getGraphics());
    }
    
    /** Sets the roll.
     *  @param dRoll    The new roll to set.
     */
    public void setRoll(double dRoll) {
        m_dRoll = dRoll;
        updateRotationMatrix();
        update(getGraphics());
    }
    
    /** Sets the maximum force.  Forces that are greater than this force will
     *  extend outside the cube borders. 
     *  @param dMaxForce    The maximum force to set.
     */
    public void setMaxForce(double dMaxForce)
    {
        m_dMaxForce = dMaxForce;
        update(getGraphics());
    }
    
    /** Sets the maximum torque.  Torques that are greater than this torque will
     *  extend outside the cube borders.
     *  @param dMaxTorque   The maixmum torque to set.
     */
    public void setMaxTorque(double dMaxTorque)
    {
        m_dMaxTorque = dMaxTorque;
        update(getGraphics());
    }
    
    /** Sets the F/T values to display.  
     *  @param  adFTValues  The force and torque values, in the order { Fx, Fy
     *      Fz, Tx, Ty, Tz }.
     */
    public void setFTValues(double[] adFTValues)
    {
        int i; /* Generic index. */
        /* Precondition: adFTValues has the new F/T values
         * Postcondition: m_adFTValues has new F/T values. */
        for( i = 0; i < 6; i++ )
        {
            m_adFTValues[i] = adFTValues[i];
        }
        update(getGraphics());
    }
    
    
    public void paint(Graphics g) {
        if ( null == g ) return;
        m_iEdgeLength = (int)(((getHeight() > getWidth()) ?  getWidth() :
            getHeight()) * FILL_SCALE);
        int iHalfEdgeLength = m_iEdgeLength / 2;
        g.clearRect(0, 0, getWidth(), getHeight());
        /* Draw axes. */
        g.setColor(Color.BLACK);
        draw3DLine(g, iHalfEdgeLength, 0, 0, -iHalfEdgeLength, 0, 0, "+X");
        draw3DLine(g, 0, iHalfEdgeLength, 0, 0, -iHalfEdgeLength, 0, "+Y");
        draw3DLine(g, 0, 0, iHalfEdgeLength, 0, 0, -iHalfEdgeLength, "+Z");
        /* Draw cube borders. */
        g.setColor(Color.BLACK);
        draw3DLine(g, iHalfEdgeLength, iHalfEdgeLength, iHalfEdgeLength, iHalfEdgeLength, -iHalfEdgeLength, iHalfEdgeLength, "");
        draw3DLine(g, iHalfEdgeLength, iHalfEdgeLength, iHalfEdgeLength, iHalfEdgeLength, iHalfEdgeLength, -iHalfEdgeLength, "" );
        draw3DLine(g, iHalfEdgeLength, iHalfEdgeLength, iHalfEdgeLength, -iHalfEdgeLength, iHalfEdgeLength, iHalfEdgeLength, "" );
        draw3DLine(g, iHalfEdgeLength, -iHalfEdgeLength, -iHalfEdgeLength, iHalfEdgeLength, -iHalfEdgeLength, iHalfEdgeLength, "" );
        draw3DLine(g, iHalfEdgeLength, -iHalfEdgeLength, -iHalfEdgeLength, iHalfEdgeLength, iHalfEdgeLength, -iHalfEdgeLength, "" );
        draw3DLine(g, iHalfEdgeLength, -iHalfEdgeLength, -iHalfEdgeLength, -iHalfEdgeLength, -iHalfEdgeLength, -iHalfEdgeLength, "");
        draw3DLine(g, -iHalfEdgeLength, iHalfEdgeLength, -iHalfEdgeLength, -iHalfEdgeLength, iHalfEdgeLength, iHalfEdgeLength, "");
        draw3DLine(g, -iHalfEdgeLength, iHalfEdgeLength, -iHalfEdgeLength, iHalfEdgeLength, iHalfEdgeLength, -iHalfEdgeLength, "");
        draw3DLine(g, -iHalfEdgeLength, iHalfEdgeLength, -iHalfEdgeLength, -iHalfEdgeLength, -iHalfEdgeLength, -iHalfEdgeLength, "");
        draw3DLine(g, -iHalfEdgeLength, -iHalfEdgeLength, iHalfEdgeLength, iHalfEdgeLength, -iHalfEdgeLength,  iHalfEdgeLength, "");
        draw3DLine(g, -iHalfEdgeLength, -iHalfEdgeLength, iHalfEdgeLength, -iHalfEdgeLength, iHalfEdgeLength, iHalfEdgeLength, "");
        draw3DLine(g, -iHalfEdgeLength, -iHalfEdgeLength, iHalfEdgeLength,  -iHalfEdgeLength, -iHalfEdgeLength, -iHalfEdgeLength, "");
        /* Draw Force. */
        g.setColor(Color.GREEN);
        draw3DLine(g, iHalfEdgeLength * m_adFTValues[0] / m_dMaxForce, iHalfEdgeLength * m_adFTValues[1] / m_dMaxForce, iHalfEdgeLength * m_adFTValues[2] / m_dMaxForce, 0, 0, 0, "F");
        /* Draw Torque. */
        g.setColor(Color.BLUE);
        draw3DLine(g, iHalfEdgeLength * m_adFTValues[3] / m_dMaxTorque, iHalfEdgeLength * m_adFTValues[4] / m_dMaxTorque, iHalfEdgeLength * m_adFTValues[5] / m_dMaxTorque, 0, 0, 0, "T");
        
    }
    
    /** Draws a line and optional label in the current color between two 3-D
     *  coordinates within the cube after rotating the coordinates according to
     *  the current roll, pitch, and yaw.  The x and y origin of the cube is
     *  located dead center of the drawing pane, and the z origin is placed
     *  1.5 edgelengths behind the screen.
     *  z coordinates of +(edgelength / 2) have a z scale divider of 1.
     *  @param g    The Graphics object to draw the line on.
     *  @param dStartX  The x position to start the line at.
     *  @param dStartY  The y position to start the line at.
     *  @param dStartZ  The z position to start the line at.
     *  @param dEndX    The x position to end the line at.
     *  @param dEndY    The y position to end the line at.
     *  @param dEndZ    The z position to end the line at.
     *  @param strLabel The text to place to the left of the starting position
     *      of the line.
     */
    public void draw3DLine(Graphics g, double dStartX, double dStartY, double dStartZ,
            double dEndX, double dEndY, double dEndZ, String strLabel) {
        /* Rotate start coordinates. */
        double[] dStartPointVector = { dStartX, dStartY, dStartZ }; /* The endpoint
         * vector. */
        rotateVector(dStartPointVector);
        /* Set front edge of cube 1 edgelength behind screen. */
        double dZDivider = ((m_dfocalLength * m_iEdgeLength) - dStartPointVector[2]) / m_iEdgeLength; /* Divide x and y coordinates by this value to create the look of scale. */
        if ( 0 >= dZDivider ) {
            dZDivider = 0.0001; /* Avoid divide-by-zero errors and prevent
             * large negative z values from reversing the x and y
             * sign values. */            
        }
        
        int i2DXStart = (int)((dStartPointVector[0] / dZDivider) + getWidth() / 2);
        /* X position to start line on screen. */
        int i2DYStart = (int)((dStartPointVector[1] / dZDivider) + getHeight() / 2);
        /* Y position to start line on screen. */
        
        /* Rotate end coordinates. */
        double[] dEndPointVector = { dEndX, dEndY, dEndZ };
        rotateVector(dEndPointVector);
        dZDivider = ((m_dfocalLength * m_iEdgeLength) - dEndPointVector[2]) / m_iEdgeLength;
        if ( 0 >= dZDivider ) {
            dZDivider = 0.0001;
        }
        int i2DXEnd = (int)((dEndPointVector[0] / dZDivider) + getWidth() / 2);
        /* X position to end line on screen. */
        int i2DYEnd = (int)((dEndPointVector[1] / dZDivider) + getHeight() / 2);
        /* Y position to end line on screen. */
        
        g.drawLine(i2DXStart, i2DYStart, i2DXEnd, i2DYEnd);
        
        if( "" != strLabel ) {
            g.drawString(strLabel, i2DXStart - 5, i2DYStart);
        }
        
    }
    
    /** Rotates a 3-D vector or coordinate using the current rotation matrix.
     *  @param ad3DVector   In - the vector to rotate.  Out - the rotated vector.
     */
    private void rotateVector(double[] ad3DVector) {
        double[] adResultVector = new double[3]; /* The rotated vector. */
        adResultVector[0] = m_adRotationMatrix[0][0] * ad3DVector[0] + m_adRotationMatrix[0][1] * ad3DVector[1] + m_adRotationMatrix[0][2] * ad3DVector[2];
        adResultVector[1] = m_adRotationMatrix[1][0] * ad3DVector[0] + m_adRotationMatrix[1][1] * ad3DVector[1] + m_adRotationMatrix[1][2] * ad3DVector[2];
        adResultVector[2] = m_adRotationMatrix[2][0] * ad3DVector[0] + m_adRotationMatrix[2][1] * ad3DVector[1] + m_adRotationMatrix[2][2] * ad3DVector[2];
        ad3DVector[0] = adResultVector[0];
        ad3DVector[1] = adResultVector[1];
        ad3DVector[2] = adResultVector[2];
    }
    
    /** Updates the rotation matrix for the current roll, pitch, and yaw. */
    private void updateRotationMatrix() {
        double cx, cy, cz, sx, sy, sz; /* sins and cosines of rotations. */
        double dRollRadians = m_dRoll * Math.PI / 180; /* Roll in radians. */
        double dPitchRadians = m_dPitch * Math.PI / 180; /* Pitch in radians. */
        double dYawRadians = m_dYaw * Math.PI / 180; /* Yaw in radians. */
        cx = Math.cos(dRollRadians);
        sx = Math.sin(dRollRadians);
        cy = Math.cos(dPitchRadians);
        sy = Math.sin(dPitchRadians);
        cz = Math.cos(dYawRadians);
        sz = Math.sin(dYawRadians);
        double[][] adNewRotationMatrix = {
            { cy*cz,    sx*sy*cz+cx*sz,     sx*sz-cx*sy*cz },
            { -cy*sz,   -sx*sy*sz+cx*cz,    sx*cz+cx*sy*sz },
            { sy,       -sx*cy,             cx*cy }
        };
        m_adRotationMatrix = adNewRotationMatrix;
    }
    
    
    
    
    
    /** This method is called from within the constructor to
     * initialize the form.
     * WARNING: Do NOT modify this code. The content of this method is
     * always regenerated by the Form Editor.
     */
    // <editor-fold defaultstate="collapsed" desc=" Generated Code ">//GEN-BEGIN:initComponents
    private void initComponents() {

        setLayout(new java.awt.BorderLayout());

    }
    // </editor-fold>//GEN-END:initComponents
    
    
    // Variables declaration - do not modify//GEN-BEGIN:variables
    // End of variables declaration//GEN-END:variables
    
}
