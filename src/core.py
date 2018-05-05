#          
# Filename: core.py
# Version : 0.1
# Author  : Lisa Esselink
# Purpose : Core class
# Usage   : Dynamic access to all classes
#
# Copyright (c) 2017 - Lisa Esselink. All rights reserved.  
# Licensend under the Creative Commons Attribution-NonCommercial 4.0 International License. 
# See LICENSE file in the project root for full license information.  
#

####################
# APP data         #
####################

__author__              = "Lisa Esselink"
__copyright__           = "Copyright 2018"
__credits__             = ["Lisa Esselink"]
__license__             = "Creative Commons Attribution-NonCommercial 4.0 International License"
__version__             = "0.3.0."
__email__               = "info@upyeasy.com"
__status__              = "Beta"
__logname__             = "uPyEasy"
__build__               = "65"

upyeasy_starttime       = 0
initial_upyeasyname     = "uPyEasy"
initial_upyeasywifi     = "STA"

import os
working_dir = os.getcwd()
if os.getcwd() != '/': working_dir+="/"

####################
# Defintions       #
####################

# Device types
DEVICE_TYPE_SINGLE      = "DEVICE_TYPE_SINGLE"      # connected through 1 datapin
DEVICE_TYPE_DUAL        = "DEVICE_TYPE_DUAL"        # connected through 2 datapins
DEVICE_TYPE_TRIPLE      = "DEVICE_TYPE_TRIPLE"      # connected through 3 datapins
DEVICE_TYPE_ANALOG      = "DEVICE_TYPE_ANALOG"      # AIN/tout pin
DEVICE_TYPE_I2C         = "DEVICE_TYPE_I2C"         # connected through I2C
DEVICE_TYPE_DUMMY       = "DEVICE_TYPE_DUMMY"       # Dummy device, has no physical connection

# Sensor types
SENSOR_TYPE_SINGLE          = "SENSOR_TYPE_SINGLE"          # Single value
SENSOR_TYPE_TEMP_HUM        = "SENSOR_TYPE_TEMP_HUM"        # Dual values
SENSOR_TYPE_TEMP_BARO       = "SENSOR_TYPE_TEMP_BARO"       # Dual values
SENSOR_TYPE_TEMP_HUM_BARO   = "SENSOR_TYPE_TEMP_HUM_BARO"   # Triple values
SENSOR_TYPE_DUAL            = "SENSOR_TYPE_DUAL"            # Dual values
SENSOR_TYPE_TRIPLE          = "SENSOR_TYPE_TRIPLE"          # Triple values
SENSOR_TYPE_QUAD            = "SENSOR_TYPE_QUAD"            # Quad values
SENSOR_TYPE_SWITCH          = "SENSOR_TYPE_SWITCH"          # Single value
SENSOR_TYPE_DIMMER          = "SENSOR_TYPE_DIMMER"          # Single value
SENSOR_TYPE_LONG            = "SENSOR_TYPE_LONG"            # Single value
SENSOR_TYPE_WIND            = "SENSOR_TYPE_WIND"            # Single value

# Queueu types
QUEUE_MESSAGE_START         = "UPYEASY_QMS"         # Start of every queue message

# Status types
STATUS_INIT                 = "INIT"                # initialising
STATUS_RUNNING              = "RUNNING"             # running normally
STATUS_WARNING              = "WARNING"             # warning message printed
STATUS_ERROR                = "ERROR"               # encountered error
STATUS_IDLE                 = "IDLE"                # running idle, no plugin defined
STATUS_WEB_REQUEST          = "WEBREQUEST"          # web requested received
STATUS_PLUGIN_PROCESS       = "PLUGIN_PROCESS"      # processing plugin 
STATUS_CONTROLLER_PROCESS   = "CONTROLLER_PROCESS"  # processing controller

# Network types
NET_STA                 = "STA"
NET_STA_AP              = "STA+AP"
NET_AP                  = "AP"
NET_ETH                 = "ETH"

# Pin Options
PIN_PULL_UP         = 0
PIN_PULL_DOWN       = 1
PIN_IN              = 2
PIN_OUT             = 3
PIN_OPEN_DRAIN      = 4
PIN_ALT             = 5
PIN_ALT_OPEN_DRAIN  = 6

####################
# CORE             #
####################

# Shared classes

_plugins   = None
_protocols = None
_nic       = None
_log       = None
_hal       = None
_utils     = None
_scripts   = None
