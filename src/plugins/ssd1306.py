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

name                = "SSD1306"                 # Name of the plugin
dtype               = core.DEVICE_TYPE_SINGLE   # Device type
stype               = core.SENSOR_TYPE_SINGLE   # Sensor type
template            = "ssd1306.html"            # HTML template for device screen
pullup              = "off"
inverse             = "off"
port                = "off"
formula             = "off"
senddata            = "off"
timer               = "off"
sync                = "off"
delay               = 0                         # Delay is ms between measurement IF device delay == 0
pincnt              = 0
valuecnt            = 3
i2c                 = 1
ssd_i2c             = 60
ssd_rotation        = 'normal'
ssd_size            = 128
ssd_timeout         = 300
ssd_line1           = ''
ssd_line2           = ''
ssd_line3           = ''
ssd_line4           = ''
ssd_line5           = ''
ssd_line6           = ''
ssd_line7           = ''
ssd_line8           = ''
content             = '<a class="button link" href="" target="_blank">?</a>'    # Additional HTML for device screen

#
#
#

class ssd1306_plugin:
    datastore           = None                      # Place where plugin data is stored for reboots
    
    def __init__(self) :
        # generic section
        self._log       = core._log
        self._log.debug("Plugin: ssd1306 contruction")
        self._utils     = core._utils
        self._plugins   = core._plugins
        self._lock      = Event()
        # plugin specific section
        self.valuenames = {}
        self.valuenames["valueN1"]= ""
        self.valuenames["valueF1"]= ""
        self.valuenames["valueD1"]= 0
        # release lock, ready for next measurement
        self._lock.clear()
        
    def init(self, plugin, device, queue, scriptqueue):        
        self._log.debug("Plugin: ssd1306 init")
        # generic section
        self._utils.plugin_initdata(self, plugin, device, queue, scriptqueue)
        self.content            = plugin.get('content',content)
        self.pincnt             = pincnt
        self.valuecnt           = valuecnt
        self.stype              = stype
        self.dtype              = dtype
        self.ssd_rotation       = ssd_rotation
        self.ssd_size           = ssd_size
        self.ssd_timeout        = ssd_timeout
        self.ssd_line1          = ssd_line1
        self.ssd_line2          = ssd_line2
        self.ssd_line3          = ssd_line3
        self.ssd_line4          = ssd_line4
        self.ssd_line5          = ssd_line5
        self.ssd_line6          = ssd_line6
        self.ssd_line7          = ssd_line7
        self.ssd_line8          = ssd_line8
        self._device            = device
        plugin['dtype']         = dtype
        plugin['stype']         = stype
        plugin['template']      = template
        datastore               = self._plugins.readstore(name)
        # Load values
        self._plugins.loadvalues(self._device,self.valuenames)
        
        # Set triggers
        self.triggers           = name+"#"+self.valuenames["valueN1"]
        self._plugins.triggers(device, self.triggers)
        return True

    def loadform(self,plugindata):
        self._log.debug("Plugin: ssd1306 loadform")
        # generic section
        self._utils.plugin_loadform(self, plugindata)
        # plugin specific section
        
    def saveform(self,plugindata):
        self._log.debug("Plugin: ssd1306 saveform")
        # generic section
        self._utils.plugin_saveform(self, plugindata)
        # plugin specific section
        self._plugins.savevalues(self._device,self.valuenames)
        
    def read(self, values):
        self._log.debug("Plugin: ssd1306 read")
        # generic section
        values['valueN1'] = self.valuenames["valueN1"]
        # plugin specific section
        values['valueV1'] = 'on'

    def write(self, values):
        self._log.debug("Plugin: ssd1306 write")
        #print(values)
        
    async def asyncprocess(self):
        self._log.debug("Plugin: ssd1306 process")
        # send data to protocol and script/rule queues
        self.valuenames["valueV1"] = 'on'        
        self._utils.plugin_senddata(self)
        # release lock, ready for next measurement
        self._lock.clear()

