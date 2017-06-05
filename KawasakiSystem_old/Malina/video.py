import cv2
import sys
import time
import os
import numpy

import io
import picamera


class RaspPiCapture():
    def __init__(self,resolution,showImage):
        print 'init'
        self.resolution = resolution
        
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.showImage = showImage
        self.algorithmHandler = None
        self.algArgs = None
    
        return

    def outputs(self):
        stream = io.BytesIO()
        fps = 0
        
        while True:
            start = time.time()
            
            yield stream
            stream.seek(0)

            data = numpy.fromstring(stream.getvalue(), dtype=numpy.uint8)
            frame = cv2.imdecode(data, 1)

            if self.algorithmHandler != None:
                frame = self.algorithmHandler(frame,self.algArgs)
            
            if self.showImage:
                cv2.namedWindow( "Raspberri Pi Camera Capture", cv2.WINDOW_AUTOSIZE )
                self.drawNumber(frame,fps,0)           
                cv2.imshow('Raspberri Pi Camera Capture', frame)
                
                if cv2.waitKey(10) & 0xFF == ord('q'):
                    self.closeAll()
                    break
            else:
                if self.frameNumber == 300:
                    break
            
            stream.seek(0)
            stream.truncate()

            fps = 1.0/(time.time() - start)
            self.frameNumber += 1
            
        return
        

    def run(self):
        print 'run'
        totalStart = time.time()
        self.frameNumber = 0

        with picamera.PiCamera() as camera:   
            camera.resolution = self.resolution
            camera.framerate = 90

            camera.video_stabilization = False
            camera.exposure_mode = 'off' #'spotlight'#'auto'
            #camera.shutter_speed = int(2500)
            
            time.sleep(2)
            start = time.time()
            camera.capture_sequence(
                self.outputs(),
                format='jpeg',
                use_video_port=True)
            
            totalTime = time.time() - start
            self.closeAll()

        avrgFps = self.frameNumber /totalTime
        print 'Resolution: ' + str(self.resolution)
        print 'Frames: ' + str(int(self.frameNumber))
        print 'Time: ' + str(round(totalTime,2)) + ' s'
        print 'FPS: ' + str(round(avrgFps,1))
        return

    def closeAll(self):
        cv2.destroyAllWindows()
        return

    def setAlgorithm(self,algorithm,args):
        print 'algo'
        self.algorithmHandler = algorithm
        self.algArgs = args
        return

    def drawNumber(self,frame,number,roundNum):
        string = 'Fps: ' + str(round(number,roundNum)) + 's'
        scale = 0.3
        white = (255,255,255)
        black = (0,0,0)
        pts = numpy.array([[0,0],[100,0],[100,30],[0,30]])
            
        cv2.fillPoly(frame, [pts], black)
        cv2.putText(frame,string,(10,10),self.font,scale,white)
        return

class VideoCapture():
    def __init__(self,camNumber,resolution,showImage):
        self.cap = cv2.VideoCapture(camNumber)
        self.cap.set(3,resolution[0])
        self.cap.set(4,resolution[1])
        self.cap.set(cv2.CAP_PROP_FPS,100)
        self.cap.set(cv2.CAP_PROP_CONVERT_RGB,True)

        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.showImage = showImage
        self.algorithmHandler = None
        self.algArgs = None
        return

    def run(self):
        totalStart = time.time()
        frame = 0
        fps = 0
        
        while True:            
            start = time.time()
            ret, self.frame = self.cap.read()

            if not ret:
                break

            if self.algorithmHandler != None:
                self.frame = self.algorithmHandler(self.frame,self.algArgs)
            
            if self.showImage:
                cv2.namedWindow( "Camera Capture", cv2.WINDOW_AUTOSIZE )
                self.drawNumber(self.frame,fps,0)           
                cv2.imshow('Camera Capture', self.frame)
            else:
                cv2.namedWindow( "Camera Capture", cv2.WINDOW_AUTOSIZE )

            if cv2.waitKey(10) & 0xFF == ord('q'):
                break
            
            frame += 1
            fps = 1.0/(time.time() - start)

        totalTime = time.time() - totalStart
        avrgFps = frame/totalTime
        print 'Frames: ' + str(int(frame))
        print 'Time: ' + str(round(totalTime,2)) + 's'
        print 'FPS: ' + str(int(avrgFps))
        return

    def closeAll(self):
        self.cap.release()
        cv2.destroyAllWindows()
        return

    def setAlgorithm(self,algorithm,args):
        self.algorithmHandler = algorithm
        self.algArgs = args
        return

    def drawNumber(self,frame,number,roundNum):
        string = 'Fps: ' + str(round(number,roundNum)) + 's'
        scale = 0.3
        white = (255,255,255)
        black = (0,0,0)
        pts = numpy.array([[0,0],[100,0],[100,30],[0,30]])
            
        cv2.fillPoly(frame, [pts], black)
        cv2.putText(frame,string,(10,10),self.font,scale,white)
        return


class VideoPlayer():
    def __init__(self,fileName,showImage):
        self.cap = cv2.VideoCapture(fileName)

        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.showImage = showImage
        self.algorithmHandler = None
        self.algArgs = None
        self.fileName = fileName
        return

    def run(self):
        totalStart = time.time()
        frame = 0
        fps = 0
        
        while True:            
            start = time.time()
            ret, self.frame = self.cap.read()

            if not ret:
                break

            if self.algorithmHandler != None:
                self.frame = self.algorithmHandler(self.frame,self.algArgs)
            
            if self.showImage:
                cv2.namedWindow( self.fileName, cv2.WND_PROP_FULLSCREEN )
                self.drawNumber(self.frame,fps,0)            
                cv2.imshow(self.fileName, self.frame)

            if cv2.waitKey(10) & 0xFF == ord('q'):
                break
            
            frame += 1
            fps = 1.0/(time.time() - start)

        totalTime = time.time() - totalStart
        avrgFps = frame/totalTime
        print 'Frames: ' + str(int(frame))
        print 'Time: ' + str(round(totalTime,2)) + 's'
        print 'FPS: ' + str(int(avrgFps))
        
        self.waitForAkey()
        self.closeAll()
        return

    def closeAll(self):
        self.cap.release()
        cv2.destroyAllWindows()
        return

    def setAlgorithm(self,algorithm,args):
        self.algorithmHandler = algorithm
        self.algArgs = args
        return
    
    def waitForAkey(self):
        while True:
            if cv2.waitKey(10) & 0xFF == ord('q'):
                return

    def drawNumber(self,frame,number,roundNum):
        string = 'FPS: ' + str(round(number,roundNum)) + 's'
        scale = 0.3
        white = (255,255,255)
        black = (0,0,0)
        pts = numpy.array([[0,0],[100,0],[100,30],[0,30]])
            
        cv2.fillPoly(frame, [pts], black)
        cv2.putText(frame,string,(10,10),self.font,scale,white)
        return
