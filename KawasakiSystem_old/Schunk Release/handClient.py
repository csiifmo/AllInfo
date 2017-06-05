#!/usr/bin/env python
# -*- coding: latin-1 -*-
## \addtogroup sdh_library_python_demo_scripts_group
#  @{
'''
    ToDO:
    1) ?????? ???? ??????????? ????? ? ????? ??? ????????, ????? TCP ?? ????????????
    ????? ??????? ??????? ?? TCP ????????? ???????.
'''

import sys
import time
import sdh
import sdh.dsa
import threading
import socket

__author__    = "Alexey Klyunin"
__version__   = "$ V1.0 $"

# ????????? ????????? ??? ??????
start_pose = [0, -60, 30, -60, 30, -60, 30]

# ?????????? ?????
def CreateOptionParser():
    parser = sdh.cSDHOptionParser( usage    =  __doc__ + "\nusage: %prog [options]",
                                   revision = __version__ )
    parser.add_option("--dsadebug",
                      dest="dsa_debug_level", default=0, type=int, metavar="LEVEL",
                      help="Print debug messages of the cDSA object of level LEVEL or lower while processing the python script. Level 0 (default): No messages,\r 1: cDSA-level messages, 2: cSDHSerial-level messages")
    parser.add_option("--dsadebuglog",
                      dest="dsa_debug_output", default=sys.stderr, type=str, metavar="LOGFILE",
                      action="callback", callback=parser.CBDebugLog,
                      help="Redirect the printed dsa debug messages to LOGFILE instead of standard error (default). If LOGFILE starts with '+' then the output will be appended to the file (without the leading '+'), else the file will be rewritten.")
    return parser
# ????? ? ?????
def GotoPose( hand, ta ):
    # ?????? ??? ?????????? ?????: ?? ?????????
    hand.SetController( hand.eControllerType["eCT_POSE"] )
    # ?????? ???????? ????????
    hand.SetAxisTargetVelocity( sdh.All, 50 )
    # ?????? ??????? ????
    hand.SetAxisTargetAngle( sdh.All, ta )
    # ?????? ?????????? ?????
    hand.MoveAxis( sdh.All )

global hand # ?????????? ????
global ts # ?????????? ???????
global t2_stop # ??????????, ?????????? ?? ????????? ????????
global sock # ?????????? ??????
# ????
forces = [[0, 0], [0, 0], [0, 0]]
# ????????? ????????? ????????? ???????
def processForces():
    global forces
    # ???? ?? ?????????? ?????
    while (not t2_stop.is_set()):
        # ???????? ??? ????????? ???????
        for fi in range(0, 3):
            for part in range(0, 2):
                (force, cog_x, cog_y, area) = ts.GetContactForce(fi, part)
                forces[fi][part] = force
        t2_stop.wait(0.5)
# ????????? ???????? ?? TCP ????????? ??????? ? ????????? ????
def writeStats():
    global forces
    try:
        # ???????? ??????? ????????? ???????
        aaa = hand.GetAxisActualAngle(sdh.All)
        s = "1 %6.3f:%6.3f:%6.3f:%6.3f:%6.3f:%6.3f:%6.3f:%6.3f:%6.3f:%6.3f:%6.3f:%6.3f:%6.3f" % (
            forces[0][0], forces[0][1], forces[1][0], forces[1][1], forces[2][0], forces[2][1],
            aaa[0], aaa[1], aaa[2], aaa[3], aaa[4], aaa[5], aaa[6])
        sock.send( s )
    except:
        print "Error sending stats"
# ?????????? TCP
def reader():
    msg = sock.recv(1024)
    #print msg
    if msg:
        try:
            arr = map(int, msg[3:].split(" "))
            if arr[0] == 1:
                print "command to pose"
                GotoPose(hand, arr[1:])
            if arr[0] == 0:
                print "command to stop"
                t2_stop.set()
            if arr[0] == 2:
                print "command to grasp"
                grasping(5)
            if arr[0]==3:
                print "command to start pose"
                GotoPose( hand, start_pose )
            if arr[0]==4:
                writeStats()
        except:
            "Can't parse message"
# ????????? ???????? ? ???????? ?????
def grasping(desired_force):
    print "begin grasping"
    # ???????? ??? ?????????? ?? ???????? ? ?????????
    hand.SetController(hand.eControllerType["eCT_VELOCITY_ACCELERATION"])
    # ????????????? ??????? ?????????
    hand.SetAxisTargetAcceleration(sdh.All, 100);
    global forces
    # ???????? ???-?? ???? ????
    nb_axes = hand.NUMBER_OF_AXES
    # ?????? ?????
    loop_time = 0.1
    # ???????????????? ???????????
    k_pow = 0.3
    # ???????????? ????????
    max_v = 7
    # ???? ????, ??? ?????? ????????
    flgGrasped = False
    # ?????????????? ?????? ?????????
    v = [0]*nb_axes
    # ???? ?????? ?? ????????
    while not flgGrasped:
        # ?.?. ? ????? ??????? ?????? ??? ??????, ? ? ?????? - ????,
        # ?? ????? ???????? ?????? ? ?????????? ?????? ?????????????
        # ? ??? ???? ??????, ? ?????? ??????? ??????? ?????? ?????????
        # ? ??? ???? ?????????
        v[1] = (desired_force - forces[0][0]) * k_pow/2
        v[2] = (desired_force - forces[0][1]) * k_pow
        v[3] = (desired_force*2 - forces[1][0]) * k_pow/2
        v[4] = (desired_force*2 - forces[1][1]) * k_pow
        v[5] = (desired_force - forces[2][0]) * k_pow/2
        v[6] = (desired_force - forces[2][1]) * k_pow
        # ??????????? ?????????
        for i in range(1,nb_axes):
            if v[i] <-5: v[i] = -5
            if v[i] > max_v: v[i] = max_v
        # ?????????, ??? ?? ??????? ??????? ???????? ????
        flgFing = True
        for i in range(3):
            if forces[i][1]<0.1:flgFing=False
        # ???? ????????
        if (flgFing) :
            print "hand stopped"
            flgGrasped = True
            # ???????? ????????
            v = [0] * nb_axes
            # ????????????? ????
            hand.Stop()
        else:
            hand.SetAxisTargetVelocity(sdh.All, v)
        time.sleep(loop_time)
    print "Grasped"
    # ?????????? ????????? ?? PC, ??? ?????? ???????
    sock.send("2 ")
# ????????????? ????
def prepareHand():
    global hand
    global ts
    global t2_stop
    # ??????????? ??????
    parser = CreateOptionParser()
    (options, args) = parser.parse_args()
    options.debug_level -= 1
    options.framerate = 30
    options.timeout = 1.0
    # ???????????? ? ??????????? ????????
    print "Connecting to joint controller...",
    hand = sdh.cSDH(options=options.__dict__)
    hand.Open()
    print "OK"
    # ????????? ???? ? ????????? ??? ?????????
    GotoPose(hand, start_pose)
    # ???????????? ? ??????????? ???????
    print "Connecting to tactile sensor controller. This may take up to 8 seconds...",
    ts = sdh.dsa.cDSA(port=options.dsaport, debug_level=options.dsa_debug_level, debug_output=options.dsa_debug_output)
    print "OK"
    ts.StartUpdater(framerate=options.framerate, do_RLE=True)
    # ????????? ??????????? ???????
    t2_stop = threading.Event()
    t2 = threading.Thread(target=processForces)
    try:
        t2.start()
    except:
        print "error running async task"

def openSocket():
    global sock
    TCP_IP = '192.168.1.110'
    TCP_PORT = 2009
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((TCP_IP, TCP_PORT))
    print "Connected to PC"

def main():
    openSocket()
    try:
        prepareHand()
    except sdh.cSDHError, e:
        print "caught exception: %r" % e
    while (not t2_stop.is_set()):
        reader()
        time.sleep(0.1)
    print "done"
    ts.Close()
    hand.Close()

if __name__ == "__main__":
    #import pdb
    #pdb.runcall( main )
    main()
