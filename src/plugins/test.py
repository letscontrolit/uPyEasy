#          
# Filename: test.py
# Version : 0.1
# Author  : Lisa Esselink
# Purpose : Plugin test
# Usage   : Get fixed sensor data
#
# Copyright (c) 2018 - Lisa Esselink. All rights reserved.  
# Licensend under the Creative Commons Attribution-NonCommercial 4.0 International License.
# See LICENSE file in the project root for full license information.  
#

from upyeasy import core
from asyn import Event

#
# CUSTOM SENSOR GLOBALS
#

name                = "Test"                    # Name of the plugin
dtype               = core.DEVICE_TYPE_SINGLE   # Device type
stype               = core.SENSOR_TYPE_SWITCH   # Sensor type
template            = "test.html"               # HTML template for device screen
pullup              = "off"
inverse             = "off"
port                = "off"
formula             = "off"
senddata            = "off"
timer               = "off"
sync                = "off"
delay               = 0                         # Delay is ms between measurement IF device delay == 0
pincnt              = 1                         # Number of dxpins needed 
valuecnt            = 1                         # Number of values needed
dxpin               = 0                         # dxpin number where to measure
content             = '<a class="button link" href="" target="_blank">?</a>'    # Additional HTML for device screen

#
#
#

class test_plugin:
    gpiotype            = "input"                   # Default GPIO type
    inputtype           = "normal"                  # Default GPIO input type
    datastore           = None                      # Place where plugin data is stored for reboots
    
    def __init__(self) :
        # generic section
        self._log       = core._log
        self._log.debug("Plugin: test contruction")
        self._utils     = core._utils
        self._plugins   = core._plugins
        self._lock      = Event()
        # plugin specific section
        self.valuenames = {}
        self.valuenames["valueN1"]= "GPIO"
        self.valuenames["valueF1"]= ""
        self.valuenames["valueD1"]= 0
        # release lock, ready for next measurement
        self._lock.clear()
        
    def init(self, plugin, device, queue, scriptqueue):        
        self._log.debug("Plugin: test init")
        # generic section
        self._utils.plugin_initdata(self, plugin, device, queue, scriptqueue)
        self.content            = plugin.get('content',content)
        self.pincnt             = pincnt
        self.valuecnt           = valuecnt
        self.stype              = stype
        self.dtype              = dtype
        plugin['dtype']         = dtype
        plugin['stype']         = stype
        plugin['template']      = template
        datastore               = self._plugins.readstore(name)
        return True

    def loadform(self,plugindata):
        self._log.debug("Plugin: test loadform")
        # generic section
        self._utils.plugin_loadform(self, plugindata)
        # plugin specific section
        plugindata['gpiotype']  = self.gpiotype
        plugindata['inputtype'] = self.inputtype
        
    def saveform(self,plugindata):
        self._log.debug("Plugin: test saveform")
        # generic section
        self._utils.plugin_saveform(self, plugindata)
        # plugin specific section
        self.gpiotype               = plugindata['gpiotype']
        self.inputtype              = plugindata['inputtype']
        self.dxpin                  = plugindata['dxpin0']
        
    def read(self, values):
        self._log.debug("Plugin: test read")
        # generic section
        values['valueN1'] = self.valuenames["valueN1"]
        # plugin specific section
        values['valueV1'] = 'on'

    def write(self, values):
        self._log.debug("Plugin: test write")
        
    async def asyncprocess(self):
        self._log.debug("Plugin: test process")
        # send data to protocol and script/rule queues
        self.valuenames["valueV1"] = 'on'        
        self._utils.plugin_senddata(self)
        # release lock, ready for next measurement
        self._lock.clear()

