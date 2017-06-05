 # -*- coding: utf-8 -*-
import sys
import getopt
import os

import algorithms
import image
import video
from Tkinter import *
from tkFileDialog   import askopenfilename
import socket

CAM_NUMBER = 0
CAPTURE_RES = (320,240)

SHOW_IMAGE = True
CONTINUES_IMAGE = True

ALGORITHM = algorithms.shipFounder
ALG_ARGS = 180
  
    
def main():
    global sock1
    print('Main func')
    root = Tk()
    root.withdraw()
   ## arg = askopenfilename()
    arg = ''
    
    videoCapture = len(arg) == 0
    
    if videoCapture:
        obj = video.RaspPiCapture(CAPTURE_RES,SHOW_IMAGE)
        obj.setAlgorithm(ALGORITHM,ALG_ARGS)
        obj.run()

    else:
        imageInput = (arg[-3:] == 'jpg' or
                      arg[-3:] == 'png' or
                      arg[-4:] == 'jpeg')
            
        videoInput = (arg[-3:] == 'avi' or
                      arg[-3:] == 'mpg')

        if imageInput:
            obj = image.Image(arg,SHOW_IMAGE)
            obj.setAlgorithm(ALGORITHM,ALG_ARGS)

            if CONTINUES_IMAGE:
                obj.runContinues()
            else:
                obj.run()

        if videoInput:
            obj = video.VideoPlayer(arg,SHOW_IMAGE)
            obj.setAlgorithm(ALGORITHM,ALG_ARGS)
            obj.run()

    os.system("pause")
    obj.closeAll()
    return

if __name__ == "__main__":
    main()
