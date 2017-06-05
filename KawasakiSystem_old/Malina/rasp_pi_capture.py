# -*- coding: utf-8 -*-

import algorithms
import image
import video
import socket

CAPTURE_RES = (480,320)
SHOW_IMAGE = False

ALGORITHM = algorithms.shipFounder
ALG_ARGS = 140

def main():
    
    obj = video.RaspPiCapture(CAPTURE_RES,SHOW_IMAGE)
    obj.setAlgorithm(ALGORITHM,ALG_ARGS)
    obj.run()
    return

if __name__ == "__main__":
    main()
