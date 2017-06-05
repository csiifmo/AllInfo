import cv2
import sys
import time
import numpy

class Image():
    def __init__(self,fileName,showImage):
        self.fileName = fileName

        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.showImage = showImage
        self.algorithmHandler = None
        self.algArgs = None

    def run(self):
        start = time.time()
        frame = cv2.imread(self.fileName)

        if self.algorithmHandler != None:
            frame = self.algorithmHandler(frame,self.algArgs)
            
        if self.showImage:     
            cv2.namedWindow(self.fileName, cv2.WINDOW_AUTOSIZE )       
            totalTime = time.time() - start
            self.drawNumber(frame,totalTime,2)
            print 'Time: ' + str(round(totalTime,2)) + 's'

            asp = frame.shape[0]/frame.shape[1]

            cv2.imshow(self.fileName,frame)
            self.waitForAkey()
            self.closeAll()
            
        else:
            totalTime = time.time() - start
            print 'Time: ' + str(round(totalTime,2)) + 's'

        return

    def runContinues(self):
        start = time.time()
        frameNumber = 0
        frame = cv2.imread(self.fileName)

        while True:
            if self.algorithmHandler != None:
                imProccesed = self.algorithmHandler(frame,self.algArgs)
                
            if self.showImage:     
                cv2.namedWindow(self.fileName, cv2.WINDOW_AUTOSIZE )       
                totalTime = time.time() - start
                self.drawNumber(imProccesed,totalTime,2)
                cv2.imshow(self.fileName,imProccesed)

                if cv2.waitKey(10) & 0xFF == ord('q'):
                    break

            else:
                if frameNumber == 100:
                    break
            
            frameNumber += 1
                
        totalTime = time.time() - start
        avrgFps = frameNumber/totalTime
        print 'Frames: ' + str(int(frameNumber))
        print 'Time: ' + str(round(totalTime,2)) + 's'
        print 'FPS: ' + str(int(avrgFps))

        return

    def closeAll(self):
        cv2.destroyAllWindows()

    def setAlgorithm(self,algorithm,args):
        self.algorithmHandler = algorithm
        self.algArgs = args

    def waitForAkey(self):
        while True:
            if cv2.waitKey(10) & 0xFF == ord('q'):
                return

    def drawNumber(self,frame,number,roundNum):
        string = 'Time: ' + str(round(number,roundNum)) + 's'
        scale = 0.3
        white = (255,255,255)
        black = (0,0,0)
        pts = numpy.array([[0,0],[100,0],[100,30],[0,30]])
            
        cv2.fillPoly(frame, [pts], black)
        cv2.putText(frame,string,(10,10),self.font,scale,white)
        return

##obj = Image('test.jpg',True)
##obj.runContinues()
