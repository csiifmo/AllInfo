# -*- coding: latin-1 -*-
#######################################################################
## \file
#  \section sdhlibrary_python_sdh_py_general General file information
#
#    \author   Dirk Osswald
#    \date     2007-01-15
#
#  \brief  
#    Implementation of the python import module #sdh
#
#  \section sdhlibrary_python_sdh_py_copyright Copyright
#
#  - Copyright (c) 2007 SCHUNK GmbH & Co. KG
#
#  <HR>
#  \internal
#
#    \subsection sdhlibrary_python_sdh_py_details SVN related, detailed file specific information:
#      $LastChangedBy: Osswald2 $
#      $LastChangedDate: 2013-11-27 16:12:49 +0100 (Wed, 27 Nov 2013) $
#      \par SVN file revision:
#        $Id: sdh.py 11045 2013-11-27 15:12:49Z Osswald2 $
#
#  \subsection sdhlibrary_python_sdh_py_changelog Changelog of this file:
#      \include sdh.py.log
#
#######################################################################

#######################################################################
## \anchor sdhlibrary_python_sdh_py_python_vars
#  \name   Python specific variables
#  
#  Some definitions that describe the module for python.
#
#  @{

# pylint: disable-msg=W0622
__doc__       = "python module with end user interface to control a SDH (SCHUNK Dexterous Hand)"
__author__    = "Dirk Osswald: dirk.osswald@de.schunk.com"
__url__       = "http://www.schunk.com"
__version__   = "$Id: sdh.py 11045 2013-11-27 15:12:49Z Osswald2 $"
__copyright__ = "Copyright (c) 2007 SCHUNK GmbH & Co. KG"

## end of doxygen name group sdhlibrary_python_sdh_py_python_vars
#  @}
######################################################################


##########################################################################
# import needed modules:

# standard python modules
import sys, time, math, array

# submodules from this package:
# pylint: disable-msg=W0614,W0401,F0401
from sdhbase   import *
from sdhserial import *
from auxiliary import *
from unit      import *
from . import release

# 
##########################################################################


######################################################################
#


######################################################################
# The actual SDH classes

######################################################################
######################################################################
#    
## \ingroup sdh_library_python_primary_user_interface_classes_group
#  \brief The end user interface class to control a SDH (SCHUNK Dexterous Hand).
#  
#  A general overview of the structure and architecture is given \ref
#  sdhlibrary_python__init__py_package_overview "here".
#
#  \remark
#  \anchor sdhlibrary_python_sdh_py_csdh_axis_vs_fingers
#  - The cSDH class provides methods to access the 7 axes of the SDH
#    individually as well as on a finger level.
#    - When accessing the axes individually then following axis
#      indices must be used to address an axis/ some axes:
#      - 0 : common base axis of finger 0 and 2
#      - 1 : proximal axis of finger 0
#      - 2 : distal axis of finger 0
#      - 3 : proximal axis of finger 1
#      - 4 : distal axis of finger 1
#      - 5 : proximal axis of finger 2
#      - 6 : distal axis of finger 2
#    - When accessing the axes on finger level then every finger has 3
#      axes for a uniform interface of the access methods. Her the
#      following finger axis indices must be used:
#      - 0 : base axis of finger (for finger 1 this is a "virtual" axis with min angle = max angle = 0.0)
#      - 1 : proximal axis of finger 
#      - 2 : distal axis of finger
#  \anchor sdhlibrary_python_sdh_py_csdh_vector
#  - Vector-like parmeters: The interface functions defined here make
#    full use of pythons flexibility. I.E. for parameters of functions
#    like axis indices or axis angles not only single numerical values
#    can be given, but also python-lists, -tuples or -arrays of
#    values. This way the same interface function can address a single
#    axis individually or multiple axes in one call, as required by the
#    application. Such parameters are herein refered to as
#    "vectors". The actual allowed types for such vectors is determined
#    by cSDHBase#vector_types.
#  - Parameters for methods are checked for validity. In case an
#    invalid parameter is given the method raises a
#    cSDHErrorInvalidParameter exception.
#  \anchor sdhlibrary_python_sdh_py_csdh_unit
#  - The underlying physical unit system of parameters that have a
#    unit (like angles, velocities or temperatures) can be adapted to
#    the users or the applications need. See also \ref
#    sdhlibrary_python_unit_py_unit_conversion_objects "unit conversion
#    objects". The default converter objects are set as the uc_*
#    member variables (#uc_angle, #uc_angular_velocity, #uc_angular_acceleration, #uc_time,
#    #uc_temperature, #uc_position). The units are changed in the
#    communication between user application and Python import module
#    only (USERAPP.py and sdh.py in the \ref
#    sdhlibrary_python__init__py_sdhpackage_overview "overview
#    figure"). For now the SDH firmware knows only about its internal unit
#    system.
#    
#  <hr>
class cSDH( cSDHBase ):
    '''
    The actual class to control the SCHUNK Dexterous Hand. See
    html/pdf documentation for details.
    '''

    #-----------------------------------------------------------------
    ## \brief Constructor of cSDH class.
    #  
    #  Creates an new object of type cSDH. One such object is needed
    #  for each SDH that you want to control.  The constructor
    #  initializes internal data structures. A connection the SDH is
    #  \b not yet established, see Open() on how to do that.
    #
    #  After an object is created the user can adjust the unit systems
    #  used to set/report parameters to/from SDH. This is shown in the
    #  example code below. The default units used (if not overwritten
    #  by \a options) are:
    #  - \c degrees for (axis) angles
    #  - \c degrees \c per \c second for (axis) angular velocities
    #  - \c seconds for times
    #  - \c degrees \c celsius for temperatures
    #
    #  \param self    - reference to the object itself
    #  \param options - a collection of additional settings, like returned e.g. from cSDHOptionParser.parse_args()
    #  - Settings used by the base class cSDHBase:
    #    - \c "debug_level" :   The level of debug messages to print
    #                           - 0: (default) no messages
    #                           - 1: messages of this cSDH instance
    #                           - 2: like 1 plus messages of the inner cSDHSerial instance
    #  - Settings used by the interface class cSDHSerial:                             
    #    - \c "port" :          if set, then it is used as the port numter or device name of
    #                           the serial port to use. The default
    #                           value port=0 refers to 'COM1' in Windows and
    #                           to the corresponding '/dev/ttyS0' in Linux.
    #    - \c "timeout" :       the timeout to use:
    #                           - None : wait forever
    #                           - T    : wait for T seconds (float accepted)                   
    #  - Settings used by this cSDH class only:
    #    - \c "use_radians" :   Flag, if True then use radians and radians/second
    #                           to set/report (axis) angles and angular velocities
    #                           instead of default degrees and degrees/s
    #    - \c "use_fahrenheit": Flag, if True then use degrees fahrenheit
    #                           to report temperatures instead of default degrees celsius
    #
    #
    #  \par Examples:
    #
    #  Common use:
    #  \code
    #    # Import the sdh.py python import module:
    #    import sdh
    #  
    #    # Create a cSDH object 'hand'. This calls the constructor sdh.cSDH.__init__():
    #    hand = sdh.cSDH()
    #  \endcode
    #
    #  The mentioned change of a unit system can be done like this:
    #  \code
    #    # Assuming 'hand' is a sdh.cSDH object ...
    #  
    #    # override default unit converter for (axis) angles: 
    #    hand.uc_angle = sdh.uc_angle_radians
    #
    #    # override default unit converter for (axis) angular velocities:
    #    hand.uc_angular_velocity = sdh.uc_angular_velocity_radians_per_second
    #
    #    # override default unit converter for (axis) angular accelerations:
    #    hand.uc_angular_acceleration = sdh.uc_angular_acceleration_radians_per_second_squared
    #
    #    # instead of the last 3 calls the following shortcut could be used:
    #    hand.UseRadians()
    #    
    #    # override default unit converter for times: 
    #    hand.uc_time  = sdh.uc_time_milliseconds
    #
    #    # override default unit converter for temperatures: 
    #    hand.uc_temperature = sdh.uc_temperature_fahrenheit
    #
    #    # override default unit converter for positions:
    #    hand.uc_position = sdh.uc_position_meter
    #    
    #  \endcode
    #
    #
    #  For convenience the most common settings can be specified as a
    #  dictionary-style parameter \a options for the constructor.
    #
    #  This can be done either manually, like in:
    #  \code
    #    #import the sdh.py python
    #    import module import sdh
    #  
    #    # Create a cSDH object 'hand'
    #    hand = sdh.cSDH( options=dict( port=1, debug_level=2, use_radians=True) )
    #
    #  \endcode
    #
    #  Or for the deluxe, 'all batteries included' variant, the
    #  options can be used automagically from a cSDHOptionParser
    #  object, like in:
    #
    #  \code
    #    #import the sdh.py python
    #    import module import sdh
    #  
    #    # Create an option parser object to parse common command line options:
    #    parser = sdh.cSDHOptionParser( usage    = "Your mighty explanative description",
    #                                   revision = "0.0-pre_alpha" )
    #
    #    # Parse (and handle, if possible) the command line options of the script:
    #    (options, args) = parser.parse_args()
    #  
    #    # Create a cSDH object 'hand' using the parsed options:
    #    hand = sdh.cSDH( options=options.__dict__ )
    #    # (We cannot use options directly, but its __dict__ attribut
    #    # holds the dictionary that the constructor needs)
    #  \endcode
    #
    #  <hr>
    def __init__( self, options=None ):
        '''
        Constructor of cSDH class. See html/pdf documentation for details.
        '''

        #---------------------
        # Option handling: 

        # Set class specific default options:
        default_options = dict( use_radians=False, use_fahrenheit=False, debug_output=sys.stderr )

        # Overwrite class specific defaults with settings from caller, if any:
        if ( options ):   default_options.update( options )
        #---------------------
                    
        # Call base class constructor using default + user options:
        cSDHBase.__init__( self, options=default_options )
        
        self.dbg.PDM( "Debug messages of cSDH are printed like this." )

        #---------------------
        # Initialize unit converters:
        if (self.options[ "use_radians" ]):
            self.UseRadians()
        else:
            self.UseDegrees()

        ## unit convert for times: default = unit#uc_time_seconds
        self.uc_time  = uc_time_seconds

        if (self.options[ "use_fahrenheit" ]):
            self.uc_temperature = uc_temperature_fahrenheit
        else:
            ## unit convert for temperatures: default = unit#uc_temperature_celsius
            self.uc_temperature = uc_temperature_celsius

        ## unit converter for motor curent: default = unit#uc_motor_current_ampere
        self.uc_motor_current = uc_motor_current_ampere
        
        ## unit converter for position: default = unit#uc_position_millimeter
        self.uc_position = uc_position_millimeter
        
        #---------------------

        #---------------------
        # Initialize misc member variables
        
        ## The interface to the SDH hardware:
        self.interface = None

        ## The number of axis per finger (for finger 1 this includes the "virtual" base axis)
        self.NUMBER_OF_AXES_PER_FINGER = 3
        
        ## The number of virtual axes
        self.NUMBER_OF_VIRTUAL_AXES = 1
        
        ## Mapping of finger index to number of real axes of fingers:
        self.finger_number_of_axes = (3,2,3)

        ## Mapping of finger index, finger axis index to axis index:
        self.finger_axis_index     = ((0,1,2), (7, 3,4), (0,5,6))

        ## array of 3 epsilon values
        self.f_eps_a   = array.array( "d",  [ self.eps ]* self.NUMBER_OF_AXES_PER_FINGER )

        ## array of 3 0 values
        self.f_zeros_a = array.array( "d",  [ 0.0 ]* self.NUMBER_OF_AXES_PER_FINGER )

        ## array of 3 1 values
        self.f_ones_a  = array.array( "d",  [ 1.0 ]* self.NUMBER_OF_AXES_PER_FINGER )

        ## Maximum allowed motor currents (in internal units (Ampere)), including the virtual axis
        self.f_max_motor_current_a = array.array( "d",  ([ 1.0 ]*self.NUMBER_OF_AXES) +  ([ 0.0 ]*self.NUMBER_OF_VIRTUAL_AXES))

        ## the motor current can be set specifically for these modes:
        self.eMotorCurrentMode = dict( move=0,
                                       grip=1,
                                       hold=2 )

        ## Minimum allowed axis angles (in internal units (degrees)), including the virtual axis
        self.f_min_angle_a = array.array( "d",  list(self.min_angle_a) + [0.0] )

        ## Maximum allowed axis angles (in internal units (degrees)), including the virtual axis
        self.f_max_angle_a = array.array( "d",  list(self.max_angle_a) + [0.0] )

        ## Maximum allowed axis velocity (in internal units (degrees/second)), including the virtual axis
        #  we cannot read the real limits from the SDH firmware yet, since we are not yet connected
        self.f_max_velocity_a = self.max_angular_velocity_a

        ## Minimum allowed axis velocity (in internal units (degrees/second)), including the virtual axis
        #  we cannot read the real limits from the SDH firmware yet, since we are not yet connected
        self.f_min_velocity_a = self.min_angular_velocity_a

        ## Maximum allowed axis acceleration (in internal units (degrees/second²)), including the virtual axis
        self.f_max_acceleration_a = self.max_angular_acceleration_a
        
        ## Minimum allowed axis acceleration (in internal units (degrees/second²)), including the virtual axis
        self.f_min_acceleration_a = self.min_angular_acceleration_a

        ## Maximum allowed grip velocity (in internal units (degrees/second))
        self.grip_max_velocity = 100.0


        ## \anchor sdhlibrary_python_sdh_py_kinematic_vars
        #  \name   Kinematic parameters of the Hand
        #  
        #  @{

        ## length of limb 1 (proximal joint to distal joint) in mm
        self.l1 = 87.0

        ## length of limb 2 (distal joint to fingertip) in mm
        self.l2 = 70.0

        # distance between center points of base joints f0<->f1, f1<->f2, f0<->f2
        d = 110.0 - 44.8

        # height of center of base joints above finger base plate
        h = 17.0
        
        ## list of xyz-arrays for all fingers with offset from (0,0,0) of proximal joint in mm
        #                                                                       x,       y, z
        self.offset = [ array.array( "d",  [  d/2.0*math.tan( DegToRad(30.0) ),  d/2.0, h ] ), # finger 0
                        array.array( "d",  [ -d/(2.0*math.cos( DegToRad(30.0) )),  0.0, h ] ), # finger 1
                        array.array( "d",  [  d/2.0*math.tan( DegToRad(30.0) ), -d/2.0, h ] )] # finger 2

        ## end of doxygen name group sdhlibrary_python_sdh_py_kinematic_vars
        #  @}
        
        self._last_grip = self.eGraspId["GRIP_INVALID"]
        
        self.controller_type = None
        #---------------------
        

            
    #######################################################################
    ## \anchor sdhlibrary_python_sdh_py_csdh_internal
    #  \name   Internal helper methods
    #  
    #  @{
    
    #-----------------------------------------------------------------
    def _ToIndexList( self, index, all_replacement, maxindex, name="" ):
        '''
        Internal helper function: return a new list of checked indices according to index.
        '''
        if (index == All):
            return all_replacement
        elif (type( index ) in self.vector_types):
            for i in index:
                self.CheckIndex( i, maxindex, name )
            self.CheckRange( len( index ), 1, maxindex, "number of %ss" % name )
            return list(index)
        else:
            self.CheckIndex( index, maxindex, name )
            return [index]


    #-----------------------------------------------------------------
    def _ToValueList( self, value, length, convert ):
        '''
        Internal helper function: return a new list of values according to value and convert().
        '''
        if (type( value ) in self.vector_types):
            return [ convert( v ) for v in value ]
        elif (value is None):
            return [ value ]*length
        else:
            return [ convert( value ) ]*length


    #-----------------------------------------------------------------
    def _GetMotorCurrentModeFunction( self, mode ):
        '''
        Internal helper function: return the get/set function of the
        self.interface object that is responsible for setting/getting
        motor currents in mode 
        '''
        if   ( mode == self.eMotorCurrentMode["move"] ):
            return self.interface.ilim
        elif ( mode == self.eMotorCurrentMode["grip"] ):
            return self.interface.igrip
        elif ( mode == self.eMotorCurrentMode["hold"] ):
            return self.interface.ihold
        else:
            raise cSDHErrorInvalidParameter( "Unknown mode '%s', not in [0..%d]!" % (str(mode), len(self.eMotorCurrentMode)-1) )


    #-----------------------------------------------------------------
    def _AnglesToRad( self, angles_external ):
        '''
        Internal helper function: return the angles_external vector of
        angles given in external units uc_angle, converted to
        radians.
        '''
        if (self.uc_angle != uc_angle_radians):
            # angles is in other units

            # convert to internal (deg)
            angles_deg = [ self.uc_angle.ToInternal(ae) for ae in angles_external ]
            # convert to rad
            angles_rad = [ DegToRad(ad) for ad in angles_deg ]
        else:
            angles_rad = angles_external
            
        return angles_rad


    #-----------------------------------------------------------------
    def _AxisAnglesToFingerAngles( self, a_angles ):
        '''
        Return a list [ f0a, f1a, f2a ] where fia is a list of finger
        angles of finger i from the given axis angles
        '''
        # append virtual axis angles    
        av_angles = a_angles + [ 0.0 ]*self.NUMBER_OF_VIRTUAL_AXES

        fingers_angles = []
        for fi in range( 0, self.NUMBER_OF_FINGERS ):
            f_angles = []
            for fai in range( 0, self.NUMBER_OF_AXES_PER_FINGER ):
                f_angles.append( av_angles[ self.GetFingerAxisIndex( fi, fai ) ] )
            fingers_angles.append( f_angles )
            
        return fingers_angles


    #-----------------------------------------------------------------
    def _GetHandXYZ( self, angles ):
        '''
        return [[x0,y0,z0], [x1,y1,z1], [x2,y2,z2]] positions of fingertips of all fingers at angles fi_angles (rad)
        '''
        f0_angles = [ angles[i]  for i in self.finger_axis_index[0] ]
        f1_angles = [ angles[i]  for i in self.finger_axis_index[1] ]
        f2_angles = [ angles[i]  for i in self.finger_axis_index[2] ]

        return [self._GetFingerXYZ( 0, f0_angles ), # finger 0
                self._GetFingerXYZ( 1, f1_angles ), # finger 1
                self._GetFingerXYZ( 2, f2_angles )] # finger 2


    #-----------------------------------------------------------------
    def _GetFingerXYZ( self, fi, r_angles, proximal=None, distal=None ):
        '''
        return [x,y,z] position in mm of a position proximal mm on the proximal finger
	limb and distal mm on the distal finger limb of finger fi at angles r_angles (rad).
        If proximal/distal is None (default) then the corresponding
        maximum length of the finger limb is used. Therefore if
        proximal and distal are none the xyz position of the finger
        tip is returned.
        '''
        if proximal is None: proximal = self.l1
        if distal is None: distal   = self.l2
        
        s_b  = math.sin( r_angles[1] )
        s_bc = math.sin( r_angles[1] + r_angles[2] )
        l1_s_b_l2_s_bc = (proximal*s_b + distal*s_bc)
        fac_x = [-1.0, 1.0, -1.0]
        fac_y = [-1.0, 1.0,  1.0]
        return [ fac_x[fi] * (l1_s_b_l2_s_bc) * math.cos( r_angles[0] ) + self.offset[ fi ][0], # x
		 fac_y[fi] * (l1_s_b_l2_s_bc) * math.sin( r_angles[0] ) + self.offset[ fi ][1], # y
                 proximal*math.cos( r_angles[1] ) + distal*math.cos( r_angles[1] + r_angles[2] ) + self.offset[ fi][2] ] # z


    #-----------------------------------------------------------------
    def _GetFingerSphereHull( self, fi, r_angles ):
        """
        Return a list of spheres that form an enclosing hull (virtual
        airbag) for finger fi at angles r_angles (rad)
        """
        # number of spheres on proximal / distal finger limb
        n_prox = 6
        n_dist = 4
    
        # diameter of a fingerlimb
        dia = 27 #!!!
    
        result = []

        #-----------
        # proximal limb:
        
        # distance of spheres
        d = self.l1 / n_prox
        # radius of spheres r = math.sqrt( Square( dia/2.0 ) + Square( d/2.0 ) )
        r = math.sqrt( Square( dia/2.0 ) + Square( d/2.0 ) )
        for i in range( 0, n_prox ):
            (x,y,z) = self._GetFingerXYZ( fi, r_angles, d/2.0 + i*d, 0.0 )
            result.append( cSphere( x, y, z, r ) )
        #-----------


        #-----------
        # distal limb:
        ## make the limb slightly longer than in reality
        #d = self.l2 / n_dist
        #r = math.sqrt( Square( dia/2.0 ) + Square( d/2.0 ) )
        #for i in range( 0, n_dist ):
        #    (x,y,z) = self._GetFingerXYZ( fi, r_angles, self.l1, d/2.0 + i*d )
        #    result.append( cSphere( x, y, z, r ) )

        d = self.l2 / n_dist
        r = math.sqrt( Square( dia/2.0 ) + Square( d/2.0 ) )
        for i in range( 0, n_dist ):
            if (i< n_dist-1):
                (x,y,z) = self._GetFingerXYZ( fi, r_angles, self.l1, d/2.0 + i*d )
            else:
                (x,y,z) = self._GetFingerXYZ( fi, r_angles, self.l1, self.l2-r )
            result.append( cSphere( x, y, z, r ) )
        #-----------

        return result

    
    #-----------------------------------------------------------------
    def _GetFingerHullCollision( self, hull_a, hull_b ):
        """
        Return a pair (c,min_dist)
    
        c is a Bool flag and True if any of the spheres in hull_a collides with any of the spheres in hull_b.
        min_dist is the minimum distance of spheres (negative if c is True)
        """
        min_dist = 999999.9
        for sphere_i in hull_a:
            for sphere_j in hull_b:
                dist = sphere_i.Distance( sphere_j )
                min_dist = min( min_dist, dist )
                if  dist < 0.0:
                    return (True, min_dist)
        return (False, min_dist)


    #-----------------------------------------------------------------
    
    ## end of doxygen name group sdhlibrary_python_sdh_py_csdh_internal
    #  @}
    ######################################################################
            
    #######################################################################
    ## \anchor sdhlibrary_python_sdh_py_csdh_misc
    #  \name   Miscellaneous methods
    #  
    #  @{
    
    #-----------------------------------------------------------------
    ## Shortcut to set the unit system to radians
    #
    #  After calling this (axis) angles are set/reported in radians and
    #  angular velocities are set/reported in radians/second
    #
    #  \par Examples:
    #  \code
    #    # Assuming 'hand' is a sdh.cSDH object ...
    #
    #    # make hand object use radians and radians/second for angles and angular velocities
    #    hand.UseRadians()
    #    
    #  \endcode
    #
    #  <hr>
    def UseRadians( self ):
        '''
        Shortcut to set the unit system to radians.
        '''
        # pylint: disable-msg=W0201
        # set unit convert for (axis) angles: 
        self.uc_angle = uc_angle_radians
    
        # set unit convert for (axis) angular velocities:
        self.uc_angular_velocity = uc_angular_velocity_radians_per_second
    
        # set unit convert for (axis) angular accelerations:
        self.uc_angular_acceleration = uc_angular_acceleration_radians_per_second_squared


    #-----------------------------------------------------------------
    ## Shortcut to set the unit system to degrees
    #
    #  After calling this (axis) angles are set/reported in degrees and
    #  angular velocities are set/reported in degrees/second
    #
    #  \par Examples:
    #  \code
    #    # Assuming 'hand' is a sdh.cSDH object ...
    #
    #    # make hand object use degrees and degrees/second for angles and angular velocities
    #    hand.UseDegrees()
    #    # as degrees, degrees/second are the default this is needed only if the
    #    # unit system was changed before
    #    
    #  \endcode
    #
    #  <hr>
    def UseDegrees( self ):
        '''
        Shortcut to set the unit system to degrees.
        '''
        ## unit convert for (axis) angles: default = unit#uc_angle_degrees
        self.uc_angle = uc_angle_degrees
        ## unit convert for (axis) angular velocities: default = unit#uc_angular_velocity_degrees_per_second
        self.uc_angular_velocity = uc_angular_velocity_degrees_per_second
        ## unit convert for (axis) angular accelerations: default = unit#uc_angular_acceleration_degrees_per_second_squared
        self.uc_angular_acceleration = uc_angular_acceleration_degrees_per_second_squared


    #-----------------------------------------------------------------
    ## Return the number of real axes of finger with index \a iFinger.
    #
    #  \param self    - reference to the object itself
    #  \param iFinger - index of finger in range [0..NUMBER_OF_FINGERS-1]
    #
    #  \return number of real axes of finger with index \a iFinger
    #      
    #  \par Examples:
    #  \code
    #    # Assuming 'hand' is a sdh.cSDH object ...
    #
    #    print "The finger 0 has %d real axes" % ( hand.GetFingerNumberOfAxes( 0 ) )
    #    
    #  \endcode
    #
    #  <hr>
    def GetFingerNumberOfAxes( self, iFinger ):
        '''
        Return the number of axes of finger with index iFinger.
        '''
        return self.finger_number_of_axes[iFinger]


    #-----------------------------------------------------------------
    ## Return axis index of \a iFingerAxis axis of finger with index iFinger
    #
    #  For \a iFinger=2, iFingerAxis=0 this will return the index of
    #  the virtual base axis of the finger
    #
    #  \param self    - reference to the object itself
    #  \param iFinger - index of finger in range [0..NUMBER_OF_FINGERS-1]
    #  \param iFingerAxis - index of finger axis in range [0..NUMBER_OF_AXES_PER_FINGER-1]
    #
    #  \return axis index of \a iFingerAxis-th axis of finger with index \a iFinger
    #
    #  \par Examples:
    #  \code
    #    # Assuming 'hand' is a sdh.cSDH object ...
    #
    #    print "The 1st axis of finger 2 has real axis index %d" % ( hand.GetFingerNumberOfAxes( 2, 0 ) )
    #    
    #  \endcode
    #
    #  <hr>
    def GetFingerAxisIndex( self, iFinger, iFingerAxis ):
        '''
        Return axis index of iFingerAxis axis of finger with index iFinger
        '''
        return self.finger_axis_index[ iFinger ][ iFingerAxis ]


    #-----------------------------------------------------------------
    ## Return the actual release of the firmware of the %SDH (not the library) as string.
    #
    #  This will throw a cSDHErrorCommunication exception if the
    #  connection to the %SDH is not yet opened.
    #
    #   \par Examples:
    #   \code
    #     # Assuming 'hand' is a sdh.cSDH object ...
    #     
    #     print "The SDH firmware reports release ", hand.GetFirmwareRelease()
    #
    #   \endcode
    #
    #   \see See GetFirmwareReleaseRecommended() to get the actual release of the SDH firmware
    #   <hr>
    def GetFirmwareRelease( self ):
        if ( not self.IsOpen() ):
            raise cSDHErrorCommunication( "No connection to SDH" )
        
        return self.GetInfo( "release-firmware" )

    #-----------------------------------------------------------------
    ## Return the recommended release of the firmware of the %SDH by this library as string.
    #
    #   \par Examples:
    #   \code
    #     # Assuming 'hand' is a sdh.cSDH object ...
    #     
    #     print "This SDHLibrary recommends an SDH firmware release", hand.GetFirmwareReleaseRecommended()
    #
    #   \endcode
    #
    #   \see See GetFirmwareRelease() to get the actual release of the SDH firmware
    #   <hr>
    @staticmethod
    def GetFirmwareReleaseRecommended():
        return release.FIRMWARE_RELEASE_RECOMMENDED;


    #-----------------------------------------------------------------
    ## Check the actual release of the firmware of the connected %SDH against the
    #  recommended firmware release.
    #  \return true - if the actual firmware is the recommended one
    #          false - the actual firmware is NOT the recommended one (communication with the SDH might not work as expected)
    #
    #  This will throw a (cSDHErrorCommunication*) exception if the
    #  connection to the %SDH is not yet opened.
    #
    #   \par Examples:
    #   \code
    #     // Assuming 'hand' is a cSDH object ...
    #
    #     if ( hand.CheckFirmwareRelease() )
    #     {
    #         cout << "The firmware release of the connected SDH is the one recommended by this SDHLibrary\n";
    #     }
    #     else
    #     {
    #         cout << "The firmware release of the connected SDH is NOT the one recommended by this SDHLibrary\n";
    #         cout << "  Actual SDH firmware release      " << hand.GetFirmwareRelease() << "\n";
    #         cout << "  Recommended SDH firmware release " << hand.GetFirmwareReleaseRecommended() << "\n";
    #     }
    #
    #   \endcode
    #
    #   \see See GetFirmwareReleaseRecommended() to get the recommended SDH firmware release.
    #   <hr>
    def CheckFirmwareRelease( self ):
        return (self.GetInfo("release-firmware") == self.GetFirmwareReleaseRecommended())


    #-----------------------------------------------------------------
    ## Return info according to \a what
    #
    #  The following values are valid for \a what:
    #  - "date-library"     : date of the SDHLibrary-python release   
    #  - "release-library"  : release name of the sdh.py python module
    #  - "release-firmware" : release name of the SDH firmware (requires
    #                         an opened communication to the SDH)
    #  - "release-firmware-recommended" : recommended release name of the %SDH
    #                         firmware
    #  - "date-firmware"    : date of the SDH firmware (requires
    #                         an opened communication to the SDH)
    #  - "release-soc"      : release name of the SDH SoC (requires
    #                         an opened communication to the SDH)
    #  - "date-soc"         : date of the SDH SoC (requires
    #                         an opened communication to the SDH)
    #  - "id-sdh"           : ID of SDH
    #  - "sn-sdh"           : Serial number of SDH
    #
    #  \par Examples:
    #  \code
    #    # Assuming 'hand' is a sdh.cSDH object ...
    #
    #    print "The SDH firmware reports release %s" % ( hand.GetInfo( "release-firmware" ) )
    #    
    #  \endcode
    #
    #  <hr>
    def GetInfo( self, what ):
        '''
        Return info according to \a what. See html/pdf documentation for details.
        '''
        self.dbg.PDM( "GetInfo: %s is requested" % what )
        
        if ( what in ("release", "release-library") ):
            return release.PROJECT_RELEASE
        if ( what in ("date", "date-library") ):
            return release.PROJECT_DATE
        if ( what in ("release-firmware-recommended",) ):
            return self.GetFirmwareReleaseRecommended()

        if ( not self.interface ):
            raise cSDHErrorCommunication("Interface is not open")

        if ( what in ("release-firmware") ):
            return self.interface.ver()
        if ( what in ("date-firmware") ):
            return self.interface.ver_date()
        if ( what in ("release-soc") ):
            return self.interface.soc()
        if ( what in ("date-soc") ):
            return self.interface.soc_date()
        if ( what in ("date-soc") ):
            return self.interface.soc_date()
        if ( what in ("id-sdh") ):
            return self.interface.id()
        if ( what in ("sn-sdh") ):
            return self.interface.sn()


    #-----------------------------------------------------------------
    ## Return temperature(s) measured within the SDH
    #
    #  \param self    - reference to the object itself
    #  \param iSensor - index of temperature sensor to access.
    #                  This can be All, a single index or a \ref sdhlibrary_python_sdh_py_csdh_vector "vector" of indices.
    #                  - index 0 is sensor near motor of axis 0 (root)
    #                  - index 1 is sensor near motor of axis 1 (proximal finger 1)
    #                  - index 2 is sensor near motor of axis 2 (distal finger 1)
    #                  - index 3 is sensor near motor of axis 3 (proximal finger 2)
    #                  - index 4 is sensor near motor of axis 4 (distal finger 2)
    #                  - index 5 is sensor near motor of axis 5 (proximal finger 3)
    #                  - index 6 is sensor near motor of axis 6 (distal finger 3)
    #                  - index 7 is FPGA temperature (controller chip)
    #                  - index 8 is PCB temperature (Printed Circuit Board)
    #
    #  \return
    #    The temperature(s) returned are reported in the configured
    #    temperature unit system #uc_temperature.
    #    - if iSensor is a single index then a single float value is returned
    #    - else a list of the selected sensor values is returned
    #                  
    #  \par Examples:
    #  \code
    #    # Assuming 'hand' is a sdh.cSDH object ...
    #    
    #    # Get measured values of all sensors
    #    temps = hand.GetTemperature()
    #    # Now temps is something like [ 38.500,37.250,35.750,37.250,33.500,36.500,32.250,59.625,52.500 ]
    #
    #    # Get controller temperature only:
    #    temp_controller = hand.GetTemperature( 0 )
    #    # Now temp_controller is something like 38.5
    #    
    #    # If we - for some obscure islandish reason - would want
    #    # temperatures reported in degrees fahrenheit, the unit
    #    # converter can be changed:
    #    hand.uc_temperature = sdh.uc_temperature_fahrenheit
    #
    #    # Get all temperaturs again:
    #    temps_f = hand.GetTemperature() 
    #    # Now temps_f is something like [ 100.0, 96.8, 92.3, 97.7, 91.8, 96.8, 90.1,  137.5,  125.2]
    #
    #  \endcode
    #
    #  <hr>
    def GetTemperature( self, iSensor = All ):
        '''
        Return temperature(s) measured within the SDH. See html/pdf documentation for details.
        '''
        sensors = self._ToIndexList( iSensor, range( 0, self.NUMBER_OF_TEMPERATURE_SENSORS ), self.NUMBER_OF_TEMPERATURE_SENSORS, "temperature sensor" )
        
        temperatures = self.interface.temp()

        if (type(iSensor) == int):
            return self.uc_temperature.ToExternal( temperatures[ iSensor ] )
        else:
            return [ self.uc_temperature.ToExternal( temperatures[ i ] )   for i in sensors ]


    ####
    # unimplemented from SAH:
    # def GetTipTemp( self, int iFinger,float* pfTipTemp):
    # def GetFingerTemp( self, int iFinger,float* pfFingerTemp):
    # def GetPalmTemp( self, float* pfPalmTemp):
                
    #  end of doxygen name group sdhlibrary_python_sdh_py_csdh_common
    ## @}
    ######################################################################
        
    #######################################################################
    ## \anchor sdhlibrary_python_sdh_py_csdh_communication
    #  \name   Communication methods
    #  
    #  @{
    
    #-----------------------------------------------------------------
    ## Open connection to SDH according to \a options.
    #  
    #  \param self    - reference to the object itself
    #  \param options - a collection of additional settings, like returned e.g. from cSDHOptionParser.parse_args()
    #  - Settings used by the base class cSDHBase:
    #    - \c "debug_level" :   The level of debug messages to print
    #                           - 0: (default) no messages
    #                           - 1: messages of the internal cSDHSerial instance
    #  - Settings used by the internal cSDHSerial instance:                             
    #    - \c "port" :          if set, then it is used as the port number or the device name of
    #                           the serial port to use. The default
    #                           value port=0 refers to 'COM1' in Windows and
    #                           to the corresponding '/dev/ttyS0' in Linux.
    #    - \c "timeout" :       the timeout to use:
    #                           - None : wait forever
    #                           - T    : wait for T seconds (float accepted)                   
    #  
    #  \par Examples:
    #  \code
    #    # Assuming 'hand' is a sdh.cSDH object ...
    #  
    #    # Open connection to SDH according to options given to constructor:
    #    hand.Open()
    #
    #    # Or use a different RS232 port 2 = COM3:
    #    hand.Open( options=dict( port=2 ) )
    #  
    #    # Or use settings from the command line:
    #    parser = sdh.cSDHOptionParser( usage    =  "YOUR PROGRAM DESCRIPTION HERE" + "\nusage: %prog [options]",
    #                                   revision =  "YOUR PROGRAM VERSION HERE" )
    #    (options, args) = parser.parse_args()
    #    hand.Open( options=options )
    #  
    #  \endcode
    #
    #  <hr>
    def Open( self, options=None ):
        '''
        Open communication to the SDH according to options. See html/pdf documentation for details.
        '''
    
        #---------------------
        # Option handling: 

        # Make a copy of our own options as default:
        default_options = dict(self.options)

        # and reduce debug_level by one
        default_options["debug_level"] -= 1

        # Overwrite the defaults with the now given settings from caller, if any:
        if ( options ):   default_options.update( options )
        #---------------------

        #---------------------
        # Try to create a cSDHSerial object and save as member interface:
        try:
            self.interface = cSDHSerial( options=default_options )

        except serial.SerialException,e:
            raise cSDHErrorCommunication("%s. Could not open communication interface %s." % (str(e), GetCommunicationInterfaceName( default_options ) ))
        self.dbg.PDM("cSDH.Open() successfully opened communication via %s.\n" % (GetCommunicationInterfaceName( default_options )))
        
        self._UpdateSettingsFromSDH()


    def OpenRS232( self, options=None ):
        '''Alias for Open() function for compatibility reasons. 
        Deprecated, use Open() instead.
        '''
        self.Open( options )
        
    #-----------------------------------------------------------------
    ## Close connection to SDH.
    #
    #  The default behaviour is to \b not leave the controllers of the
    #  SDH enabled (to prevent overheating). To keep the controllers
    #  enabled (e.g. to keep the finger axes actively in position) set
    #  \a leave_enabled to True. Only already enabled axes will be
    #  left enabled.
    #
    #  \param self          - reference to the object itself
    #  \param leave_enabled - Flag: True to leave the controllers on,
    #                         False (default) to disable the
    #                         controllers (switch powerless)
    #
    #  \par Examples:
    #  \code
    #    # Assuming 'hand' is a sdh.cSDH object ...
    #  
    #    # Close connection to SDH, power off controllers:
    #    hand.Close()
    #
    #    # To leave the already enabled controllers enabled:
    #    hand.Close( True )
    #  
    #  \endcode
    #
    #  <hr>
    def Close( self, leave_enabled=False ):
        '''
        Close connection to SDH.
        '''
        if self.interface:
            if not leave_enabled:
                self.interface.power( flag=False )

            self.interface.Close()
        else:
            sys.stderr.write( "Warning cannot Close() not opened connection! Ignored.\n" )
            
        self.interface = None
    
    def IsOpen( self ):
        '''
        return wether the communication to the sdh is open or not
        '''
        return self.interface is not None
            
    #  end of doxygen name group sdhlibrary_python_sdh_py_csdh_communication
    ## @}
    ######################################################################
        
    #######################################################################
    ## \anchor sdhlibrary_python_sdh_py_csdh_auxilliary
    #  \name   Auxiliary movement methods
    #  
    #  @{
    
    #-----------------------------------------------------------------
    ## Stop movement of all axes of the SDH and switch off the controllers
    #
    #  This command will always be executed sequentially: it will return
    #  only after the SDH has performed and confirmed the fast stop.
    #  
    #  \bug
    #  For now this will \b NOT work while a GripHand() command is
    #  executing, even if that was initiated non-sequentially!
    #
    #  \par Examples:
    #  \code
    #    # Assuming 'hand' is a sdh.cSDH object ...
    #  
    #    # Perform an fast stop:
    #    hand.FastStop()
    #  
    #  \endcode
    #
    #  <hr>
    def FastStop( self ):
        '''
        Stop movement of all axes of the SDH and switch off the controllers. See html/pdf documentation for details.
        '''
        # switch off controllers 
        self.interface.power( All, False )

        # save current actual axis angles as new target axis angles
        angles = self.interface.pos( All )
        angles = ToRange_a( angles, self.min_angle_a, self.max_angle_a )
        self.interface.p( All, angles )

    #-----------------------------------------------------------------
    ## Stop movement of all axes but keep controllers on
    #
    #  This command will always be executed sequentially: it will return
    #  only after the SDH has performed and confirmed the stop
    #  
    #  \bug
    #  For now this will \b NOT work while a GripHand() command is
    #  executing, even if that was initiated non-sequentially!
    #
    #  \bug
    #  With SDH firmware < 0.0.2.7 this made the axis jerk in eCT_POSE controller type.
    #  <br><b>=> Resolved in SDH firmware 0.0.2.7</b>
    #
    #  \par Examples:
    #  \code
    #    # Assuming 'hand' is a sdh.cSDH object ...
    #  
    #    # Perform a stop:
    #    hand.Stop()
    #  
    #  \endcode
    #
    #  <hr>
    def Stop( self ):
        '''
        Stop movement of all axes of the SDH. See html/pdf documentation for details.
        '''
        self.interface.stop()

    #-----------------------------------------------------------------
    #-----------------------------------------------------------------
    # unimplemented from SAH:
    # def GetFastStop( self, int* piBrakeState):

    #-----------------------------------------------------------------
    ## Set the type of axis controller to be used in the SDH
    #
    #  With SDH firmware >= 0.0.2.7 this will automatically set valid
    #  default values for all target velocities, accelerations and positions
    #  in the firmware, according to the \a controller type:
    #  - eCT_POSE:
    #    - target velocities will be set to default (40 deg/s)
    #    - target accelerations will be set to default (100 deg/(s*s))
    #    - target positions will be set to default (0.0 deg)
    #  - eCT_VELOCITY:
    #    - target velocities will be set to default (0 deg/s)
    #  - eCT_VELOCITY_ACCELERATION:
    #    - target velocities will be set to default (0 deg/s)
    #    - target accelerations will be set to default (100 deg/(s*s))
    #
    #  This will also adjust the lower limits of the allowed velocities
    #  here in the SDHLibrary, since the eCT_POSE controller allows only
    #  positive velocities while the eCT_VELOCITY and
    #  eCT_VELOCITY_ACCELERATION controllers require also negative
    #   velocities.
    #
    #  \param self       - reference to the object itself
    #  \param controller - identifier of controller to set. Valid
    #                      values are defined in self.eControllerType
    #  
    #  \attention The availability of a controller type depends on the 
    #     SDH firmware of the attached SDH and is checked here.
    #     - firmware <= 0.0.2.5: only eCT_POSE
    #     - firmware >= 0.0.2.6: eCT_POSE, eCT_VELOCITY, eCT_VELOCITY_ACCELERATION
    # 
    #  \par Examples:
    #  \code
    #    # Assuming 'hand' is a sdh.cSDH object ...
    #  
    #    # Set the default coordinated position controller in the SDH:
    #    # (see e.g. demo-simple.cpp, demo-simple2.cpp, demo-simple3.cpp for further examples)
    #    hand.SetController( hand.eControllerType.eCT_POSE )
    #
    #    # Set the velocity controller in the SDH:
    #    hand.SetController( hand.eControllerType.eCT_VELOCITY )
    #
    #    # Or set the velocity controller using a string parameter:
    #    # (see e.g. demo-velocity-acceleration.cpp for further examples)    
    #    hand.SetController( "eCT_VELOCITY_ACCELERATION" )
    #
    #  \endcode
    #
    #  <hr>
    def SetController( self, controller ):
        '''
        Set the type of axis controller to be used in the SDH. See html/pdf documentation for details.
        '''
        if ( type( controller ) == str ):
            controller = self.eControllerType[ controller ]
        
        if (controller not in self.eControllerType.values() ):
            raise cSDHErrorInvalidParameter( "Invalid controller type %s" % repr(controller) )
            
        if ( controller != self.eControllerType["eCT_POSE"] and CompareReleases( self.release_firmware, "0.0.2.6" ) < 0 ):
            raise cSDHErrorInvalidParameter( "controller type %s not available in SDH firmware %s of currently attached SDH" % (repr(controller), self.release_firmware) )

        if ( controller == self.eControllerType["eCT_POSE"] and CompareReleases( self.release_firmware, "0.0.2.6" ) < 0 ):
            # nothing more to do here: for SDH firmwares prior to 0.0.2.6 the controller is fixed to eCT_POSE anyway
            # (and setting the controller would yield an error from the SDH firmware (unknown command))
            self.controller_type = controller
        else:
            self.controller_type = self.interface.con( controller )
        
        self._AdjustLimits( self.controller_type )
        return self.controller_type
        
    #-----------------------------------------------------------------
    ## Get the type of axis controller used in the SDH
    #
    #  The currently set controller type will be queried and returned
    #  (One of self.eControllerType) 
    #  
    #  \par Examples:
    #  \code
    #    # Assuming 'hand' is a sdh.cSDH object ...
    #  
    #    # Get the controller type of the attached SDH:
    #    ct = hand.GetController()
    #
    #    # Print result, numerically and symbolically
    #    print "Currently the axis controller type is set to %d (%s)" % (ct, [ v for (k,v) in hand.eControllerType.iteritems() if v == ct ][0])
    #  \endcode
    #
    #  <hr>
    def GetController( self ):
        '''
        Get the type of axis controller used in the SDH. See html/pdf documentation for details.
        '''
        if ( CompareReleases( self.release_firmware, "0.0.2.6" ) < 0.0 ):
            # cannot read controller in firmwares prior to 0.0.2.6 where controller is fixed to POSE
            self.controller_type = self.eControllerType["eCT_POSE"]
        else:
            # read the real controller from the SDH
            self.controller_type = self.interface.con()
             
        return self.controller_type
       

    #-----------------------------------------------------------------
    ## Set the type of velocity profile to be used in the SDH
    #
    #  \param self             - reference to the object itself
    #  \param velocity_profile - Name or number of velocity profile to set. Valid
    #                            values are defined in self.eVelocityProfileType
    #
    #                            
    #  \par Examples:
    #  \code
    #    # Assuming 'hand' is a sdh.cSDH object ...
    #  
    #    # Set the sin square velocity profile in the SDH:
    #    hand.SetVelocityProfile( hand.eVelocityProfile.eVP_SIN_SQUARE )
    #
    #    # Or else set the ramp velocity profile in the SDH:
    #    hand.SetVelocityProfile( hand.eVelocityProfile.eVP_RAMP )
    #
    #    # Or else set the ramp velocity profile using a string:
    #    hand.SetVelocityProfile( "eVP_RAMP" )
    #  \endcode
    #
    #  <hr>
    def SetVelocityProfile( self, velocity_profile ):
        '''
        Set the type of velocity profile to be used in the SDH. See html/pdf documentation for details.
        '''
        if ( type( velocity_profile ) == str ):
            velocity_profile = self.eVelocityProfile[ velocity_profile ]

        if (velocity_profile not in self.eVelocityProfile.values() ):
            raise cSDHErrorInvalidParameter( "Invalid velocity profile %s" % repr(velocity_profile) )

        return self.interface.vp( velocity_profile )


    #-----------------------------------------------------------------
    ## Get the type of velocity profile used in the SDH
    #
    #  \return the currently set velocity profile as integer, see self.eVelocityProfileType
    #
    #                            
    #  \par Examples:
    #  \code
    #    # Assuming 'hand' is a sdh.cSDH object ...
    #  
    #    # Get the velocity profile from the SDH:
    #    velocity_profile = hand.GetVelocityProfile()
    #    # now velocity_profile is something like
    #    # - self.eVelocityProfile["eVP_SIN_SQUARE"] == 0
    #    # - or self.eVelocityProfile["eVP_RAMP"] == 1
    #
    #  \endcode
    #
    #  <hr>
    def GetVelocityProfile( self ):
        '''
        Get the type of velocity profile used in the SDH. See html/pdf documentation for details.
        '''

        return self.interface.vp()

    #  end of doxygen name group sdhlibrary_python_sdh_py_csdh_auxilliary
    ## @}
    ######################################################################


    #######################################################################
    ## \anchor sdhlibrary_python_sdh_py_csdh_axis
    #  \name   Methods to access SDH on axis-level
    #  
    #  @{

    #-----------------------------------------------------------------
    ## Set the maximum allowed motor current(s) for axis(axes).
    #
    #  The maximum allowed motor currents are stored in the SDH.
    #  The motor currents can be stored:
    #  - axis specific
    #  - mode specific (see eMotorCurrentMode):
    #    - move : (default) The motor currents used while "moving" with a MoveHand() or MoveFinger() command
    #             (These will be overwritten by the "hold" motor currents after a GripHand() command
    #    - grip : The motor currents used while "gripping" with a GripHand() command
    #    - hold : The motor currents used after "gripping" with a GripHand() command (i.e. "holding")
    #    
    #  \param self          - reference to the object itself
    #  \param iAxis -         index of axis to access.
    #                         This can be All, a single index or a \ref sdhlibrary_python_sdh_py_csdh_vector "vector" of indices.
    #  \param motor_current - the motor current to set or \c None to keep the currently set axis motor current.
    #                         This can be a single number or a \ref sdhlibrary_python_sdh_py_csdh_vector "vector" of numbers.
    #                         The value(s) are expected in the configured motor current unit system #uc_motor_current.
    #  \param mode          - the mode to set the maximum motor current for. One of the eMotorCurrentMode modes
    #  
    #  \remark
    #    - If both \a iAxis and \a motor_current are vectors then the order of
    #      their elements must match, i.e. \c motor_current[i] will be applied
    #      to axis \c iAxis[i] (not axis \c i)
    #    - If \a iAxis is \c All then the order will be the natural
    #      one (as if \a iAxis=[0,1,2,3,4,5,6] had been given).
    # 
    #  \par Examples:
    #  \code
    #    # Assuming "hand" is a sdh.cSDH object ...
    #    
    #    # Set maximum allowed motor current of axis 3 to 0.75 A in mode "move":
    #    hand.SetAxisMotorCurrent( 3, 0.75, hand.eMotorCurrentMode["move"] )
    #
    #    # Set maximum allowed motor current of axis 3 to 0.75 A and axis 5 to 0.5 A in mode "grip":
    #    hand.SetAxisMotorCurrent( [3,5], [0.75, 0.5], hand.eMotorCurrentMode["grip"]  )
    #
    #    # Set maximum allowed motor current of all axes to 1.0 A in mode "hold":
    #    hand.SetAxisMotorCurrent( sdh.All, 1.0, hand.eMotorCurrentMode["hold"]   )
    #
    #    # Set maximum allowed motor current of all axes to the given values in mode "move"::
    #    hand.SetAxisMotorCurrent( motor_current=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6 ] )
    #  
    #    # Set maximum allowed motor current of all axes in mode "move" to the current axis motor currents in mode "move":
    #    hand.SetAxisMotorCurrent( motor_current=None )
    #  
    #    # Set maximum allowed motor current of axis 3 to 0.9 A and axis 1 to its current motor current, all in mode "hold" 
    #    hand.SetAxisMotorCurrent( [3,1], motor_current=[1.0,None], hand.eMotorCurrentMode["hold"] )
    #  \endcode
    #  
    #  <hr>
    def SetAxisMotorCurrent( self, iAxis=All, motor_current=None, mode=0 ):
        '''
        Set the maximum allowed motor current(s) for axis(axes)
        '''
        axes = self._ToIndexList( iAxis, self.all_axes, self.NUMBER_OF_AXES + self.NUMBER_OF_VIRTUAL_AXES, "axis" )
        # now axes is a list of all axis indices to access

        n = len(axes)
        motor_currents = self._ToValueList( motor_current, n, self.uc_motor_current.ToInternal )
        # now motor_currents is a list of all axis motor currents in internal unit
        # system (or None to set current actual axis motor current)

        if (n != len(motor_currents)):
            raise cSDHErrorInvalidParameter( "Lengths of iAxis and motor_current vectors do not match (%d != %d)" % (n, len(motor_currents)) )

        # ??? the motor_currents are not checked here

        base_function = self._GetMotorCurrentModeFunction( mode )
        
        # get current motor current for those axes where the motor_current is None
        c_motor_current = None
        for (ai,c) in zip( axes, motor_currents ):
            if (ai >= self.NUMBER_OF_AXES):    # handle virutal axes differently
                if (c is not None):
                    self.CheckRange(c, 0.0, self.f_max_motor_current_a[ai], "virtual axis %d motor_current" % ai )
                continue

            if (c is None):
                if (c_motor_current is None):
                    c_motor_current = base_function( All )
                c = c_motor_current[ ai ]
            # now c is the maximum allowed motor current to set

            # and send to firmware
            base_function( ai, c ) # ANOTE: communicates more often than strictly necessary
        
    #-----------------------------------------------------------------
    ## Get the maximum allowed motor current(s) of axis(axes).
    #
    #  The maximum allowed motor currents are read from the SDH.
    #  The motor currents are stored:
    #  - axis specific
    #  - mode specific (see eMotorCurrentMode):
    #  
    #  \param self  - reference to the object itself
    #  \param iAxis - index of axis to access.
    #                 This can be All, a single index or a \ref sdhlibrary_python_sdh_py_csdh_vector "vector" of indices.
    #  \param mode  - move (default): The motor currents used while "moving" with a MoveHand() or MoveFinger() command
    #               - grip : The motor currents used while "gripping" with a GripHand() command
    #               - hold : The motor currents used after "gripping" with a GripHand() command (i.e. "holding")
              
    #
    #  \return
    #    - if \a iAxis is a single index then a single float value is returned
    #    - else a list of the selected axes maximum allowed motor currents is returned
    #    - The value(s) are returned in the configured motor current unit system #uc_motor_current.
    #
    #  \remark
    #    - The order of the returned list (if any) depends on the
    #      order of the axis indices given in \a iAxis. I.E. if a list
    #      \c rc is returned, then \c rc[i] will be the maximum allowed motor current of axis
    #      \a iAxis[i] (not axis \c i).
    #    - If \a iAxis is \c All then the order will be the natural
    #      one (as if \a iAxis=[0,1,2,3,4,5,6] had been given).
    #    
    #
    #  \par Examples:
    #  \code
    #    # Assuming "hand" is a sdh.cSDH object ...
    #    
    #    # Get maximum allowed motor current of axis 3 in mode "move"
    #    v = hand.GetAxisMotorCurrent( 3, hand.eMotorCurrentMode["move"] )
    #    # v is now something like 0.75
    #
    #    # Get maximum allowed motor current of axis 3 in mode "move"
    #    L = hand.GetAxisMotorCurrent( [3] )
    #    # now L is something like [0.75]
    #    #   (if a vector is given as parameter then a list is returned,
    #    #    even if it contains a single element only)
    #
    #    # Get maximum allowed motor current of axis 3 and 5 in mode "grip"
    #    L = hand.GetAxisMotorCurrent( [3,5], hand.eMotorCurrentMode["grip"] )
    #    # now L is something like [0.5,0.5]
    #
    #    # Get maximum allowed motor current of all axes
    #    L = hand.GetAxisMotorCurrent( sdh.All )
    #    # now L is something like [0.1, 0.2, 0.3, 0.4, 0.5, 0,6, 0.7]
    #
    #  \endcode
    #  
    #  <hr>
    def GetAxisMotorCurrent( self, iAxis=All, mode=0 ):
        '''
        Get the maximum allowed motor current(s) of axis(axes)
        '''
        axes = self._ToIndexList( iAxis, self.all_axes, self.NUMBER_OF_AXES + self.NUMBER_OF_VIRTUAL_AXES, "axis" )
        # now axes is a list of all axis indices to access

        base_function = self._GetMotorCurrentModeFunction( mode )
        

        if (type(iAxis) == int):
            return self.uc_motor_current.ToExternal( base_function( iAxis, None ) )
        else:
            # we want a list of (most likely) more than one motor current, so 
            # read all motor currents at once to communicate as few as possible
            all_motor_currents = base_function( All, None )

            # append motor current 0.0 for all virtual axes 
            all_motor_currents += [ 0.0 ]*self.NUMBER_OF_VIRTUAL_AXES

            return [ self.uc_motor_current.ToExternal( all_motor_currents[ ai ] )   for ai in axes ]

   
    #-----------------------------------------------------------------
    ## Set enabled/disabled state of axis controller(s).
    #
    #  The controllers of the selected axes are enabled/disabled in
    #  the SDH.
    #    
    #  \param self  - reference to the object itself
    #  \param iAxis - index of axis to access.
    #                 This can be All, a single index or a \ref sdhlibrary_python_sdh_py_csdh_vector "vector" of indices.
    #  \param state - flag: the enabled/disabled state to set
    #                 This can be a single number/bool or a \ref sdhlibrary_python_sdh_py_csdh_vector "vector" of numbers/bools.
    #  
    #  \remark
    #    - Only enabled axes can move.
    #    - Disabled axes are not powered and thus might not remain
    #      in their current position due to gravity, inertia or other
    #      external influences.
    #    - If both \a iAxis and \a state are vectors then the order of
    #      their elements must match, i.e. \c state[i] will be applied
    #      to axis \c iAxis[i] (not axis \c i).
    #
    #  \par Examples:
    #  \code
    #    # Assuming 'hand' is a sdh.cSDH object ...
    #    
    #    # Enable all axes:
    #    hand.SetAxisEnable( sdh.All, True )
    #    
    #    # Disable all axes:
    #    hand.SetAxisEnable( state = 0 )
    #    
    #    # Enable axis 0 and 2 while disabling axis 4:
    #    hand.SetAxisEnable( [0,2,4], (True,1,False) )
    #
    #    # Enable axis 0:
    #    hand.SetAxisEnable( 0 )
    #  \endcode
    #  
    #  <hr>
    def SetAxisEnable( self, iAxis=All, state=True ):
        '''
        Set enabled/disabled state of axis/axes. See html/pdf documentation for details.
        '''
        axes = self._ToIndexList( iAxis, self.all_axes, self.NUMBER_OF_AXES + self.NUMBER_OF_VIRTUAL_AXES, "axis" )
        # now axes is a list of all axis indices to access

        n = len(axes)
        states = self._ToValueList( state, n, int )
        # now states is a list of all axis states 

        if (n != len(states)):
            raise cSDHErrorInvalidParameter( "Lengths of iAxis and state vectors do not match (%d != %d)" % (n, len(states)) )

        for (ai,s) in zip( axes, states ):
            if (ai < self.NUMBER_OF_AXES):    # ignore virutal axes
                self.interface.power( ai, s ) # ANOTE: communicates more often than strictly necessary


    #-----------------------------------------------------------------
    ## Get enabled/disabled state of axis controller(s).
    #
    #  The enabled/disabled state of the controllers of the selected
    #  axes is read from the SDH.
    #    
    #  \param self   - reference to the object itself
    #  \param iAxis  - index of axis to access.
    #                  This can be All, a single index or a \ref sdhlibrary_python_sdh_py_csdh_vector "vector" of indices.
    #
    #  \return
    #    - if \a iAxis is a single index then a single int value \c (0|1) is returned
    #    - else a list of the selected axes enabled states as int values \c (0|1) is returned
    #
    #  \remark
    #    - The order of the returned list (if any) depends on the
    #      order of the axis indices given in \a iAxis. I.E. if a list
    #      \c rc is returned, then \c rc[i] will be the enabled state of axis
    #      \a iAxis[i] (not axis \c i).
    #    - If \a iAxis is \c All then the order will be the natural
    #      one (as if \a iAxis=[0,1,2,3,4,5,6] had been given).
    #      
    #  \par Examples:
    #  \code
    #    # Assuming 'hand' is a sdh.cSDH object ...
    #    
    #    # Get enabled state of all axes:
    #    L = hand.GetAxisEnable( sdh.All )
    #    # now L is something like [0,0,0,1,1,0,0]
    #    
    #    # Get enabled state of axis 0 and 3 
    #    L = hand.GetAxisEnable( [0,3] )
    #    # now L is something like [0,1]
    #
    #    # Get enabled state of axis 3  
    #    v = hand.GetAxisEnable( 3 )
    #    # now v is something like 1
    #    
    #    # Get enabled state of axis 2
    #    L = hand.GetAxisEnable( [2] )
    #    # now L is something like [0]
    #    #   (if a vector is given as parameter then a list is returned,
    #    #    even if it contains a single element only)
    #  \endcode
    #  
    #  <hr>
    def GetAxisEnable( self, iAxis=All ):
        '''
        Get enabled/disabled state of axis/axes. See html/pdf documentation for details.
        '''
        axes = self._ToIndexList( iAxis, self.all_axes, self.NUMBER_OF_AXES + self.NUMBER_OF_VIRTUAL_AXES, "axis" )
        # now axes is a list of all axis indices to access

        if (type(iAxis) == int):
            return self.interface.power( iAxis, None )
        else:
            # we want a list of (most likely) more than one enabled state, so 
            # read all enabled states at once to communicate as few as possible
            all_states = self.interface.power( All, None )

            # append state True for all virtual axes
            all_states += [ True ]*self.NUMBER_OF_VIRTUAL_AXES

            
            return [ all_states[ ai ]   for ai in axes ]
        

    #-----------------------------------------------------------------
    ## Get the current actual state(s) of axis(axes).
    #
    #  The actual axis states are read from the SDH.
    #
    #  \param self  - reference to the object itself
    #  \param iAxis - index of axis to access.
    #                 This can be All, a single index or a \ref sdhlibrary_python_sdh_py_csdh_vector "vector" of indices.
    #
    #  \return
    #    - if \a iAxis is a single index then a single int value is returned
    #    - else a list of the selected axes actual states is returned
    #    - The value(s) are returned numerically, (see also cSDHBase#eAxisState):
    #      - 0 : controller on but not moving
    #      - 1 : controller on and moving
    #      - 6 : controller off 
    #
    #  \remark
    #    - The order of the returned list (if any) depends on the
    #      order of the axis indices given in \a iAxis. I.E. if a list
    #      \c rc is returned, then \c rc[i] will be the current actual
    #      state of axis \a iAxis[i] (not axis \c i).
    #    - If \a iAxis is \c All then the order will be the natural
    #      one (as if \a iAxis=[0,1,2,3,4,5,6] had been given
    #    
    #
    #  \par Examples:
    #  \code
    #    # Assuming "hand" is a sdh.cSDH object ...
    #    
    #    # Get actual axis state of axis 3 
    #    v = hand.GetAxisActualState( 3 )
    #    # v is now something like 0
    #
    #    # Get actual axis state of axis 3
    #    L = hand.GetAxisActualState( [3] )
    #    # now L is something like [0]
    #    #   (if a vector is given as parameter then a list is returned,
    #    #    even if it contains a single element only)
    #
    #    # Get actual axis state of axis 3 and 5
    #    L = hand.GetAxisActualState( [3,5] )
    #    # now L is something like [0, 6]
    #
    #    # Get actual axis state of all axes
    #    L = hand.GetAxisActualState( sdh.All )
    #    # now L is something like [0, 0, 0, 0, 0, 6, 0]
    #
    #    # Get actual axis state of all axes 
    #    L = hand.GetAxisActualState()
    #    # now L is something like [0, 0, 0, 0, 0, 6, 0]
    #  \endcode
    #  
    #  <hr>
    def GetAxisActualState( self, iAxis=All ):
        '''
        Get the current actual state(s) of axis(axes)
        '''
        axes = self._ToIndexList( iAxis, self.all_axes, self.NUMBER_OF_AXES + self.NUMBER_OF_VIRTUAL_AXES, "axis" )
        # now axes is a list of all axis indices to access

        if (type(iAxis) == int):
            return self.interface.state( iAxis )
        else:
            # we want a list of (most likely) more than one state, so 
            # read all states at once to communicate as few as possible
            all_states = self.interface.state( All )

            # append state 6 for all virtual axes 
            all_states += [ 6 ]*self.NUMBER_OF_VIRTUAL_AXES

            return [ all_states[ ai ]   for ai in axes ]


    #-----------------------------------------------------------------
    ## Wait until the movement(s) of of axis(axes) has finished
    #
    #  The state of the given axis(axes) is(are) queried until all
    #  axes are no longer moving.
    #
    #  \param self  - reference to the object itself
    #  \param iAxis - index of axis to access.
    #                 This can be All, a single index or a \ref sdhlibrary_python_sdh_py_csdh_vector "vector" of indices.
    #  \param timeout - a timeout in seconds or None (default). 
    #  
    #  \remark
    #    - If timeout is None is given then this function will wait arbitrarily long
    #    - If a timeout is given then this function will raise a
    #      cSDHErrorTimeout exception if the given axes are still
    #      moving after timeout many seconds
    #
    #  \bug
    #    Due to a bug in SDH firmwares prior to 0.0.2.6 the WaitAxis() command
    #    was somewhat unreliable there. When called immediately after a movement command like MoveHand(),
    #    then the WaitAxis() command returned immediately without waiting for the end of the movement.
    #    With SDH firmwares 0.0.2.6 and newer this is no longer problematic and WaitAxis() works as expected.
    #    <br><b>=> Resolved in SDH firmware 0.0.2.6</b> 
    #
    #  \bug With SDH firmware 0.0.2.6 WaitAxis() did not work if one of the new
    #       velocity based controllers (eCT_VELOCITY, eCT_VELOCITY_ACCELERATION)
    #       was used. With SDH firmwares 0.0.2.7 and newer this now works. Here
    #       the WaitAxis() waits until the selected axes come to velocity 0.0
    #       <br><b>=> Resolved in SDH firmware 0.0.2.7</b>
    #
    #  \par Examples:
    #  Example 1, WaitAxis and eCT_POSE controller, see also the demo program demo-simple3
    #  \code
    #    # Assuming "hand" is a sdh.cSDH object ...
    #    
    #    hand.SetController( eCT_POSE );
    #
    #    # Set a new target pose for axis 1,2 and 3
    #    hand.SetAxisTargetAngle( [1, 2, 3], [-10,-20,-30] )
    #
    #    # Move axes there non sequentially:
    #    hand.MoveAxis( [1, 2, 3], False )
    #
    #    # The last call returned immediately so we now have time to
    #    # do something else while the hand is moving:
    #    # ... insert any calculation here ...
    #
    #    # Before doing something else with the hand make shure the
    #    # selected axes have finished the last movement:
    #    hand.WaitAxis( [1, 2, 3] )
    #
    #    
    #    # go back home (all angles to 0.0):
    #    hand.SetAxisTargetAngle( sdh.All, 0.0 )
    #
    #    # Move all axes there non sequentially:
    #    hand.MoveAxis( sdh.All, False )
    #
    #    # Wait until all axes are there:
    #    hand.WaitAxis()
    #    # now we are at the desired position.
    #  \endcode
    #
    #  Example 2, WaitAxis and eCT_VELOCITY_ACCELERATION controller, see also the demo program demo-velocity-acceleration
    #  \code
    #    # Assuming "hand" is a sdh.cSDH object ...
    #    
    #    hand.SetController( eCT_VELOCITY_ACCELERATION );
    #
    #    # Set a new target pose for axis 1,2 and 3
    #    hand.SetAxisTargetVelocity( [1, 2, 3], [-10,-20,-30] ) # will make the axes move!
    #
    #    # The last call returned immediately so we now have time to
    #    # do something else while the hand is moving:
    #    # ... insert any calculation here ...
    #
    #    # to break and stop the movement just set the target velocities to 0.0
    #    hand.SetAxisTargetVelocity( [1, 2, 3], [0,0,0] ) # will make the axes stop with the default (de)acceleration
    #
    #    # The previous command returned immediately, so
    #    # before doing something else with the hand make shure the
    #    # selected axes have stopped:
    #    hand.WaitAxis( [1,2,3] );
    #
    #    # now the axes have stopped
    #  \endcode
    #  
    #  <hr>
    def WaitAxis( self, iAxis=All, timeout=None ):
        '''
        Wait until the axis(axes) have actually finished their movement
        '''
        axes = self._ToIndexList( iAxis, self.all_axes, self.NUMBER_OF_AXES + self.NUMBER_OF_VIRTUAL_AXES, "axis" )
        # now axes is a list of all axis indices to access


        finished = False
        if (timeout is not None):
            end = time.time() + timeout

        if ( self.controller_type == self.eControllerType["eCT_POSE"]):
            busy = self.eAxisState[ "eAS_POSITIONING" ]
        else:
            busy = self.eAxisState[ "eAS_SPEED_MODE" ]
            
        while ( not finished ):
            states = self.GetAxisActualState( axes )
            finished = True
            for s in states:
                finished = finished  and  (s != busy)

            if (timeout is not None  and  time.time() > end):
                raise cSDHErrorTimeout( "Timeout in WaitAxis" )
            

         
    #-----------------------------------------------------------------
    ## Set the target angle(s) for axis(axes).
    #
    #  The target angles are stored in the SDH, the movement
    #  is not executed until an additional move command is sent.
    # 
    #  \param self  - reference to the object itself
    #  \param iAxis - index of axis to access.
    #                 This can be All, a single index or a \ref sdhlibrary_python_sdh_py_csdh_vector "vector" of indices.
    #  \param angle - the angle to set or \c None to set the current actual axis angle as target angle.
    #                 This can be a single number or a \ref sdhlibrary_python_sdh_py_csdh_vector "vector" of numbers.
    #                 The value(s) are expected in the configured angle unit system #uc_angle.
    #  
    #  \remark
    #    - Setting the target angle will \b not make the axis/axes move.
    #    - If both \a iAxis and \a angle are vectors then the order of
    #      their elements must match, i.e. \c angle[i] will be applied
    #      to axis \c iAxis[i] (not axis \c i)
    #    - If \a iAxis is \c All then the order will be the natural
    #      one (as if \a iAxis=[0,1,2,3,4,5,6] had been given).
    # 
    #  \par Examples:
    #  \code
    #    # Assuming "hand" is a sdh.cSDH object ...
    #    
    #    # Set target axis angle of axis 3 to 42 deg
    #    hand.SetAxisTargetAngle( 3, 42 )
    #
    #    # Set target axis angle of axis 3 to 42 deg and axis 5 to 47.11 deg
    #    hand.SetAxisTargetAngle( [3,5], [42, 47.11] )
    #
    #    # Set target axis angle of all axes to 08.15
    #    hand.SetAxisTargetAngle( sdh.All, 08.15 )
    #
    #    # Set target axis angle of all axes to the given values
    #    hand.SetAxisTargetAngle( angle=[0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0 ] )
    #  
    #    # Set target axis angle of all axes to the current actual axis angles
    #    hand.SetAxisTargetAngle( angle=None )
    #  
    #    # Set target axis angle of axis 3 to 42 deg and axis 1 to its current actual axis angle 
    #    hand.SetAxisTargetAngle( [3,1], angle=[42,None] )
    #  \endcode
    #  
    #  <hr>
    def SetAxisTargetAngle( self, iAxis=All, angle=None ):
        '''
        Set the target angle(s) for axis(axes)
        '''
        axes = self._ToIndexList( iAxis, self.all_axes, self.NUMBER_OF_AXES + self.NUMBER_OF_VIRTUAL_AXES, "axis" )
        # now axes is a list of all axis indices to access

        n = len(axes)
        angles = self._ToValueList( angle, n, self.uc_angle.ToInternal )
        # now angles is a list of all axis angles in internal unit
        # system (or None to set current actual axis angle)

        if (n != len(angles)):
            raise cSDHErrorInvalidParameter( "Lengths of iAxis and angle vectors do not match (%d != %d)" % (n, len(angles)) )

        # ??? the angles are not checked here

        # get current angle for those axes where the angle is None
        c_ang = None
        for (ai,a) in zip( axes, angles ):
            if (ai >= self.NUMBER_OF_AXES):    # handle virutal axes differently
                if (a is not None):
                    self.CheckRange(a, self.f_min_angle_a[ai], self.f_max_angle_a[ai], "virtual axis %d angle" % ai )
                continue

            if (a is None):
                if (c_ang is None):
                    c_ang = self.interface.p( All )
                a = c_ang[ ai ]
            # now a is the target angle to set

            # and send to firmware
            self.interface.p( ai, a ) # ANOTE: communicates more often than strictly necessary
        
    #-----------------------------------------------------------------
    ## Set the target angle(s) and read the actual angle(s) for axis(axes).
    #
    #  Opposed to SetAxisTargetAngle() this will make the fingers move to the
    #  set target angles immediately, if the axis controllers are already enabled!
    #
    #  \param self  - reference to the object itself
    #  \param iAxis - index of axis to access.
    #                 This can be All, a single index or a \ref sdhlibrary_python_sdh_py_csdh_vector "vector" of indices.
    #  \param angle - the angle to set or \c None to set the current actual axis angle as target angle.
    #                 This can be a single number or a \ref sdhlibrary_python_sdh_py_csdh_vector "vector" of numbers.
    #                 The value(s) are expected in the configured angle unit system #uc_angle.
    #  
    #  \return
    #    - if \a iAxis is a single index then a single float value is returned
    #    - else a list of the selected axes actual angles is returned
    #    - The value(s) are returned in the configured angle unit system #uc_angle.
    #
    #  \remark
    #    - Setting the target angle will \b not make the axis/axes move.
    #    - If both \a iAxis and \a angle are vectors then the order of
    #      their elements must match, i.e. \c angle[i] will be applied
    #      to axis \c iAxis[i] (not axis \c i)
    #    - If \a iAxis is \c All then the order will be the natural
    #      one (as if \a iAxis=[0,1,2,3,4,5,6] had been given).
    # 
    #  \par Examples:
    #  \code
    #    # Assuming "hand" is a sdh.cSDH object ...
    #    
    #    # Set target axis angle of axis 3 to 42 deg
    #    hand.SetAxisTargetAngle( 3, 42 )
    #
    #    # Set target axis angle of axis 3 to 42 deg and axis 5 to 47.11 deg
    #    hand.SetAxisTargetAngle( [3,5], [42, 47.11] )
    #
    #    # Set target axis angle of all axes to 08.15
    #    hand.SetAxisTargetAngle( sdh.All, 08.15 )
    #
    #    # Set target axis angle of all axes to the given values
    #    hand.SetAxisTargetAngle( angle=[0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0 ] )
    #  
    #    # Set target axis angle of all axes to the current actual axis angles
    #    hand.SetAxisTargetAngle( angle=None )
    #  
    #    # Set target axis angle of axis 3 to 42 deg and axis 1 to its current actual axis angle 
    #    hand.SetAxisTargetAngle( [3,1], angle=[42,None] )
    #  \endcode
    #  
    #  <hr>
    def SetAxisTargetGetAxisActualAngle( self, iAxis=All, angle=None ):
        '''
        Set the target angle(s) and get the actual angle(s) for axis(axes)
        '''
        axes = self._ToIndexList( iAxis, self.all_axes, self.NUMBER_OF_AXES + self.NUMBER_OF_VIRTUAL_AXES, "axis" )
        # now axes is a list of all axis indices to access

        n = len(axes)
        angles = self._ToValueList( angle, n, self.uc_angle.ToInternal )
        # now angles is a list of all axis angles in internal unit
        # system (or None to set current actual axis angle)

        if (n != len(angles)):
            raise cSDHErrorInvalidParameter( "Lengths of iAxis and angle vectors do not match (%d != %d)" % (n, len(angles)) )

        # ??? the angles are not checked here

        # get current angle for those axes where the angle is None
        c_ang = None
        ta = [None] * self.NUMBER_OF_AXES 
        for (ai,a) in zip( axes, angles ):
            if (ai >= self.NUMBER_OF_AXES):    # handle virtual axes differently
                if (a is not None):
                    self.CheckRange(a, self.f_min_angle_a[ai], self.f_max_angle_a[ai], "virtual axis %d angle" % ai )
                continue

            if (a is None):
                if (c_ang is None):
                    c_ang = self.interface.p( All )
                ta[ai] = c_ang[ ai ]
            else:
                ta[ai] = a

        for i in range( self.NUMBER_OF_AXES ):
            if (ta[i] is None):
                if (c_ang is None):
                    c_ang = self.interface.p( All )
                ta[i] = c_ang[ i ]
        # now ta is a list of all target angles

        # and send to firmware
        aa = self.interface.tpap( All, ta )
        aa += [ 0.0 ]*self.NUMBER_OF_VIRTUAL_AXES
        return [ self.uc_angle.ToExternal( aa[ ai ] )   for ai in axes ]
        
    #-----------------------------------------------------------------
    ## Get the target angle(s) of axis(axes).
    #
    #  The target angles are read from the SDH.
    #
    #  \param self  - reference to the object itself
    #  \param iAxis - index of axis to access.
    #                 This can be All, a single index or a \ref sdhlibrary_python_sdh_py_csdh_vector "vector" of indices.
    #
    #  \return
    #    - if \a iAxis is a single index then a single float value is returned
    #    - else a list of the selected axes target angles is returned
    #    - The value(s) are returned in the configured angle unit system #uc_angle.
    #
    #  \remark
    #    - The order of the returned list (if any) depends on the
    #      order of the axis indices given in \a iAxis. I.E. if a list
    #      \c rc is returned, then \c rc[i] will be the target angle of axis
    #      \a iAxis[i] (not axis \c i).
    #    - If \a iAxis is \c All then the order will be the natural
    #      one (as if \a iAxis=[0,1,2,3,4,5,6] had been given).
    #    
    #
    #  \par Examples:
    #  \code
    #    # Assuming "hand" is a sdh.cSDH object ...
    #    
    #    # Get target axis angle of axis 3 
    #    v = hand.GetAxisTargetAngle( 3 )
    #    # v is now something like 42.0
    #
    #    # Get target axis angle of axis 3
    #    L = hand.GetAxisTargetAngle( [3] )
    #    # now L is something like [42.0]
    #    #   (if a vector is given as parameter then a list is returned,
    #    #    even if it contains a single element only)
    #
    #    # Get target axis angle of axis 3 and 5
    #    L = hand.GetAxisTargetAngle( [3,5] )
    #    # now L is something like [42.0, 47.11]
    #
    #    # Get target axis angle of all axes
    #    L = hand.GetAxisTargetAngle( sdh.All )
    #    # now L is something like [0.0, 0.0, 42.0, 0.0, 47.11, 0,0, 0.0]
    #
    #    # Get target axis angle of all axes 
    #    L = hand.GetAxisTargetAngle()
    #    # now L is something like [0.0, 0.0, 42.0, 0.0, 47.11, 0,0, 0.0]
    #  \endcode
    #  
    #  <hr>
    def GetAxisTargetAngle( self, iAxis=All ):
        '''
        Get the target angle(s) of axis(axes)
        '''
        axes = self._ToIndexList( iAxis, self.all_axes, self.NUMBER_OF_AXES + self.NUMBER_OF_VIRTUAL_AXES, "axis" )
        # now axes is a list of all axis indices to access

        if (type(iAxis) == int):
            return self.uc_angle.ToExternal( self.interface.p( iAxis, None ) )
        else:
            # we want a list of (most likely) more than one angle, so 
            # read all angles at once to communicate as few as possible
            all_angles = self.interface.p( All, None )

            # append angle 0.0 for all virtual axes 
            all_angles += [ 0.0 ]*self.NUMBER_OF_VIRTUAL_AXES

            return [ self.uc_angle.ToExternal( all_angles[ ai ] )   for ai in axes ]


    #-----------------------------------------------------------------
    ## Get the current actual angle(s) of axis(axes).
    #
    #  The actual angles are read from the SDH.
    #
    #  \param self  - reference to the object itself
    #  \param iAxis - index of axis to access.
    #                 This can be All, a single index or a \ref sdhlibrary_python_sdh_py_csdh_vector "vector" of indices.
    #
    #  \return
    #    - if \a iAxis is a single index then a single float value is returned
    #    - else a list of the selected axes actual angles is returned
    #    - The value(s) are returned in the configured angle unit system #uc_angle.
    #
    #  \remark
    #    - The order of the returned list (if any) depends on the
    #      order of the axis indices given in \a iAxis. I.E. if a list
    #      \c rc is returned, then \c rc[i] will be the current actual
    #      angle of axis \a iAxis[i] (not axis \c i).
    #    - If \a iAxis is \c All then the order will be the natural
    #      one (as if \a iAxis=[0,1,2,3,4,5,6] had been given
    #    
    #
    #  \par Examples:
    #  \code
    #    # Assuming "hand" is a sdh.cSDH object ...
    #    
    #    # Get actual axis angle of axis 3 
    #    v = hand.GetAxisActualAngle( 3 )
    #    # v is now something like 42.0
    #
    #    # Get actual axis angle of axis 3
    #    L = hand.GetAxisActualAngle( [3] )
    #    # now L is something like [42.0]
    #    #   (if a vector is given as parameter then a list is returned,
    #    #    even if it contains a single element only)
    #
    #    # Get actual axis angle of axis 3 and 5
    #    L = hand.GetAxisActualAngle( [3,5] )
    #    # now L is something like [42.0, 47.11]
    #
    #    # Get actual axis angle of all axes
    #    L = hand.GetAxisActualAngle( sdh.All )
    #    # now L is something like [0.0, 0.0, 42.0, 0.0, 47.11, 0,0, 0.0]
    #
    #    # Get actual axis angle of all axes 
    #    L = hand.GetAxisActualAngle()
    #    # now L is something like [0.0, 0.0, 42.0, 0.0, 47.11, 0,0, 0.0]
    #  \endcode
    #  
    #  <hr>
    def GetAxisActualAngle( self, iAxis=All ):
        '''
        Get the current actual angle(s) of axis(axes)
        '''
        axes = self._ToIndexList( iAxis, self.all_axes, self.NUMBER_OF_AXES + self.NUMBER_OF_VIRTUAL_AXES, "axis" )
        # now axes is a list of all axis indices to access

        if (type(iAxis) == int):
            return self.uc_angle.ToExternal( self.interface.pos( iAxis ) )
        else:
            # we want a list of (most likely) more than one angle, so 
            # read all angles at once to communicate as few as possible
            all_angles = self.interface.pos( All )

            # append angle 0.0 for all virtual axes 
            all_angles += [ 0.0 ]*self.NUMBER_OF_VIRTUAL_AXES

            return [ self.uc_angle.ToExternal( all_angles[ ai ] )   for ai in axes ]

         
    #-----------------------------------------------------------------
    ## Set the target velocity(s) for axis(axes).
    #
    #  The target velocities are stored in the SDH. The time at which
    #  a new target velocity will take effect depends on the current
    #  axis controller type:
    #  - in eCT_POSE controller type the new target velocities will
    #    not take effect until an additional move command is sent:
    #    MoveAxis(), MoveFinger(), MoveHand()
    #  - in eCT_VELOCITY and eCT_VELOCITY_ACCELERATION controller type
    #    the new target velocity will take effect immediately,
    #    if the axis controllers are already enabled.
    #    This means that in eCT_VELOCITY_ACCELERATION controller type
    #    the accelerations must be set with SetAxisTargetAcceleration() 
    #    \b before calling SetAxisTargetVelocity().
    #
    #
    #  \param self     - reference to the object itself
    #  \param iAxis    - index of axis to access.
    #                    This can be All, a single index or a \ref sdhlibrary_python_sdh_py_csdh_vector "vector" of indices.
    #  \param velocity - the velocity to set or \c None to keep the currently set target velocity of the axis
    #                    This can be a single number or a \ref sdhlibrary_python_sdh_py_csdh_vector "vector" of numbers.
    #                    The value(s) are expected in the configured angular velocity unit system #uc_angular_velocity.
    #  
    #  \remark
    #    - If both \a iAxis and \a velocity are vectors then the order of
    #      their elements must match, i.e. \c velocity[i] will be applied
    #      to axis \c iAxis[i] (not axis \c i). 
    #    - If \a iAxis is \c All then the order will be the natural
    #      one (as if \a iAxis=[0,1,2,3,4,5,6] had been given
    #      
    #  \par Examples:
    #  \code
    #    # Assuming "hand" is a sdh.cSDH object ...
    #    
    #    # Set target axis velocity of axis 3 to 14 deg/s
    #    hand.SetAxisTargetVelocity( 3, 14 )
    #
    #    # Set target axis velocity of axis 3 to 14 deg/s and axis 5 to 12.34 degs
    #    hand.SetAxisTargetVelocity( [3,5], [14, 12.34] )
    #
    #    # Set target axis velocity of all axes to 08.15 deg/s
    #    hand.SetAxisTargetVelocity( sdh.All, 08.15 )
    #
    #    # Set target axis velocity of all axes to the given values
    #    hand.SetAxisTargetVelocity( velocity=[10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0 ] )
    #  
    #    # Set target axis velocity of all axes to the currently set axis velocities (well, this is not very usefull...)
    #    hand.SetAxisTargetVelocity( velocity=None )
    #  
    #    # Set target axis velocity of axis 3 to 14 deg/s and keep axis 1 at its currently set target velocity 
    #    hand.SetAxisTargetVelocity( [3,1], velocity=[14,None] )
    #  \endcode
    #  
    #  <hr>
    def SetAxisTargetVelocity( self, iAxis=All, velocity=None ):
        '''
        Set the target velocity(s) for axis(axes)
        '''
        axes = self._ToIndexList( iAxis, self.all_axes, self.NUMBER_OF_AXES + self.NUMBER_OF_VIRTUAL_AXES, "axis" )
        # now axes is a list of all axis indices to access

        n = len(axes)
        velocities = self._ToValueList( velocity, n, self.uc_angular_velocity.ToInternal )
        # now velocities is a list of all axis velocities in the
        # internal unit system (or None to set the current axis
        # velocity)

        if (n != len(velocities)):
            raise cSDHErrorInvalidParameter( "Lengths of iAxis and velocity vectors do not match (%d != %d)" % (n, len(velocities)) )


        # get all currently set velocities
        all_velocities = self.interface.v( All, None )

        # overwrite where selected with user given value:
        for (ai,v) in zip( axes, velocities ):
            if (ai >= self.NUMBER_OF_AXES):    # handle virutal axes differently
                continue

            if (v is not None):
                # overwrite
                all_velocities[ ai ] = v
            
        # and send to firmware
        self.interface.v( All, all_velocities )
        
    #-----------------------------------------------------------------
    ## Set the target velocity(s) and get actual velocity(s) of axis(axes).
    #
    #  The target velocities are stored in the SDH. The time at which
    #  a new target velocity will take effect depends on the current
    #  axis controller type:
    #  - in eCT_POSE controller type the new target velocities will
    #    not take effect until an additional move command is sent:
    #    MoveAxis(), MoveFinger(), MoveHand()
    #  - in eCT_VELOCITY and eCT_VELOCITY_ACCELERATION controller type
    #    the new target velocity will take effect immediately,
    #    if the axis controllers are already enabled.
    #    This means that in eCT_VELOCITY_ACCELERATION controller type
    #    the accelerations must be set with SetAxisTargetAcceleration() 
    #    \b before calling SetAxisTargetVelocity().
    #
    #
    #  \param self     - reference to the object itself
    #  \param iAxis    - index of axis to access.
    #                    This can be All, a single index or a \ref sdhlibrary_python_sdh_py_csdh_vector "vector" of indices.
    #  \param velocity - the velocity to set or \c None to keep the currently set target velocity of the axis
    #                    This can be a single number or a \ref sdhlibrary_python_sdh_py_csdh_vector "vector" of numbers.
    #                    The value(s) are expected in the configured angular velocity unit system #uc_angular_velocity.
    #  
    #  \return
    #    - if \a iAxis is a single index then a single float value is returned
    #    - else a list of the selected axes actual velocities is returned
    #    - The value(s) are reported in the configured angular velocity unit system #uc_angular_velocity.
    #
    #  \remark
    #    - If both \a iAxis and \a velocity are vectors then the order of
    #      their elements must match, i.e. \c velocity[i] will be applied
    #      to axis \c iAxis[i] (not axis \c i). 
    #    - If \a iAxis is \c All then the order will be the natural
    #      one (as if \a iAxis=[0,1,2,3,4,5,6] had been given
    #      
    #  \par Examples:
    #  \code
    #    # Assuming "hand" is a sdh.cSDH object ...
    #    
    #    # Set target axis velocity of axis 3 to 14 deg/s
    #    hand.SetAxisTargetGetAxisActualVelocity( 3, 14 )
    #
    #    # Set target axis velocity of axis 3 to 14 deg/s and axis 5 to 12.34 degs
    #    hand.SetAxisTargetGetAxisActualVelocity( [3,5], [14, 12.34] )
    #
    #    # Set target axis velocity of all axes to 08.15 deg/s
    #    hand.SetAxisTargetGetAxisActualVelocity( sdh.All, 08.15 )
    #
    #    # Set target axis velocity of all axes to the given values
    #    hand.SetAxisTargetGetAxisActualVelocity( velocity=[10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0 ] )
    #  
    #    # Set target axis velocity of all axes to the currently set axis velocities (well, this is not very usefull...)
    #    hand.SetAxisTargetGetAxisActualVelocity( velocity=None )
    #  
    #    # Set target axis velocity of axis 3 to 14 deg/s and keep axis 1 at its currently set target velocity 
    #    hand.SetAxisTargetGetAxisActualVelocity( [3,1], velocity=[14,None] )
    #  \endcode
    #  
    #  <hr>
    def SetAxisTargetGetAxisActualVelocity( self, iAxis=All, velocity=None ):
        '''
        Set the target velocity(s) and get the actual velocity(s) for axis(axes)
        '''
        axes = self._ToIndexList( iAxis, self.all_axes, self.NUMBER_OF_AXES + self.NUMBER_OF_VIRTUAL_AXES, "axis" )
        # now axes is a list of all axis indices to access

        n = len(axes)
        velocities = self._ToValueList( velocity, n, self.uc_angular_velocity.ToInternal )
        # now velocities is a list of all axis velocities in internal unit
        # system (or None to set current actual axis velocity)

        if (n != len(velocities)):
            raise cSDHErrorInvalidParameter( "Lengths of iAxis and velocity vectors do not match (%d != %d)" % (n, len(velocity)) )

        # ??? the velocities are not checked here

        # get current velocities for those axes where the velocity is None
        c_ang = None
        tv = [None] * self.NUMBER_OF_AXES 
        for (ai,v) in zip( axes, velocities ):
            if (ai >= self.NUMBER_OF_AXES):    # handle virtual axes differently
                if (v is not None):
                    self.CheckRange(v, self.f_min_velocity_a[ai], self.f_max_velocity_a[ai], "virtual axis %d velocity" % ai )
                continue

            if (v is None):
                if (c_ang is None):
                    c_ang = self.interface.p( All )
                tv[ai] = c_ang[ ai ]
            else:
                tv[ai] = v

        # get current velocities for those axes still missing
        for i in range( self.NUMBER_OF_AXES ):
            if (tv[i] is None):
                if (c_ang is None):
                    c_ang = self.interface.v( All )
                tv[i] = c_ang[ i ]
        # now tv is a list of all target velocities

        # and send to firmware
        av = self.interface.tvav( All, tv )
        av += [ 0.0 ]*self.NUMBER_OF_VIRTUAL_AXES
        return [ self.uc_angular_velocity.ToExternal( av[ ai ] )   for ai in axes ]
        
    #-----------------------------------------------------------------
    ## Get the target velocity(s) of axis(axes).
    #
    #  The target velocities are read from the SDH.
    #
    #  \param self  - reference to the object itself
    #  \param iAxis - index of axis to access.
    #                 This can be All, a single index or a \ref sdhlibrary_python_sdh_py_csdh_vector "vector" of indices.
    #
    #  \return
    #    - if \a iAxis is a single index then a single float value is returned
    #    - else a list of the selected axes target velocities is returned
    #    - The value(s) are reported in the configured angular velocity unit system #uc_angular_velocity.
    #
    #  \remark
    #    - The order of the returned list (if any) depends on the
    #      order of the axis indices given in \a iAxis. I.E. if a list
    #      \c rc is returned, then \c rc[i] will be the target velocity of axis
    #      \a iAxis[i] (not axis \c i).
    #    - If \a iAxis is \c All then the order will be the natural
    #      one (as if \a iAxis=[0,1,2,3,4,5,6] had been given
    #    
    #  \par Examples:
    #  \code
    #    # Assuming "hand" is a sdh.cSDH object ...
    #    
    #    # Get target axis velocity of axis 3 
    #    v = hand.GetAxisTargetVelocity( 3 )
    #    # v is now something like 14.0
    #
    #    # Get target axis velocity of axis 3
    #    L = hand.GetAxisTargetVelocity( [3] )
    #    # now L is something like [14.0]
    #    #   (if a vector is given as parameter then a list is returned,
    #    #    even if it contains a single element only)
    #
    #    # Get target axis velocity of axis 3 and 5
    #    L = hand.GetAxisTargetVelocity( [3,5] )
    #    # now L is something like [14.0, 12.34]
    #
    #    # Get target axis velocity of all axes
    #    L = hand.GetAxisTargetVelocity( sdh.All )
    #    # now L is something like [100.0, 40.0, 40.0, 14.0, 40.0, 12.34, 40.0]
    #
    #    # Get target axis velocity of all axes 
    #    L = hand.GetAxisTargetVelocity()
    #    # now L is something like [100.0, 40.0, 40.0, 14.0, 40.0, 12.34, 40.0]
    #  \endcode
    #  
    #  <hr>
    def GetAxisTargetVelocity( self, iAxis=All ):
        '''
        Get the target velocity(s) of axis(axes)
        '''
        axes = self._ToIndexList( iAxis, self.all_axes, self.NUMBER_OF_AXES + self.NUMBER_OF_VIRTUAL_AXES, "axis" )
        # now axes is a list of all axis indices to access

        if (type(iAxis) == int):
            return self.uc_angular_velocity.ToExternal( self.interface.v( iAxis, None ) )
        else:
            # we want a list of (most likely) more than one velocity, so 
            # read all velocities at once to communicate as few as possible
            all_velocities = self.interface.v( All, None )

            # append velocity 0.0 for all virtual axes 
            all_velocities += [ 0.0 ]*self.NUMBER_OF_VIRTUAL_AXES
            
            return [ self.uc_angular_velocity.ToExternal( all_velocities[ ai ] )   for ai in axes ]  # ANOTE: communicates more often than strictly necessary


    #-----------------------------------------------------------------
    ## Get the velocity limit(s) of axis(axes).
    #
    #  The velocity limit(s) are read from the SDH.
    #
    #  \param self  - reference to the object itself
    #  \param iAxis - index of axis to access.
    #                 This can be All, a single index or a \ref sdhlibrary_python_sdh_py_csdh_vector "vector" of indices.
    #
    #  \return
    #    - if \a iAxis is a single index then a single float value is returned
    #    - else a list of the selected axes velocity limits is returned
    #    - The value(s) are reported in the configured angular velocity unit system #uc_angular_velocity.
    #
    #  \remark
    #    - The order of the returned list depends on the
    #      order of the axis indices given in \a iAxis. I.E. if a list
    #      \c rc is returned, then \c rc[i] will be the target velocity of axis
    #      \a iAxis[i] (not axis \c i).
    #    - If \a iAxis is \c All then the order will be the natural
    #      one (as if \a iAxis=[0,1,2,3,4,5,6] had been given
    #    
    #  \par Examples:
    #  \code
    #    # Assuming "hand" is a sdh.cSDH object ...
    #    
    #    # Get axis velocity limit of axis 3 
    #    v = hand.GetAxisLimitVelocity( 3 )
    #    # v is now something like 14.0
    #
    #    # Get axis velocity limit of axis 3
    #    L = hand.GetAxisLimitVelocity( [3] )
    #    # now L is something like [140.0]
    #    #   (if a vector is given as parameter then a list is returned,
    #    #    even if it contains a single element only)
    #
    #    # Get axis velocity limit of axis 3 and 5
    #    L = hand.GetAxisLimitVelocity( [3,5] )
    #    # now L is something like [140.0, 140.0]
    #
    #    # Get axis velocity limit of all axes
    #    L = hand.GetAxisLimitVelocity( sdh.All )
    #    # now L is something like [81.0, 140.0, 120.0, 140.0, 120.0, 140.0, 120.0]
    #
    #    # Get axis velocity limit of all axes 
    #    L = hand.GetAxisLimitVelocity()
    #    # now L is something like [81.0, 140.0, 120.0, 140.0, 120.0, 140.0, 120.0]
    #  \endcode
    #  
    #  <hr>
    def GetAxisLimitVelocity( self, iAxis=All ):
        '''
        Get the velocity limit(s) of axis(axes)
        '''
        axes = self._ToIndexList( iAxis, self.all_axes, self.NUMBER_OF_AXES + self.NUMBER_OF_VIRTUAL_AXES, "axis" )
        # now axes is a list of all axis indices to access

        if ( CompareReleases( self.release_firmware, "0.0.2.1" ) < 0 ):
            # if firmware is older than "0.0.2.1" then use fixed default:
            all_velocities = [85.7, 200.0, 157.8, 200.0, 157.8, 200.0, 157.8, 85.7 ]
            if (type(iAxis) == int):
                return self.uc_angular_velocity.ToExternal( all_velocities[ iAxis ] )
            return [ self.uc_angular_velocity.ToExternal( all_velocities[ ai ] )   for ai in axes ]
            
        if (type(iAxis) == int):
            return self.uc_angular_velocity.ToExternal( self.interface.vlim( iAxis ) )
        else:
            # we want a list of (most likely) more than one velocity, so 
            # read all velocities at once to communicate as few as possible
            all_velocities = self.interface.vlim( All )

            # append velocity 0.0 for all virtual axes 
            all_velocities += [ 0.0 ]*self.NUMBER_OF_VIRTUAL_AXES
            
            return [ self.uc_angular_velocity.ToExternal( all_velocities[ ai ] )   for ai in axes ]


    #-----------------------------------------------------------------
    ## Get the acceleration limit(s) of axis(axes).
    #
    #  The acceleration limit(s) are read from the SDH.
    #
    #  \param self  - reference to the object itself
    #  \param iAxis - index of axis to access.
    #                 This can be All, a single index or a \ref sdhlibrary_python_sdh_py_csdh_vector "vector" of indices.
    #
    #  \return
    #    - if \a iAxis is a single index then a single float value is returned
    #    - else a list of the selected axes acceleration limits is returned
    #    - The value(s) are reported in the configured angular acceleration unit system #uc_angular_acceleration.
    #
    #  \remark
    #    - The order of the returned list depends on the
    #      order of the axis indices given in \a iAxis. I.E. if a list
    #      \c rc is returned, then \c rc[i] will be the target acceleration of axis
    #      \a iAxis[i] (not axis \c i).
    #    - If \a iAxis is \c All then the order will be the natural
    #      one (as if \a iAxis=[0,1,2,3,4,5,6] had been given
    #    
    #  \par Examples:
    #  \code
    #    # Assuming "hand" is a sdh.cSDH object ...
    #    
    #    # Get axis acceleration limit of axis 3 
    #    a = hand.GetAxisLimitAcceleration( 3 )
    #    # a is now something like 400.0
    #
    #    # Get axis acceleration limit of axis 3
    #    L = hand.GetAxisLimitAcceleration( [3] )
    #    # now L is something like [400.0]
    #    #   (if a vector is given as parameter then a list is returned,
    #    #    even if it contains a single element only)
    #
    #    # Get axis acceleration limit of axis 3 and 5
    #    L = hand.GetAxisLimitAcceleration( [3,5] )
    #    # now L is something like [400.0, 400.0]
    #
    #    # Get axis acceleration limit of all axes
    #    L = hand.GetAxisLimitAcceleration( sdh.All )
    #    # now L is something like [5000.0, 400.0, 1500.0, 400.0, 1500.0, 400.0, 1500.0]
    #
    #    # Get axis acceleration limit of all axes 
    #    L = hand.GetAxisLimitAcceleration()
    #    # now L is something like [5000.0, 400.0, 1500.0, 400.0, 1500.0, 400.0, 1500.0]
    #  \endcode
    #  
    #  <hr>
    def GetAxisLimitAcceleration( self, iAxis=All ):
        '''
        Get the acceleration limit(s) of axis(axes)
        '''
        axes = self._ToIndexList( iAxis, self.all_axes, self.NUMBER_OF_AXES + self.NUMBER_OF_VIRTUAL_AXES, "axis" )
        # now axes is a list of all axis indices to access

        if ( CompareReleases( self.release_firmware, "0.0.2.7" ) < 0 ):
            # firmware before 0.0.2.7 does not provide the acceleration limit
            # so use fake default:
            all_accelerations = [5000.0, 400.0, 1500.0, 400.0, 1500.0, 400.0, 1500.0, 400.0]
            if (type(iAxis) == int):
                return self.uc_angular_acceleration.ToExternal( iAxis )
            return [ self.uc_angular_acceleration.ToExternal( all_accelerations[ ai ] )   for ai in axes ]
            
        if (type(iAxis) == int):
            return self.uc_angular_acceleration.ToExternal( self.interface.alim( iAxis ) )
        else:
            # we want a list of (most likely) more than one acceleration, so 
            # read all accelerations at once to communicate as few as possible
            all_accelerations = self.interface.alim( All )

            # append acceleration 0.0 for all virtual axes 
            all_accelerations += [ 0.0 ]*self.NUMBER_OF_VIRTUAL_AXES
            
            return [ self.uc_angular_acceleration.ToExternal( all_accelerations[ ai ] )   for ai in axes ]  # ANOTE: communicates more often than strictly necessary


    #-----------------------------------------------------------------
    ## Get the actual velocity(s) of axis(axes).
    #
    #  The actual velocities are read from the SDH.
    #
    #  \param self  - reference to the object itself
    #  \param iAxis - index of axis to access.
    #                 This can be All, a single index or a \ref sdhlibrary_python_sdh_py_csdh_vector "vector" of indices.
    #
    #  \return
    #    - if \a iAxis is a single index then a single float value is returned
    #    - else a list of the selected axes actual velocities is returned
    #    - The value(s) are reported in the configured angular velocity unit system #uc_angular_velocity.
    #
    #  \remark
    #    - The order of the returned list (if any) depends on the
    #      order of the axis indices given in \a iAxis. I.E. if a list
    #      \c rc is returned, then \c rc[i] will be the actual velocity of axis
    #      \a iAxis[i] (not axis \c i).
    #    - If \a iAxis is \c All then the order will be the natural
    #      one (as if \a iAxis=[0,1,2,3,4,5,6] had been given
    #    
    #  \par Examples:
    #  \code
    #    # Assuming "hand" is a sdh.cSDH object ...
    #    
    #    # Get actual axis velocity of axis 3 
    #    v = hand.GetAxisActualVelocity( 3 )
    #    # v is now something like 13.2
    #
    #    # Get actual axis velocity of axis 3
    #    L = hand.GetAxisActualVelocity( [3] )
    #    # now L is something like [13.2]
    #    #   (if a vector is given as parameter then a list is returned,
    #    #    even if it contains a single element only)
    #
    #    # Get actual axis velocity of axis 3 and 5
    #    L = hand.GetAxisActualVelocity( [3,5] )
    #    # now L is something like [13.2, 0.0]
    #
    #    # Get actual axis velocity of all axes
    #    L = hand.GetAxisActualVelocity( sdh.All )
    #    # now L is something like [0.1, 0.2, 0.3, 13.2, 0.5, 0.0, 0.7]
    #
    #    # Get actual axis velocity of all axes 
    #    L = hand.GetAxisActualVelocity()
    #    # now L is something like [0.1, 0.2, 0.3, 13.2, 0.5, 0.0, 0.7]
    #  \endcode
    #  \latexonly
    #     \clearpage
    #  \endlatexonly
    #  <hr>
    def GetAxisActualVelocity( self, iAxis=All ):
        '''
        Get the actual velocity(s) of axis(axes)
        '''
        axes = self._ToIndexList( iAxis, self.all_axes, self.NUMBER_OF_AXES + self.NUMBER_OF_VIRTUAL_AXES, "axis" )
        # now axes is a list of all axis indices to access

        if (type(iAxis) == int):
            return self.uc_angular_velocity.ToExternal( self.interface.vel( iAxis ) )
        else:
            # we want a list of (most likely) more than one velocity, so 
            # read all velocities at once to communicate as few as possible
            all_velocities = self.interface.vel( All )

            # append velocity 0.0 for all virtual axes 
            all_velocities += [ 0.0 ]*self.NUMBER_OF_VIRTUAL_AXES
            
            return [ self.uc_angular_velocity.ToExternal( all_velocities[ ai ] )   for ai in axes ]  # ANOTE: communicates more often than strictly necessary


    #-----------------------------------------------------------------
    ## Get the current reference velocity(s) of axis(axes). (This velocity is used internally by the SDH in eCT_VELOCITY_ACCELERATION mode)
    #
    #  The reference velocities are read from the SDH.
    #
    #  \param self  - reference to the object itself
    #  \param iAxis - index of axis to access.
    #                 This can be All, a single index or a \ref sdhlibrary_python_sdh_py_csdh_vector "vector" of indices.
    #
    #  \return
    #    - if \a iAxis is a single index then a single float value is returned
    #    - else a list of the selected axes reference velocities is returned
    #    - The value(s) are reported in the configured angular velocity unit system #uc_angular_velocity.
    #
    #  \remark
    #    - The order of the returned list (if any) depends on the
    #      order of the axis indices given in \a iAxis. I.E. if a list
    #      \c rc is returned, then \c rc[i] will be the reference velocity of axis
    #      \a iAxis[i] (not axis \c i).
    #    - If \a iAxis is \c All then the order will be the natural
    #      one (as if \a iAxis=[0,1,2,3,4,5,6] had been given
    #    - the underlying rvel command of the SDH firmware is not
    #      available in SDH firmwares prior to 0.0.2.6. For such hands
    #      calling rvel will fail miserably.
    #    - The availability of an appropriate SDH firmware is \b not checked
    #      here due to performance losses when this function is used often.
    #    
    #  \par Examples:
    #  \code
    #    # Assuming "hand" is a sdh.cSDH object ...
    #    
    #    # Switch to "velocity control with acceleration ramp" controller mode first.
    #    # (When in another controller mode like the default eCT_POSE,
    #    #  then the reference velocities will not be valid):
    #    hand.SetController( eCT_VELOCITY_ACCELERATION );
    #
    #    # Get reference axis velocity of axis 3 
    #    v = hand.GetAxisReferenceVelocity( 3 )
    #    # v is now something like 13.2
    #
    #    # Get reference axis velocity of axis 3
    #    L = hand.GetAxisReferenceVelocity( [3] )
    #    # now L is something like [13.2]
    #    #   (if a vector is given as parameter then a list is returned,
    #    #    even if it contains a single element only)
    #
    #    # Get reference axis velocity of axis 3 and 5
    #    L = hand.GetAxisReferenceVelocity( [3,5] )
    #    # now L is something like [13.2, 0.0]
    #
    #    # Get reference axis velocity of all axes
    #    L = hand.GetAxisReferenceVelocity( sdh.All )
    #    # now L is something like [0.1, 0.2, 0.3, 13.2, 0.5, 0.0, 0.7]
    #
    #    # Get reference axis velocity of all axes 
    #    L = hand.GetAxisReferenceVelocity()
    #    # now L is something like [0.1, 0.2, 0.3, 13.2, 0.5, 0.0, 0.7]
    #  \endcode
    #  
    #  <hr>
    def GetAxisReferenceVelocity( self, iAxis=All ):
        '''
        Get the reference velocity(s) of axis(axes)
        '''
        axes = self._ToIndexList( iAxis, self.all_axes, self.NUMBER_OF_AXES + self.NUMBER_OF_VIRTUAL_AXES, "axis" )
        # now axes is a list of all axis indices to access

        if (type(iAxis) == int):
            return self.uc_angular_velocity.ToExternal( self.interface.rvel( iAxis ) )
        else:
            # we want a list of (most likely) more than one velocity, so 
            # read all velocities at once to communicate as few as possible
            all_velocities = self.interface.rvel( All )

            # append velocity 0.0 for all virtual axes 
            all_velocities += [ 0.0 ]*self.NUMBER_OF_VIRTUAL_AXES
            
            return [ self.uc_angular_velocity.ToExternal( all_velocities[ ai ] )   for ai in axes ]  # ANOTE: communicates more often than strictly necessary


    #-----------------------------------------------------------------
    ## Set the target acceleration(s) for axis(axes).
    #
    #  The target accelerations are stored in the SDH and are used only for:
    #  - the eCT_POSE controller type with eVP_RAMP velocity profile
    #  - the eCT_VELOCITY_ACCELERATION controller type
    #   
    #  Setting the target acceleration will not effect an ongoing movement,
    #  nor will it start a new movement. To take effect an additional command 
    #  must be sent:
    #  - in eCT_POSE controller type a move command: MoveAxis() MoveFinger() MoveHand()
    #  - in eCT_VELOCITY_ACCELERATION controller type the velocity must be set: SetAxisTargetVelocity(), SetAxisTargetGetAxisActualVelocity()
    #
    #  \param self     - reference to the object itself
    #  \param iAxis    - index of axis to access.
    #                    This can be All, a single index or a \ref sdhlibrary_python_sdh_py_csdh_vector "vector" of indices.
    #  \param acceleration - the acceleration to set or \c None to keep the currently set target acceleration of the axis
    #                    This can be a single number or a \ref sdhlibrary_python_sdh_py_csdh_vector "vector" of numbers.
    #                    The value(s) are expected in the configured angular acceleration unit system #uc_angular_acceleration.
    #  
    #  \remark
    #    - Setting the target acceleration will \b not make the axis/axes move.
    #    - If both \a iAxis and \a acceleration are vectors then the order of
    #      their elements must match, i.e. \c acceleration[i] will be applied
    #      to axis \c iAxis[i] (not axis \c i). 
    #    - If \a iAxis is \c All then the order will be the natural
    #      one (as if \a iAxis=[0,1,2,3,4,5,6] had been given
    #      
    #  \par Examples:
    #  \code
    #    # Assuming "hand" is a sdh.cSDH object ...
    #    
    #    # Set target axis acceleration of axis 3 to 100 deg/(s*s)
    #    hand.SetAxisTargetAcceleration( 3, 100 )
    #
    #    # Set target axis acceleration of axis 3 to 300 deg/(s*s) and axis 5 to 350 deg/(s*s)
    #    hand.SetAxisTargetAcceleration( [3,5], [300, 350] )
    #
    #    # Set target axis acceleration of all axes to 111
    #    hand.SetAxisTargetAcceleration( sdh.All, 111 )
    #
    #    # Set target axis acceleration of all axes to the given values
    #    hand.SetAxisTargetAcceleration( acceleration=[100, 101, 102, 103, 104, 105, 106 ] )
    #  
    #    # Set target axis acceleration of all axes to the currently set axis accelerations (well, this is not very usefull...)
    #    hand.SetAxisTargetAcceleration( acceleration=None )
    #  
    #    # Set target axis acceleration of axis 3 to 333 deg/(s*s) and keep axis 1 at its currently set target acceleration 
    #    hand.SetAxisTargetAcceleration( [3,1], acceleration=[333,None] )
    #  \endcode
    #  
    #  <hr>
    def SetAxisTargetAcceleration( self, iAxis=All, acceleration=None ):
        '''
        Set the target acceleration(s) for axis(axes)
        '''
        axes = self._ToIndexList( iAxis, self.all_axes, self.NUMBER_OF_AXES + self.NUMBER_OF_VIRTUAL_AXES, "axis" )
        # now axes is a list of all axis indices to access

        n = len(axes)
        accelerations = self._ToValueList( acceleration, n, self.uc_angular_acceleration.ToInternal )
        # now accelerations is a list of all axis accelerations in the
        # internal unit system (or None to set the current axis
        # acceleration)

        if (n != len(accelerations)):
            raise cSDHErrorInvalidParameter( "Lengths of iAxis and acceleration vectors do not match (%d != %d)" % (n, len(accelerations)) )


        # get all currently set accelerations
        all_accelerations = self.interface.a( All, None )

        # overwrite where selected with user given value:
        for (ai,v) in zip( axes, accelerations ):
            if (ai >= self.NUMBER_OF_AXES):    # handle virutal axes differently
                continue

            if (v is not None):
                # overwrite
                all_accelerations[ ai ] = v
            
        # and send to firmware
        self.interface.a( All, all_accelerations )
        
    #-----------------------------------------------------------------
    ## Get the target acceleration(s) of axis(axes).
    #
    #  The target accelerations are read from the SDH.
    #
    #  \param self  - reference to the object itself
    #  \param iAxis - index of axis to access.
    #                 This can be All, a single index or a \ref sdhlibrary_python_sdh_py_csdh_vector "vector" of indices.
    #
    #  \return
    #    - if \a iAxis is a single index then a single float value is returned
    #    - else a list of the selected axes target accelerations is returned
    #    - The value(s) are reported in the configured angular acceleration unit system #uc_angular_acceleration.
    #
    #  \remark
    #    - The order of the returned list (if any) depends on the
    #      order of the axis indices given in \a iAxis. I.E. if a list
    #      \c rc is returned, then \c rc[i] will be the target acceleration of axis
    #      \a iAxis[i] (not axis \c i).
    #    - If \a iAxis is \c All then the order will be the natural
    #      one (as if \a iAxis=[0,1,2,3,4,5,6] had been given
    #    
    #  \par Examples:
    #  \code
    #    # Assuming "hand" is a sdh.cSDH object ...
    #    
    #    # Get target axis acceleration of axis 3 
    #    v = hand.GetAxisTargetAcceleration( 3 )
    #    # v is now something like 100.0
    #
    #    # Get target axis acceleration of axis 3
    #    L = hand.GetAxisTargetAcceleration( [3] )
    #    # now L is something like [100.0]
    #    #   (if a vector is given as parameter then a list is returned,
    #    #    even if it contains a single element only)
    #
    #    # Get target axis acceleration of axis 3 and 5
    #    L = hand.GetAxisTargetAcceleration( [3,5] )
    #    # now L is something like [100.0, 100.0]
    #
    #    # Get target axis acceleration of all axes
    #    L = hand.GetAxisTargetAcceleration( sdh.All )
    #    # now L is something like [100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0 ]
    #
    #    # Get target axis acceleration of all axes 
    #    L = hand.GetAxisTargetAcceleration()
    #    # now L is something like [100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0 ]
    #  \endcode
    #  
    #  <hr>
    def GetAxisTargetAcceleration( self, iAxis=All ):
        '''
        Get the target acceleration(s) of axis(axes)
        '''
        axes = self._ToIndexList( iAxis, self.all_axes, self.NUMBER_OF_AXES + self.NUMBER_OF_VIRTUAL_AXES, "axis" )
        # now axes is a list of all axis indices to access

        if (type(iAxis) == int):
            return self.uc_angular_acceleration.ToExternal( self.interface.a( iAxis, None ) )
        else:
            # we want a list of (most likely) more than one acceleration, so 
            # read all accelerations at once to communicate as few as possible
            all_accelerations = self.interface.a( All, None )

            # append acceleration 0.0 for all virtual axes 
            all_accelerations += [ 0.0 ]*self.NUMBER_OF_VIRTUAL_AXES
            
            return [ self.uc_angular_acceleration.ToExternal( all_accelerations[ ai ] )   for ai in axes ]  # ANOTE: communicates more often than strictly necessary


    #-----------------------------------------------------------------
    ## Get the minimum angle(s) of axis(axes).
    #
    #  \param self  - reference to the object itself
    #  \param iAxis - index of axis to access.
    #                 This can be All, a single index or a \ref sdhlibrary_python_sdh_py_csdh_vector "vector" of indices.
    #
    #  \return
    #    - if \a iAxis is a single index then a single float value is returned
    #    - else a list of the selected axes minimum angles is returned
    #    - The value(s) are returned in the configured angle unit system #uc_angle.
    #
    #  \remark
    #    - The order of the returned list (if any) depends on the
    #      order of the axis indices given in \a iAxis. I.E. if a list
    #      \c rc is returned, then \c rc[i] will be the minimum
    #      angle of axis \a iAxis[i] (not axis \c i).
    #    - If \a iAxis is \c All then the order will be the natural
    #      one (as if \a iAxis=[0,1,2,3,4,5,6] had been given
    #    
    #
    #  \par Examples:
    #  \code
    #    # Assuming "hand" is a sdh.cSDH object ...
    #    
    #    # Get minimum axis angle of axis 3 
    #    v = hand.GetAxisMinAngle( 3 )
    #    # v is now something like -90.0
    #
    #    # Get minimum axis angle of axis 3
    #    L = hand.GetAxisMinAngle( [3] )
    #    # now L is something like [-90.0]
    #    #   (if a vector is given as parameter then a list is returned,
    #    #    even if it contains a single element only)
    #
    #    # Get minimum axis angle of axis 3 and 5
    #    L = hand.GetAxisMinAngle( [3,5] )
    #    # now L is something like [-90.0, -90.0]
    #
    #    # Get minimum axis angle of all axes
    #    L = hand.GetAxisMinAngle( sdh.All )
    #    # now L is something like [0.0, -90.0, -90.0, -90.0, -90.0, -90.0, -90.0]
    #
    #    # Get minimum axis angle of all axes 
    #    L = hand.GetAxisMinAngle()
    #    # now L is something like [0.0, -90.0, -90.0, -90.0, -90.0, -90.0, -90.0]
    #
    #    # Or if you change the angle unit system:
    #    hand.UseRadians()
    #    L = hand.GetAxisMinAngle()
    #    # now L is something like [0.0, -1.5707963267948966, -1.5707963267948966, -1.5707963267948966, -1.5707963267948966, -1.5707963267948966, -1.5707963267948966]
    #  \endcode
    #  
    #  <hr>
    def GetAxisMinAngle( self, iAxis=All ):
        '''
        Get the minimum angle(s) of axis(axes)
        '''
        axes = self._ToIndexList( iAxis, self.all_axes, self.NUMBER_OF_AXES + self.NUMBER_OF_VIRTUAL_AXES, "axis" )
        # now axes is a list of all axis indices to access

        if (type(iAxis) == int):
            return self.uc_angle.ToExternal( self.interface.p_min( iAxis, None ) )
        else:
            # we want a list of (most likely) more than one angle, so 
            # read all angles at once to communicate as few as possible
            all_angles = self.interface.p_min( All, None )

            # append minimum angle 0.0 for all virtual axes 
            all_angles += [ 0.0 ]*self.NUMBER_OF_VIRTUAL_AXES
            
            return [ self.uc_angle.ToExternal( all_angles[ ai ] )   for ai in axes ]  # ANOTE: communicates more often than strictly necessary

        
    #-----------------------------------------------------------------
    ## Get the maximum angle(s) of axis(axes).
    #
    #  \param self  - reference to the object itself
    #  \param iAxis - index of axis to access.
    #                 This can be All, a single index or a \ref sdhlibrary_python_sdh_py_csdh_vector "vector" of indices.
    #
    #  \return
    #    - if \a iAxis is a single index then a single float value is returned
    #    - else a list of the selected axes maximum angles is returned
    #    - The value(s) are returned in the configured angle unit system #uc_angle.
    #
    #  \remark
    #    - The order of the returned list (if any) depends on the
    #      order of the axis indices given in \a iAxis. I.E. if a list
    #      \c rc is returned, then \c rc[i] will be the maximum
    #      angle of axis \a iAxis[i] (not axis \c i).
    #    - If \a iAxis is \c All then the order will be the natural
    #      one (as if \a iAxis=[0,1,2,3,4,5,6] had been given
    #    
    #
    #  \par Examples:
    #  \code
    #    # Assuming "hand" is a sdh.cSDH object ...
    #    
    #    # Get maximum axis angle of axis 3 
    #    v = hand.GetAxisMaxAngle( 3 )
    #    # v is now something like 90.0
    #
    #    # Get maximum axis angle of axis 3
    #    L = hand.GetAxisMaxAngle( [3] )
    #    # now L is something like [90.0]
    #    #   (if a vector is given as parameter then a list is returned,
    #    #    even if it contains a single element only)
    #
    #    # Get maximum axis angle of axis 3 and 5
    #    L = hand.GetAxisMaxAngle( [3,5] )
    #    # now L is something like [90.0, 90.0]
    #
    #    # Get maximum axis angle of all axes
    #    L = hand.GetAxisMaxAngle( sdh.All )
    #    # now L is something like [90.0, 90.0, 90.0, 90.0, 90.0, 90.0, 90.0]
    #
    #    # Get maximum axis angle of all axes 
    #    L = hand.GetAxisMaxAngle()
    #    # now L is something like [90.0, 90.0, 90.0, 90.0, 90.0, 90.0, 90.0]
    #
    #    # Or if you change the angle unit system:
    #    hand.UseRadians()
    #    L = hand.GetAxisMaxAngle()
    #    # now L is something like [1.5707963267948966, 1.5707963267948966, 1.5707963267948966, 1.5707963267948966, 1.5707963267948966, 1.5707963267948966, 1.5707963267948966]
    #  \endcode
    #  
    #  <hr>
    def GetAxisMaxAngle( self, iAxis=All ):
        '''
        Get the maximum angle(s) of axis(axes)
        '''
        axes = self._ToIndexList( iAxis, self.all_axes, self.NUMBER_OF_AXES + self.NUMBER_OF_VIRTUAL_AXES, "axis" )
        # now axes is a list of all axis indices to access

        if (type(iAxis) == int):
            return self.uc_angle.ToExternal( self.interface.p_max( iAxis, None ) )
        else:
            # we want a list of (most likely) more than one angle, so 
            # read all angles at once to communicate as few as possible
            all_angles = self.interface.p_max( All, None )

            # append maximum angle 0.0 for all virtual axes 
            all_angles += [ 0.0 ]*self.NUMBER_OF_VIRTUAL_AXES
            
            return [ self.uc_angle.ToExternal( all_angles[ ai ] )   for ai in axes ]  # ??? communicates more often than strictly necessary


         
    #-----------------------------------------------------------------
    ## Get the offset angle(s) of axis(axes).
    #
    #  \param self  - reference to the object itself
    #  \param iAxis - index of axis to access.
    #                 This can be All, a single index or a \ref sdhlibrary_python_sdh_py_csdh_vector "vector" of indices.
    #
    #  \return
    #    - if \a iAxis is a single index then a single float value is returned
    #    - else a list of the selected axes offset angles is returned
    #    - The value(s) are returned in the configured angle unit system #uc_angle.
    #
    #  \remark
    #    - The order of the returned list (if any) depends on the
    #      order of the axis indices given in \a iAxis. I.E. if a list
    #      \c rc is returned, then \c rc[i] will be the offset
    #      angle of axis \a iAxis[i] (not axis \c i).
    #    - If \a iAxis is \c All then the order will be the natural
    #      one (as if \a iAxis=[0,1,2,3,4,5,6] had been given
    #    
    #
    #  \par Examples:
    #  \code
    #    # Assuming "hand" is a sdh.cSDH object ...
    #    
    #    # Get offset axis angle of axis 3 
    #    v = hand.GetAxisMaxAngle( 3 )
    #    # v is now something like 3.45
    #
    #    # Get offset axis angle of axis 3
    #    L = hand.GetAxisMaxAngle( [3] )
    #    # now L is something like [3.45]
    #    #   (if a vector is given as parameter then a list is returned,
    #    #    even if it contains a single element only)
    #
    #    # Get offset axis angle of axis 3 and 5
    #    L = hand.GetAxisMaxAngle( [3,5] )
    #    # now L is something like [3.45, 5.67]
    #
    #    # Get offset axis angle of all axes
    #    L = hand.GetAxisMaxAngle( sdh.All )
    #    # now L is something like [0.12, 1.23, 2.34, 3.45, 4.56, 5.67, 6.78]
    #
    #    # Get offset axis angle of all axes 
    #    L = hand.GetAxisMaxAngle()
    #    # now L is something like [0.12, 1.23, 2.34, 3.45, 4.56, 5.67, 6.78]
    #
    #    # Or if you change the angle unit system:
    #    hand.UseRadians()
    #    L = hand.GetAxisMaxAngle()
    #    # now L is something like [0.0020943951023931952, 0.021467549799530253, 0.04084070449666731, 0.06021385919380437, 0.079587013890941416, 0.09896016858807849, 0.11833332328521554]
    #  \endcode
    #  
    #  <hr>
    def GetAxisOffsetAngle( self, iAxis=All ):
        '''
        Get the offset angle(s) of axis(axes)
        '''
        axes = self._ToIndexList( iAxis, self.all_axes, self.NUMBER_OF_AXES + self.NUMBER_OF_VIRTUAL_AXES, "axis" )
        # now axes is a list of all axis indices to access

        if (type(iAxis) == int):
            return self.uc_angle.ToExternal( self.interface.p_offset( iAxis, None ) )
        else:
            # we want a list of (most likely) more than one angle, so 
            # read all angles at once to communicate as few as possible
            all_angles = self.interface.p_max( All, None )

            # append offset angle 0.0 for all virtual axes 
            all_angles += [ 0.0 ]*self.NUMBER_OF_VIRTUAL_AXES
            
            return [ self.uc_angle.ToExternal( all_angles[ ai ] )   for ai in axes ]  # ??? communicates more often than strictly necessary


         
    #-----------------------------------------------------------------
    ## Get the maximum velocity(s) of axis(axes).
    #
    #  The maximum velocitys are currently not read from the SDH, but are stored in the base class.
    #
    #  \param self  - reference to the object itself
    #  \param iAxis - index of axis to access.
    #                 This can be All, a single index or a \ref sdhlibrary_python_sdh_py_csdh_vector "vector" of indices.
    #
    #  \return
    #    - if \a iAxis is a single index then a single float value is returned
    #    - else a list of the selected axes maximum velocitys is returned
    #
    #  \remark
    #    - The order of the returned list (if any) depends on the
    #      order of the axis indices given in \a iAxis. I.E. if a list
    #      \c rc is returned, then \c rc[i] will be the maximum
    #      velocity of axis \a iAxis[i] (not axis \c i).
    #    - If \a iAxis is \c All then the order will be the natural
    #      one (as if \a iAxis=[0,1,2,3,4,5,6] had been given
    #    
    #
    #  \par Examples:
    #  \code
    #    # Assuming "hand" is a sdh.cSDH object ...
    #    
    #    # Get maximum axis velocity of axis 3 
    #    v = hand.GetAxisMaxVelocity( 3 )
    #    # v is now something like 100.0
    #
    #    # Get maximum axis velocity of axis 3
    #    L = hand.GetAxisMaxVelocity( [3] )
    #    # now L is something like [100.0]
    #    #   (if a vector is given as parameter then a list is returned,
    #    #    even if it contains a single element only)
    #
    #    # Get maximum axis velocity of axis 3 and 5
    #    L = hand.GetAxisMaxVelocity( [3,5] )
    #    # now L is something like [100.0, 100.0]
    #
    #    # Get maximum axis velocity of all axes
    #    L = hand.GetAxisMaxVelocity( sdh.All )
    #    # now L is something like [100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0]
    #
    #    # Get maximum axis velocity of all axes 
    #    L = hand.GetAxisMaxVelocity()
    #    # now L is something like [100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0]
    #
    #    # Or if you change the velocity unit system:
    #    hand.UseRadians()
    #    L = hand.GetAxisMaxVelocity()
    #    # now L is something like [0.488692190, 1.74532925, 1.74532925, 1.74532925, 1.74532925, 1.74532925, 1.74532925]
    #  \endcode
    #  
    #  <hr>
    def GetAxisMaxVelocity( self, iAxis=All ):
        '''
        Get the maximum velocity(s) of axis(axes)
        '''
        axes = self._ToIndexList( iAxis, self.all_axes, self.NUMBER_OF_AXES + self.NUMBER_OF_VIRTUAL_AXES, "axis" )
        # now axes is a list of all axis indices to access

        if (type(iAxis) == int):
            return self.uc_angular_velocity.ToExternal( self.f_max_velocity_a[ iAxis ] )
        else:
            return [ self.uc_angular_velocity.ToExternal( self.f_max_velocity_a[ ai ] )   for ai in axes ]


    #-----------------------------------------------------------------
    ## Get the maximum acceleration(s) of axis(axes).
    #
    #  The maximum accelerations are currently not read from the SDH, but are stored in the base class.
    #
    #  \param self  - reference to the object itself
    #  \param iAxis - index of axis to access.
    #                 This can be All, a single index or a \ref sdhlibrary_python_sdh_py_csdh_vector "vector" of indices.
    #
    #  \return
    #    - if \a iAxis is a single index then a single float value is returned
    #    - else a list of the selected axes maximum accelerations is returned
    #
    #  \remark
    #    - The order of the returned list (if any) depends on the
    #      order of the axis indices given in \a iAxis. I.E. if a list
    #      \c rc is returned, then \c rc[i] will be the maximum
    #      acceleration of axis \a iAxis[i] (not axis \c i).
    #    - If \a iAxis is \c All then the order will be the natural
    #      one (as if \a iAxis=[0,1,2,3,4,5,6] had been given
    #    
    #
    #  \par Examples:
    #  \code
    #    # Assuming "hand" is a sdh.cSDH object ...
    #    
    #    # Get maximum axis acceleration of axis 3 
    #    v = hand.GetAxisMaxAcceleration( 3 )
    #    # v is now something like 1000.0
    #
    #    # Get maximum axis acceleration of axis 3
    #    L = hand.GetAxisMaxAcceleration( [3] )
    #    # now L is something like [1000.0]
    #    #   (if a vector is given as parameter then a list is returned,
    #    #    even if it contains a single element only)
    #
    #    # Get maximum axis acceleration of axis 3 and 5
    #    L = hand.GetAxisMaxAcceleration( [3,5] )
    #    # now L is something like [1000.0, 1000.0]
    #
    #    # Get maximum axis acceleration of all axes
    #    L = hand.GetAxisMaxAcceleration( sdh.All )
    #    # now L is something like [1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0]
    #
    #    # Get maximum axis acceleration of all axes 
    #    L = hand.GetAxisMaxAcceleration()
    #    # now L is something like [1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0]
    #
    #    # Or if you change the acceleration unit system:
    #    hand.UseRadians()
    #    L = hand.GetAxisMaxAcceleration()
    #    # now L is something like [17.4532925, 17.4532925, 17.4532925, 17.4532925, 17.4532925, 17.4532925, 17.4532925]
    #  \endcode
    #  
    #  <hr>
    def GetAxisMaxAcceleration( self, iAxis=All ):
        '''
        Get the maximum acceleration(s) of axis(axes)
        '''
        axes = self._ToIndexList( iAxis, self.all_axes, self.NUMBER_OF_AXES + self.NUMBER_OF_VIRTUAL_AXES, "axis" )
        # now axes is a list of all axis indices to access

        if (type(iAxis) == int):
            return self.uc_angular_acceleration.ToExternal( self.f_max_acceleration_a[ iAxis ] )
        else:
            return [ self.uc_angular_acceleration.ToExternal( self.f_max_acceleration_a[ ai ] )   for ai in axes ]



         
    # unimplemented from SAH:
    # def GetJointAngle( self, int iFinger,float* pafAngle):
    # def GetJointSpeed( self, int iFinger,float* pafSpeed):
    # def GetJointTorque( self, int iFinger,float* pafTorque):


    #  end of doxygen name group sdhlibrary_python_sdh_py_csdh_axis
    ## @}
    ######################################################################
        
    #######################################################################
    ## \anchor Sdhlibrary_python_sdh_py_csdh_finger
    #  \name   Methods to access SDH on finger-level
    #  
    #  @{

    #-----------------------------------------------------------------
    ## Set enabled/disabled state of axis controllers of finger(s).
    #
    #  \param self    - reference to the object itself
    #  \param iFinger - index of finger to access.
    #                   This can be All, a single index or a \ref sdhlibrary_python_sdh_py_csdh_vector "vector" of indices.
    #  \param state   - flag: the enabled/disabled state to set
    #                   This can be a single number/bool or a \ref sdhlibrary_python_sdh_py_csdh_vector "vector" of numbers/bools.
    #  
    #  \remark
    #    - Only enabled fingers can move.
    #    - The axes of disabled fingers are not powered and thus might
    #      not remain in their current position due to gravity, inertia
    #      or other external influences.
    #    - As axis 0 is used for finger 0 and 2, axis 0 is disabled only 
    #      if both finger 0 and 1 are disabled.
    #    - If both \a iFinger and \a state are vectors then the order of
    #      their elements must match, i.e. \c state[i] will be applied
    #      to all axes of finger \c iFinger[i] (not finger \c i).
    #    - If \a iFinger is \c All then the order will be the natural
    #      one (as if \a iFinger=[0,1,2] had been given
    #
    #  \par Examples:
    #  \code
    #    # Assuming "hand" is a sdh.cSDH object ...
    #    
    #    # Enable all fingers:
    #    hand.SetFingerEnable( sdh.All, True )
    #    
    #    # Disable all fingers:
    #    hand.SetFingerEnable( state = 0 )
    #    
    #    # Enable finger 1 and 2 while disabling finger 0 :
    #    hand.SetFingerEnable( sdh.All, (False,True, True) )
    #    # (this will keep axis 0 (used by finger 0) enabled, as axis 0 is needed by finger 2 too)
    #
    #    # Disable finger 2:
    #    hand.SetFingerEnable( 2, False )
    #    
    #    # Enable fingers 0 and 2
    #    hand.SetFingerEnable( [0,2], [True,1] )
    #  \endcode
    #  
    #  <hr>
    def SetFingerEnable( self, iFinger=All, state=True ):
        '''
        Set enabled/disabled state of finger(s). See html/pdf documentation for details.
        '''
        fingers = self._ToIndexList( iFinger, self.all_fingers, self.NUMBER_OF_FINGERS, "finger" )
        # now fingers is a list of all finger indices to access

        n = len(fingers)
        states = self._ToValueList( state, n, int )
        # now states is a list of all axis states 

        if (n != len(states)):
            raise cSDHErrorInvalidParameter( "Lengths of iFinger and state vectors do not match (%d != %d)" % (n, len(states)) )

        # get current axis states
        all_states = self.GetAxisEnable() + [ True ]*self.NUMBER_OF_VIRTUAL_AXES
        axis0_state = all_states[0]
        
        for (fi,fsi) in zip(fingers, range(0,len(fingers))):
            self.CheckIndex( fi, self.NUMBER_OF_FINGERS, "finger" )
            for fai in range( 0, self.NUMBER_OF_AXES_PER_FINGER ):
                # set axes of selected fingers to given state
                all_states[ self.GetFingerAxisIndex( fi, fai ) ] = states[fsi]
        
        #  As axis 0 is used for finger 0 and 2 it is disabled only if
        #  both finger 0 and 2 are disabled.
        for (fi,fsi) in zip(fingers, range(0,len(fingers))):
            if (axis0_state   and   not states[fsi]   and   0 in self.finger_axis_index[ fi ]):
                # yes axis0 was enabled before and we are disabling a finger that is using axis 0
            
                # set other finger that uses axis 0 to False as default state
                other_finger_state = False
                for ofi in self.all_fingers:
                    if (ofi in fingers  or  0 not in self.finger_axis_index[ ofi ]): continue
                    for fai in range(0, self.GetFingerNumberOfAxes(ofi)):
                        # 'or' the  state of the other axes of the other finger that uses axis 0 to it
                        # (this will be used to keep axis 0 enabled if at least one of the axes of the other
                        # finger that uses axis 0 is enabled)
                        other_finger_state = other_finger_state or all_states[ self.GetFingerAxisIndex( ofi, fai ) ] 

                all_states[ 0 ] = other_finger_state

        # now send to SDH
        self.interface.power( All, all_states[0:self.NUMBER_OF_AXES] )

    #-----------------------------------------------------------------
    ## Get enabled/disabled state of axis controllers of finger(s).
    #
    #  The enabled/disabled state of the controllers of the selected
    #  fingers is read from the SDH. A finger is reported disabled if
    #  any of its axes is disabled and reported enabled if all its
    #  axes are enabled.
    #    
    #  \param self    - reference to the object itself
    #  \param iFinger - index of finger to access.
    #                   This can be All, a single index or a \ref sdhlibrary_python_sdh_py_csdh_vector "vector" of indices.
    #
    #  \return
    #    - if \a iFinger is a single index then a single int value \c (0|1) is returned
    #    - else a list of the selected fingers enabled states as int values \c (0|1) is returned
    #
    #  \remark
    #    - The order of the returned list (if any) depends on the
    #      order of the finger indices given in \a iFinger. I.E. if a list
    #      \c rc is returned, then \c rc[i] will be the enabled state of finger
    #      \a iFinger[i] (not finger \c i).
    #    - If \a iFinger is \c All then the order will be the natural
    #      one (as if \a iFinger=[0,1,2] had been given
    #    
    #  \par Examples:
    #  \code
    #    # Assuming "hand" is a sdh.cSDH object ...
    #    
    #    # Get enabled state of all fingers:
    #    L = hand.GetFingerEnable( sdh.All )
    #    # now L is something like [0,1,0]
    #    
    #    # Get enabled state of finger 0 and 2
    #    L = hand.GetFingerEnable( [0,2] )
    #    # now L is something like [0,0]
    #
    #    # Get enabled state of finger 1  
    #    v = hand.GetFingerEnable( 1 )
    #    # now v is something like 1
    #    
    #    # Get enabled state of finger 0
    #    L = hand.GetFingerEnable( [0] )
    #    # now L is something like [0]
    #    #   (if a vector is given as parameter then a list is returned,
    #    #    even if it contains a single element only)
    #  \endcode
    #  
    #  <hr>
    def GetFingerEnable( self, iFinger=All ):
        '''
        Get enabled/disabled state of finger(s). See html/pdf documentation for details.
        '''
        fingers = self._ToIndexList( iFinger, self.all_fingers, self.NUMBER_OF_FINGERS, "finger" )
        # now fingers is a list of all finger indices to access

        return [ Alltrue( self.GetAxisEnable( self.finger_axis_index[fi] ) )   for fi in fingers ]


    #-----------------------------------------------------------------
    ## Set the target angle(s) for a single finger.
    #
    #  The target axis angles \a angle of finger \a iFinger are stored
    #  in the SDH. The movement is not executed until an additional
    #  move command is sent.
    #
    #  \param self    - reference to the object itself
    #  \param iFinger - index of finger to access.
    #                   This must be a single index.
    #  \param angle   - the angle(s) to set or \c None to set the current actual axis angles of the finger as target angle.
    #                   This can be a single number or a \ref sdhlibrary_python_sdh_py_csdh_vector "vector" of numbers.
    #                   The value(s) are expected in the configured angle unit system #uc_angle.
    #  
    #  \remark
    #    - Setting the target angles will \b not make the finger move.
    #
    #  \par Examples:
    #  \code
    #    # Assuming "hand" is a sdh.cSDH object ...
    #    
    #    # Set target axis angles of finger 0 to [ 10.0, -08.15, 47.11 ]
    #    hand.SetFingerTargetAngle( 0, [ 10.0, -08.15, 47.11 ] )
    #
    #    # Set target axis angles of finger 1 to [ 0.0, 24.7, 17.4 ]
    #    hand.SetFingerTargetAngle( 1, [ 0.0, 24.7, 17.4 ] )
    #
    #    # Set target axis angles of all axes of finger 0 to 12.34
    #    hand.SetFingerTargetAngle( 0, 12.34 )
    #
    #    # Setting target axis angles of all axes of finger 1 to 42.0
    #    # would result in cSDHErrorInvalidParameter exception since the virtual
    #    # axis 0 of finger 1 can only be set to 0.0
    #    
    #    # Set target axis angles of all axes of finger 2 to their current actual angles
    #    hand.SetFingerTargetAngle( 2, None )
    #  \endcode
    #  
    #  <hr>
    def SetFingerTargetAngle( self, iFinger, angle=None ):
        '''
        Set the target axis angles for a single finger. See html/pdf documentation for details.
        '''
        self.CheckIndex( iFinger, self.NUMBER_OF_FINGERS, "finger" )
        
        angles = self._ToValueList( angle, self.GetFingerNumberOfAxes( iFinger ), self.uc_angle.ToInternal )
        # now angles is a list of all axis angles of the finger in the
        # internal unit system (or None to set current actual finger
        # axis angle)
        # ??? the angles are not checked here

        finger_axes = self.finger_axis_index[iFinger]

        if ( len( angles ) != len( finger_axes ) ):
            raise cSDHErrorInvalidParameter( "Number of finger %d finger axes and angle vectors do not match (%d != %d)" % (iFinger, len(finger_axes),len(angles)) )


        # get currently set target axis angles
        # cannot use self.GetAxisTargetAngle() here, since we need internal units
        t_ang = self.interface.p(All)

        # now overwrite the axes of finger iFinger
        # with the user given target angles or if that is None: the current actual angle
        c_ang = None
        for (ai,a) in zip( finger_axes, angles ):
            if (ai >= self.NUMBER_OF_AXES):
                # virtual axes are just checked:
                if ( a is not None):
                    self.CheckRange(a, self.f_min_angle_a[ai], self.f_max_angle_a[ai], "virtual axis %d angle" % ai )
                continue
            
            if (a is None):
                if (c_ang is None):
                    # cannot use self.GetAxisActualAngle() here since we need internal units
                    c_ang = self.interface.pos(All)
                # limit the angle to the allowed range since c_ang might be slightly off range due to positioning inaccuracies
                t_ang[ ai ] = ToRange( c_ang[ ai ], self.f_min_angle_a[ai], self.f_max_angle_a[ai] )
            else:
                t_ang[ ai ] = a

        # now the modified t_ang is the complete new target angle vector to write, so send to firmware
        
        # cannot use self.SetAxisTargetAngle() here since that expects external units, but t_ang is in internal units
        self.interface.p( All, t_ang )

        
    #-----------------------------------------------------------------
    ## Get the target axis angles of a single finger.
    #
    #  The target axis angles of finger \a iFinger are read from the SDH.
    #
    #  \param self    - reference to the object itself
    #  \param iFinger - index of finger to access.
    #                   This must be a single index
    #
    #  \return
    #    - A list of the selected fingers target axis angles
    #    - The values are returned in the configured angle unit system #uc_angle.
    #
    #  \par Examples:
    #  \code
    #    # Assuming "hand" is a sdh.cSDH object ...
    #    
    #    # Get target axis angle of finger 0
    #    L = hand.GetFingerTargetAngle( 0 )
    #    # now L is something like [42.0, -10.0, 47.11]
    #
    #    # Get target axis angle of finger 1
    #    L = hand.GetFingerTargetAngle( 1 )
    #    # now L is something like [0.0, 24.7, -5.5]
    #  \endcode
    #  
    #  <hr>
    def GetFingerTargetAngle( self, iFinger ):
        '''
        Get the target axis angles of a single finger. See html/pdf documentation for details.
        '''
        self.CheckIndex( iFinger, self.NUMBER_OF_FINGERS, "finger" )
        
        finger_axes = self.finger_axis_index[iFinger]

        return self.GetAxisTargetAngle( finger_axes )


    #-----------------------------------------------------------------
    ## Get the current actual axis angles of a single finger.
    #
    #  The current actual axis angles of finger \a iFinger are read from the SDH.
    #
    #  \param self    - reference to the object itself
    #  \param iFinger - index of finger to access.
    #                   This must be a single index.
    #
    #  \return
    #    - A list of the current actual axis angles of the selected finger
    #    - The values are returned in the configured angle unit system #uc_angle.
    #
    #  \par Examples:
    #  \code
    #    # Assuming "hand" is a sdh.cSDH object ...
    #    
    #    # Get actual axis angles of finger 0 
    #    L = hand.GetFingerActualAngle( 0 )
    #    # L is now something like [42.0, -10.0, 47.11]
    #
    #    # Get actual axis angles of finger 1
    #    L = hand.GetFingerActualAngle( 1 )
    #    # now L is something like [0.0, 24.7, -5.5]
    #  \endcode
    #  
    #  <hr>
    def GetFingerActualAngle( self, iFinger ):
        '''
        Get the current actual axis angles of a single finger. See html/pdf documentation for details.
        '''
        self.CheckIndex( iFinger, self.NUMBER_OF_FINGERS, "finger" )
        
        finger_axes = self.finger_axis_index[iFinger]

        return self.GetAxisActualAngle( finger_axes )

    
    #-----------------------------------------------------------------
    ## Get the minimum axis angles of a single finger.
    #
    #  \param self    - reference to the object itself
    #  \param iFinger - index of finger to access.
    #                   This must be a single index
    #
    #  \return
    #    - A list of the selected fingers minimum axis angles
    #    - The values are returned in the configured angle unit system #uc_angle.
    #
    #  \par Examples:
    #  \code
    #    # Assuming "hand" is a sdh.cSDH object ...
    #    
    #    # Get minimum axis angles of finger 0
    #    L = hand.GetFingerMinAngle( 0 )
    #    # now L is something like [0.0, -90.0, -90.0]
    #
    #    # Get minimum axis angles of finger 1
    #    L = hand.GetFingerMinAngle( 1 )
    #    # now L is something like [0.0, -90.0, -90.0]
    #
    #    # Or if you change the angle unit system:
    #    hand.UseRadians()
    #    L = hand.GetFingerMinAngle( 0 )
    #    # now L is something like [0.0, -1.5707963267948966, -1.5707963267948966]
    #
    #  \endcode
    #  
    #  <hr>
    def GetFingerMinAngle( self, iFinger ):
        '''
        Get the minimum axis angles of a single finger. See html/pdf documentation for details.
        '''
        self.CheckIndex( iFinger, self.NUMBER_OF_FINGERS, "finger" )
        
        finger_axes = self.finger_axis_index[iFinger]

        return self.GetAxisMinAngle( finger_axes )


    #-----------------------------------------------------------------
    ## Get the maximum axis angles of a single finger.
    #
    #  The maximum axis angles of finger \a iFinger are read from the base class and returned.
    #
    #  \param self    - reference to the object itself
    #  \param iFinger - index of finger to access.
    #                   This must be a single index
    #
    #  \return
    #    - A list of the selected fingers maximum axis angles
    #    - The values are returned in the configured angle unit system #uc_angle.
    #
    #  \par Examples:
    #  \code
    #    # Assuming "hand" is a sdh.cSDH object ...
    #    
    #    # Get maximum axis angles of finger 0
    #    L = hand.GetFingerMaxAngle( 0 )
    #    # now L is something like [90.0, 90.0, 90.0]
    #
    #    # Get maximum axis angles of finger 1
    #    L = hand.GetFingerMaxAngle( 1 )
    #    # now L is something like [0.0, 90.0, 90.0]
    #
    #    # Or if you change the angle unit system:
    #    hand.UseRadians()
    #    L = hand.GetFingerMaxAngle( 0 )
    #    # now L is something like [1.5707963267948966, 1.5707963267948966, 1.5707963267948966]
    #  \endcode
    #  
    #  <hr>
    def GetFingerMaxAngle( self, iFinger ):
        '''
        Get the maximum axis angles of a single finger. See html/pdf documentation for details.
        '''
        self.CheckIndex( iFinger, self.NUMBER_OF_FINGERS, "finger" )
        
        finger_axes = self.finger_axis_index[iFinger]

        return self.GetAxisMaxAngle( finger_axes )


    #-----------------------------------------------------------------
    ## Get the xyz finger tip position of a single finger.
    #
    #  
    #  \param self    - reference to the object itself
    #  \param iFinger - index of finger to access.
    #                   This must be a single index
    #  \param angles - a vector of NUMBER_OF_AXES_PER_FINGER angles (in external units, see #uc_angle)
    #                  If the default \c None is used then the current actual axis angles are read from
    #                  the SDH and used.
    #                  The values are expected in the configured angle unit system #uc_angle.
    #                  
    #  \return
    #    - A list of the x,y,z values of the finger tip position
    #    - The values are returned in the configured position unit system #uc_position.
    #
    #  \par Examples:
    #  \code
    #    # Assuming "hand" is a sdh.cSDH object ...
    #    
    #    # Get actual finger tip position of finger 0:
    #    P = hand.GetFingerXYZ( 0 )
    #    # now P is something like [18.821618775581801, 32.600000000000001, 174.0]
    #    # if finger 0 is at axis angles [0,0,0]
    #
    #    # Get finger tip position of finger 0 at axis angles [90,-90,-90]:
    #    P = hand.GetFingerXYZ( 0, [90,-90,-90] )
    #    # now P is something like [18.821618775581804, 119.60000000000002, -53.0]
    #
    #    # Or if you change the angle unit system:
    #    hand.UseRadians()
    #    P = hand.GetFingerXYZ( 0, [1.5707963267948966, -1.5707963267948966, -1.5707963267948966] )
    #    # now P is still something like [18.821618775581804, 119.60000000000002, -53.0]
    #
    #    # Or if you change the position unit system too:
    #    hand.uc_position = sdh.uc_position_meter
    #    P = hand.GetFingerXYZ( 0, [1.5707963267948966, -1.5707963267948966, -1.5707963267948966] )
    #    # now P is still something like [0.018821618775581, 0.119.60000000000002, -0.052999999999]
    #  \endcode
    #  
    #  <hr>
    def GetFingerXYZ( self, iFinger, angles=None ):
        '''
        Get the xyz finger tip position of a single finger.
        '''
        self.CheckIndex( iFinger, self.NUMBER_OF_FINGERS, "finger" )

        if (angles is None):
            finger_axes = self.finger_axis_index[iFinger]
            angles = self.GetAxisActualAngle( finger_axes )

        # The internal _GetFingerXYZ expects angles in radians, so convert:
        angles_rad = self._AnglesToRad( angles )
        
        # get xyz in internal unit (mm) and return converted to external
        return map( self.uc_position.ToExternal, self._GetFingerXYZ( iFinger, angles_rad ) ) # pylint: disable-msg=W0141


    #-----------------------------------------------------------------
    ## Check for internal collisions at the given finger angles
    #
    #  \param self - reference to the object itself
    #  \param f0aa - a vector of NUMBER_OF_AXES_PER_FINGER angles for
    #                finger 0. If the default \c None is used then the
    #                current actual axis angles are read from the SDH
    #                and used.
    #  \param f1aa - a vector of NUMBER_OF_AXES_PER_FINGER angles for
    #                finger 1. If the default \c None is used then the
    #                current actual axis angles are read from the SDH
    #                and used.
    #  \param f2aa - a vector of NUMBER_OF_AXES_PER_FINGER angles for
    #                finger 2. If the default \c None is used then the
    #                current actual axis angles are read from the SDH
    #                and used.
    #  \param iv_filename - A filename for an OpenInventor ivfile to generate or None
    #
    #  \return a tuple (cxy, (c01, d01), (c02,d02), (c12, d12) ) with:
    #  - cxy is True if there are any internal finger collisions
    #  - c01 is True if finger 0 and 1 collide
    #  - c02 is True if finger 0 and 2 collide
    #  - c12 is True if finger 1 and 2 collide
    #  - d01 is the minimum distance of fingers 0 and 1
    #  - d02 is the minimum distance of fingers 0 and 2
    #  - d12 is the minimum distance of fingers 1 and 2
    #
    #  \remark
    #  - The angle values are expected in the configured angle unit
    #    system #uc_angle.
    #  - the returned distance is given in the configured position
    #    unit system #uc_position.
    #  - If all the angle values are given (not \c None) then no
    #    communication is performed with the SDH. This function can
    #    then be used 'offline'.
    #  - The finger joint angles must be given as the corresponding
    #    parameter, i.e. giving the joint angles of finger 0 as f2aa and
    #    those of finger 2 as f0aa will NOT work!
    #
    #  <hr>
    def CheckFingerCollisions( self, f0aa=None, f1aa=None, f2aa=None, iv_filename=None ):

        if f0aa is None: f0aa = self.GetFingerActualAngle( 0 )
        if f1aa is None: f1aa = self.GetFingerActualAngle( 1 )
        if f2aa is None: f2aa = self.GetFingerActualAngle( 2 )

        # The internal _GetFingerSphereHull expects angles in radians, so convert:
        f0aa_rad = self._AnglesToRad( f0aa )
        f1aa_rad = self._AnglesToRad( f1aa )
        f2aa_rad = self._AnglesToRad( f2aa )

        # potential speed up: reuse of generated hulls !!!
        hulls = [ self._GetFingerSphereHull( 0, f0aa_rad ),
                  self._GetFingerSphereHull( 1, f1aa_rad ),
                  self._GetFingerSphereHull( 2, f2aa_rad ) ]
        
        results = []
        cxy = False
        for  fi in range( 0, 2 ):
            for fj in range( fi+1, 3):
                (cij,dij) = self._GetFingerHullCollision( hulls[ fi ], hulls[ fj ] )
                
                results.append( (cij,self.uc_position.ToExternal( dij )) )
                cxy = cxy or cij

        if iv_filename is not None:
            WriteIVFile( iv_filename, hulls )
    	    
        return ( cxy, results[0], results[1], results[2] )


    #-----------------------------------------------------------------
    ## Move one or more axes to the previously set target position with
    #  the previously set (maximum) velocities.
    #
    #
    #  \param self  - reference to the object itself
    #  \param iAxis -   index of axis to access.
    #                   This can be All, a single index or a \ref sdhlibrary_python_sdh_py_csdh_vector "vector" of indices.
    #  \param sequ    - flag: if True (default) then the function executes sequentially
    #                   and returns not until after the SDH has
    #                   finished the movement. If False then the
    #                   function returns immediately after the
    #                   movement command has been sent to the SDH
    #                   (the currently set target axis angles for other axes will
    #                   then be overwritten with their current actual
    #                   axis angles).
    #  \param check_collisions - flag: If True (default) then
    #                   collisions between the set target angles of
    #                   the selected axes \a iAxes and the actual angles of the
    #                   other axes are checked. If a collision is
    #                   detected then the movement is \b NOT performed
    #                   and a cSDHErrorInternalCollision exception is
    #                   thrown.
    #                   If False then no collision check is performed. 
    #
    #  \return The expected execution time for the movement in the configured time unit system #uc_time
    #
    #  \remark
    #    - Currently the actual movement velocity of an axis is
    #      determined by the SDH firmware to make the movements of all
    #      involved axes start and end synchronously at the same time. Therefore
    #      the axis that needs the longest time for its movement at its
    #      given maximum velocity determines the velocities of all the
    #      other axes.
    #    - Other axes than \a iAxis will \b NOT move, even if
    #      target axis angles for their axes have been set.
    #    - If \a sequ is True then the currently set target axis angles for other
    #      axes will be restored upon return of the function.
    #    - If \a sequ is False then the currently set target axis angles for other
    #      axes will be overwritten with their current actual axis angles
    #
    #  
    #  \par Examples:
    #  \code
    #    # Assuming 'hand' is a sdh.cSDH object ...
    #  
    #    # Set a new target pose for axis 0:
    #    hand.SetAxisTargetAngle( 0, 0 )
    #
    #    # Set a new target pose for axis 1,2 and 3
    #    hand.SetAxisTargetAngle( [1, 2, 3], [-10,-20,-30] )
    #
    #    # Move axis 0 only 
    #    hand.MoveAxis( 0, True )
    #    # The axis 0 has been moved to 0.0
    #
    #    # The target poses for axis 1,2 and 3 are still set since the
    #    # last MoveAxis() call was sequentially.
    #    # So move axis 1 and 2 now:
    #    t = hand.MoveAxis( [1,2], False )
    #  
    #    # wait until the non-sequential call has finished:
    #    sdh.time.sleep( t )
    #
    #    # The axis 1 has been moved to -10 and axis 2 to -20
    #
    #    # The target angles for axis 3 have been overwritten since the 
    #    # last MoveAxis() call was non-sequentially.
    #  
    #  \endcode
    #
    #  \bug
    #  With SDH firmware < 0.0.2.7 calling MoveAxis() while some axes are moving 
    #  in eCT_POSE controller type will make the joints jerk.
    #  This is resolved in %SDH firmware 0.0.2.7 for the eCT_POSE controller type with
    #  velocity profile eVP_RAMP. For the eCT_POSE controller type with velocity profile
    #  eVP_SIN_SQUARE changing target points/ velocities while moving will still make 
    #  the axes jerk. 
    #  <br><b>=> Partly resolved in SDH firmware 0.0.2.7</b>
    #  <hr>
    def MoveAxis( self, iAxis, sequ=True, check_collisions=True ):
        '''
        Move an axis or some axes to the previously set target positions with
        the previously set (maximum) target velocities. See html/pdf
        documentation for details.
        '''
        axes = self._ToIndexList( iAxis, self.all_axes, self.NUMBER_OF_AXES + self.NUMBER_OF_VIRTUAL_AXES, "axis" )
        # now axes is a list of all axis indices to access

        # save currently set target axis angles of all axes (in external units)
        t_angles = self.GetAxisTargetAngle( All )

        # save current actual axis angles of all axes (in external units)
        a_angles = ToRange_a( self.GetAxisActualAngle( All ), self.f_min_angle_a, self.f_max_angle_a )

        #---------------------
        # generate new target axis angles:
        # - actual axis angle for other axes
        # - target axis angle for iAxiss axes
        #
        for ai in axes:
            if (ai >= self.NUMBER_OF_AXES): # skip virtual axes
                continue
            # set new target axis angles for the axes selected by iAxis in actual axis angles
            a_angles[ ai ] = t_angles[ ai ]
         
        #---------------------

        #---------------------
        if check_collisions:
            fingers_angles = self._AxisAnglesToFingerAngles( a_angles )
            
            (cxy, (c01,d01), (c02,d02), (c12,d12)) = self.CheckFingerCollisions( fingers_angles[0], fingers_angles[1], fingers_angles[2] )
            if cxy:
                self.dbg << "Internal collision detected in MoveAxis():" # pylint: disable-msg=W0104
                self.dbg.var( "cxy c01 d01 c02 d02 c12 d12" )
                raise cSDHErrorInternalCollision( "Potential internal collision detected, movement not executed!\n" )
        #---------------------
        
        
        # set modified actual axis angles as new target axis angles
        self.SetAxisTargetAngle( All, a_angles )
        # and move there
        t = self.interface.m(sequ)

        # restore the saved target axis angle so that previously set
        # target axis angles for other axes remain active
        if sequ:
            self.WaitAxis( axes )

            self.SetAxisTargetAngle( All, t_angles )
            
        return self.uc_time.ToExternal( t )


    #-----------------------------------------------------------------
    ## Get Duration of movement of one or more axes to the previously 
    #  set target position with the previously set (maximum) velocities.
    #
    #  \param self  - reference to the object itself
    #  \param iAxis -   index of axis to access.
    #                   This can be All, a single index or a \ref sdhlibrary_python_sdh_py_csdh_vector "vector" of indices.
    #
    #  \return The expected execution time for the movement in the configured time unit system #uc_time
    #
    #  \remark
    #    - Currently the actual movement velocity of an axis is
    #      determined by the SDH firmware to make the movements of all
    #      involved axes start and end synchronously at the same time. Therefore
    #      the axis that needs the longest time for its movement at its
    #      given maximum velocity determines the velocities of all the
    #      other axes.
    #    - Other axes than \a iAxis will \b NOT move, even if
    #      target axis angles for their axes have been set.
    #    - If \a sequ is True then the currently set target axis angles for other
    #      axes will be restored upon return of the function.
    #    - If \a sequ is False then the currently set target axis angles for other
    #      axes will be overwritten with their current actual axis angles
    #
    #  
    #  \par Examples:
    #  \code
    #    # Assuming 'hand' is a sdh.cSDH object ...
    #  
    #    # Set a new target pose for axis 0:
    #    hand.SetAxisTargetAngle( 0, 0 )
    #
    #    # Set a new target pose for axis 1,2 and 3
    #    hand.SetAxisTargetAngle( [1, 2, 3], [-10,-20,-30] )
    #
    #    # Get duration for moving axis 0 only 
    #    t = hand.GetDuration( 0 )
    #    # The axis 0 would move for t seconds.
    #
    #    # The target poses for axis 1,2 and 3 are still set since the
    #    # last GetDuration() call did not really change the target positions set.
    #    # So get duration of movement of axis 1 and 2 now:
    #    t = hand.GetDuration( [1,2] )
    #  
    #  \endcode
    #
    #  <hr>
    def GetDuration( self, iAxis ):
        '''
        Get duration of a movement of an axis or some axes to the previously 
        set target positions with the previously set (maximum) target velocities. 
        See html/pdf documentation for details.
        '''
        axes = self._ToIndexList( iAxis, self.all_axes, self.NUMBER_OF_AXES + self.NUMBER_OF_VIRTUAL_AXES, "axis" )
        # now axes is a list of all axis indices to access

        # save currently set target axis angles of all axes (in external units)
        t_angles = self.GetAxisTargetAngle( All )

        # save current actual axis angles of all axes (in external units)
        a_angles = ToRange_a( self.GetAxisActualAngle( All ), self.f_min_angle_a, self.f_max_angle_a )

        #---------------------
        # generate new target axis angles:
        # - actual axis angle for other axes
        # - target axis angle for iAxiss axes
        #
        for ai in axes:
            if (ai >= self.NUMBER_OF_AXES): # skip virtual axes
                continue
            # set new target axis angles for the axes selected by iAxis in actual axis angles
            a_angles[ ai ] = t_angles[ ai ] 
        #---------------------

        # set modified actual axis angles as new target axis angles
        self.SetAxisTargetAngle( All, a_angles )
        # and get duration
        t = self.interface.get_duration()

        # restore the saved target axis angle so that previously set
        # target axis angles remain active
        self.SetAxisTargetAngle( All, t_angles )
            
        return self.uc_time.ToExternal( t )


    #-----------------------------------------------------------------
    ## Move a single finger to the previously set target position with
    #  the previously set (maximum) velocities.
    #
    #  \param self    - reference to the object itself
    #  \param iFinger - index of the finger to move
    #  \param sequ    - flag: if True (default) then the function executes sequentially
    #                   and returns not until after the SDH has
    #                   finished the movement. If False then the
    #                   function returns immediately after the
    #                   movement command has been sent to the SDH
    #                   (the currently set target axis angles for other fingers will
    #                   then be overwritten with their current actual
    #                   axis angles).
    #  \param check_collisions - flag: If True (default) then
    #                   collisions between the given target angles of
    #                   finger \a iFinger and the actual angles of the
    #                   other fingers are checked. If a collision is
    #                   detected then the movement is \b NOT performed
    #                   and a cSDHErrorInternalCollision exception is
    #                   thrown.
    #                   If False then no collision check is performed. 
    #
    #  \return The expected execution time for the movement in the configured time unit system #uc_time
    #
    #  \remark
    #    - The finger (i.e. all its axes) must be enabled to make the axes move
    #    - Currently the actual movement velocity of an axis is
    #      determined by the SDH firmware to make the movements of all
    #      involved axes start and end synchronously at the same time. Therefore
    #      the axis that needs the longest time for its movement at its
    #      given maximum velocity determines the velocities of all the
    #      other axes.
    #    - Other fingers than \a iFinger will \b NOT move, even if
    #      target axis angles for their axes have been set.
    #      (Exception: as axis 0 is used by finger 0 and 2 these
    #      two fingers cannot be moved completely idependent of each other.)
    #    - If \a sequ is True then the currently set target axis angles for other
    #      fingers will be restored upon return of the function.
    #    - If \a sequ is False then the currently set target axis angles for other
    #      fingers will be overwritten with their current actual axis angles
    #
    #  
    #  \par Examples:
    #  \code
    #    # Assuming 'hand' is a sdh.cSDH object ...
    #  
    #    # Set a new target pose for finger 0:
    #    hand.SetFingerTargetAngle( 0, [0,0,0] )
    #
    #    # Set a new target pose for finger 1
    #    hand.SetFingerTargetAngle( 1, [0,-10,-10] )
    #
    #    # Set a new target pose for finger 2
    #    hand.SetFingerTargetAngle( 2, [20,-20,-20] )
    #  
    #    # Move finger 0 only (and finger 2 as axis 0 also belongs to finger 2)
    #    hand.MoveFinger( 0, True )
    #    # The finger 0 has been moved to [20,0,0]
    #    # (axis 0 is 'wrong' since the target angle for axis 0 has been overwritten
    #    #  while setting the target angles for finger 2)
    #
    #    # The target poses for finger 1 and 2 are still set since the
    #    # last MoveFinger() call was sequentially.
    #    # So move finger 1 now:
    #    t = hand.MoveFinger( 1, False )
    #  
    #    # wait until the non-sequential call has finished:
    #    sdh.time.sleep( t )
    #
    #    # The finger 1 has been moved to [0,-10,-10].
    #
    #    # The target angles for finger 2 have been overwritten since the 
    #    # last MoveFinger() call was non-sequentially.
    #  
    #  \endcode
    #
    #  \bug
    #  With SDH firmware < 0.0.2.7 calling MoveFinger() while some axes are moving 
    #  in eCT_POSE controller type will make the joints jerk.
    #  This is resolved in %SDH firmware 0.0.2.7 for the eCT_POSE controller type with
    #  velocity profile eVP_RAMP. For the eCT_POSE controller type with velocity profile
    #  eVP_SIN_SQUARE changing target points/ velocities while moving will still make 
    #  the axes jerk. 
    #  <br><b>=> Partly resolved in SDH firmware 0.0.2.7</b>
    #  <hr>
    def MoveFinger( self, iFinger, sequ=True, check_collisions=True ):
        '''
        Move a finger to the previously set target positions with
        the previously set (maximum) target velocities. See html/pdf
        documentation for details.
        '''
        self.CheckIndex( iFinger, self.NUMBER_OF_FINGERS, "finger" )

        # save currently set target axis angles of all axes (in external units)
        t_angles = self.GetAxisTargetAngle( All )
        self.dbg.var( "t_angles" )
        
        # save current actual axis angles of all axes (in external units).
        # Limit the returned result to the allowed range. This is necessary since
        # the SDH sometimes reports the current angles slightly out of range
        a_angles = ToRange_a( self.GetAxisActualAngle( All ), self.f_min_angle_a, self.f_max_angle_a )
        self.dbg.var( "a_angles" )

        #---------------------
        # generate new target axis angles:
        # - actual axis angle for other fingers axes
        # - target axis angle for iFingers axes
        #
        for ai in self.finger_axis_index[ iFinger ]:
            if (ai >= self.NUMBER_OF_AXES): # skip virtual axes
                continue
            # set new target axis angles for the axes of finger iFinger in actual axis angles
            a_angles[ ai ] = t_angles[ ai ] 
        #---------------------
        self.dbg.var( "a_angles" )

        #---------------------
        if check_collisions:
            fingers_angles = self._AxisAnglesToFingerAngles( a_angles )
            
            (cxy, (c01,d01), (c02,d02), (c12,d12)) = self.CheckFingerCollisions( fingers_angles[0], fingers_angles[1], fingers_angles[2] )
            if cxy:
                self.dbg << "Internal collision detected in MoveFinger():" # pylint: disable-msg=W0104
                self.dbg.var( "cxy c01 d01 c02 d02 c12 d12" )
                raise cSDHErrorInternalCollision( "Potential internal collision detected, movement not executed!\n" )
        #---------------------
        
        
        # set modified actual axis angles as new target axis angles
        self.SetAxisTargetAngle( All, a_angles )
        # and move there
        t = self.interface.m(sequ)

        # restore the saved target axis angle so that previously set
        # target axis angles for other fingers remain active
        if sequ:
            self.WaitAxis( self.finger_axis_index[ iFinger ] )
            
            self.SetAxisTargetAngle( All, t_angles )
            self.dbg.var( "t_angles" )
            
        return self.uc_time.ToExternal( t )


    #-----------------------------------------------------------------
    ## Move all selected fingers to the previously set target position with
    #  the previously set (maximum) velocities.
    #
    #  \param self    - reference to the object itself
    #  \param iFinger - Indices of the finger to move. Default: All fingers
    #                   This can be All, a single index or a \ref sdhlibrary_python_sdh_py_csdh_vector "vector" of indices.
    #  \param sequ    - flag: if True (default) then the function executes sequentially
    #                   and returns not until after the SDH has
    #                   finished the movement. If False then the
    #                   function returns immediately after the
    #                   movement command has been sent to the SDH
    #                   (the currently set target axis angles for other fingers will
    #                   then be overwritten with their current actual
    #                   axis angles).
    #  \param check_collisions - flag: If True (default) then
    #                   collisions between the given target angles of
    #                   finger \a iFinger and the actual angles of the
    #                   other fingers are checked. If a collision is
    #                   detected then the movement is \b NOT performed
    #                   and a cSDHErrorInternalCollision exception is
    #                   thrown.
    #                   If False then no collision check is performed. 
    #
    #  \return The expected execution time for the movement in the configured time unit system #uc_time
    #
    #  \remark
    #    - Only previously enabled axes will move.
    #    - Currently the actual movement velocity of an axis is
    #      determined by the SDH firmware to make the movements of all
    #      involved axes start and end synchronously at the same time. Therefore
    #      the axis that needs the longest time for its movement at its
    #      given maximum velocity determines the velocities of all the
    #      other axes.
    #    - As axis 0 is used by finger 0 and 2 these
    #      two fingers cannot be moved completely idependent of each
    #      other. Therefor these fingers might move even if not
    #      selected.
    #    - If \a sequ is True then the currently set target axis angles for other
    #      fingers will be restored upon return of the function.
    #    - If \a sequ is False then the currently set target axis angles for other
    #      fingers will be overwritten with their current actual axis angles
    #
    #  \par Examples:
    #  \code
    #    # Assuming 'hand' is a sdh.cSDH object ...
    #  
    #    # Set a new target pose for finger 0:
    #    hand.SetFingerTargetAngle( 0, [0,0,0] )
    #
    #    # Set a new target pose for finger 1
    #    hand.SetFingerTargetAngle( 1, [0,-10,-10] )
    #
    #    # Set a new target pose for finger 2
    #    hand.SetFingerTargetAngle( 2, [20,-20,-20] )
    #  
    #    # Move fingers 0 and 2 to their target positions
    #    hand.MoveHand( [0,2], True )
    #    # The finger 0 has been moved to [20,0,0] and
    #    # finger 2 to [20,-20,-20]
    #    # (axis 0 is 'wrong' for finger 0 since the target angle for
    #    #  axis 0 has been overwritten while setting the target angles
    #    #  for finger 2)
    #
    #    # The target poses for finger 1 are still set since the
    #    # last MoveHand() call was sequentially.
    #    # So move finger 1 now:
    #    t = hand.MoveHand( 1, False )
    #  
    #    # Wait until the non-sequential call has finished:
    #    sdh.time.sleep( t )
    #    # The finger 1 has been moved to [0,-10,-10].
    #
    #
    #    # Set new target angles for all axes ("home position")
    #    hand.SetAxisTargetAngle( All, [ 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0 ] )
    #
    #    # To move all axes back to home position:
    #    hand.MoveHand()
    #  
    #  \endcode
    #
    #  \bug
    #  With SDH firmware < 0.0.2.7 calling MoveHand() while some axes are moving 
    #  in eCT_POSE controller type will make the joints jerk.
    #  This is resolved in %SDH firmware 0.0.2.7 for the eCT_POSE controller type with
    #  velocity profile eVP_RAMP. For the eCT_POSE controller type with velocity profile
    #  eVP_SIN_SQUARE changing target points/ velocities while moving will still make 
    #  the axes jerk. 
    #  <br><b>=> Resolved in SDH firmware 0.0.2.7</b>
    #  <hr>
    def MoveHand( self, iFinger = All, sequ=True, check_collisions=True ):
        '''
        Move selected fingers to their previously set target positions with
        the previously set (maximum) target velocities. See html/pdf
        documentation for details.
        '''
        fingers = self._ToIndexList( iFinger, self.all_fingers, self.NUMBER_OF_FINGERS, "finger" )
        # now fingers is a list of all finger indices to access

        # save currently set target axis angles of all axes in external units
        t_angles = self.GetAxisTargetAngle( All )

        # save current actual axis angles of all axes in external units
        a_angles = ToRange_a( self.GetAxisActualAngle( All ), self.f_min_angle_a, self.f_max_angle_a )

        #---------------------
        # generate new target axis angles:
        # - actual axis angle for not selected fingers axes
        # - target axis angle for iFingers axes
        #
        for fi in fingers:
            for ai in self.finger_axis_index[ fi ]:
                if (ai >= self.NUMBER_OF_AXES): continue   # ignore virtual axes
                # set new target axis angles for the axes of finger iFinger in actual axis angles
                a_angles[ ai ] = t_angles[ ai ] 
        #---------------------

        #---------------------
        if check_collisions:
            fingers_angles = self._AxisAnglesToFingerAngles( a_angles )
            
            (cxy, (c01,d01), (c02,d02), (c12,d12)) = self.CheckFingerCollisions( fingers_angles[0], fingers_angles[1], fingers_angles[2] )
            if cxy:
                self.dbg << "Internal collision detected in MoveHand():" # pylint: disable-msg=W0104
                self.dbg.var( "cxy c01 d01 c02 d02 c12 d12" )
                raise cSDHErrorInternalCollision( "Potential internal collision detected, movement not executed!\n" )
        #---------------------
            
        # set modified actual axis angles as new target axis angles
        self.SetAxisTargetAngle( All, a_angles )
        # and move there
        t = self.interface.m(sequ)

        # restore the saved target axis angles so that
        # previously set target axis angles for unselected fingers remain
        # active
        if sequ:
            self.WaitAxis()
            self.SetAxisTargetAngle( All, t_angles )
            
        return self.uc_time.ToExternal( t )

    #  end of doxygen name group sdhlibrary_python_sdh_py_csdh_finger
    ## @}
    ######################################################################


    #######################################################################
    ## \anchor sdhlibrary_python_sdh_py_csdh_grip
    #  \name   Methods to access SDH grip skills
    #  
    #  @{
    
    #-----------------------------------------------------------------
    ## Get the maximum velocity of grip skills
    #
    #  The maximum velocity is currently not read from the SDH, but is stored in the base class.
    #
    #  \return
    #    - a single float value is returned representing the velocity in the #uc_angular_velocity unit system
    #
    #
    #  \par Examples:
    #  \code
    #    # Assuming "hand" is a sdh.cSDH object ...
    #    
    #    # Get maximum grip skill velocity
    #    v = hand.GetGripMaxVelocity()
    #    # v is now something like 100.0
    #
    #    # Or if you change the velocity unit system:
    #    hand.UseRadians()
    #    v = hand.GetGripMaxVelocity()
    #    # now v is something like 1.7453292519943295
    #  \endcode
    #  
    #  <hr>
    def GetGripMaxVelocity( self ):
        '''
        Get the maximum velocity of axis(axes)
        '''
        return self.uc_angular_velocity.ToExternal( self.grip_max_velocity )
    

    #-----------------------------------------------------------------
    ## Perform one of the internal skills (a "grip"). 
    #
    #   \warning THIS DOES NOT WORK WITH SDH FIRMWARE PRIOR TO 0.0.2.6
    #     This was a feature in the ancient times of the SDH1 and now does work
    #     again for SDH firmware 0.0.2.6 and newer. We intend to further improve this
    #     feature (e.g. store user defined grips within the SDH) in the future,
    #     but a particular deadline a has not been determined yet.
    #
    #   \bug 
    #     With SDH firmware < 0.0.2.6 GripHand() does not work and might 
    #     yield undefined behaviour there
    #     <br><b>=> Resolved in SDH firmware 0.0.2.6</b> 
    #   
    #   \bug 
    #     Currently the performing of a skill or grip with GripHand() can \b NOT be
    #     interrupted!!!  Even if the command is sent with \a sequ=false it \b cannot 
    #     be stopped or fast stopped.
    # 
    #  \param self     - reference to the object itself
    #  \param grip     - The index of the grip to perform [0..self.NUMBER_OF_GRIPS-1] (s.a. self.eGraspId)
    #  \param close    - close-ratio: [0.0 .. 1.0] where 0.0 is 'fully opened' and 1.0 is 'fully closed'
    #  \param velocity - maximum allowed angular axis velocity in the chosen external unit system
    #  \param sequ     - flag: if True (default) then the function executes sequentially
    #                    and returns not until after the SDH has
    #                    finished the movement. If False then the
    #                    function returns immediately after the
    #                    movement command has been sent to the SDH.
    #
    #  \return The expected execution time for the movement in the configured time unit system #uc_time.
    #
    #  \remark
    #    - Only previously enabled axes will move.
    #    - Currently the actual movement velocity of an axis is
    #      determined by the SDH firmware to make the movements of all
    #      involved axes start and end synchronously at the same time. Therefore
    #      the axis that needs the longest time for its movement at its
    #      given maximum velocity determines the velocities of all the
    #      other axes.
    #    - The currently set target axis angles are not changed by this command
    #    - The movement uses the eMotorCurrentMode motor current modes "grip"
    #      while gripping and then changes the motor current mode to
    #      "hold". After the movement previously set motor currents
    #      set for mode "move" are overwritten!
    #
    #  \par Examples:
    #  \code
    #    # Assuming 'hand' is a sdh.cSDH object ...
    #  
    #    # Perform a fully opened centrical grip 
    #    hand.GripHand( self.eGraspId[ "GRIP_CENTRICAL" ], 0.0, 50.0, True )
    #  \endcode
    #  <hr>
    def GripHand( self, grip, close, velocity, sequ=True ):
        '''
        Perform one of the internal skills (a "grip"). See html/pdf documentation for details.
        '''
        self.CheckIndex( grip, self.eGraspId["NUMBER_OF_GRIPS"], "grip" )
        
        # change grip if different from last one
        t0 = 0.0
        if ( self._last_grip != grip ):
            # yes, so select new grip first
            t0 = self.interface.selgrip( grip, True ) # the selgrip must always be sequential
            self._last_grip = grip
        
        t1 = self.interface.grip( close, velocity, sequ )

        return self.uc_time.ToExternal( t0 + t1 )

    ## end of doxygen name group sdhlibrary_python_sdh_py_csdh_grip
    #  @}
    ######################################################################

    def _UpdateSettingsFromSDH(self):
        '''Update settings like min/max velocities and accelerations from the connected SDH    
        '''
        # pylint: disable-msg=W0201
        self.release_firmware = self.GetInfo("release-firmware")

        # update the velocity limits to the actual values according to the firmware:
        # (the limits are converted to internal units and rounded downwards to the nearest integer to get around rounding errors)
        limits_external = self.GetAxisLimitVelocity(self.all_axes)
        limits_internal = [ self.uc_angular_velocity.ToInternal(ae) for ae in limits_external ]    
        self.f_max_velocity_a     = array.array( "d",  map( int, limits_internal ) ) # pylint: disable-msg=W0141
        
        limits_external = self.GetAxisLimitAcceleration(self.all_axes)
        limits_internal = [ self.uc_angular_velocity.ToInternal(ae) for ae in limits_external ]    
        self.f_max_acceleration_a = array.array( "d",  map( int, limits_internal ) ) # pylint: disable-msg=W0141
        self.max_angular_velocity_a = self.f_max_velocity_a
        self.max_angular_acceleration_a = self.f_max_acceleration_a
        self.interface.max_angular_velocity_a = self.f_max_velocity_a
        self.interface.max_angular_acceleration_a = self.f_max_acceleration_a
        self._AdjustLimits( self.GetController() )

    def _AdjustLimits( self, controller ):
        ''' Adjust the limits for the velocity according to the controller type.
     
        - in pose controller the velocities are always positive and thus the minimum is 0.0
        - in velocity based controllers the velocities can be positive or negative and thus the minimum is -maximum
        '''
        self.f_min_acceleration_a = array.array( "d",  [ 0.0 ]* len(self.f_max_acceleration_a) )
        if ( controller == self.eControllerType["eCT_POSE"] ):
            self.f_min_velocity_a     = array.array( "d",  [ 0.0 ]* len(self.f_max_velocity_a) )
        elif ( controller == self.eControllerType["eCT_VELOCITY"] or controller == self.eControllerType["eCT_VELOCITY_ACCELERATION"]) :
            self.f_min_velocity_a     = array.array( "d",  [ -v for v in self.f_max_velocity_a ] )
        else:
            raise cSDHErrorInvalidParameter( "controller type %s not available in SDH firmware %s of currently attached SDH" % (repr(controller), self.release_firmware) )
            
        self.min_angular_velocity_a = self.f_min_velocity_a
        self.interface.min_angular_velocity_a = self.f_min_velocity_a
        
        self.dbg << "AdjustLimits( " << controller << " )\n";
        self.dbg << "  f_min_velocity_a = " << self.f_min_velocity_a << "   ";
        self.dbg << "  f_min_acceleration_a = " << self.f_min_acceleration_a << "\n";


    # unimplemented from SAH:
    # def GetFingerTipFT( self, int iFinger,float* pafFTData):

    # def GetFingerEnableState( self, int iFinger, int* piEnableState):

    # def GetCommandedValues( self, int iFinger, float* pafAngle,float* pafVelocity):
    # def GetHandConfig( self, int* piConfig):
    # def GetFingerLimitsStatus( self, int iPort,int iFinger,int* paiLimitStatus):
    # def ClearTorqueSensorOffset( self, int iPort,int iFinger):
    
    # def SetStiffnessFactor( self, int iFinger, float* pafStiffnessFactor):

# end of class cSDH
######################################################################

######################################################################
# some usefull editing settings for emacs:
#
#;;; Local Variables: ***
#;;; mode:python ***
#;;; End: ***
#
######################################################################
