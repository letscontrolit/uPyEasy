#          
# Filename: dht.py
# Version : 0.1
# Author  : Lisa Esselink
# Purpose : Plugin DHT 11/12/22
# Usage   : Get DHT sensor data
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

from machine import Pin
from aswitch import Switch, Pushbutton

name                = "Switch"            # Name of the plugin
dtype               = core.DEVICE_TYPE_SINGLE   # Device type
stype               = core.SENSOR_TYPE_SWITCH   # Sensor type
template            = "switch.html"             # HTML template for device screen
pullup              = "off"
inverse             = "off"
port                = "off"
formula             = "off"
senddata            = "off"
timer               = "off"
sync                = "off"
bootstate           = ""
delay               = 0                         # Delay is ms between measurement IF device delay == 0
pincnt              = 1                         # Number of dxpins needed 
valuecnt            = 1                         # Number of values needed
dxpin               = "d0"                      # dxpin number where to measure
content             = '<a class="button link" href="" target="_blank">?</a>'    # Additional HTML for device screen

#
#
#

class switch_plugin:
    inputtype           = "normal"                  # Default switch type
    datastore           = None                      # Place where plugin data is stored for reboots
    
    def __init__(self) :
        # generic section
        self._log           = core._log
        self._log.debug("Plugin: switch contruction")
        self._utils         = core._utils
        self._plugins       = core._plugins
        self._hal           = core._hal
        self._lock          = Event()
        self.dxpin          = dxpin
        # plugin specific section
        self.valuenames     = {}
        self.valuenames["valueN1"]= "switch"
        self.valuenames["valueF1"]= ""
        self.valuenames["valueD1"]= 0
        # release lock, ready for next measurement
        self._lock.clear()
        
    def init(self, plugin, device, queue, scriptqueue):        
        self._log.debug("Plugin: switch init")
        # generic section
        self._utils.plugin_initdata(self, plugin, device, queue, scriptqueue)
        self.content            = plugin.get('content',content)
        plugin['dtype']         = dtype
        plugin['stype']         = stype
        plugin['template']      = template
        datastore               = self._plugins.readstore(self.devicename)
        # plugin specific section
        self.switch_status      = bootstate
        if self.inputtype == 'normal':
            self._log.debug("Plugin: switch init normal, pin: "+self.dxpin)
            # Setup switch
            self.swpin                  = self._hal.pin(self.dxpin, core.PIN_IN, core.PIN_PULL_UP)
            self.switch                 = Switch(self.swpin)
            # Register coros to launch on contact close and open
            self.switch.close_func(self.asyncswitchopen)
            self.switch.open_func(self.asyncswitchclosed)
        elif self.inputtype == 'low':
            self._log.debug("Plugin: switch init low, pin: "+self.dxpin)
            # Setup button active low
            self.swpin                  = self._hal.pin(self.dxpin, core.PIN_IN, core.PIN_PULL_UP)
            self.switch                 = Pushbutton(self.swpin)
            self.switch.press_func(self.asyncbuttonpress)
            self.switch.release_func(self.asyncbuttonrelease)
            self.switch.double_func(self.asyncbuttondouble)
            self.switch.long_func(self.asyncbuttonlong)
        else:
            self._log.debug("Plugin: switch init high, pin: "+self.dxpin)
            # Setup button active high
            self.swpin                  = self._hal.pin(self.dxpin, core.PIN_IN, core.PIN_PULL_DOWN)
            self.switch                 = Pushbutton(self.swpin)
            self.switch.press_func(self.asyncbuttonpress)
            self.switch.release_func(self.asyncbuttonrelease)
            self.switch.double_func(self.asyncbuttondouble)
            self.switch.long_func(self.asyncbuttonlong)
        return True

    def loadform(self,plugindata):
        self._log.debug("Plugin: switch loadform")
        # generic section
        self._utils.plugin_loadform(self, plugindata)
        # plugin specific section
        plugindata['inputtype'] = self.inputtype
        plugindata['dxpin0']    = self.dxpin
        
    def saveform(self,plugindata):
        self._log.debug("Plugin: switch saveform")
        # generic section
        self._utils.plugin_saveform(self, plugindata)
        # plugin specific section
        self.inputtype              = plugindata['inputtype']
        self.dxpin                  = plugindata['dxpin0']
        
        # store values
        data = {}
        data["inputtype"]   = self.inputtype
        data["dxpin"]       = self.dxpin
        data["valueN1"]     = self.valuenames["valueN1"]
        data["valueF1"]     = self.valuenames["valueF1"] 
        data["valueD1"]     = self.valuenames["valueD1"]
        self._plugins.writestore(self.devicename, data)
        
        if self.inputtype == 'normal':
            # Setup switch
            self.swpin                  = self._hal.pin(self.dxpin, core.PIN_IN, core.PIN_PULL_UP)
            self.switch                 = Switch(self.swpin)
            # Register coros to launch on contact close and open
            self.switch.close_func(self.asyncswitchopen)
            self.switch.open_func(self.asyncswitchclosed)
        elif self.inputtype == 'low':
            # Setup button active low
            self.swpin                  = self._hal.pin(self.dxpin, core.PIN_IN, core.PIN_PULL_UP)
            self.switch                 = Pushbutton(self.swpin)
            self.switch.press_func(self.asyncbuttonpress)
            self.switch.release_func(self.asyncbuttonrelease)
            self.switch.double_func(self.asyncbuttondouble)
            self.switch.long_func(self.asyncbuttonlong)
        else:
            # Setup button active high
            self.swpin                  = self._hal.pin(self.dxpin, core.PIN_IN, core.PIN_PULL_DOWN)
            self.switch.press_func(self.asyncbuttonpress)
            self.switch.release_func(self.asyncbuttonrelease)
            self.switch.double_func(self.asyncbuttondouble)
            self.switch.long_func(self.asyncbuttonlong)
        
    def read(self, values):
        self._log.debug("Plugin: switch read")
        # generic section
        values['valueN1'] = self.valuenames["valueN1"]
        values['valueV1'] = self.switch_status

    def write(self, values):
        self._log.debug("Plugin: switch write")

    async def asyncprocess(self):
        self._log.debug("Plugin: switch process")
        # plugin specific section
        # If a switch occured
        if self.switch_status:
            # send data to protocol and script/rule queues
            self.valuenames["valueV1"] = self.switch_status        
            self._utils.plugin_senddata(self)
            # erase status
            self.switch_status = ""
        # release lock, ready for next measurement
        self._lock.clear()

    #
    #CUSTOM SENSOR CODE...    
    #
    
    async def asyncswitchopen(self):
        self.switch_status = 'open'
        # release lock, ready for next measurement
        self._lock.clear()

    async def asyncswitchclosed(self):
        self.switch_status = 'closed'
        # release lock, ready for next measurement
        self._lock.clear()

    async def asyncbuttonpress(self):
        self.switch_status = 'press'
        # release lock, ready for next measurement
        self._lock.clear()
        
    async def asyncbuttonrelease(self):
        self.switch_status = 'release'
        # release lock, ready for next measurement
        self._lock.clear()
        
    async def asyncbuttondouble(self):
        self.switch_status = 'double'
        # release lock, ready for next measurement
        self._lock.clear()
        
    async def asyncbuttonlong(self):
        self.switch_status = 'long'
         # release lock, ready for next measurement
        self._lock.clear()      

#
#Module Code...    
#

switch = switch_plugin()

def loadform(plugindata):
    switch.loadform(plugindata)
        
#
#CUSTOM SENSOR CODE...    
#
    
