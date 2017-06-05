# -*- coding: utf-8 -*-
import sys
import getopt
import os

import algorithms
import image
import video

CAM_NUMBER = 0
CAPTURE_RES = (480,320)

SHOW_IMAGE = True
CONTINUES_IMAGE = True

ALGORITHM = algorithms.shipFounder
ALG_ARGS = 180

def main():
    # Разбираем аргументы командной строки
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", ["help"])
    except getopt.error, msg:
        print msg
        print "для справки используйте --help"
        sys.exit(2)
        
    # Анализируем
    videoCapture = len(args) == 0
    
    if videoCapture:
        obj = video.VideoCapture(CAM_NUMBER,CAPTURE_RES,SHOW_IMAGE)
        obj.setAlgorithm(ALGORITHM,ALG_ARGS)
        obj.run()

    else:
        for arg in args:
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
                    
                break

            if videoInput:
                obj = video.VideoPlayer(arg,SHOW_IMAGE)
                obj.setAlgorithm(ALGORITHM,ALG_ARGS)
                obj.run()
                break

    os.system("pause")
    obj.closeAll()
    return

if __name__ == "__main__":
    main()
