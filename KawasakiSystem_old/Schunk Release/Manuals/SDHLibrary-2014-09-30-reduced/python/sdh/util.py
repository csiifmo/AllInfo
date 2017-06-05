# -*- coding: latin-1 -*-
#######################################################################
## \file
#  \section sdhlibrary_python_util_py_general General file information
#
#    \author   Dirk Osswald
#    \date     2006-04-07
#
#  \brief  
#    Some basic utilities, see also util.__doc__
#
#  \section sdhlibrary_python_util_py_copyright Copyright
#
#  - Copyright (c) 2007 SCHUNK GmbH & Co. KG
#
#  <HR>
#  \internal
#
#    \subsection sdhlibrary_python_util_py_details SVN related, detailed file specific information:
#      $LastChangedBy: Osswald2 $
#      $LastChangedDate: 2014-09-30 09:44:33 +0200 (Tue, 30 Sep 2014) $
#      \par SVN file revision:
#        $Id: util.py 12281 2014-09-30 07:44:33Z Osswald2 $
#
#  \subsection sdhlibrary_python_util_py_changelog Changelog of this file:
#      \include util.py.log
#
#######################################################################

# pylint: disable-msg=W0622
## The docstring describing the purpose of the script:
__doc__ = '''
util.py:      This is a python module. It is meant to be imported by other modules and scripts.
Brief:        A collection of generally usefull python functions and classes:
              - GetColor    : return console color code
              - Beep        : beep on console
              - GetClipboard: Return content of clipboard (on cygwin/Windows)
              - SetClipboard: Set content of clipboard to content (on cygwin/Windows)
              - WinpathToCygpath: return cygwin path from windows path
              - tMyOptionParser: OptionParser with some defaults set (like -d -v)
              - error          : print on stderr
              - Ziplen         : return a list containing tuples of elements and indexes of these elements
              - call           : call function with 0,1,n arguments
              - sgn            : return signum of numeric value
              - GetDefineOrVariable : extract value of define from header file or variable from python file
              - GetProjectName      : extract value of PROJECT_NAME from header file or variable from python file
              - GetProjectRelease   : extract value of PROJECT_RELEASE from header file or variable from python file
              - RangeDefToList      : convert a range definition description to a list of indices, like "1-3,5" => [1,2,3,5]
              
Author:       Dirk Osswald <dirk_osswald@web.de>
Date:         2006-04-07
CVS-revision: $Id: util.py 12281 2014-09-30 07:44:33Z Osswald2 $
'''
#
######################################################################

# cannot use dbg here since that uses util module

######################################################################
# 
def GetColor(c):
    '''return a string that when printed sets the color to c, where c must be in
    normal, bold, red, green, yellow, blue, magenta, cyan, white, black, for normal color or
    black_back, red_back, green_back, yellow_back, blue_back, cyan_back, magenta_back, white_back for reverse color
    If the environment variable "TERM" is set to "eclipse" then no color string is returned.
    If the environment variable "SDH_NO_COLOR" is set then "" is returned.
    If the environment variable "OS" is WIN* or Win* and "OSTYPE" is not "cygwin"
    then "" is returned. (to prevent color output on windows consoles which cannot handle it).
    If the color is not found in the list of known colors then the string "" is returned.
    '''
    import os
    # no coloring when run within a non color aware console like windows
    if ( ('TERM' in os.environ.keys() and os.environ['TERM'] == "eclipse") or
         ('SDH_NO_COLOR' in os.environ.keys()) or
         ('OS' in os.environ.keys() and ('WIN' in os.environ['OS'] or 'Win' in os.environ['OS']) and (not 'OSTYPE' in os.environ.keys() or not 'cygwin' in os.environ['OSTYPE'] )) ):
        return ""
        
    colors={ "normal" : "\x1b[0m",
             "bold" : "\x1b[1m",
             "red" : "\x1b[31m",
             "green" : "\x1b[32m",
             "yellow" : "\x1b[33m",
             "blue" : "\x1b[34m",
             "magenta" : "\x1b[35m",
             "cyan" : "\x1b[36m",
             "white" : "\x1b[37m",
             "black" : "\x1b[39m",
             "black_back" : "\x1b[40m",
             "red_back" : "\x1b[41m",
             "green_back" : "\x1b[42m",
             "yellow_back" : "\x1b[43m",
             "blue_back" : "\x1b[44m",
             "cyan_back" : "\x1b[45m",
             "magenta_back" : "\x1b[46m",
             "white_back" : "\x1b[47m" }
    return colors[c]
#
######################################################################

######################################################################
# 
def Beep( n = 1, delay = 0.2 ):
    '''Do n console beeps with a delay of delay seconds.
    '''
    while n >= 1:
        console = file("/dev/console", "w")
        console.write( "\a" )
        console.close()
        n = n-1
        if n >= 1:
            import time
            time.sleep( delay )
#
######################################################################

######################################################################
#
def GetClipboard():
    '''Return content of clipboard (on cygwin/Windows)
    '''

    cb = file( "/dev/clipboard", "r" )
    result = cb.read(-1)
    cb.close()
    return result
#
######################################################################

######################################################################
#
def SetClipboard(content):
    """Set content of clipboard to content (on cygwin/Windows)
    """

    cb = file( "/dev/clipboard", "w" )
    cb.write(content)
    cb.close()
#
######################################################################

######################################################################
#
from optparse import OptionParser

class tMyOptionParser(OptionParser):
    '''OptionParser with some default options already set:
    -d | --debug turn on debug (set options.debug flag)
    -v | --version print version and exit
    '''
    def ShowVersion(self, option, opt, value, parser):
        print self.version
        import sys
        sys.exit()
        
    def __init__(self, usage = "", version = "" ):
        '''Create a tMyOptParser instance.

        usage has the usual meaning and version is the string that is printed
        when -v | --version option is set
        '''
        OptionParser.__init__( self, usage )
        self.version = version
        
        # add common options:
        self.add_option( "-d", "--debug",
                         action="store_true", dest="debug", default=False,
                         help="Print debug messages while processing.")
        self.add_option( "-v", "--version",
                         #action="store_true", dest="print_version", default=False,
                         action="callback", callback=self.ShowVersion,
                         help="Print the version and exit.")
#
######################################################################

######################################################################
#
def WinpathToCygpath(winpath):
    '''Return the cygwin path of the file with the windows path winpath

    Will convert "c:\\bla\\blu.bli" to "/cygdrive/c/bla/blu.bli"
    '''
    if (winpath[1] != ':'):
        raise Exception( "WinpathToCygpath(): Not an absolute path, donnow what to do!" )

    result = "/cygdrive/"
    for c in winpath:
        if (c==":"):
            pass
        elif (c=="\\"):
            result += "/"
        else:
            result += c
    return result
#
######################################################################

######################################################################
#
def error( *args ):
    import sys
    for arg in args:
        print >>sys.stderr, arg,
    print >>sys.stderr
#
######################################################################

######################################################################
#
def Ziplen( l ):
    '''return a list containing tuples of elements and indexes of these elements
    Remark: this is like the std enumerate(l) with the elements in the tuples reversed
    '''
    return zip( l, range(len(l)) )
#
######################################################################

######################################################################
#
def Call(fun,pars):
 '''call function fun with arguments pars.
 - pars = None : call fun()
 - pars = SomeType : call fun(pars)
 - pars = tuple    : call fun(*pars)
 '''
 if ( type( pars ) == type(None) ):
     fun()
 elif ( type( pars ) == tuple ):
     fun(*pars)
 else:
     fun(pars)
#
######################################################################

######################################################################
#
def sgn(v):
    '''
    return signum of v
    '''
    if   (v>0.0): return  1.0
    elif (v<0.0): return -1.0
    else:         return  0.0
#
######################################################################

#######################################################################
#
def GetDefineOrVariable( ifile, name ):
    '''
    Return value of C/C++ define "name" in header file "ifile" or of
    python variable "name" in python module "ifile".
    
    \internal The regular expression works on lines formed like:
    - \#define NAME "A-Name"
    - NAME = "A-Name"
    where "NAME" is the value of name
    '''
    import re
    pattern = re.compile( '^\s*(#\s*define\s+%s|%s\s*=)\s+"([^"]*)"' % (name,name) )
    f = file( ifile, "r" )
    for l in f.readlines():
        m = pattern.match( l )
        if m:
            #print "extracted %s <%s>" % (name, m.group(2))
            return m.group(2)
    raise Exception( '%s is not defined in FILE "%s"!' % (name,ifile) )
#
#######################################################################

#######################################################################
#
def GetProjectName( release_file ):
    '''
    Return name of project (extracted from header file release_file). 
    The code below uses a regular expression to extracts the value of the C preprocessor
    macro define or the definition of a variable named PROJECT_NAME.
    The extracted value can be:
    - Used by doxygen as project name. 
    - Used as base name of the generated pdf documentation files. 
    - Used as name of project directory when installing.
    
    \internal The regular expression works on lines formed like:
    - \#define PROJECT_NAME "A-Name"
    - PROJECT_NAME = "A-Name"
    '''
    try:
        return GetDefineOrVariable( release_file, "PROJECT_NAME" )
    except Exception,e:
        error( 'Caught exception "%s", returning default "PROJECT_NAME"', str(e) )
        return "PROJECT_NAME"
#
#######################################################################


#######################################################################
#
def GetProjectRelease( release_file ):
    '''
    Return release of project (extracted from header file release_file). 
    The code below uses a regular expression to extracts the value of the C preprocessor
    macro define or the definition of a variable named PROJECT_RELEASE.
    The extracted value can be:
    - Used by doxygen as project release. 
    - Used as name of release directory when installing.
    
    \internal The regular expression works on lines formed like:
    - \#define PROJECT_RELEASE "1.0.0.0-dev"
    - PROJECT_RELEASE = "1.0.0.0-dev"
    '''
    try:
        return GetDefineOrVariable( release_file, "PROJECT_RELEASE" )
    except Exception,e:
        error( 'Caught exception "%s", returning default "PROJECT_RELEASE"', str(e) )
        return "PROJECT_RELEASE"
#
#######################################################################

#######################################################################
#
def RangeDefToList( range_definition, max=1000 ):
    '''return a list of indexes according to a range definition string
    e.g.  "1" => [1], "1,2,4" => [1,2,4], "3-6" => [3,4,5,6])
    '''
    import re
    # determine the indices of the plots to use:    
    if ( range_definition in "all" ):
        index_to_use = range( 0, max )  # should be large enough
    else:
        index_to_use = []
        # split comma separated parts
        parts = range_definition.split(",")
        parts = [ p.strip()  for p in parts ]
        re_number = re.compile("^[0-9]+$")
        re_range  = re.compile("^([0-9]+) *- *([0-9]+)$")
        for p in parts:
            n = re_number.match( p )
            r = re_range.match( p )
            if ( n ):
                index_to_use.append( eval( p ) )
                
            elif ( r ):
                for i in range( int(r.groups()[0]), int(r.groups()[1])+1 ):
                    index_to_use.append( i )
            else:
                print "illegal pattern '%s' in range_definition '%s'" % (p,range_definition)
                sys.exit(1)
                    
    #dbg << "index_to_use =" << repr( index_to_use) << "\n" # pylint: disable-msg=W0104
    return index_to_use
#
#######################################################################

def GetPersistantDict( name=None, path=None, cdbg=None ):
    '''Dictionary that stores objects persistently using shelve

    If you want to be able to generate standalone exes with py2exe
    you must add the following line to your script
    according to http://myblog.vindaloo.com/?p=129
      import anydbm, dbhash
    '''
    import shelve,os
    if ( path is None ):
        path = os.path.expanduser("~")
    path = os.path.normpath(path)
      
    if ( name is None ):
        name = ".pypersistent"
        
    if ( not os.path.exists(path) ):
        cdbg << "Given path %r does not exist. Using '.' instead\n" % (path)
        path="."
        
    db_name = os.path.join( path, name )
    persistent_dict = shelve.open( db_name )
    if ( cdbg ):
        #dbg.var( "db_name persistent_dict")
        cdbg.var( "db_name" )
        cdbg << "persistent_dict:\n"
        for (k,v) in persistent_dict.items():
            cdbg << "  %r:%r\n" % (k,v)
    return persistent_dict
