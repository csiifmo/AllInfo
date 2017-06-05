#!/usr/bin/env python
# -*- coding: latin-1 -*-
## \addtogroup sdh_library_python_demo_scripts_group
#  @{

#######################################################################
#
## \file
#  \section sdhlibrary_python_demo_gui_general General file information
#
#    \author   Dirk Osswald
#    \date     2007-01-30
#
#  \brief  
#    Simple GUI (Graphical User Interface) to control an SDH. 
#    See demo-gui.__doc__ and online help ("-h" or "--help") for available options.
#
#  \section sdhlibrary_python_demo_gui_copyright Copyright
#
#  Copyright (c) 2007 SCHUNK GmbH & Co. KG
#
#  <HR>
#  \internal
#
#    \subsection sdhlibrary_python_demo_gui_details SVN related, detailed file specific information:
#      $LastChangedBy: Osswald2 $
#      $LastChangedDate: 2014-09-30 09:44:33 +0200 (Tue, 30 Sep 2014) $
#      \par SVN file revision:
#        $Id: demo-gui.py 12281 2014-09-30 07:44:33Z Osswald2 $
#
#  \subsection sdhlibrary_python_demo_gui_changelog Changelog of this file:
#      \include demo-gui.py.log
#
#######################################################################

## 
#  @}


#######################################################################
## \anchor sdhlibrary_python_demo_gui_python_vars
#  \name   Python specific variables
#  
#  Some definitions that describe the script for python
#
#  @{

# pylint: disable-msg=W0622
## The docstring describing the purpose of the script:
__doc__ = '''
Simple GUI (Graphical User Interface) to command an SDH. 

A window based interactive application with GUI (Graphical User
Interface) is started. It allows to command the SDH interactively
with mouse and keyboard. The application uses the sdh.py python import
library to connect to the SDH and the Tkinter package (Tk for python)
to build the gui elements.
If no RS232 port or CAN options to select the communication channel are
given on the command line then an interactive window to select the 
channel is shown first before the actual program is started.

Apart from the intuitive gui elements the following keyboard shortcuts
can be used:
- <Pause/Break> : FastStop
- <CTRL-c>      : Close application after powering off the controllers
- <CTRL-C>      : Close application and keep controllers powered
- <CTRL-m>      : Move axes of hand to the values set with the sliders
- <CTRL-s>      : Stop movement of axes, but keep controllers enabled
- <CTRL-a>      : Set Sliders to the current actual angle of the corresponding
                  axis
- <CTRL-h>      : Set target position to "home" (all 0.0) Warning: collisions
                  are not checked!

- Example usage:
  - Start interactive GUI. Before the actual interface appears a
    window will appear to interactively select the interface to use.
    > demo-gui.py
    
  - Start interactive GUI using an SDH connected via Ethernet.
    The SDH has IP-Address 192.168.1.42 and is attached to TCP port 23.
    (Requires at least SDH-firmware v0.0.3.1)
    > demo-gui.py --tcp=192.168.1.42
     
  - Start interactive GUI using an SDH connected to port 2 = COM3.
    (The port for the tactile sensors can be choosen interactively)
    > demo-gui.py -p 2
        
  - Get the version info of both the joint controllers and the tactile 
    sensor firmware from an SDH connected to 
    - port 2 = COM3 (joint controllers) and 
    - port 3 = COM4 (tactile sensor controller) 
    > demo-gui.py -p 2 --dsaport=3 -v                  
'''

__author__    = "Dirk Osswald: dirk.osswald@de.schunk.com"
__url__       = "http://www.schunk.com"
__version__   = "$Id: demo-gui.py 12281 2014-09-30 07:44:33Z Osswald2 $"
__copyright__ = "Copyright (c) 2007 SCHUNK GmbH & Co. KG"

#  end of doxygen name group sdhlibrary_python_demo_gui_python_vars
#  @}
######################################################################


######################################################################
# Import the needed modules

# std modules
import sys, os, tempfile, re, time

# Import the sdh.py python import module:
import sdh, sdh.dsa, sdh.tkdsa, sdh.util

# Try to import sdh.canserial: Will only work: 
# - if using native windows python (not cygwin)
# - if using ESD CAN
# - if the ESD python wrapper is installed
try:
    import sdh.canserial
    we_have_can = True
except ImportError:
    we_have_can = False

# The GUI stuff
from Tkinter import *
import tkFileDialog
import tkMessageBox

# For saving poses to file / loading from file
import pickle


#
######################################################################


######################################################################
# global variables

hand = None
dbg  = None
options = None
root = None

persistent_settings = sdh.util.GetPersistantDict( name=".demo-gui-startsettings", cdbg = dbg )

#
######################################################################

#-----------------------------------------------------------------
## A widget for a single finger    
class cTkSDHFinger(Frame):
    #-----------------------------------------------------------------
    ## Constructor of cTkSDHFinger: create a widget to control finger with index \a iFinger
    def __init__( self, iFinger, master=None ):
        self.iFinger = iFinger
        Frame.__init__( self, master, class_="cTkSDHFinger" )

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.CreateWidgets()
        if options.port >= 0:
            self.SetToActual()

                                                                                       
    #-----------------------------------------------------------------
    ## Create GUI elements for one finger
    def CreateWidgets( self ):

        self.config( borderwidth = 2, relief=SUNKEN )

        self.l_title = Label(self, text="Finger %d" % self.iFinger )
        self.l_title.grid( row=0, sticky=NW )
        
        self.sc_axis_distal   = Scale(self, orient=VERTICAL, length=200)
        self.sc_axis_proximal = Scale(self, orient=VERTICAL, length=200)
        self.sc_axis_base     = Scale(self, orient=HORIZONTAL)

        
        if (hand.uc_angle == sdh.uc_angle_degrees):
            tickinterval = 30
            resolution   = 1
        else:
            tickinterval = 0.5
            resolution   = 0.01

        label="[%s]" % hand.uc_angle.symbol

        self.sc_axis_distal.config(   from_   = hand.GetFingerMaxAngle( self.iFinger )[2],  # FIXME: hangs on Linux!
                                      to      = hand.GetFingerMinAngle( self.iFinger )[2],
                                      tickinterval = tickinterval,
                                      resolution = resolution,
                                      label = label,
                                      command= self.master.ScaleChanged )
        self.sc_axis_proximal.config( from_ = hand.GetFingerMaxAngle( self.iFinger )[1],
                                      to    = hand.GetFingerMinAngle( self.iFinger )[1],
                                      tickinterval = tickinterval,
                                      resolution = resolution,
                                      label = label,
                                      command= self.master.ScaleChanged )
        self.sc_axis_base.config(     from_     = hand.GetFingerMinAngle( self.iFinger )[0],
                                      to        = hand.GetFingerMaxAngle( self.iFinger )[0],
                                      tickinterval = tickinterval,
                                      resolution = resolution,
                                      label = label,
                                      command= self.master.ScaleChanged )

            
        self.sc_axis_distal.grid( row=1, sticky=N+S )
        self.sc_axis_proximal.grid( row=2, sticky=N+S )
        self.sc_axis_base.grid( row=3, sticky=W+E )

       
        self.bt_move = Button(self)
        self.bt_move.config( text = "Move F%d" % self.iFinger,
                             underline = 5,
                             command =  self.MoveFinger,
                             pady = 5)
        self.bt_move.grid( row=4, pady=5 )


    #-----------------------------------------------------------------
    ## Show collision state
    def ShowCollision( self, (collision,dist) ):
        global hand
        if collision:
            self.sc_axis_distal.config( bg="red" )
            self.sc_axis_proximal.config( bg="red" )
            self.sc_axis_base.config( bg="red" )
        elif dist < 10:
            self.sc_axis_distal.config( bg="yellow" )
            self.sc_axis_proximal.config( bg="yellow" )
            self.sc_axis_base.config( bg="yellow" )
        else:
            self.sc_axis_distal.config( bg="grey87" )
            self.sc_axis_proximal.config( bg="grey87" )
            self.sc_axis_base.config( bg="grey87" )

            
    #-----------------------------------------------------------------
    ## Update GUI elements (sliders) from the actual position of the fingers axes
    def SetToActual( self ):
        global hand

        faa  = hand.GetFingerActualAngle( self.iFinger )
        self.sc_axis_base.set(     faa[ 0 ] )
        self.sc_axis_proximal.set( faa[ 1 ] )
        self.sc_axis_distal.set(   faa[ 2 ] )


    #-----------------------------------------------------------------
    ## Set target positions for finger self.iFinger
    def SetAsTarget(self):
        global hand
        
        hand.SetFingerTargetAngle( self.iFinger, [ self.sc_axis_base.get(), self.sc_axis_proximal.get(), self.sc_axis_distal.get() ] )


    #-----------------------------------------------------------------
    ## Move finger self.iFinger to the target positions set by the sliders
    def MoveFinger(self, event=None):
        global hand

        self.SetAsTarget()

        v = self.master.gr_grip.sc_velocity.get()
        velocities = [ min( v, hand.uc_angular_velocity.ToExternal( hand.f_max_velocity_a[ i ] ) )  for i in hand.all_axes ]
        hand.SetAxisTargetVelocity( sdh.All, velocities )
        
        hand.MoveFinger( self.iFinger, sequ=False )
        dbg << "Moved finger %d\n" % self.iFinger # pylint: disable-msg=W0104


#-----------------------------------------------------------------
## A widget to save restore a single pose
class cTkSDHSavePose(Frame):
    #-----------------------------------------------------------------
    ## Constructor of cTkSDHSavePose
    def __init__( self, shortcut_set="", name="", posestr="", master=None ):
        Frame.__init__( self, master, class_="cTkSDHSavePose" )

        self.shortcut_set = shortcut_set
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=5)
        self.CreateWidgets()

        self.en_name.insert( 0, name )
        if (posestr != ""):
            self.en_pose.insert( 0, posestr )
            self.bt_set.config(state = NORMAL)
            

    #-----------------------------------------------------------------
    ## Create GUI elements for one pose
    def CreateWidgets( self ):

        #self.config( borderwidth = 2, relief=SUNKEN )

        self.bt_set = Button(self)
        self.bt_set.config( text = "<-- (%s)" % self.shortcut_set,
                            underline = 5,
                            command =  self.SetPose, state=DISABLED )
        self.bt_set.grid( row=0, column=0, padx=3, pady=0 )

        self.bt_get = Button(self)
        self.bt_get.config( text = "--> (S-%s)" % self.shortcut_set,
                            underline = 9,
                            command =  self.GetPose )
        self.bt_get.grid( row=0, column=1, padx=3, pady=0 )

        self.en_name = Entry(self, width=10)
        self.en_name.grid( row=0, column=2, padx=3, pady=0, sticky=W+E )

        self.en_pose = Entry(self, validate="focus", validatecommand=self.Validate )
        self.en_pose.grid( row=0, column=3, padx=3, pady=0, sticky=W+E )

        self.iv_selected = IntVar()
        self.cb_selected = Checkbutton(self, variable=self.iv_selected)
        self.cb_selected.grid( row=0, column=4, padx=3, pady=0 )
        

        if (self.shortcut_set != ""  and len(self.shortcut_set) == 1):
            root.bind('<Control-KeyPress-%s>' % self.shortcut_set, self.SetPose )
            root.bind('<Control-Shift-KeyPress-%s>' % self.shortcut_set, self.GetPose )

        # unfocus the pose entry on mouse leave (to make <KeyPress-a> shortcuts (without 'Control-') work in rest of app)
        #self.bind('<Leave>', lambda e: self.focus_set() )

        # disable all keys but numbers, ",", ".", navigation
        self.en_pose.bind('<Key>', self.PoseInput )

        self.bt_set.bind('<Control-Button-1>', self.SetPoseMove )


    #-----------------------------------------------------------------
    ## Check if the text in the entry is a valid pose
    def Validate( self, event=None ):
        rc = True
        try:
            angles = eval( self.en_pose.get() )
            
            rc = type(angles) in (tuple,list)  and  len(angles) == hand.NUMBER_OF_AXES  and  sdh.InRange_a( angles, hand.min_angle_a, hand.max_angle_a )

        except SyntaxError:
            rc = False

        if rc:
            self.bt_set.config( state=NORMAL )
        else:
            self.bt_set.config( state=DISABLED )
            dbg << "'%s' is not a valid pose (tuple or list of %d numbers)\n" % (self.en_pose.get(), hand.NUMBER_OF_AXES) # pylint: disable-msg=W0104
        return rc

    
    #-----------------------------------------------------------------
    ## Callback for all Keyboard input in the pose entry: accept only numbers, ".", ",", .... edit keys
    def PoseInput( self, event ):
        dbg << "PoseInput char='%s' keysym='%s', keycode='%s': " % (event.char,event.keysym,event.keycode) # pylint: disable-msg=W0104
                
        if event.char in "0123456789.,()[]-+"  or  event.keysym in ("BackSpace","Delete","Left","Right","Home","End"):
            dbg << "accepted\n" # pylint: disable-msg=W0104
            self.Validate()
        else:
            dbg << "rejected\n" # pylint: disable-msg=W0104
            return "break"
    
       
    #-----------------------------------------------------------------
    ## Set finger sliders to value from the pose entry
    def SetPose(self, event=None):
        angles = eval( self.en_pose.get() )
        self.master.master.SetToSpecific( event, angles )


    #-----------------------------------------------------------------
    ## Set finger sliders to value from the pose entry and move there
    def SetPoseMove(self, event=None):
        self.SetPose(event)
        self.master.master.MoveHand( event )


    ## Get pose entry from the finger sliders
    def GetPose(self, event=None):
        angles = self.master.master.GetSliders()
        self.en_pose.delete(0,END)
        self.en_pose.insert(0, str(angles) )
        self.bt_set.config( state=NORMAL )

#-----------------------------------------------------------------
## A widget to save/restore all poses
class cTkSDHSavePoses(Frame):
    #-----------------------------------------------------------------
    ## Constructor of cTkSDHSavePoses
    def __init__( self, master=None ):
        Frame.__init__( self, master, class_="cTkSDHSavePoses" )

        self.filetypes=["demo-gui .guidat"]
        self.CreateWidgets()
        self.initialdir = ""

    #-----------------------------------------------------------------
    ## Create GUI elements for all poses + save/load buttons
    def CreateWidgets( self ):

        self.columnconfigure(0, weight=1)

        self.config( borderwidth = 2, relief=SUNKEN )

        row=0
        self.l_title = Label(self, text="Save/Restore hand poses:")
        self.l_title.grid( row=row, sticky=NW, pady=3 )
        row += 1

        self.sp_save_pose = []
        i = 0
        for (sc_set, name, pose_str) in [("0", "home", "0,0,0,0,0,0,0"),
                                         ("1", "", ""),
                                         ("2", "", ""),
                                         ("3", "", ""),
                                         ("4", "", ""),
                                         ("5", "", ""),
                                         ("6", "", ""),
                                         ("7", "", ""),
                                         ("8", "", ""),
                                         ("9", "", "") ]:
            self.sp_save_pose.append( cTkSDHSavePose( sc_set, name, pose_str, master=self ) )
            self.sp_save_pose[i].grid( row=row, sticky=W+E )
            i += 1
            row += 1

        self.bb_buttons =  cTkSDHButtonBox( self )
        self.bb_buttons.grid( row=row )
        row += 1

        self.looping = False
        self.loop_index = 0
        self.bb_buttons.AddButton( text="Save to File", command= self.SaveToFile, padx=10, pady=5 )
        self.bb_buttons.AddButton( text="Load from File", command= self.LoadFromFile, padx=10, pady=5 )
        self.bb_buttons.AddButton( text="Loop over selected", command= self.LoopOverSelected, padx=30, pady=5 )

    #-----------------------------------------------------------------
    ## Save the poses to a file. Ask for filename from user if not given. The poses are always saved in the internal unit system.
    def SaveToFile( self, filename="" ):
        if (filename == ""):
            filename = tkFileDialog.asksaveasfilename(initialdir=self.initialdir, filetypes=self.filetypes, defaultextension="guidat")
        if filename=="": return
        
        self.initialdir = os.path.dirname(filename)

        pose_struct=[]
        for i in range(0,10):
            if ( self.sp_save_pose[i].Validate() ):
                angles = eval( self.sp_save_pose[i].en_pose.get() )
                # convert to internal units
                angles_internal = map( hand.uc_angle.ToInternal, angles )
            else:
                angles_internal = ""
                
            pose_struct.append( (self.sp_save_pose[i].en_name.get(), angles_internal, self.sp_save_pose[i].iv_selected.get() ) )
                
        savefile = open(filename,'w')
        dbg << "dumping <%s>\n" % str(pose_struct) # pylint: disable-msg=W0104
        pickle.dump(pose_struct,savefile)
        savefile.close()


    #-----------------------------------------------------------------
    ## Load poses from file, ask for filename from user if not given. The poses are converted from internal to current external unit system.
    def LoadFromFile( self, filename="" ):
        if (filename == ""):
            loadfiletypes = list(self.filetypes)
            loadfiletypes.append("all .*")
            filename = tkFileDialog.askopenfilename(initialdir=self.initialdir, filetypes=loadfiletypes)
        if filename=="": return

        self.initialdir = os.path.dirname(filename)

        loadfile = open( filename )
        pose_struct = pickle.load( loadfile )
        loadfile.close()

        for i in range(0,10):
            self.sp_save_pose[i].en_name.delete(0,END)
            self.sp_save_pose[i].en_name.insert(0,pose_struct[i][0])
            self.sp_save_pose[i].en_pose.delete(0,END)
            self.sp_save_pose[i].en_pose.insert(0,pose_struct[i][1])
            self.sp_save_pose[i].iv_selected.set( pose_struct[i][2] )
            if ( self.sp_save_pose[i].Validate() ):
                angles = eval( self.sp_save_pose[i].en_pose.get() )
                # convert to external units
                angles_external = map( hand.uc_angle.ToExternal, angles )
                self.sp_save_pose[i].en_pose.delete(0,END)
                self.sp_save_pose[i].en_pose.insert(0, str(angles_external) )

            
    #-----------------------------------------------------------------
    ## Start/Stop looping over selected poses
    #  Looping status is toggled if looping is None or set to looping if True/False
    def LoopOverSelected( self, looping=None ):
        if looping is not None:
            self.looping = looping
        else:
            self.looping = not self.looping
            
        if self.looping:
            self.bb_buttons.buttons[2].config( relief=SUNKEN, bg="green" )
            self.loop_index = 0
            self.CBLooping()
        else:
            self.bb_buttons.buttons[2].config( relief=RAISED, bg="grey87" )

    #-----------------------------------------------------------------
    ## Acual looping over selected poses callback 
    def CBLooping( self ):
        dbg << "Looping\n" # pylint: disable-msg=W0104

        if not self.looping:
            return

        # find next pose to perform
        found = False
        try: 
            for i in range( self.loop_index, len(self.sp_save_pose) ) + range( 0, self.loop_index ):
                if ( self.sp_save_pose[i].iv_selected.get() and self.sp_save_pose[i].Validate() ):
                    # found selected and valid pose

                    # increment (cyclically) and save loop index for next call
                    self.loop_index = i+1
                    if ( self.loop_index >= len(self.sp_save_pose) ):
                        self.loop_index = 0
                        
                    # set as target pose:
                    angles = eval( self.sp_save_pose[i].en_pose.get() )
                    dbg << "pose %d (%s) is selected and valid, moving to %s\n" % (i,self.sp_save_pose[i].en_name.get(),str(angles)) # pylint: disable-msg=W0104
                    hand.SetAxisTargetAngle( sdh.All, angles )
                    
                    # set target velocity from slider
                    v = self.master.gr_grip.sc_velocity.get()
                    velocities = [ min( v, hand.uc_angular_velocity.ToExternal( hand.f_max_velocity_a[ i ] ) )  for i in hand.all_axes ]
                    hand.SetAxisTargetVelocity( sdh.All, velocities )
                    
                    # move there
                    t = 0 # t must be defined here in case hand.MoveHand really raises an exception
                    try:
                        t = hand.MoveHand( sdh.All, sequ=False )
                        dbg << "Loop movement will take %fs\n" % t # pylint: disable-msg=W0104
                    except sdh.cSDHError,e:
                        dbg << "Ignoring exception %s\n" % repr(e)  # pylint: disable-msg=W0104

                        
                    # arrange callback after movement is finished:
                    self.after(int(t*1000.0), self.CBLooping)

                    found = True
                    break
        finally:
            # switch off looping button in gui if no valid pose is selected or an error occured
            if not found:
                self.LoopOverSelected( False )
        
#-----------------------------------------------------------------
## A widget to access the grip skills stored in the SDH
class cTkSDHGrip(Frame):
    #-----------------------------------------------------------------
    ## Constructor of cTkSDHGrip
    def __init__( self, master=None ):
        Frame.__init__( self, master, class_="cTkSDHGrip", borderwidth = 2, relief=SUNKEN )
        self.columnconfigure(0, weight=1)
        self.CreateWidgets()
            
    #-----------------------------------------------------------------
    ## Create GUI elements 
    def CreateWidgets( self ):
        row = 0
        
        if ( sdh.CompareReleases( hand.release_firmware, "0.0.2.6" ) >= 0 ):
        
            # enable only if firmware is equal or newer than "0.0.2.6":
            Label( self, text="Select grip skill:" ).grid( row=row, sticky=NW )
            row += 1
            
            self.iv_gripno = IntVar()
            for (key,value) in hand.eGraspId.items():
                if ( value < 0  or  key == "NUMBER_OF_GRIPS" ): continue
                Radiobutton( self, text=key, variable=self.iv_gripno, value=value).grid( row=row, sticky=W )
                row += 1
    
            self.sc_close = Scale( self, orient=HORIZONTAL, from_=0, to=1, tickinterval=0.2, resolution = 0.01, label="open/close-ratio (0.0=open ... 1.0=close)" )
            self.sc_close.grid( row=row, sticky=W+E )
            row += 1
        
        self.sc_velocity = Scale( self, orient=HORIZONTAL, label="max target velocity [%s]" % hand.uc_angular_velocity.symbol )
        self.sc_velocity.grid( row=row, sticky=W+E )
        if (hand.uc_angular_velocity == sdh.uc_angular_velocity_degrees_per_second):
            tickinterval = 20
            resolution   = 1
        else:
            tickinterval = 0.6
            resolution   = 0.01
        
        self.sc_velocity.config(   from_   = 0,
                                   to      = max( hand.GetAxisMaxVelocity() ),
                                   tickinterval = tickinterval,
                                   resolution = resolution )
        self.sc_velocity.set( hand.GetGripMaxVelocity()/4 )
        row += 1

        self.bb_buttons =  cTkSDHButtonBox( self )
        self.bb_buttons.grid( row=row )
        row += 1

        if ( sdh.CompareReleases( hand.release_firmware, "0.0.2.6" ) >= 0 ):
            self.bb_buttons.AddButton( text="Perform Grip",
                                       command= self.PerformGrip,
                                       pady=1,padx=10 )

    #-----------------------------------------------------------------
    ##  Perform grip
    def PerformGrip( self ):
        hand.GripHand( self.iv_gripno.get(),
                       self.sc_close.get(),
                       self.sc_velocity.get(),
                       False )
        
        # this overwrites the motor current settings, so restore them:
        hand.SetAxisMotorCurrent( sdh.All, [0.9, # axis 0 needs much more power than default to move
                                            0.75,
                                            0.75,
                                            0.75,
                                            0.75,
                                            0.9, # axis 5 needs more power too
                                            0.75] )


#-----------------------------------------------------------------
## A simple box for buttons
class cTkSDHButtonBox(Frame):
    #-----------------------------------------------------------------
    ## Constructor of cTkSDHButtonBox
    def __init__(self, master=None):
        Frame.__init__(self, master, class_="cTkSDHButtonBox" )
        self.buttons = []
        self.nb_buttons = 0

    #-----------------------------------------------------------------
    ## Add a button to the button box, layout int auto-grid horizontally
    def AddButton( self, text="", command=None, underline=None, ipadx=None, ipady=None, padx=None, pady=None, bg=None, fg=None ):
        self.buttons.append( Button( self, text=text, command=command, underline=underline, bg=bg, fg=fg, padx=ipadx, pady=ipady ) )
        self.buttons[ self.nb_buttons ].grid( row=0, column=self.nb_buttons, padx=padx, pady=pady )
        self.nb_buttons += 1



#-----------------------------------------------------------------
## The Menu for the application
class cTkSDHMenu( Frame ):
    #-----------------------------------------------------------------
    ## Constructor of cTkSDHMenu
    def __init__( self, master=None ):
        Frame.__init__(self, master, class_="cTkSDHMenu" )

        # prepare some members for the menu
        self.iv_port = StringVar()
        self.iv_port.set( hand.options["port"] )
        self.iv_dsaport = StringVar()
        self.iv_dsaport.set( hand.options["dsaport"] )
        self.iv_uc_angle            = IntVar()
        self.iv_uc_angular_velocity = IntVar()
        self.iv_uc_temperature      = IntVar()
        self.uc_angle_list            = [ sdh.uc_angle_degrees, sdh.uc_angle_radians ]
        self.uc_angular_velocity_list = [ sdh.uc_angular_velocity_degrees_per_second, sdh.uc_angular_velocity_radians_per_second ]
        self.uc_temperature_list      = [ sdh.uc_temperature_celsius, sdh.uc_temperature_fahrenheit ]

        self.dbg_verbosity_list = [ ("demo-gui", dbg, IntVar()),
                                    ("cSDH", hand.dbg, IntVar()),
                                    ("cSDHSerial", hand.interface.dbg, IntVar()) ]
        self.iv_velocity_profile = IntVar()
        self.iv_ts = IntVar()
        
        def kv_cmp( a, b ):
            if a[1] < b[1]: return -1
            if a[1] > b[1]: return 1 
            return 0
        def first(seq):
            return seq[0]
        def second(seq):
            return seq[1]
        kv_list = hand.eVelocityProfile.items()
        kv_list.sort( cmp=kv_cmp )
        self.iv_velocity_profile_list = map( first, kv_list )
        #dbg << "hand.eVelocityProfile " << hand.eVelocityProfile << "\n" # pylint: disable-msg=W0104
        #dbg << "self.iv_velocity_profile_list " << self.iv_velocity_profile_list << "\n" # pylint: disable-msg=W0104
         
        self.iv_velocity_profile.set( hand.GetVelocityProfile() )

        self.CreateWidgets()

        # trace the menu changes for the unit system
        self.iv_port.trace(                "w", self.CBMenuPort )
        self.iv_dsaport.trace(             "w", self.CBMenuDSAPort )
        self.iv_uc_angle.trace(            "w", self.CBMenuUnitSystems )
        self.iv_uc_angular_velocity.trace( "w", self.CBMenuUnitSystems )
        self.iv_uc_temperature.trace(      "w", self.CBMenuUnitSystems )
        self.iv_velocity_profile.trace(    "w", self.CBMenuVelocityProfile )
        self.iv_ts.trace(                  "w", self.CBMenuTS )


    #-----------------------------------------------------------------
    ## Create the GUI widgets:
    def CreateWidgets( self ):
        column=0
        #---------------------
        # dsa port menu 
        self.mb_dsaports = Menubutton ( self, text="DSA-Port", relief=GROOVE )

        self.mb_dsaports.grid(row=0, column=column, sticky=W)
        column += 1
        self.mb_dsaports.menu = Menu ( self.mb_dsaports, tearoff=0 )
        self.mb_dsaports["menu"] = self.mb_dsaports.menu

        self.mb_dsaports.menu.add_radiobutton( label="No connection",
                                               variable=self.iv_dsaport,
                                               value=-1 )
        if ( hand.options["usetcp"] ):
            self.mb_dsaports.menu.add_radiobutton( label="TCP/IP:%s:%d" % (hand.options["tcp_adr"],hand.options["dsa_tcp_port"]),
                                                   variable=self.iv_dsaport,
                                                   value="%s:%d" % (hand.options["tcp_adr"],hand.options["dsa_tcp_port"]),
                                                   state=NORMAL )
            
        if ( hand.options["usetcp"] or hand.options["usecan"] ):    
            available_ports = sdh.GetAvailablePorts()
        else:                                       
            # exclude RS232 port used to communicate with the joint controller, if any                                                 
            available_ports = sdh.GetAvailablePorts( exclude=[hand.options["port"]] )                                            
        for (device_name,occupied) in available_ports:
            dbg.var("device_name occupied")
            if (occupied):
                state = DISABLED
            else:
                state = NORMAL
            
            self.mb_dsaports.menu.add_radiobutton( label="Port %s" % (device_name),
                                                   variable=self.iv_dsaport,
                                                   value=device_name,
                                                   state=state )
                




        #---------------------
        # unit system menu 
        
        self.mb_ucs = Menubutton ( self, text="Unit Systems",
                                   relief=GROOVE )
        self.mb_ucs.grid(row=0, column=column, sticky=W)
        column += 1
        self.mb_ucs.menu = Menu ( self.mb_ucs, tearoff=0 )
        self.mb_ucs["menu"] = self.mb_ucs.menu

        i = 0
        for uc in self.uc_angle_list:
            if (hand.uc_angle == uc ):
                self.iv_uc_angle.set( i )
            self.mb_ucs.menu.add_radiobutton( label="Angles: %s [%s]" % (uc.name, uc.symbol),
                                              variable=self.iv_uc_angle,
                                              value=i )
            i += 1
        self.mb_ucs.menu.add_separator()

        i = 0
        for uc in self.uc_angular_velocity_list:
            if (hand.uc_angular_velocity == uc ):
                self.iv_uc_angular_velocity.set( i )
            self.mb_ucs.menu.add_radiobutton( label="Angular Velocity: %s [%s]" % (uc.name, uc.symbol),
                                              variable=self.iv_uc_angular_velocity,
                                              value=i )
            i += 1
        self.mb_ucs.menu.add_separator()

        i = 0
        for uc in self.uc_temperature_list:
            if (hand.uc_temperature == uc ):
                self.iv_uc_temperature.set( i )
            self.mb_ucs.menu.add_radiobutton( label="Temperature: %s [%s]" % (uc.name, uc.symbol),
                                              variable=self.iv_uc_temperature,
                                              value=i )
            i += 1

        #---------------------
        # debug menu
        self.mb_dbgs = Menubutton ( self, text="Debug",
                                    relief=GROOVE )
        self.mb_dbgs.grid(row=0, column=column, sticky=W)
        column += 1
        self.mb_dbgs.menu = Menu ( self.mb_dbgs, tearoff=0 )
        self.mb_dbgs["menu"] = self.mb_dbgs.menu


        i = 0
        for (label, dbg_obj, int_var) in self.dbg_verbosity_list:

            int_var.set( int( dbg_obj.debug_flag ) )
            self.mb_dbgs.menu.add_checkbutton( label=label,
                                               variable=int_var )
            int_var.trace( mode="w", callback=self.CBMenuDebug )
            i += 1

        self.mb_dbgs.menu.add_separator()
        self.mb_dbgs.menu.add_command( label="SDH version info", command=self.CBMenuShowSDHVersionInfo )
        
        self.mb_dbgs.menu.add_separator()
        self.mb_dbgs.menu.add_command( label="PID adjust", command=self.CBMenuShowPIDAdjust )
        self.mb_dbgs.menu.add_command( label="Current adjust", command=self.CBMenuShowCurrentAdjust )
        
        
        #cTkSDHPID

        #---------------------
        # velocity profile menu 
        self.mb_vps = Menubutton ( self, text="Velocity profile",
                                   relief=GROOVE )
        self.mb_vps.grid(row=0, column=column, sticky=W)
        column += 1
        self.mb_vps.menu = Menu ( self.mb_vps, tearoff=0 )
        self.mb_vps["menu"] = self.mb_vps.menu
      
        i = 0
        for vp in self.iv_velocity_profile_list:
            self.mb_vps.menu.add_radiobutton( label=vp,
                                              variable=self.iv_velocity_profile,
                                              value=i )
            i += 1
        self.mb_vps.menu.add_separator()

        #---------------------
        # tactile sensor menu
        self.mb_ts = Menubutton ( self, text="Tactile Sensor (DSA)",
                                    relief=GROOVE )
        self.mb_ts.grid(row=0, column=column, sticky=W)
        column += 1
        self.mb_ts.menu = Menu ( self.mb_ts, tearoff=0 )
        self.mb_ts["menu"] = self.mb_ts.menu


        self.iv_ts.set( 0 ) ### !!! from cmd line option?
        self.mb_ts.menu.add_checkbutton( label="Show frame",
                                         variable=self.iv_ts )
        self.iv_ts.trace( mode="w", callback=self.CBMenuTS )

        self.mb_ts.menu.add_separator()

        self.iv_ts_styles = dict()
        for style in sdh.tkdsa.DisplayStyles():
            self.iv_ts_styles[ style ] = IntVar()
            if ( style in self.master.options.style ):
                self.iv_ts_styles[ style ].set(1)
            self.mb_ts.menu.add_checkbutton( label=style,
                                             variable=self.iv_ts_styles[ style ] )
        if ( self.iv_ts_styles[ "color" ].get() == 0 and self.iv_ts_styles[ "grey" ].get()== 0 ):
            self.iv_ts_styles[ "color" ].set(1)



        #---------------------
        # reference menu
        if ( options.with_referencing ):
            self.mb_ref = Menubutton ( self, text="Referencing",
                                       relief=GROOVE )
            self.mb_ref.grid(row=0, column=column, sticky=W)
            column += 1
            self.mb_ref.menu = Menu ( self.mb_ref, tearoff=0 )
            self.mb_ref["menu"] = self.mb_ref.menu
    
            self.ref_menue_entries = [ ("ref axis 1 (finger 1, proximal) -dir", IntVar(), self.CBMenuRef1m),
                                       ("ref axis 2 (finger 1, distal)   -dir", IntVar(), self.CBMenuRef2m),
                                       ("ref axis 3 (finger 2, proximal) -dir", IntVar(), self.CBMenuRef3m),
                                       ("ref axis 4 (finger 2, distal)   -dir", IntVar(), self.CBMenuRef4m),
                                       ("ref axis 5 (finger 3, proximal) -dir", IntVar(), self.CBMenuRef5m),
                                       ("ref axis 6 (finger 3, distal)   -dir", IntVar(), self.CBMenuRef6m),
                                       ("ref axis 1 (finger 1, proximal) +dir", IntVar(), self.CBMenuRef1p),
                                       ("ref axis 2 (finger 1, distal)   +dir", IntVar(), self.CBMenuRef2p),
                                       ("ref axis 3 (finger 2, proximal) +dir", IntVar(), self.CBMenuRef3p),
                                       ("ref axis 4 (finger 2, distal)   +dir", IntVar(), self.CBMenuRef4p),
                                       ("ref axis 5 (finger 3, proximal) +dir", IntVar(), self.CBMenuRef5p),
                                       ("ref axis 6 (finger 3, distal)   +dir", IntVar(), self.CBMenuRef6p),
                                       #("save axis 3 (finger 1, proximal)", IntVar(), self.CBMenuRef3s),
                                       #("save axis 4 (finger 1, distal)",   IntVar(), self.CBMenuRef4s),
                                       #("save axis 6 (finger 2, distal)",   IntVar(), self.CBMenuRef6s)
                                       ]
    
            for (label, iv, cb ) in self.ref_menue_entries:
                iv.set( 0 )
                self.mb_ref.menu.add_checkbutton( label=label,
                                                  variable=iv )
                iv.trace( mode="w", callback=cb)


    def CBMenuShowSDHVersionInfo( self ):
        global hand, ts
        dbg <<  "CBMenuShowSDHVersionInfo called\n" # pylint: disable-msg=W0104
        v = sdh.auxiliary.GetVersionInfo( "demo-gui.py", __version__, hand.options, hand, ts )
        dbg << "version info =\n%s" % v # pylint: disable-msg=W0104
        tkMessageBox.showinfo( "SDH version info", v )
        
    def CBMenuShowPIDAdjust(self):
        self.tl_showpidadjust = cTkSDHPID()
               
    def CBMenuShowCurrentAdjust(self):
        self.tl_showcurrentadjust = cTkSDHCurrent()
               
    def CBMenuRef( self, axis, direction ):
        if (direction == 1):
            direction_str = "+"
            fake_start_pos = -90.0
        elif (direction == 2):
            direction_str = "-"
            fake_start_pos = 90.0

        dbg << "Referencing axis %d in %cdir\n" % (axis, direction_str) # pylint: disable-msg=W0104
        hand.interface.p_offset( axis, hand.interface.pos( axis ) + hand.interface.p_offset( axis ) - fake_start_pos )
        hand.interface.ref( axis, direction )

    def CBMenuRef1p( self, a, b, c ):
        self.CBMenuRef( 1, 1 )

    def CBMenuRef1m( self, a, b, c ):
        self.CBMenuRef( 1, 2 )

    def CBMenuRef2p( self, a, b, c ):
        self.CBMenuRef( 2, 1 )

    def CBMenuRef2m( self, a, b, c ):
        self.CBMenuRef( 2, 2 )

    def CBMenuRef3p( self, a, b, c ):
        self.CBMenuRef( 3, 1 )

    def CBMenuRef3m( self, a, b, c ):
        self.CBMenuRef( 3, 2 )

    def CBMenuRef4p( self, a, b, c ):
        self.CBMenuRef( 4, 1 )

    def CBMenuRef4m( self, a, b, c ):
        self.CBMenuRef( 4, 2 )

    def CBMenuRef5p( self, a, b, c ):
        self.CBMenuRef( 5, 1 )

    def CBMenuRef5m( self, a, b, c ):
        self.CBMenuRef( 5, 2 )

    def CBMenuRef6p( self, a, b, c ):
        self.CBMenuRef( 6, 1 )

    def CBMenuRef6m( self, a, b, c ):
        self.CBMenuRef( 6, 2 )


    def CBMenuRef1s( self, a, b, c ):
        dbg << "Saving axis 1\n" # pylint: disable-msg=W0104
        hand.interface.pos_save( 1, 1 )

    def CBMenuRef2s( self, a, b, c ):
        dbg << "Saving axis 2\n" # pylint: disable-msg=W0104
        hand.interface.pos_save( 2, 1 )

    def CBMenuRef3s( self, a, b, c ):
        dbg << "Saving axis 3\n" # pylint: disable-msg=W0104
        hand.interface.pos_save( 3, 1 )

    def CBMenuRef4s( self, a, b, c ):
        dbg << "Saving axis 4\n" # pylint: disable-msg=W0104
        hand.interface.pos_save( 4, 1 )

    def CBMenuRef5s( self, a, b, c ):
        dbg << "Saving axis 5\n" # pylint: disable-msg=W0104
        hand.interface.pos_save( 5, 1 )

    def CBMenuRef6s( self, a, b, c ):
        dbg << "Saving axis 6\n" # pylint: disable-msg=W0104
        hand.interface.pos_save( 6, 1 )




        
    #-----------------------------------------------------------------
    ## Callback for menu entries in sdh port menu
    def CBMenuPort( self, a, b, c ):
        dbg << "Changing port from %r to %r\n" % (hand.options["port"], self.iv_port.get() ) # pylint: disable-msg=W0104
        hand.Close()
        hand.Open( dict( port=self.iv_port.get() ) )

        
    #-----------------------------------------------------------------
    ## Callback for menu entries in dsa port menu
    def CBMenuDSAPort( self, a, b, c ):
        dbg << "Changing port from %r to %r\n" % (hand.options["dsaport"], self.iv_dsaport.get() ) # pylint: disable-msg=W0104
        global ts, options
        if ( ts ):
            ts.Close()
        ts = sdh.dsa.cDSA( port=self.iv_dsaport.get(), debug_level=hand.options["debug_level"], debug_output=hand.options["debug_output"] )
        
        #-----------
        if ( options.showdsasettings ):
            if ( ts.controller_info.sw_version < 268 ):
                print "To be able to read the sensitivity/threshold settings you must update"
                print "the firmware of the DSACON32m (tactile sensor controller in the SDH)"
                print "to at least release R268." 
            else:
                for (i,descr) in zip( range(6), [ "finger %d %s" % (f,t) for (t,f) in zip( ["proximal", "distal"]*3, [1,1,2,2,3,3] ) ] ):
                    print "Sensor %d (%s):" % (i,descr)
                    print "         sensitivity = %f" % (ts.GetMatrixSensitivity(i).cur_sens)
                    print " factory_sensitivity = %f" % (ts.GetMatrixSensitivity(i).fact_sens)
                    print "           threshold = %d" % (ts.GetMatrixThreshold(i).threshold)
        #-----------
    
        #-----------
        # Set sensitivities if requested
        if ( options.all_sensitivities ):
            ts.SetMatrixSensitivity( 0, 
                                     options.all_sensitivities, 
                                     do_all_matrices=True, 
                                     do_reset=options.reset, 
                                     do_persistent=options.persistent )
        else:
            for mi in range(6):
                if ( getattr( options, "sensitivity%d" % mi ) ):
                    ts.SetMatrixSensitivity( mi, 
                                             getattr( options, "sensitivity%d" % mi ), 
                                             do_all_matrices=False, 
                                             do_reset=options.reset, 
                                             do_persistent=options.persistent )
    
        #-----------
        # Set thresholds if requested
        if ( options.all_thresholds ):
            ts.SetMatrixThreshold( 0, 
                                   options.all_thresholds, 
                                   do_all_matrices=True, 
                                   do_reset=options.reset, 
                                   do_persistent=options.persistent )
        else:
            for mi in range(6):
                if ( getattr( options, "threshold%d" % mi ) ):
                    ts.SetMatrixThreshold( mi, 
                                           getattr( options, "threshold%d" % mi ), 
                                           do_all_matrices=False, 
                                           do_reset=options.reset, 
                                           do_persistent=options.persistent )
        #-----------
    


        
    #-----------------------------------------------------------------
    ## Callback for menu entries in debug menu
    def CBMenuDebug( self, a, b, c ):
        debug_level=0
        for (label, dbg_obj, int_var) in self.dbg_verbosity_list:
            i = int_var.get()
            dbg_obj.SetFlag( i )
            if ( i ):
                debug_level = i
        # reflect debug_level in hand.options too (need e.g. to get debug info from GetVersionInfo())
        hand.options["debug_level"] = debug_level 

        
    #-----------------------------------------------------------------
    ## Callback for menu entries in unit systems menu
    def CBMenuUnitSystems( self, a, b, c ):
        uc_new = self.uc_angle_list[ self.iv_uc_angle.get() ]
        if ( hand.uc_angle != uc_new ):
            # different unit system chosen -> change it
            dbg << "Changing unit system for %s from %s to %s\n" % (hand.uc_angle.kind, hand.uc_angle.name, uc_new.name) # pylint: disable-msg=W0104

            # save poses first
            (tmp_handle, tmp_name) = tempfile.mkstemp()
            self.master.sps_save_poses.SaveToFile( tmp_name )

            # change the unit system
            hand.uc_angle = uc_new
            
            # recreate widgets to reflect changes
            self.master.CreateWidgets()

            # reload poses
            self.master.sps_save_poses.LoadFromFile( tmp_name )
            # remove temporary file
            os.remove( tmp_name )

        uc_new = self.uc_angular_velocity_list[ self.iv_uc_angular_velocity.get() ]
        if ( hand.uc_angular_velocity != uc_new ):
            # different unit system chosen -> change it
            dbg << "Changing unit system for %s from %s to %s\n" % (hand.uc_angular_velocity.kind, hand.uc_angular_velocity.name, uc_new.name) # pylint: disable-msg=W0104
            hand.uc_angular_velocity = uc_new
            # recreate widgets to reflect changes
            self.master.CreateWidgets()

        uc_new = self.uc_temperature_list[ self.iv_uc_temperature.get() ]
        if ( hand.uc_temperature != uc_new ):
            # different unit system chosen -> change it
            dbg << "Changing unit system for %s from %s to %s\n" % (hand.uc_temperature.kind, hand.uc_temperature.name, uc_new.name) # pylint: disable-msg=W0104
            hand.uc_temperature = uc_new
            # recreate widgets to reflect changes
            self.master.CreateWidgets()
            
    def CBMenuVelocityProfile( self, a, b, c ):
        dbg << "Changing velocity profile to %d\n" % (self.iv_velocity_profile.get()) # pylint: disable-msg=W0104
        hand.SetVelocityProfile( self.iv_velocity_profile.get() )

    #-----------------------------------------------------------------
    ## Callback for menu entries in tactile sensor menu
    def CBMenuTS( self, a, b, c ):
        if ( self.iv_ts.get() and self.master.ts_toplevel is None):
            dbg << "adding Tactile sensor display\n" # pylint: disable-msg=W0104
            style = []
            for (k,v) in self.iv_ts_styles.items():
                if ( v.get() ):
                    style.append( k )
            self.master.ShowTactileSensors( True, style )
        elif ( not self.iv_ts.get() and self.master.ts_toplevel is not None):
            dbg << "deleting Tactile sensor display\n" # pylint: disable-msg=W0104
            self.master.ShowTactileSensors( False )


# the SCHUNK logo in base64 coding (generated with uuencode)
schunk_logo = """R0lGODlhoQA6ANUAAEhhgMLK1IWWqho5YNHX3/Dy9KOwvwhKdAdYgzlUdQKT
wAZnkgSEsGd7lSpGagozXVhuigKbx+Dl6rK9yglCbAdgi3aJoJSitAhRewV2
oQOMuAo7ZAVumQR9qRpBZwGiz////wssVQAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACH5BAAAAAAALAAAAAChADoAAAb/
wJBwSCwaj8ikcslsOp/QqHRKrVqv2Kx2y+16v+CweEwum8/otHrNbrvf8Lh8
Tq/b7/YNft9+LCJ8gWd+ER8fgohiFYWGh4mPWwgKjY2Qlk4UB5oHD0KSlJSX
okYPFQyghgqTqJWjow8crLKsrqIYjLO5hrWWsbq/jryIGcDAwogVxcbHfBTK
vxliAABMDtPMRxrPsx16QgMWAhBZAAQg5yAEDUYNE+jnBRPrAe8gRQL1APTo
AUX75wEAvCuQwEg9ASHq9RsywNy7cSEQbGPFgFMFIQkIXAhn4EqDevyGZAT5
Tl+9e/n+gVg4RGXAegSLHEz4jmUIA/XWCTk1K8IC/wohHmDg2ahixEkYQkxw
IMHABHFVBhQgeQ7jVKrnTL5DWdKlv5oCYQ4gMlPhEHzvOgrZkEvDg3YBAlwY
IPGDgqSfDEXrJ+GCAQAIqVjAam+ABMJZVdojghadVoBf+YWtR2CskLI1hXzM
PKQuKwUPcA5MgABBiAPaKCkI0Y8ABHkWqjRON7bB1BCzzxEQAMCCgamPqzJO
ybklWKqVL79DaDYBZctCfLE6kBveAApEQb01sO6CBOhSZn//RiDE4XexiQy4
kEDxtPeiHXsl4nIyyOSY+Tm4Cq8gkeyqhcBfPRZ4hsoBIbw2wVJWQACTAJYN
YBYSiiEWnE2sHYdVZfnp5v+QY0YAWJR99UxwwCwIclGhBNSQGNgRFRJ2YWQA
kQiSAR+CwBxhL/4nCwM28nOiLClu0RBJDbiYRIxYzUifhujkSNKOWBUA3k6y
KCAhVQIYCEqRXAgwIAgFOJjWkogRh44ERQz4UknxTUlTlGNiGAIxFN1ElQMi
NuKNFtANECcIFozpHxEOOODeewAMGhwIh5L4JoiDLjdnjSD1GEIyoBhVwZE5
YdBTFwIwqBw6AgxagAAFDQABTo9y5digEkDggG0EkrgOqJleuhJuIFEzhDON
aIDgJxl48FuNB+CCSgek6objQUEGq5isWVVLkjUzhcCrpRMqZiURkyhgWl6p
mCb6BAV4zqLuFtW9U9AFacY6XElKpQnCBSEoSV6vE0o1oSemHdDnM4BES5Va
esp47b0gDsAkOmr5+y+4xdnYo8ETsXJRF+WQxC8REEh5jgQQPnxWPkM0cF49
EujUb7cMDUglZEPQy/IGHXTMigZhWCPA0BBcOYQDEAwtzqEJMCrs0U5fmUDS
Qzdw6DdOO2CENe9p7fTV/X4dwgI+oxIBUNjgQXbZlCSVttpsGxLBu2/bsXbZ
CqBd9x13T+RTJ3vDPZEGFQAeuOCoGEUBBgs0XgEnhwvSd7qR19K3uZXzsnYE
H2du+d+eC0OB4aGXbvrpqKeu+uqst+7667UEAQA7"""
        
class cTkSDHPID(object):
    '''Toplevel window to show and adjust the pid parameters of an SDH
    '''
    def __init__(self,master=None):
        global hand
        self.tl = Toplevel()
        self.tl.title("Axis controller PID")

        self.p = []
        self.i = []
        self.d = []
        for ai in range(hand.NUMBER_OF_AXES):
            f = Frame( self.tl )
            Label( f, text="axis%d" % ai ).pack(side=LEFT)
            for t,l in (("P:",self.p),("I:",self.i),("D:",self.d)):
                Label( f, text=t).pack(side=LEFT,padx="5")
                l.append( StringVar() )
                entry = Entry(f, textvariable=l[-1] )
                entry.bind("<Return>", self.ReturnPressed )
                entry.bind("<Control-Return>", self.ControlReturnPressed )
                entry.pack(side=LEFT)
            f.pack(side=TOP)
        Label( self.tl, text="Press 'Enter' to set all values temporarily\nPress 'CTRL+Enter' to store all values persistently").pack(side=TOP,pady="5")
        
        self.UpdateFromSDH()
 
      
    def CheckValues(self):
        for v in self.p + self.i + self.d:
            try:
                val = float( v.get() )
            except ValueError,e:
                tkMessageBox.showerror( "Invalid value",
                                        "Value %r is not a valid float!" % (v.get()) 
                                        )
                return False
        return True
                
    def ReturnPressed(self,event):
        if ( self.CheckValues() ):
            self.UpdateToSDHTemporarily()
 
        
    def ControlReturnPressed(self,event):
        if ( self.CheckValues() ):
            self.UpdateToSDHPersistently()
 
        
    def UpdateToSDHTemporarily(self):
        '''Update the SDH pid parameters from the entries in the cTkSDHPID toplevel window 
        The values are stored temporarily, i.e. remain active until changed or until power cycle or reset
        '''
        global hand
        for ai in range(hand.NUMBER_OF_AXES):
            p = float(self.p[ai].get())
            i = float(self.i[ai].get())
            d = float(self.d[ai].get())
            dbg << "Updating pid(%d,%f,%f,%f) temporarily\n" % (ai,p,i,d)
            hand.interface.pid( ai, p, i, d )
        self.UpdateFromSDH() # reread since not all values are valid
        

    def UpdateToSDHPersistently(self):
        '''Update the SDH pid parameters from the entries in the cTkSDHPID toplevel window 
        The values are stored persistently, i.e. will survive a power cycle or reset
        '''
        self.UpdateToSDHTemporarily() # update temporarily first, since this will correct invalid/inadequate values
        global hand
        for ai in range(hand.NUMBER_OF_AXES):
            p = float(self.p[ai].get())
            i = float(self.i[ai].get())
            d = float(self.d[ai].get())
            dbg << "Updating pid(%d,%f,%f,%f) persistently\n" % (ai,p,i,d)
            re_obj = re.compile( "CFG_PID\(\d\)=(.*)" )
            hand.interface.SendParse("cfg_pid(%d)=%f,%f,%f" % (ai,float(self.p[ai].get()),float(self.i[ai].get()),float(self.d[ai].get())), re_obj)
        

    def UpdateFromSDH(self):
        '''Update the entries in the cTkSDHPID toplevel window from the SDH
        '''
        global hand
        for ai in range(hand.NUMBER_OF_AXES):
            (p,i,d) = hand.interface.pid(ai)
            self.p[ai].set( p )
            self.i[ai].set( i )
            self.d[ai].set( d )
            
            
class cTkSDHCurrent(object):
    '''Toplevel window to show and adjust the motor current parameters of an SDH
    '''
    def __init__(self,master=None):
        global hand
        self.tl = Toplevel()
        self.tl.title("Axis controller motor currents")

        self.currents = []
        for ai in range(hand.NUMBER_OF_AXES):
            f = Frame( self.tl )
            Label( f, text="axis%d current" % ai ).pack(side=LEFT)
            self.currents.append( StringVar() )
            entry = Entry(f, textvariable=self.currents[-1] )
            entry.bind("<Return>", self.ReturnPressed )
            entry.pack(side=LEFT)
            f.pack(side=TOP)
        Label( self.tl, text="Press 'Enter' to set all values.").pack(side=TOP,pady="5")
        
        self.UpdateFromSDH()
 
      
    def CheckValues(self):
        for v in self.currents:
            try:
                val = float( v.get() )
            except ValueError,e:
                tkMessageBox.showerror( "Invalid value",
                                        "Value %r is not a valid float!" % (v.get()) 
                                        )
                return False
        return True
                
    def ReturnPressed(self,event):
        if ( self.CheckValues() ):
            self.UpdateToSDHTemporarily()
 
        
    def UpdateToSDHTemporarily(self):
        '''Update the SDH current parameters from the entries in the cTkSDHCurrent toplevel window 
        The values are stored temporarily, i.e. remain active until changed or until power cycle or reset
        '''
        global hand
        values = [ float(v.get())   for v in self.currents ]
        dbg << "Updating currents in SDH temporarily to %r\n" % (values)
        hand.SetAxisMotorCurrent( sdh.All, values )

        self.UpdateFromSDH() # reread since not all values are valid
        

    def UpdateFromSDH(self):
        '''Update the entries in the cTkSDHCurrent toplevel window from the SDH
        '''
        global hand
        values = hand.GetAxisMotorCurrent( sdh.All )
        for (ai,v) in enumerate( values ):
            self.currents[ai].set( str(v) )

            
#-----------------------------------------------------------------
## \brief The "Application" class of the simple SDH GUI
#
#  - creates the widgets
#  - defines Keyboard shortcuts (see docstring of file)
#  - defines callbacks to command the SDH
#  <hr>
class cTkSDHApplication(Frame):
    #-----------------------------------------------------------------
    ## Constructor of cTkSDHApplication
    def __init__(self, options=None, master=None):
        Frame.__init__(self, master, class_="cTkSDHApplication" )
        self.grid(sticky=N+S+W+E)
        self.options = options
        self.ts_toplevel = None
        self.pid_toplevel = None

        # create all subwidgets
        self.CreateWidgets()

        if (options.filename):
            self.sps_save_poses.LoadFromFile( options.filename )
            
        # seems to be required on Linux
        # (when missing then the window is sixe 1x1 when started with the port selection toplevel)
        master.geometry( "770x710" )

       
    #-----------------------------------------------------------------
    ## Create the GUI widgets: 
    def CreateWidgets(self):
        global schunk_logo
        top=self.winfo_toplevel()
        top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=2)


        #---------------------
        # menu
        self.me_menue = cTkSDHMenu( master=self )
        self.me_menue.grid( row=0,column=0, columnspan=4, sticky=W )
        
        #---------------------
        
        self.fi_finger0 = cTkSDHFinger( iFinger=0, master=self )
        self.fi_finger0.grid( row=1, column=0, rowspan=2, sticky=N+S+W+E )

        self.fi_finger1 = cTkSDHFinger( iFinger=1, master=self )
        self.fi_finger1.grid( row=1, column=1, rowspan=2, sticky=N+S+W+E )

        self.fi_finger2 = cTkSDHFinger( iFinger=2, master=self )
        self.fi_finger2.grid( row=1, column=2, rowspan=2, sticky=N+S+W+E )

        # make bases of finger 0 and 2 move together
        def _Base0ScaleChanged( v ):
            self.fi_finger2.sc_axis_base.set( v )
            self.ScaleChanged( v )
        def _Base2ScaleChanged( v ):
            self.fi_finger0.sc_axis_base.set( v )
            self.ScaleChanged( v )
        self.fi_finger0.sc_axis_base.config( command= _Base0ScaleChanged )
        self.fi_finger2.sc_axis_base.config( command= _Base2ScaleChanged )


        
        self.bb_buttons =  cTkSDHButtonBox( self )
        self.bb_buttons.grid( row = 3, column=0, columnspan=4, ipadx=5, ipady=5, sticky=W+E)

        self.bb_buttons.AddButton( text = "Set to actual",
                                   underline = 7,
                                   padx = 10, pady = 10 )
        self.keep_actual_button_no = len(self.bb_buttons.buttons)-1
        self.bb_buttons.buttons[-1].bind('<Button-1>', self.SetToActual )
        self.bb_buttons.buttons[-1].bind('<Control-Button-1>', self.SetToActualToggle )
        self.keep_actual = False
        
        self.bb_buttons.AddButton( text = "Move Hand",
                                   command=  self.MoveHand,
                                   underline = 0,
                                   padx = 10, pady = 10 )
        self.bb_buttons.AddButton( text = "Stop Hand",
                                   command=  self.Stop,
                                   underline = 0,
                                   padx = 10, pady = 10 )
        self.bb_buttons.AddButton( text = "Fast Stop", bg="red", fg="white",
                                   command=  self.FastStop,
                                   padx = 10, pady = 10, ipadx=5, ipady=10 )

        self.bb_buttons.AddButton( text = "Get temperature", 
                                   command=  self.GetTemperature,
                                   padx = 10, pady = 10 )

        self.l_temperature = Label( self.bb_buttons )
        self.l_temperature.grid( row=0, column=self.bb_buttons.nb_buttons )
        self.bb_buttons.nb_buttons += 1


        image = PhotoImage(data=schunk_logo,format="gif")

        self.l_logo = Label( self.bb_buttons, image=image )
        self.l_logo.image = image # keep a reference!
        self.l_logo.grid(row=0, column=self.bb_buttons.nb_buttons, sticky = SE)
        self.bb_buttons.nb_buttons += 1
        
        #---------------------
        

        self.sps_save_poses = cTkSDHSavePoses( master=self )
        self.sps_save_poses.grid( row=1, column=3, sticky=N+W+E )


        self.gr_grip = cTkSDHGrip( master=self )
        self.gr_grip.grid( row=2, column=3, sticky=S+W+E )

        #---------------------
        # define key shortcuts

        root.bind_all('<KeyPress-Pause>', self.FastStop )
        root.bind_all('<Control-KeyPress-c>', lambda e: self.quit() )
        root.bind_all('<Control-KeyPress-C>', self.QuitAndKeep )
        
        root.bind('<Control-KeyPress-s>', self.Stop)
        root.bind('<Control-KeyPress-m>', self.MoveHand)
        root.bind('<Control-KeyPress-a>', self.SetToActual)
        
    #-----------------------------------------------------------------
    ## One of the scales has moved
    def ScaleChanged( self, v ):
        #print "ScaleCmd called <%s>" % repr(v)
        
        f0a = [ self.fi_finger0.sc_axis_base.get(),
                self.fi_finger0.sc_axis_proximal.get(),
                self.fi_finger0.sc_axis_distal.get() ]
        f1a = [ self.fi_finger1.sc_axis_base.get(),
                self.fi_finger1.sc_axis_proximal.get(),
                self.fi_finger1.sc_axis_distal.get() ]
        f2a = [ self.fi_finger2.sc_axis_base.get(),
                self.fi_finger2.sc_axis_proximal.get(),
                self.fi_finger2.sc_axis_distal.get() ]
        global options
        (cxy, (c01,d01), (c02,d02), (c12,d12)) = hand.CheckFingerCollisions( f0a, f1a, f2a, iv_filename=options.iv_filename )

        dbg.var( "cxy c01 d01 c02 d02 c12 d12" )
        self.fi_finger0.ShowCollision( (c01 or c02, min(d01, d02)) )
        self.fi_finger1.ShowCollision( (c01 or c12, min(d01, d12)) )
        self.fi_finger2.ShowCollision( (c12 or c02, min(d12, d02)) )

        
    #-----------------------------------------------------------------
    ## Quit but keep the controllers enabled
    def QuitAndKeep( self, event ):
        hand.Close(True)
        self.quit()

    #-----------------------------------------------------------------
    ## Set all axis sliders of all fingers to the values specified in angles
    def SetToSpecific( self, event, angles ):
        self.fi_finger0.sc_axis_base.set( angles[0] )
        self.fi_finger0.sc_axis_proximal.set( angles[1] )
        self.fi_finger0.sc_axis_distal.set( angles[2] )
        self.fi_finger1.sc_axis_proximal.set( angles[3] )
        self.fi_finger1.sc_axis_distal.set( angles[4] )
        self.fi_finger2.sc_axis_base.set( angles[0] )
        self.fi_finger2.sc_axis_proximal.set( angles[5] )
        self.fi_finger2.sc_axis_distal.set( angles[6] )

    #-----------------------------------------------------------------
    ## Get all axis sliders of all fingers
    def GetSliders( self, event=None):
        return [ self.fi_finger0.sc_axis_base.get(),
                 self.fi_finger0.sc_axis_proximal.get(),
                 self.fi_finger0.sc_axis_distal.get(),
                 self.fi_finger1.sc_axis_proximal.get(),
                 self.fi_finger1.sc_axis_distal.get(),
                 self.fi_finger2.sc_axis_proximal.get(),
                 self.fi_finger2.sc_axis_distal.get() ]
                 
    #-----------------------------------------------------------------
    ## Set all axis sliders of all fingers to their current actual angle
    def SetToActual( self, event=None ):
        dbg << "SetToActual called\n" # pylint: disable-msg=W0104
        self.fi_finger0.SetToActual()
        self.fi_finger1.SetToActual()
        self.fi_finger2.SetToActual()
        self.SetToActualToggle( flag=False )
        
    #-----------------------------------------------------------------
    ## Toggle keeping SetToActual
    def SetToActualToggle( self, event=None, flag=None ):
        dbg << "SetToActualToggle called\n" # pylint: disable-msg=W0104
        if flag is None:
            self.keep_actual = not self.keep_actual
        else:
            self.keep_actual = flag

        if self.keep_actual:
            self.bb_buttons.buttons[self.keep_actual_button_no].config( relief=SUNKEN, bg="green" )
            self.SetToActualKeep()
        else:
            self.bb_buttons.buttons[self.keep_actual_button_no].config( relief=RAISED, bg="grey87" )
            

    #-----------------------------------------------------------------
    ## Call SetToActual periodically if desired
    def SetToActualKeep( self ):
        dbg << "SetToActualKeep called\n" # pylint: disable-msg=W0104
        if (self.keep_actual):
            self.fi_finger0.SetToActual()
            self.fi_finger1.SetToActual()
            self.fi_finger2.SetToActual()
            
            # arrange callback after 100ms
            self.after(100, self.SetToActualKeep)


    #-----------------------------------------------------------------
    ## Set target positons for all fingers from gui and make hand (all fingers) move there
    def MoveHand( self, event=None ):
        global hand

        self.fi_finger0.SetAsTarget()
        self.fi_finger1.SetAsTarget()
        self.fi_finger2.SetAsTarget()

        v = self.gr_grip.sc_velocity.get()
        velocities = [ min( v, hand.uc_angular_velocity.ToExternal( hand.f_max_velocity_a[ i ] ) )  for i in hand.all_axes ]
        hand.SetAxisTargetVelocity( sdh.All, velocities )

        t = hand.MoveHand( sdh.All, sequ=False )
        dbg << "Moved hand (will take %fs)\n" % t # pylint: disable-msg=W0104

    #-----------------------------------------------------------------
    ## Stop movement of fingers (keep controllers enabled)
    def Stop(self, event=None):
        hand.Stop()
        self.sps_save_poses.LoopOverSelected( False )
        dbg << "Stopped hand\n"  # pylint: disable-msg=W0104

    #-----------------------------------------------------------------
    ## Fast stop movement of fingers (disable controllers)
    def FastStop(self, event=None):
        hand.FastStop()
        self.sps_save_poses.LoopOverSelected( False )
        dbg << "FastStopped hand\n"  # pylint: disable-msg=W0104

    #-----------------------------------------------------------------
    ## GetTemperatures of axis motors, FPGA and PCB
    def GetTemperature( self, event=None ):
        temps = hand.GetTemperature( )
        text = ""
        sep = ""
        for t in temps:
            text += "%s%.*f [%s]" % (sep,hand.uc_temperature.decimal_places, t, hand.uc_temperature.symbol)
            sep = "\n"
        self.l_temperature.configure( text = text )

    #-----------------------------------------------------------------
    ## Show the tactile sensors 
    def ShowTactileSensors( self, flag, style=["color"] ):
        global ts, options
        if (flag):
            self.ts_toplevel = Toplevel()
            self.ts_toplevel.rowconfigure(0, weight=1)
            self.ts_toplevel.columnconfigure(0, weight=1)

            #self.ts_toplevel.l_optional = Label(self.ts_toplevel, text="Optional label" )
            #self.ts_toplevel.l_optional.grid( row=0, column=0, sticky=NW )
            if ( ts is None ):
                ts = sdh.dsa.cDSA( port=self.me_menue.iv_dsaport.get(), debug_level=self.options.debug_level, debug_output=self.options.debug_output )

            #-----------
            if ( options.showdsasettings ):
                if ( ts.controller_info.sw_version < 268 ):
                    print "To be able to read the sensitivity/threshold settings you must update"
                    print "the firmware of the DSACON32m (tactile sensor controller in the SDH)"
                    print "to at least release R268." 
                else:
                    for (i,descr) in zip( range(6), [ "finger %d %s" % (f,t) for (t,f) in zip( ["proximal", "distal"]*3, [1,1,2,2,3,3] ) ] ):
                        print "Sensor %d (%s):" % (i,descr)
                        print "         sensitivity = %f" % (ts.GetMatrixSensitivity(i).cur_sens)
                        print " factory_sensitivity = %f" % (ts.GetMatrixSensitivity(i).fact_sens)
                        print "           threshold = %d" % (ts.GetMatrixThreshold(i).threshold)
            #-----------
        
            #-----------
            # Set sensitivities if requested
            if ( options.all_sensitivities ):
                ts.SetMatrixSensitivity( 0, 
                                         options.all_sensitivities, 
                                         do_all_matrices=True, 
                                         do_reset=options.reset, 
                                         do_persistent=options.persistent )
            else:
                for mi in range(6):
                    if ( getattr( options, "sensitivity%d" % mi ) ):
                        ts.SetMatrixSensitivity( mi, 
                                                 getattr( options, "sensitivity%d" % mi ), 
                                                 do_all_matrices=False, 
                                                 do_reset=options.reset, 
                                                 do_persistent=options.persistent )
        
            #-----------
            # Set thresholds if requested
            if ( options.all_thresholds ):
                ts.SetMatrixThreshold( 0, 
                                       options.all_thresholds, 
                                       do_all_matrices=True, 
                                       do_reset=options.reset, 
                                       do_persistent=options.persistent )
            else:
                for mi in range(6):
                    if ( getattr( options, "threshold%d" % mi ) ):
                        ts.SetMatrixThreshold( mi, 
                                               getattr( options, "threshold%d" % mi ), 
                                               do_all_matrices=False, 
                                               do_reset=options.reset, 
                                               do_persistent=options.persistent )
            #-----------

            self.ts_toplevel.patches =  sdh.tkdsa.cTkSDHTactileSensorPatches( ts, master=self.ts_toplevel, debug_level=self.options.debug_level, debug_output=self.options.debug_output, style=style )
            self.ts_toplevel.patches.grid( row=0, column=0, sticky=N+S+W+E )
            
            self.ts_toplevel.protocol( 'WM_DELETE_WINDOW', lambda : self.ShowTactileSensors( False ) )
            self.me_menue.iv_ts.set( 1 )

            # Create a thread that reads the tactile sensor data continuously:
            # (For now the actual sending framerate of the remote DSACON32m is always as fast as possible (30 FPS).)
            ts.StartUpdater( self.options.framerate, do_RLE = TRUE )
            self.UpdateTSFrame()
        else:
            ts.Close()
            
            self.ts_toplevel.destroy()
            self.ts_toplevel = None
            self.me_menue.iv_ts.set( 0 )
            ts = None

    #-----------------------------------------------------------------
    def UpdateTSFrame( self ):
        if (self.ts_toplevel is None): return

        global ts
        dbg << "UpdateTSFrame updating %d\n" % ts.frame.timestamp # pylint: disable-msg=W0104
        try:
            # read a single frame only
            ts.SetFramerateRetries( framerate=0, do_RLE=TRUE, ignore_exceptions=True )
            ts.ReadFrame()
        except sdh.dsa.cDSAError,e:
            dbg << "ignoring " << str(e) << "\n"              # pylint: disable-msg=W0104
        #ts.SetFramerateRetries( framerate=0, do_RLE=TRUE, retries=0, ignore_exceptions=True )
        #ts.CleanCommunicationLine()
        
        self.ts_toplevel.patches.Repaint()
        # arrange callback:
        timeout_ms = sdh.ToRange( 1000/self.options.framerate, 1, 1000 )
        dbg << "UpdateTSFrame updated age of frame %d ms (next timeout %d)\n" % (ts.GetAgeOfFrame(), timeout_ms) # pylint: disable-msg=W0104
        self.after( timeout_ms, self.UpdateTSFrame)


#-----------------------------------------------------------------
## \brief A toplevel widget class, used to select the communication interface to the SDH
#
#  - creates the widgets
#  <hr>
class cTkSDHInterfaceSelectorToplevel(Toplevel):
    #-----------------------------------------------------------------
    ## Constructor of cTkSDHInterfaceSelectorToplevel
    def __init__(self, options, parser, master=None ):
        Toplevel.__init__(self, master=master, class_="cTkSDHInterfaceSelectorToplevel" )
        self.options = options
        self.parser = parser

        self.protocol("WM_DELETE_WINDOW", self.CBQuit )
        # create all subwidgets
        self.CreateWidgets()

    def CBQuit(self):
        self.quit()
        sys.exit(0)
            

    #-----------------------------------------------------------------
    def RS232Callback(self ):
        if ( self.p.get() == -1 ):
            self.options.port = -1
        else:
            self.options.port = self.available_ports[self.p.get()][0]
        self.options.usecan = False
        
    def CANCallback(self ):
        self.options.usecan = True
        
    def OKCallback(self):
        if ( self.p.get() == 2000 ):
            self.parser.CBTCP( self.parser.get_option( "--tcp" ), "--tcp", self.tcp_adr.get(), self.parser )
            persistent_settings[ "last_tcp_adr" ] = self.options.tcp_adr
            persistent_settings[ "last_tcp_port" ] = self.options.tcp_port
        self.withdraw()
        persistent_settings[ "last_port" ] = self.p.get()
        self.quit()
        
    #-----------------------------------------------------------------
    ## Create the GUI widgets: 
    def CreateWidgets(self):
        Label( self, text="Please select the communication interface to the SDH:\n(I.E. the connection to the joint controller,\nnot the tactile sensor system.)\n" ).pack(anchor=N)
        #---------------------
        self.p = IntVar(0)
        values=[]
        Radiobutton(self, text="virtual port  (no external communication)", variable=self.p, value=-1, command=self.RS232Callback).pack(side=TOP, anchor=W)
        
        #-----
        self.available_ports = sdh.GetAvailablePorts()
        i=0                                        
        for (device_name,occupied) in self.available_ports:
            if (occupied):
                state = DISABLED
                hint = "  (used by another application)"
            else:
                state = NORMAL
                hint = ""
            Radiobutton(self, state=state, text="RS232 Port %s%s" % (device_name,hint), variable=self.p, value=i, command=self.RS232Callback).pack(side=TOP, anchor=W)
            values.append(i)
            i += 1
        #-----
        global we_have_can
        if ( we_have_can ):
            Radiobutton(self, text="CAN", variable=self.p, value=1000, command=self.CANCallback).pack(side=TOP, anchor=W)
            values.append(1000)
        #-----

        #-----
        self.tcp_adr = StringVar()
        last_tcp_adr = persistent_settings.setdefault( "last_tcp_adr", self.parser.default_tcp_adr)
        last_tcp_port = persistent_settings.setdefault( "last_tcp_port", self.parser.default_tcp_port)
        self.tcp_adr.set( "%s:%s" % (last_tcp_adr, last_tcp_port) )
        tcp_frame = Frame( self )
        Radiobutton(tcp_frame, text="TCP/IP: ", variable=self.p, value=2000 ).pack(side=LEFT, anchor=W)
        values.append(2000)
        Entry( tcp_frame, textvariable=self.tcp_adr).pack(side=LEFT)
        Label( tcp_frame, text="   (ADDRESS[:PORT])" ).pack(side=LEFT)
        tcp_frame.pack(side=TOP, anchor=W)
        #-----

        #---------------------
        Frame( self, height=3, borderwidth=2, relief=GROOVE ).pack( side=TOP, fill=X, padx=5, pady=5 )
        Button( self, text="  OK  ", command=self.OKCallback).pack(side=TOP)

        last_port = persistent_settings.setdefault( "last_port", 0 )
        if ( last_port in values ):
            self.p.set( last_port )

######################################################################
def main():
    global dbg, hand, options, root, ts
    # Command line option handling:
    
    ## Create an option parser object to parse common command line options:
    parser = sdh.cSDHOptionParser( usage    =  __doc__ + "\nusage: %prog [options]",
                                   revision = __version__ )
    
    # Add a script specific option to the OptionParser:
    parser.add_option( "-f", "--file",
                       dest="filename", 
                       help="Load positions from file FILE.",
                       metavar="FILE" )
    # redefine -r / --framrate option:
    parser.remove_option( "-r" ) # will also remove --framerate
    parser.add_option( "-r", "--framerate",
                       dest="framerate", default=10, type=int,
                       help="Framerate for updating the tactile sensor display. The DSACON32m controller in the SDH will always send data at the highest possible rate (ca. 30 FPS (frames per second)). The actual reachable rate of updates depends on your system (CPU/memory)." )
    parser.add_option( "-s", "--style",
                       dest="style", default=[], type=str, action="append",
                       help="Display style. Valid styles are: %s. This option can be given multiple times. So to set grey and percent use '-s grey -s percent'." % sdh.tkdsa.DisplayStyles() )
    parser.add_option( "--ivfile",
                       dest="iv_filename", default=None,
                       help="Use FILE as iv_filename parameter to cSDH.CheckFingerCollisions().",
                       metavar="FILE" )
    parser.add_option( "--sensitivity",
                       dest="all_sensitivities", default=None, type=float, metavar="SENSITIVITY",
                       help="""Set the sensor sensitivities for all tactile sensor pads 
                            to the given value [0.0 .. 1.0] (0.0 is minimum, 1.0 
                            is maximum sensitivity).
                             
                            If --reset is given as well then SENSITIVITY is ignored and
                            the sensitivities are reset to the factory defaults.
                            To see the current setting for sensitivity use  
                            --showdsasettings.
                            
                            For setting sensitivities individually for a specific 
                            sensor X [0..5] use --sensitivityX=SENSITIVITY""" )
    for i in range(6):
        parser.add_option( "--sensitivity%d" % i,
                           dest="sensitivity%d" % i, default=None, type=float, metavar="SENSITIVITY",
                           help="Set sensor sensitivity specifically for sensor %d." % i )
    parser.add_option( "--threshold",
                       dest="all_thresholds", default=None, type=float, metavar="THRESHOLD",
                       help="""Set the sensor threshold for all tactile sensor pads 
                            to the given value [0.0 .. 1.0] (0.0 is minimum, 1.0 
                            is maximum threshold).
                            
                            If --reset is given as well then THRESHOLD is ignored
                            and the thresholds are reset to the factory defaults.
                            To see the current setting for threshold use 
                            --showdsasettings.
                            
                            For setting thresholds individually for a specific 
                            sensor X [0..5] use --thresholdX=THRESHOLD""" )
    for i in range(6):
        parser.add_option( "--threshold%d" % i,
                           dest="threshold%d" % i, default=None, type=float, metavar="THRESHOLD",
                           help="Set sensor threshold specifically for sensor %d." % i )
    parser.add_option( "--reset",
                       dest="reset", default=False, action="store_true", 
                       help="""If given, then the values given with --sensitivity(X)
                               and/or --threshold(X) are reset to their factory default.""" )
    parser.add_option( "--persistent",
                       dest="persistent", default=False, action="store_true",
                       help="""If given then all the currently set values for the
                       sensitivity or threshold are saved persistently 
                       in the configuration memory of the DSACON32m 
                       controller in the SDH.
                       
                       PLEASE NOTE: the maximum write endurance of the 
                       configuration memory is about 100.000 times!""" )
    parser.add_option( "--showdsasettings",
                       dest="showdsasettings", default=False, action="store_true", 
                       help="""If given, then current settings for sensitivity and 
                       threshold will be printed on stdout first.""" )
    

                       
    # Parse (and handle, if possible) the command line options of the script:
    (options, args) = parser.parse_args()
    
    # disable referencing for now
    options.with_referencing = False
    
    # The parsed command line options are now stored in the options
    # object. E.g. options.port is the communication port to use, either
    # the default one or the one read from the -p | --port command line
    # option
    
    ## An object to print script-level debug messages, if requested.
    dbg = sdh.dbg.tDBG( flag=options.debug_level>0, fd=options.debug_output )
    dbg << "Debug messages of script are printed like this.\n" # pylint: disable-msg=W0104
    dbg << sdh.PrettyStruct( "options", options )  # pylint: disable-msg=W0104
    
    # reduce debug level for subsystems
    options.debug_level-=1
    
    if ( options.framerate <= 0 ):
        dbg << "Overriding user set framerate %d with 1, since else no data will be read\n"   # pylint: disable-msg=W0104
        options.framerate = 1
    #
    ######################################################################

    ######################################################################
    # if no explicit communication interface was given on the command line
    # then query the user graphically
    root = None
    if ( not options.port_set_by_user  and  not options.usecan  and  not options.usetcp ):
        try:
            root = Tk()
            try:
                root.wm_iconbitmap(sdh.GetIconPath())
            except tkinter.TclError,e:
                dbg << "Ignoring tkinter.TclError %r\n" % e
                pass # ignore error
            root.withdraw()

            app = cTkSDHInterfaceSelectorToplevel( options=options, parser=parser )
            app.title("demo-gui interface selector" )
            root.mainloop()
        finally:
            try:
                root.deiconify()
            except tkinter.TclError:
                pass
        dbg << "using port %r" % options.port # pylint: disable-msg=W0104
    #
    ######################################################################
        
    
    ######################################################################
    # The actual script code 
    
    ## Create a global instance "hand" of the class cSDH according to the given options:
    hand = sdh.cSDH( options=options.__dict__ )
    dbg << "Successfully created cSDH instance\n"  # pylint: disable-msg=W0104
    
    # Open configured communication to the SDH device
    hand.Open()
    dbg << "Successfully opened communication to SDH\n" # pylint: disable-msg=W0104
    
    # set the controller type to use:
    hand.SetController( hand.eControllerType["eCT_POSE"] )
    
    ts = None
    
    # ???
    if options.port >= 0 or options.usecan:
        # axes need more power than default to move:
        hand.SetAxisMotorCurrent( sdh.All, [0.9,
                                            0.9,
                                            0.9,
                                            0.9,
                                            0.9,
                                            0.9,
                                            0.9] )
    
    # Pack the actual movement commands in a try block
    try:
        if ( not root ):
            root = Tk()
            try:
                root.wm_iconbitmap(sdh.GetIconPath())
            except tkinter.TclError,e:
                dbg << "Ignoring tkinter.TclError %r\n" % e
                pass # ignore error
        app = cTkSDHApplication( options=options, master=root )
        app.master.title("demo-gui: Demonstration of a simple SDH graphical user interface" )
        app.mainloop()

    # Close the connection to the SDH in an except/finally clause. This
    # way we can stop the hand even if an error or a user interruption
    # (KeyboardInterrupt) occurs.
    finally:
        if ( options.port < 0 ):
            pass
        else:
            hand.Close()
        dbg << "Successfully disabled controllers of SDH and closed connection\n"  # pylint: disable-msg=W0104

#
######################################################################


if __name__ == "__main__":
    #import pdb
    #pdb.runcall( main )
    main()
