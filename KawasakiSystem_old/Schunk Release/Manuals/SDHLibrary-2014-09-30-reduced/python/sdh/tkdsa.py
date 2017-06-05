#!/usr/bin/env python
#######################################################################
#
## \file
#  \section sdhlibrary_python_dsatk_py_general General file information
#
#    \author   Dirk Osswald
#    \date     2007-05-14
#
#  \brief  
#    Simple tkInter elements to visualize tactile sensors of SDH.
#
#  \section sdhlibrary_python_dsatk_py_copyright Copyright
#
#  Copyright (c) 2007 SCHUNK GmbH & Co. KG
#
#  <HR>
#  \internal
#
#    \subsection sdhlibrary_python_dsatk_py_details SVN related, detailed file specific information:
#      $LastChangedBy: Osswald2 $
#      $LastChangedDate: 2009-05-04 19:17:39 +0200 (Mon, 04 May 2009) $
#      \par SVN file revision:
#        $Id: tkdsa.py 4355 2009-05-04 17:17:39Z Osswald2 $
#
#  \subsection sdhlibrary_python_dsatk_py_changelog Changelog of this file:
#      \include tkdsa.py.log
#
#######################################################################


#######################################################################
## \anchor sdhlibrary_python_dsatk_py_python_vars
#  \name   Python specific variables
#  
#  Some definitions that describe the module for python.
#
#  @{

__doc__       = "Simple tkInter elements to visualize tactile sensors of SDH"
__author__    = "Dirk Osswald: dirk.osswald@de.schunk.com"
__url__       = "http://www.schunk.com"
__version__   = "$Id: tkdsa.py 4355 2009-05-04 17:17:39Z Osswald2 $"
__copyright__ = "Copyright (c) 2007 SCHUNK GmbH & Co. KG"

#  end of doxygen name group sdhlibrary_python_dsatk_py_python_vars
#  @}
######################################################################


######################################################################
# Import the needed modules

import sys

# Import the sdh.py and dsa.py python import modules:
from . import sdh
from . import dsa
from . import dbg

dbg = sdh.dbg.tDBG( False, "cyan" )
dbg << "Debug messages of tkdsa are printed like this.\n" # pylint: disable-msg=W0104

# The GUI stuff
from Tkinter import *
import tkFileDialog


#
######################################################################

#-----------------------------------------------------------------
## A class to store a tactile sensor patch
class cSDHTactileSensorPatch:
    #-----------------------------------------------------------------
    ## Constructor of cSDHTactileSensorPatch: 
    def __init__( self, fi, part, ts ):
        self.part = part
        self.fi   = fi
        self.ts   = ts
        self.m    = ts.GetMatrixIndex( fi, part )
        dbg.var( "self.m" )
        
        self.columns = ts.matrix_info[ self.m ].cells_x
        self.rows    = ts.matrix_info[ self.m ].cells_y
        self.bit_resolution=12
        self.maxvalue = (1 << self.bit_resolution)-1
            
    def GetTexel( self, x, y ):
        #dbg.var( "x y" )
        assert x >= 0  and x < self.columns
        assert y >= 0  and y < self.rows
        #dbg << "acessing texel at (%d,%d) timestamp %d\n" % (x,y,self.ts.frame.timestamp) # pylint: disable-msg=W0104
        return self.ts.GetTexel( self.m, x, y )
    
# end of class cSDHTactileSensorPatch
#######################################################################
            
## Return a list of valid display styles
def DisplayStyles():
    return [ "color", "grey", "dec", "percent" ]
        
#-----------------------------------------------------------------
## A widget to display a single tactile sensor patch
class cTkSDHTactileSensorPatch(Frame):
    #-----------------------------------------------------------------
    ## Constructor of cTkSDHTactileSensorPatch
    def __init__( self, patch, master=None, style=["color"] ):
        self.patch = patch
        Frame.__init__( self, master, class_="cTkSDHTactileSensorPatch" )

        for r in range(0,self.patch.rows):
            self.rowconfigure(r, weight=1)
        for c in range(0,self.patch.columns):
            self.columnconfigure(c, weight=1)

        self.texel_display_style = style
        self.CreateWidgets()

        
    #-----------------------------------------------------------------
    ## Create GUI elements for one tactile sensor patch
    def CreateWidgets( self ):

        self.config( borderwidth = 2, relief=SUNKEN )

        self.texel = []
        #dbg << "creating r x c = %d x %d\n" % (self.patch.rows,self.patch.columns) # pylint: disable-msg=W0104
        for r in range(0,self.patch.rows):
            texelrow=[]
            for c in range(0,self.patch.columns):
                l = Label(self, relief=RAISED)
                l.grid( row=r, column=c, sticky=N+S+W+E )
                texelrow.append( l )
            self.texel.append( texelrow )
        self.Repaint()


    #-----------------------------------------------------------------
    def Repaint( self ):
        #dbg << "r x c = %d x %d\n" % (self.patch.rows,self.patch.columns) # pylint: disable-msg=W0104
        
        for r in range(0,self.patch.rows):
            for c in range(0,self.patch.columns):
                bg = "grey"
                fg = "black"
                text = ""
                if ("color" in self.texel_display_style):
                    bg, fg = self.ToColor( r, c )
                if ("grey" in self.texel_display_style):
                    bg, fg = self.ToGrey( r, c )
                if ("dec" in self.texel_display_style):
                    text = "%04d" % self.patch.GetTexel( c, r )
                if ("percent" in self.texel_display_style):
                    text = "%03d" % int( 100 * self.patch.GetTexel( c, r ) / self.patch.maxvalue )
                self.texel[r][c].configure( bg=bg, fg=fg, text=text )

    #-----------------------------------------------------------------
    ## Return a pair of background and foreground color for texel at (\a r,\a c)
    def ToColor( self, r, c ):
        v = float(self.patch.GetTexel( c, r )) / self.patch.maxvalue
        if ( v < 0.5 ):
            bg = "#%02x%02x%02x" % (0, int(255*v/0.5), 255-int(255*v/0.5))
        else:
            bg = "#%02x%02x%02x" % (int(255*(v-0.5)/0.5), 255-int(255*(v-0.5)/0.5), 0)
        #dbg.var( "v bg fg" )
        fg = "white"
        return (bg,fg)
            
    #-----------------------------------------------------------------
    ## Return a pair of background and foreground color for texel at (\a r,\a c)
    def ToGrey( self, r, c ):
        v = self.patch.GetTexel( c, r )
        grey = 10*int( 10 * v / self.patch.maxvalue)
        bg = "grey%d" % grey
        fg = "blue"
        #dbg.var( "v bg fg" )
        return (bg, fg)

    #-----------------------------------------------------------------
    
    
# end of class cTkSDHTactileSensorPatch
#######################################################################


#-----------------------------------------------------------------
## \brief Widget to display all tactile sensor patches of an SDH
#
#  - creates the widgets
#  - defines Keyboard shortcuts (see docstring of file)
#  - defines callbacks to command the SDH
#  <hr>
class cTkSDHTactileSensorPatches(Frame):
    #-----------------------------------------------------------------
    ## Constructor of cTkSDHTactileSensorPatches
    def __init__( self, ts, master=None, debug_level=0, debug_output=sys.stderr, style=["color"] ):
        global dbg
        dbg.SetFlag( debug_level > 0 )
        dbg.SetOutput( debug_output )
        self.debug_level = debug_level
        
        self.ts = ts
        Frame.__init__( self, master, class_="cTkSDHTactileSensorPatches" )

        #top=self.winfo_toplevel()
        #top.rowconfigure(0, weight=1)
        #top.columnconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # create all subwidgets
        self.CreateWidgets(style)

        self.Repaint()

    #-----------------------------------------------------------------
    ## Create the GUI widgets: 
    def CreateWidgets(self, style ):

        shaft0 = cSDHTactileSensorPatch( 0, 0, self.ts )
        shaft1 = cSDHTactileSensorPatch( 1, 0, self.ts )
        shaft2 = cSDHTactileSensorPatch( 2, 0, self.ts )
        tip0 = cSDHTactileSensorPatch( 0, 1, self.ts )
        tip1 = cSDHTactileSensorPatch( 1, 1, self.ts )
        tip2 = cSDHTactileSensorPatch( 2, 1, self.ts )
                

        self.tsps = [ cTkSDHTactileSensorPatch( shaft0, master=self, style=style),
                      cTkSDHTactileSensorPatch( tip0, master=self, style=style ),
                      cTkSDHTactileSensorPatch( shaft1, master=self, style=style ),
                      cTkSDHTactileSensorPatch( tip1, master=self, style=style ),
                      cTkSDHTactileSensorPatch( shaft2, master=self, style=style ),
                      cTkSDHTactileSensorPatch( tip2, master=self, style=style ) ]

        self.tsps[ 0 ].grid( row=1, column=0, sticky=N+S+W+E )
        self.tsps[ 1 ].grid( row=0, column=0, sticky=N+S+W+E )
        self.tsps[ 2 ].grid( row=1, column=1, sticky=N+S+W+E )
        self.tsps[ 3 ].grid( row=0, column=1, sticky=N+S+W+E )
        self.tsps[ 4 ].grid( row=1, column=2, sticky=N+S+W+E )
        self.tsps[ 5 ].grid( row=0, column=2, sticky=N+S+W+E )

    #-----------------------------------------------------------------
    def Repaint( self ):
        for w in self.tsps:
            w.Repaint()
            
# end of class cTkSDHTactileSensorPatches
#######################################################################
