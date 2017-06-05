Overview:
=========

This is the README file of SDHLibrary-python, the Python package to
access an SDH (SCHUNK Dexterous Hand).


Directory structure:
====================

This directory contains the overall Makefile and subdirs:
- ./      : Additional files like this README or the makefile
- ./demo/ : scripts that demonstrate the use of the package
- ./dist/ : precompiled 'binary' distributions (for windows and cygwin)
- ./doc/  : pregenerated documentation 
- ./misc/ : additional external packages you might need to run this package
- ./sdh/  : the python package itself


Usage instructions:
===================

Build:
------

You can run the demo programs directly from here, but the paths have
to be adjusted accordingly. Use the sdhsetenv script in the
parent-directory of this directory to set the paths. That script must
be sourced-in like in:
  > cd .. ; source sdhsetenv

To ease the usage of the package from your own scripts you should install
the package:


Install:
--------

To install the package, the demo-scripts and the documentation run 
  > make install
in this directory. This will use the python distutils and thus install 
the package in a standard pythonic way. The documentation is installed
in /usr/share/doc/SDHLibrary-python.



Uninstall:
----------
To uninstall the library, demo-programs and documentation run 
  > make uninstall
in this directory. (This works only after a previous install from within
this very directory!)


Further info:
=============
See the demonstration scripts ./demo/demo-*.py and the documentation in ./doc/ 
on how to use the offered functionality.


Contact information:
====================
Dirk Osswald: mailto:dirk.osswald@de.schunk.com
              http://www.schunk.com
