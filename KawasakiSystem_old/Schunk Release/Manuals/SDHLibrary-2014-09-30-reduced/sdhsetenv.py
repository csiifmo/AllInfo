#!/usr/bin/env python
# this is a -*- python -*- file
#
# Print out shell commands that set environment variables suitable to
# run the sdh demo programs found here (and in subdirs) without installing.
#
# This file should not be run directly, instead it is called from the
# sdhsetenv shell script that must be sourced in.
#
# This file is based on / copied from mca2 http://www.mca2.org/
#

import os
import platform
import sys
import re
import getopt
import ConfigParser

#
# global variables init
#
verbose=False
config_dict_cmd={}

sdh_config_name_default='.sdh-config.'+platform.node()
sdh_config_name=sdh_config_name_default

#
# Functions
#
regex_yes=re.compile("[Yy]([Ee][Ss])?")
def IsYes(str):
    return regex_yes.match(str)

def PrintSettings():
    sys.stderr.write("----------------------------------\n")
    sys.stderr.write(" SDH Settings\n")
    sys.stderr.write("----------------------------------\n")
    sys.stderr.write(" Home:         "+ env_dict["SDHHOME"]+"\n");
##    sys.stderr.write(" Project:      "+ env_dict["SDHPROJECT"]+"\n");
##    sys.stderr.write(" Project Home: "+ env_dict["SDHPROJECTHOME"]+"\n");
##    sys.stderr.write(" SubProject:   "+ env_dict["SDHSUBPROJECT"]+"\n");
##    sys.stderr.write(" Target:       "+ env_dict["SDHTARGET"]+"\n");
    if sdh_debug:
        sys.stderr.write(" Debug:        On\n")
    else:
        sys.stderr.write(" Debug:        Off\n")
        
    sys.stderr.write("----------------------------------\n")


def Usage():
	sys.stderr.write("usage:")
	sys.stderr.write( sys.argv[0]+"[options]\n")
	sys.stderr.write( "options:\n")
        sys.stderr.write( "-h,--help show this help\n")
        sys.stderr.write( "-c CONFIGFILE,--config=CONFIGFILE (use given CONFIGFILE instead of '.sdh-config.[hostname]')\n")
##        sys.stderr.write( "-p PROJECT,--project=PROJECT (override project name)\n")
##        sys.stderr.write( "-s SUBPROJECT,--subproject=SUBPROJECT (override subproject name)\n")
        sys.stderr.write( "-d,--debug=[y/n] (override debug settings)\n")

def CmdConfig(key):
    if config_dict_cmd.has_key(key):
        return config_dict_cmd[key]
    else:
        return ''
    
#
# Main
#

# redirect output to stderr
#print >> sys.stderr

# Read command line arguments
cmdline_arguments={}
try:                                
##    opts, args = getopt.getopt(sys.argv[1:], "hp:s:d:c:", ["help", "project=", "subproject=", "debug=","config="]) 
    opts, args = getopt.getopt(sys.argv[1:], "hd:c:", ["help", "debug=","config="]) 
except getopt.GetoptError:           
    Usage()                          
    sys.exit(2)
    
for opt, arg in opts:
    if opt in ("-h", "--help"):
        Usage()
        sys.exit(0)
##    elif opt in ("-p","--project"):
##        cmdline_arguments['project']=arg
##        config_dict_cmd["Project_main"]=arg
    elif opt in ("-c","--config"):
        sdh_config_name=arg
##    elif opt in ("-s","--subproject"):
##        cmdline_arguments['subproject']=arg
##        config_dict_cmd["Project_sub"]=arg
    elif opt in ("-d","--debug"):
        cmdline_arguments['debug_mode']=arg
        config_dict_cmd["Build_debug"]=arg

# Read SDH config file if available
config_file_entries={}
if not os.access(sdh_config_name,os.R_OK):
##    sys.stderr.write("Cannot open config file "+sdh_config_name+"\n")
##    sys.stderr.write("Make sure you have already run scons or read the README file for more information.\n")
##    sys.exit(1)
    cf=open(sdh_config_name,'w')
    cf.close()
    
cf=open(sdh_config_name,'r')
for line in cf.readlines():
    line_match=re.match("(.*?)\s*=\s*(['\"]?)(.*)\\2",line)
    key=line_match.group(1)
    value=line_match.group(3)
    config_file_entries[key]=value
cf.close()

# Overwrite values in the config file with the commandline arguments
##for entry in ['project','subproject','debug_mode']:
for entry in ['debug_mode']:
    if cmdline_arguments.has_key(entry):
        config_file_entries[entry]=cmdline_arguments[entry]

# Write back the config file
cf=open(sdh_config_name,'w')
for (key,value) in config_file_entries.iteritems():
    if value.isdigit():
    	cf.write('%s = %s\n' % (key,value))
    elif re.match(".*'.*",value):
        cf.write('%s = "%s"\n' % (key,value))
    else:
        cf.write("%s = '%s'\n" % (key,value))
cf.close()

## Extract necessary information from the configfile

# Check for debug mode
sdh_debug=True
if config_file_entries.has_key('debug_mode'):
    sdh_debug=IsYes(config_file_entries['debug_mode'])
else:
    sdh_debug=True

# Detect architecture and system
config_arch=platform.machine()
if config_arch=='':
    (config_arch,_)=platform.architecture()

config_system=platform.system()

# Build target string
sdh_target=config_arch+'_'+config_system
try:
    if config_file_entries['target_extra']!='':
        sdh_target+='_'+config_file_entries['target_extra']
except:
    pass
if sdh_debug:
    sdh_target+='_debug'

## Evaluate environment variables
env_dict={}

# SDHPROJECT
##if config_file_entries.has_key('project'):
##   env_dict['SDHPROJECT']=config_file_entries['project']
##else:
##    env_dict['SDHPROJECT']='test'

# SDHSUBPROJECT
##if config_file_entries.has_key('subproject'):
##    env_dict['SDHSUBPROJECT']=config_file_entries['subproject']
##else:
##    env_dict['SDHSUBPROJECT']=''

# SDHHOME
env_dict['SDHHOME']=os.getcwd()

# SDHPROJECTHOME
##sdh_project_directory=env_dict['SDHHOME']
##project_directories=[os.path.join(env_dict['SDHHOME'],env_dict['SDHPROJECT']),
##                     os.path.join(env_dict['SDHHOME'],'project',env_dict['SDHPROJECT'])]
##for project_directory in project_directories:
##    if os.path.exists(project_directory):
##        sdh_project_directory=project_directory
##env_dict['SDHPROJECTHOME']=sdh_project_directory

# SDHTARGET
##env_dict['SDHTARGET']=sdh_target

#-----------------------------
# PATH
env_name='PATH'
if os.environ.has_key(env_name):
    env_dict[env_name]=os.environ[env_name]
else:
    env_dict[env_name]=''

#clean old sdh PATH entries
env_dict[env_name]=re.sub(":?"+env_dict["SDHHOME"]+"[^:]*","",env_dict[env_name])
#add new sdh PATH entries
sdh_path_directories=[]
sdh_path_directories.append(os.path.join(env_dict["SDHHOME"],"cpp/bin"))
sdh_path_directories.append(os.path.join(env_dict["SDHHOME"],"python/demo"))

# on cygwin the lib dir with the dlls must be in the path too (as $LD_LIBRARY_PATH seems to be ignored)
if 'CYGWIN' in platform.system():
    sdh_path_directories.append(os.path.join(env_dict["SDHHOME"],"lib"))

##sdh_path_directories.append(os.path.join(env_dict["SDHPROJECTHOME"],"script"))
##sdh_path_directories.append(os.path.join(env_dict["SDHHOME"],"script"))
for sdh_path_directory in sdh_path_directories:
    if (os.path.exists(sdh_path_directory)):
        env_dict[env_name]= sdh_path_directory + ":" + env_dict[env_name]
# always add $SDHHOME/export/$SDHTARGET/bin
##env_dict[env_name]=os.path.join(env_dict["SDHHOME"],"export",env_dict["SDHTARGET"],"bin") + ":" + env_dict[env_name]

##if 'CYGWIN' in platform.system():
##    env_dict[env_name]=os.path.join(env_dict["SDHHOME"],"export",env_dict["SDHTARGET"],"lib") + ":" + env_dict[env_name]

#delete :: 
env_dict[env_name]=re.sub("::",":",env_dict[env_name])

#-----------------------------
# LDLIBRARYPATH
env_name='LD_LIBRARY_PATH'
if os.environ.has_key(env_name):
    env_dict[env_name]=os.environ[env_name]
else:
    env_dict[env_name]=''
#clean old sdh LD_LIBRARY_PATH entries
env_dict[env_name]=re.sub(env_dict["SDHHOME"]+":?[^:]*","",env_dict[env_name])
# add new  sdh LD_LIBRARY_PATH entries
sdh_lib_directories=[]
sdh_lib_directories.append(os.path.join(env_dict["SDHHOME"],"cpp/bin"))
for sdh_lib_directory in sdh_lib_directories:
    if (os.path.exists(sdh_lib_directory)):
        env_dict[env_name]=sdh_lib_directory + ":" + env_dict[env_name]
# always add $SDHHOME/export/$SDHTARGET/lib
##env_dict[env_name]=os.path.join(env_dict["SDHHOME"],"export",env_dict["SDHTARGET"],"lib") + ":" + env_dict[env_name]
#delete :: 
env_dict[env_name]=re.sub("::",":",env_dict[env_name])

#-----------------------------
# PYTHONPATH
env_name='PYTHONPATH'
if os.environ.has_key(env_name):
    env_dict[env_name]=os.environ[env_name]
else:
    env_dict[env_name]=''
#clean old sdh PYTHONPATH entries
env_dict[env_name]=re.sub(env_dict["SDHHOME"]+":?[^:]*","",env_dict[env_name])
# add new  sdh PYTHONPATH entries
sdh_pypath_directories=[]
sdh_pypath_directories.append(os.path.join(env_dict["SDHHOME"],"python"))
for sdh_lib_directory in sdh_pypath_directories:
    if (os.path.exists(sdh_lib_directory)):
        env_dict[env_name]=sdh_lib_directory + ":" + env_dict[env_name]
#delete :: 
env_dict[env_name]=re.sub("::",":",env_dict[env_name])


#-----------------------------

PrintSettings()

# Add other shell detection and environment set commands to the following code detect shell
shell=''
for line in sys.stdin:
    if re.match(".*tcsh.*",line):
        shell="tcsh"
        break
    elif re.match(".*(z|ba)sh.*",line):
        shell="bash"
        break

#write setenv/export commands
if shell=="bash":
    for element in env_dict:
        sys.stdout.write("export "+element+"=\""+env_dict[element]+"\";")
elif shell=="tcsh":
    for element in env_dict:
        sys.stdout.write("setenv "+element+" "+env_dict[element]+";")
#place any other shell command output here!
else:
    sys.stderr.write("echo Unknown shell type\nEnvironment variables not set\n")
