# -*- coding: latin-1 -*-
#######################################################################
## \file
#  \section sdhlibrary_python_setup_py_general General file information
#
#    \author   Dirk Osswald
#    \date     2007-05-11
#
#  \brief  
#    Python distutils setup script for #sdh package
#
#  \section sdhlibrary_python_setup_py_copyright Copyright
#
#  - Copyright (c) 2007 SCHUNK GmbH & Co. KG
#
#  <HR>
#  \internal
#
#    \subsection sdhlibrary_python_setup_py_details SVN related, detailed file specific information:
#      $LastChangedBy: Osswald2 $
#      $LastChangedDate: 2013-11-27 16:12:49 +0100 (Wed, 27 Nov 2013) $
#      \par SVN file revision:
#        $Id: setup.py 11045 2013-11-27 15:12:49Z Osswald2 $
#
#  \subsection sdhlibrary_python_setup_py_changelog Changelog of this file:
#      \include sdh.py.log
#
#######################################################################

# This is the python script to build the SDHLibrary-python python extension module.

from distutils.core import setup
import os, glob

# read in utilities of package
# (we cannot just import sdh.release since the installed sdh package is likeley older than the one we are generating)
sdh_locals = dict()
sdh_globals = dict()
execfile( "sdh/release.py", sdh_globals, sdh_locals )




def Pathify( *dirs ):
    '''join dirs (list of directory names/files) to a list of paths using the right path separator'''
    return glob.glob(os.path.join( *dirs ))

#---------------------
# create list of generated doc files to include in distribution
doc_files = [ ( 'share/doc/%s' %  sdh_locals[ "PROJECT_NAME" ],         # target dir 
                Pathify('doc', 'index-sdhlibrary-python.html')          # list of files to install in target dir
                + Pathify('doc', 'SDHLibrary-python-external.pdf')  
                + Pathify('..', '..', 'software', 'doc', 'SDH2_configuration-and-update.pdf') 
#                + Pathify('doc', 'Inbetriebnahme.doc')
                )
              ]

guidat_files = [ ('scripts',  # target dir
                  Pathify( 'demo', 'positions.guidat' )
                  + Pathify( 'demo', 'warmup.guidat' )
                  )
               ]

# the generated html doc_files must be calculated:
for r,d,f in os.walk(Pathify('doc', 'external', 'html')[0]):
    if f == []: continue

    src_rel_paths = map( lambda n: Pathify( r, n )[0], f )
    #target_path = r.replace( 'doc/', 'share/doc/%s/' % sdh_locals[ "PROJECT_NAME" ] )
    target_path = r.replace( os.path.join( 'doc', ''),
                             os.path.join( 'share', 'doc', sdh_locals[ "PROJECT_NAME" ], '' ) )
    print "          r=", r
    print "target_path=", target_path
    doc_files.append( (target_path, src_rel_paths) )

#
#---------------------

        
# add guidat files to distro???

setup ( name             = sdh_locals[ "PROJECT_NAME" ],
        version          = sdh_locals[ "PROJECT_RELEASE" ],
        description      = 'sdh: the python package to access an SDH (SCHUNK Dexterous Hand)',
        author           = 'Dirk Osswald',
        author_email     = 'dirk.osswald@de.schunk.com',
        url              = 'http://www.schunk.com/',
        long_description = '''
This is a python package to access an SDH (SCHUNK Dexterous Hand).
It provides a class interface to access the functionality of the SDH
and some example scripts that demonstrate its use.
For details see the included documentation in html- or pdf-format.
''',
        packages         = [ 'sdh' ],
#        py_modules       = [ 'sdh',
#                             'dsa', 'tkdsa',
#                             'util', 'utils', 'dbg'
#                            ],

        # when modifying the list below then consider modifying EXT_DEMO_SCRIPTS in python/Makefile:235
        scripts          =   Pathify('demo', 'demo-simple.py') +
                             Pathify('demo', 'demo-radians.py') +
                             Pathify('demo', 'demo-simple2.py') +
                             Pathify('demo', 'demo-simple3.py') +
                             Pathify('demo', 'demo-gui.py') +
                             Pathify('demo', 'demo-GetAxisActualAngle.py') +
                             Pathify('demo', 'demo-calc-workspace.py') +
                             Pathify('demo', 'demo-contact-grasping.py') +
                             Pathify('demo', 'demo-dsa.py') +
                             Pathify('demo', 'demo-tactile.py') +
                             Pathify('demo', 'demo-temperature.py') +
                             Pathify('demo', 'demo-workspace.py') +
                             Pathify('demo', 'demo-benchmark.py') +
                             Pathify('demo', 'demo-velocity-acceleration.py') +
                             Pathify('demo', 'miniterm.py') +
                             #Pathify('demo', 'demo-collision.py') +
                             #Pathify('demo', 'demo-endurance-run.py') +
                             Pathify('demo', 'schunk.ico') +
                             Pathify('demo', 'schunk.xbm') +
                             #Pathify('demo', 'demo-torquemeasurement.py') +
                             #Pathify('demo', 'demo-workspace.py') +
                             #Pathify('ramp.py') +
                             Pathify('test_sdh.py' ) +
                             Pathify('demo', 'sdhoff') +
                             #Pathify('demo', 'switch2dsa.py') +
                             Pathify('postinstall_sdh.py'),
        data_files       =   doc_files + guidat_files
        )

######################################################################
# some usefull editing settings for emacs:
#
#;;; Local Variables: ***
#;;; mode:python ***
#;;; End: ***
#
######################################################################
