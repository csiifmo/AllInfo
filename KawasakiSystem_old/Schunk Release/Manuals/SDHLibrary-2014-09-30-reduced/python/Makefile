#=======================================================================
#//! \file
#//! \section sdhlibrary_python_makefile_general General file information
#//!   \author    Dirk Osswald 
#//!   \date      2007-01-03
#//!  
#//! \brief  
#//!   Makefile for SDH SDHLibrary python project.
#//!
#//!   This makefile can install/uninstall the python package, generate
#//!   auxiliary stuff like doxygen documentation or generate a
#//!   distribution for delivery to end users.
#//!
#//!   For a general description of the project see \ref sdhlibrary_python_dox_general "general project information".
#//!
#//! \section sdhlibrary_python_makefile_variables Makefile variables
#//!   The variables defined here state project specific settings which are
#//!   then used by the goals and/or by the included, more generic sub makefiles
#//!   like:
#//!   - \ref Makefile-common "Makefile-common"
#//!   \internal 
#//!   - \ref Makefile-doc    "Makefile-doc"
#//!   - \ref Makefile-plot   "Makefile-plot"
#//!   - \ref Makefile-dist   "Makefile-dist"
#//! 
#//! \section sdhlibrary_python_makefile_targets Makefile targets
#//!   - \b \c all : generate everything
#//!     - \b \c doc    : generate all documentation (not available in distribution)
#//!   - \b \b install  : install python package, demo scripts and 
#//!                      documentation in a native pythonic way using distutils 
#//!   - \b \b uninstall: uninstall previously installed stuff
#//!   - \b \c clean    : clean up generated program files, but not TAGS or doxygen doc
#//!   - \b \c mrproper : clean up all generated files, including TAGS and doxygen doc
#//!   - \b \c tags     : generate emacs TAGS file
#//!   - \b \c test     : run automated unit tests using py.test
#//!   - \b \c dos2unix : convert line endings from dos/windows format to unix format
#//!   - \b \c unix2dos : convert line endings from unix format to dos/windows format
#//!   \internal
#//!   - \b \c dist     : create a distribution
#//!     - \b \c dist_only : create a distribution without regenerating doc or plot
#//!   - \b \c plot_all : generate 2D and 3D plots in pdf format
#//!     - \b \c plot_show : generate 2D and 3D plots as X11 windows (needs a runnging X11 Server)
#//!
#//! \section sdhlibrary_python_makefile_links Links
#//!   - The online documentation for \c gnu \c make can be found at
#//!     <a href="http://www.gnu.org/software/make/manual/make.html">
#//!     http://www.gnu.org/software/make/manual/make.html</a>
#//!  
#//! \section sdhlibrary_python_makefile_copyright Copyright
#//!
#//!  Copyright (c) 2007 SCHUNK GmbH & Co. KG
#//!
#//!  <HR>
#//!  \internal
#//!
#//!    \subsection sdhlibrary_python_makefile_details SVN related, detailed file specific information:
#//!      $LastChangedBy: Osswald2 $
#//!      $LastChangedDate: 2013-11-27 16:12:49 +0100 (Wed, 27 Nov 2013) $
#//!      \par SVN file revision:
#//!        $Id: Makefile 11045 2013-11-27 15:12:49Z Osswald2 $
#//!
#//!  \subsection sdhlibrary_python_makefile_changelog Changelog of this file:
#//!      \include Makefile.log
#//!
#=======================================================================
#//! \cond ignore_me   doxygen cannot parse Makefiles, so just ignore it

.DEFAULT_GOAL := all

########################################################################
# first some variables

## Path and name of the header file containing the 
#  PROJECT_NAME and PROJECT_RELEASE defines (see Makefile-common).
export RELEASE_FILE=./sdh/release.py

#----------------------------
# some directories:

## Path to common stuff like sub-makefiles
export COMMON_DIR=${shell if [ -d "../../../common" ]; then \
	             echo "../../../common";\
		   else \
	             echo "./" ; \
	           fi}


# Documentation files directory
export DOCDIR = ./doc

## specify target specific definitions for TAGFILES:
#  (links to internal tag files make sense only for the internal docu,
#   for the external docu it would lead to broken links)
doc_internal_html: TAGFILES=../../../../tags/Protocol.tag=../../../../../../Protocol/doc/internal/html/ ../../../../tags/MotionControl.tag=../../../../../../MotionControl/doc/internal/html/ ../../../../tags/common.tag=../../../../../../common/doc/internal/html/
doc_internal: DOC_EXTRA_INPUT=
doc_internal: DOC_EXTRA_EXCLUDE=
doc_internal: DOC_EXTRA_EXCLUDE_PATTERNS=

doc_external_html: TAGFILES=
doc_external: DOC_EXTRA_EXCLUDE= \
						 plot.py \
	                     ramp.py \
	                     demo/demo-endurance-run.py \
	                     demo/demo-collision.py \
	                     demo/demo-temperature-pcb-fpga.py \
	                     demo/demo-torquemeasurement.py \
	                     record_positioning.py \
	                     record_temperature.py \
	                     sdh/jtagserial.py \
	                     demo/sdhflash.py \
	                     demo/record_temperature.py \
	                     demo/sdhrecord.py \
	                     demo/switch2dsa.py \
	                     demo/test-crc.py \
	                     Makefile-dist \
	                     conftest.py 

doc_external: DOC_EXTRA_EXCLUDE_PATTERNS=

#
########################################################################

########################################################################
# now the goals

## Default goal: Make all (programs and documentation)
.PHONY: all
all: build doc

.PHONY: build
build: 
	@echo "Nothing to build here"

## Generate and install generated files 
.PHONY: install
install: doc install_only


## Install already generated files only 
#  (usefull since docu is always regenerated and is rather slow)
.PHONY: install_only
install_only .installed_files.lst: 
# 	# install and save the list of all the files installed:
#	# extract lines where files are copied to an absolute dir
#	# format is like "copying build/lib/dbg.py -> /usr/lib/python2.4/site-packages"
	python setup.py install | tee install_only_output  | \
	  grep -e " -> /"                                  | \
	  sed "s,copying .*/\([^/ ]*\) -> \(.*\)$$,\2/\1,"   \
	> .tmp_installed_files.lst
	@cat install_only_output
	@rm  install_only_output
#	#
#	# append unique list of installed files
	cat .tmp_installed_files.lst .installed_files.lst 2> /dev/null | sort | uniq > .installed_files.lst

## Uninstall is not supported by distutils, so try this:
#  (if .installed_files.lst does not exist (yet/any more) then this will install everything first!)
.PHONY: uninstall
uninstall: .installed_files.lst
	@echo "uninstalling files from generated list .installed_files.lst"
	xargs rm -f < .installed_files.lst


## Clean up generated files, but not doc or tags.
.PHONY: clean
clean: 
	rm -rf build/*

## Clean up generated files including doc and tags.
.PHONY: mrproper
mrproper: clean doc_clean plot_clean
	rm -rf TAGS

PYTEST=/usr/local/src/py-dist/py/bin/py.test
cygwin_root=${shell cygpath -m $$CYGWIN_ROOT}

## Run automated unit tests
.PHONY: test
test: 
	@echo "using PYTEST=<{$PYTEST}>"
#	#${PYTEST} ${PYTEST_OPTIONS} --verbose
	cd test; \
	${PYTEST} --verbose |                            \
	  sed --unbuffered "s,/cygdrive/\(.\)/,\1:/,g" | \
	  sed --unbuffered "s,/usr/,${cygwin_root}/,g" | \
	  sed --unbuffered "s,\(\(/[^:]*\):\([0-9]*\):\(.*\)\),\1\n  File \"\2\"\, line \3 \4,g"  

.PHONY: tags
tags:
	etags `find . -name "*.py"  -a ! -path "./build/*" ` Makefile Doxyfile *.dox


## Check if the file Makefile-doc is available:
ifeq (${wildcard ${COMMON_DIR}/Makefile-doc},)
#  No, Makefile-doc is not available so use pregenerated documentation:

.PHONY: doc doc_clean plot_clean
doc: 
	@echo "Using pregenerated documentation"
#  some dummies to keep make happy
doc_clean:
plot_clean:

else
## specify target specific definitions for TAGFILES:
#  (links to SCHUNK-internal tag files make sense only for the internal docu,
#   for the external docu it would lead to broken links)
doc_internal_html: TAGFILES=../../../../tags/Protocol.tag=../../../../../../Protocol/doc/internal/html/ ../../../../tags/MotionControl.tag=../../../../../../MotionControl/doc/internal/html/ ../../../../tags/common.tag=../../../../../../common/doc/internal/html/ ../../../../tags/MD-SE.tag=../../../../../../MD-SE/doc/internal/html/
doc_internal: DOC_EXTRA_INPUT=${COMMON_DIR}/Makefile-common ${COMMON_DIR}/Makefile-doc Makefile-dist Makefile-plot

doc_external_html: TAGFILES=
doc_external: DOC_EXTRA_INPUT=Makefile-common
endif

# convert all python files from windows line endings (CR LF) to unix line endings (LF)
.PHONY: dos2unix
dos2unix:
	@for f in demo/*.py sdh/*.py ; do \
	  dos2unix $$f ;                  \
	done

# convert all python files from unix line endings (LF) to windows line endings (CR LF) 
.PHONY: unix2dos
unix2dos2:
	@for f in demo/*.py sdh/*.py ; do \
	  unix2dos $$f ;                  \
	done
#
########################################################################

########################################################################
# additional rules for including the online help of the demo scripts
# into the doxygen documentation

# when modifying the list below then consider modifying scripts in python/setup.py:101
export EXT_DEMO_SCRIPTS = \
	        demo/demo-simple.py                 \
	        demo/demo-radians.py                \
	        demo/demo-simple2.py                \
	    	demo/demo-simple3.py                \
	       	demo/demo-gui.py                    \
	        demo/demo-GetAxisActualAngle.py     \
	        demo/demo-calc-workspace.py         \
	        demo/demo-contact-grasping.py       \
	        demo/demo-dsa.py                    \
	        demo/demo-tactile.py                \
	        demo/demo-temperature.py            \
	        demo/demo-workspace.py              \
	        demo/demo-benchmark.py              \
	        demo/demo-velocity-acceleration.py  \
	        demo/miniterm.py                    

## the dox files to generate
ONLINE_HELP_DOX = ${patsubst demo/%.py,${DOCDIR}/onlinehelp-%.dox,${EXT_DEMO_SCRIPTS}}

ttt:
	echo EXT_DEMO_SCRIPTS=${EXT_DEMO_SCRIPTS}
	echo ONLINE_HELP_DOX=${ONLINE_HELP_DOX}

## add dependencies to the doc_*_html targets
doc_external_html: ${ONLINE_HELP_DOX} 
doc_internal_html: ${ONLINE_HELP_DOX} 

## add extra dependency to the doc_clean target
doc_clean: doc_clean_onlinehelp

## pattern rule for generating the onlinehelp-*.dox file from the program
${DOCDIR}/onlinehelp-%.dox: demo/%.py
	@echo "Generating $@ from $<:" ;\
	echo -e "// auto generated file, do not edit!\n/*!\n  \\\file\n\n  \\\addtogroup sdh_library_python_onlinehelp_group\n  @{\n\n  \\\par Online help for script \\\c $*.py\n\n \\\code\n" > $@ ;\
	export PYTHONPATH=.:$$PYTHONPATH ;\
	export TERM=dumb ;\
	$< --help               >> $@ ;\
	echo -e "\n\n\\\endcode\n  @} \n*/"   >> $@ ;\
	echo -e "finished $@\n"

## rule to clean the generated onlinehelp-*.dox files
doc_clean_onlinehelp:
	rm -f ${ONLINE_HELP_DOX}
#
########################################################################

########################################################################
#

# some common settings and targets are defined separately to keep this
# main Makefile more concise
include ${COMMON_DIR}/Makefile-common

## For internal use only:
# The variables and targets to generate documentation are defined
# separately to keep this main Makefile clearly laid out.
-include ${COMMON_DIR}/Makefile-doc

## For internal use only:
#  The variables and targets to generate plots are defined
#  separately to keep this main Makefile clearly laid out.
-include Makefile-plot

## For internal use only:
#  The variables and targets to generate a distribution are defined
#  separately to keep this main Makefile clearly laid out.
-include Makefile-dist

#
########################################################################


#-----------------------------------------------------------------------
# emacs settings:
# Local Variables:
# mode: Makefile
# End:
#-----------------------------------------------------------------------
##
#//! \endcond
########################################################################
