# -*- coding: latin-1 -*-
#######################################################################
#
## \file
#  \section sdhlibrary_python_unit_py_general General file information
#
#    \author   Dirk Osswald
#    \date     2007-06-13
#
#  \brief  
#    Implementation of classes that deal with physical units
#
#  \section sdhlibrary_python_unit_py_copyright Copyright
#
#  Copyright (c) 2007 SCHUNK GmbH & Co. KG
#
#  <HR>
#  \internal
#
#    \subsection sdhlibrary_python_unit_py_details SVN related, detailed file specific information:
#      $LastChangedBy: Osswald2 $
#      $LastChangedDate: 2009-02-11 20:30:06 +0100 (Wed, 11 Feb 2009) $
#      \par SVN file revision:
#        $Id: unit.py 4121 2009-02-11 19:30:06Z Osswald2 $
#
#  \subsection sdhlibrary_python_unit_py_changelog Changelog of this file:
#      \include unit.py.log
#
#######################################################################


#######################################################################
## \anchor sdhlibrary_python_unit_py_python_vars
#  \name   Python specific variables
#  
#  Some definitions that describe the module for python.
#
#  @{

__doc__       = "Unit conversion class and objects."
__author__    = "Dirk Osswald: dirk.osswald@de.schunk.com"
__url__       = "http://www.schunk.com"
__version__   = "$Id: unit.py 4121 2009-02-11 19:30:06Z Osswald2 $"
__copyright__ = "Copyright (c) 2007 SCHUNK GmbH & Co. KG"

#  end of doxygen name group sdhlibrary_python_unit_py_python_vars
#  @}
######################################################################


import array, math

## \brief Unit conversion class
#
#  An object of this class can be configured to convert values of a
#  physical unit between 2 physical unit systems. An angle value given
#  in degrees can e.g. be converted from/to radians or vice versa by
#  an object of this class.
#
#  <hr>
class cUnitConverter:
    '''
    Unit conversion class. See html/pdf documentation for details.
    '''

    ## Constructor of cUnitConverter class.
    #
    #  At construction time the conversion parameters - a \a factor
    #  and an \a offset - must be provided along with elements that
    #  describe the unit of a value
    #
    #  \param self   - reference to the object itself
    #  \param kind   - a string describing the kind of unit to be converted (something like "angle" or "time")
    #  \param name   - the name of the external unit (something like "degrees" or "milliseconds")
    #  \param symbol - the symbol of the external unit (something like "deg" or "ms")
    #  \param factor - the conversion factor from internal to external units
    #  \param offset - the conversion offset from internal to external units
    #  \param decimal_places - A usefull number of decimal places for printing values in the external unit system
    #
    #  <hr>
    def __init__(self, kind, name, symbol, factor = 1.0, offset = 0.0, decimal_places=1 ):
        '''
        Constructor of cUnitConverter class. 
        '''
        assert factor != 0.0 # must not be 0 since we devide by it
        
        ## the kind of unit to be converted (something like "angle" or "time")
        self.kind   = kind

        ## the name of the external unit (something like "degrees" or "milliseconds")
        self.name   = name

        ## the symbol of the external unit (something like "deg" or "ms")
        self.symbol   = symbol

        ## the conversion factor from internal to external units
        self.factor = factor

        ## the conversion offset from internal to external units
        self.offset = offset

        ## A usefull number of decimal places for printing values in the external unit system
        self.decimal_places = decimal_places
        
        ## dummy array needed to complare types of arrays
        self._dummy_array = array.array( "d",  (0.0,0.0) )
        
    def ToExternal( self, internal ):
        '''
        Convert value 'internal' given in internal 'self.name' units into external units.
        Returns internal * factor + offset

        The value 'internal' can be a single number or a vector-like
        object (list, tuple, array.array). In the latter 3 cases every
        member of the vector is converted and a new object of the same
        type is returned
        '''
        if (type( internal ) == list):
            return [ v * self.factor + self.offset   for v in internal ]
        if (type( internal ) == tuple):
            return tuple( v * self.factor + self.offset   for v in internal )
        if (type( internal ) == type(self._dummy_array)):
            return array.array( "d",  [ v * self.factor + self.offset   for v in internal ] )
        return internal * self.factor + self.offset

    def ToInternal( self, external ):
        '''
        Convert value 'external' given in external 'self.name' units into internal units.
        Returns (external - offset) / factor 

        The value 'external' can be a single number or a vector-like
        object (list, tuple, array.array). In the latter 3 cases every
        member of the vector is converted and a new object of the same
        type is returned
        '''
        if (type( external ) == list):
            return [ (v - self.offset) / self.factor   for v in external ]
        if (type( external ) == tuple):
            return tuple( (v - self.offset) / self.factor   for v in external )
        if (type( external ) == type(self._dummy_array)):
            return array.array( "d",  [ (v - self.offset) / self.factor   for v in external ] )
        return (external - self.offset) / self.factor

#######################################################################
## \anchor sdhlibrary_python_unit_py_unit_conversion_objects
#  \name   Predefined unit conversion objecs
#  
#  Some predefined cUnitConverter unit conversion objects to convert values between
#  different unit systems. These can be used e.g. to convert angle values between degrees and radians,
#  temperatures between degrees celsius and degrees fahrenheit or the like.
#
#  The cSDH class uses such objects to convert between external (user)
#  and internal (SDH) units. The user can easily change the converter object
#  that is used for a certain kind of unit. This way a cSDH object
#  can easily report and accept parameters in the user or application
#  specific unit system.
#
#  Additionally, users can easily add conversion objects for their own,
#  even more user- or application-specific unit systems.
#
#  @{

## Default converter for angles (internal unit == external unit): degrees
uc_angle_degrees = cUnitConverter( "angle", "degrees", u"\N{DEGREE SIGN}", 1.0, 0.0, 1 )

## Converter for angles: external unit = radians
uc_angle_radians = cUnitConverter( "angle", "radians", "rad", (2.0*math.pi)/360.0, 0.0, 3 )

## Default converter for times (internal unit == external unit): seconds
uc_time_seconds = cUnitConverter( "time", "seconds", "s", 1.0, 0.0, 3 )

## Converter for times: external unit = milliseconds
uc_time_milliseconds = cUnitConverter( "time", "milliseconds", "ms", 1000.0, 0.0, 0 )

## Default converter for temparatures (internal unit == external unit): degrees celsius
uc_temperature_celsius = cUnitConverter( "temparature", "degrees celsius", u"\N{DEGREE SIGN}C", 1.0, 0.0, 1 )

## Converter for temperatures: external unit = degrees fahrenheit
uc_temperature_fahrenheit = cUnitConverter( "temparature", "degrees fahrenheit", u"\N{DEGREE SIGN}F", 1.8, 32.0, 1 )

## Default converter for angular velocities (internal unit == external unit): degrees / second
uc_angular_velocity_degrees_per_second = cUnitConverter( "angular velocity", "degrees/second", u"\N{DEGREE SIGN}/s", 1.0, 0.0, 2 )

## Converter for angular velocieties: external unit = radians/second
uc_angular_velocity_radians_per_second = cUnitConverter( "angular velocity", "radians/second", "rad/s", (2.0*math.pi)/360.0, 0.0, 4 )

## Default converter for angular velocities (internal unit == external unit): degrees / (second * second)
uc_angular_acceleration_degrees_per_second_squared = cUnitConverter( "angular acceleration", "degrees/(second*second)", u"\N{DEGREE SIGN}/s\N{SUPERSCRIPT TWO}", 1.0, 0.0, 1 )

## Converter for angular velocieties: external unit = radians/(second*second)
uc_angular_acceleration_radians_per_second_squared = cUnitConverter( "angular acceleration", "radians/(second*second)", u"rad/s\N{SUPERSCRIPT TWO}", (2.0*math.pi)/360.0, 0.0, 3 )

## Default converter for motor current (internal unit == external unit): Ampere
uc_motor_current_ampere = cUnitConverter( "motor current", "Ampere", "A", 1.0, 0.0, 3 )

## Converter for motor current: external unit = milli Ampere
uc_motor_current_milliampere = cUnitConverter( "motor current", "milli Ampere", "mA", 1000.0, 0.0, 0 )

## Default converter for position (internal unit == external unit): millimeter
uc_position_millimeter = cUnitConverter( "position", "millimeter", "mm", 1.0, 0.0, 1 )

## Converter for position: external unit = meter
uc_position_meter = cUnitConverter( "position", "meter", "m", 1/1000.0, 0.0, 4 )


#  end of doxygen name group sdhlibrary_python_unit_py_unit_conversion_objects
## @}

#
######################################################################
