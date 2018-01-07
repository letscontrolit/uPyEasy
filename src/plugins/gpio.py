#          
# Filename: dht.py
# Version : 0.1
# Author  : Lisa Esselink
# Purpose : Plugin DHT 11/12/22
# Usage   : Get DHT sensor data
#
# Copyright (c) 2017 - Lisa Esselink. All rights reserved.  
# Licensend under the Creative Commons Attribution-NonCommercial 4.0 International License.
# See LICENSE file in the project root for full license information.  
#

from machine import Pin
from upyeasy import core
from asyn import Event

#
# CUSTOM SENSOR GLOBALS
#

name                = "GPIO Control"            # Name of the plugin
dtype               = core.DEVICE_TYPE_SINGLE   # Device type
stype               = core.SENSOR_TYPE_SWITCH   # Sensor type
template            = "gpio.html"               # HTML template for device screen
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

class gpio_plugin:
    gpiotype            = "input"                   # Default GPIO type
    inputtype           = "normal"                  # Default GPIO input type
    datastore           = None                      # Place where plugin data is stored for reboots
    
    def __init__(self) :
        self._log       = core._log
        self._log.debug("Plugin: gpio contruction")
        self._lock      = Event()
        # release lock, ready for next measurement
        self._lock.clear()
        self.valuenames = {}
        self.valuenames["valueN1"]= "switch"
        self.valuenames["valueF1"]= ""
        self.valuenames["valueD1"]= 0
        
    def init(self, plugin, device, queue):        
        self._log.debug("Plugin: gpio init")
        self._plugins           = core._plugins
        self.pullup             = plugin['pullup'] # 0=false, 1=true
        self.inverse            = plugin['inverse']
        self.port               = plugin['port']
        self.formula            = plugin['formula']
        self.senddata           = plugin['senddata']
        self.timer              = plugin['timer']
        self.sync               = plugin['sync']
        self.content            = plugin.get('content', content)
        self.queue              = queue
        self.queue_sid          = device["controllerid"]
        self.devicename         = device["name"]
        plugin['dtype']         = dtype
        plugin['stype']         = stype
        plugin['template']      = template
        datastore               = self._plugins.readstore(name)
        return True

    def loadform(self,plugindata):
        self._log.debug("Plugin: gpio loadform")
        plugindata['gpiotype']  = self.gpiotype
        plugindata['inputtype'] = self.inputtype
        plugindata['pincnt']    = pincnt
        plugindata['valuecnt']  = valuecnt
        plugindata['valueN1']   = self.valuenames["valueN1"]
        plugindata['valueF1']   = self.valuenames["valueF1"]
        plugindata['valueD1']   = self.valuenames["valueD1"]
        plugindata['content']   = content
        
    def saveform(self,plugindata):
        self._log.debug("Plugin: gpio saveform")
        self.gpiotype               = plugindata['gpiotype']
        self.inputtype              = plugindata['inputtype']
        self.dxpin                  = plugindata['dxpin0']
        self.valuenames["valueN1"]  = plugindata['valueN1']
        self.valuenames["valueF1"]  = plugindata['valueF1']
        self.valuenames["valueD1"]  = plugindata['valueD1']
        
    def read(self, values):
        self._log.debug("Plugin: gpio read")
        values['valueN1'] = self.valuenames["valueN1"]
        values['valueD1'] = 1

    def write(self, values):
        self._log.debug("Plugin: gpio write")
        
    async def asyncprocess(self):
        # processing todo for plugin
        self._log.debug("Plugin: gpio process")
        # If a controller is attached
        if self.queue:
            # Put start message in queue
            self.queue.put_nowait(core.QUEUE_MESSAGE_START)
            # put sensor type in queue
            self.queue.put_nowait(stype)
            # put HA server id in queue
            self.queue.put_nowait(self.queue_sid)
            # put on / off value(s) in queue
            self.queue.put_nowait("On")
        # release lock, ready for next measurement
        self._lock.clear()

#
#Module Code...    
#

gpio = gpio_plugin()

def loadform(plugindata):
    gpio.loadform(plugindata)
        
#
#CUSTOM SENSOR CODE...    
#
    
