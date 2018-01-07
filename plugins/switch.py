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
        self._log           = core._log
        self._log.debug("Plugin: switch contruction")
        self._lock          = Event()
        self.dxpin          = dxpin
        # release lock, ready for next measurement
        self._lock.clear()
        self.valuenames     = {}
        self.valuenames["valueN1"]= "switch"
        self.valuenames["valueF1"]= ""
        self.valuenames["valueD1"]= 0
        
    def init(self, plugin, device, queue):        
        self._log.debug("Plugin: switch init")
        self._plugins           = core._plugins
        self._hal               = core._hal
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
        self.dxpin              = device['dxpin']
        self.switch_status      = bootstate
        plugin['dtype']         = dtype
        plugin['stype']         = stype
        plugin['template']      = template
        datastore               = self._plugins.readstore(self.devicename)
        print(self.inputtype)
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
        plugindata['inputtype'] = self.inputtype
        plugindata['dxpin0']    = self.dxpin
        plugindata['pincnt']    = pincnt
        plugindata['valuecnt']  = valuecnt
        plugindata['valueN1']   = self.valuenames["valueN1"]
        plugindata['valueF1']   = self.valuenames["valueF1"]
        plugindata['valueD1']   = self.valuenames["valueD1"]
        plugindata['content']   = content
        
    def saveform(self,plugindata):
        self._log.debug("Plugin: switch saveform")
        self.inputtype              = plugindata['inputtype']
        self.dxpin                  = plugindata['dxpin0']
        self.valuenames["valueN1"]  = plugindata['valueN1']
        self.valuenames["valueF1"]  = plugindata['valueF1']
        self.valuenames["valueD1"]  = plugindata['valueD1']
        
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
        values['valueN1'] = self.valuenames["valueN1"]
        values['valueD1'] = self.switch_status

    def write(self, values):
        self._log.debug("Plugin: switch write")

    async def asyncprocess(self):
        # processing todo for plugin
        self._log.debug("Plugin: switch process")
        # If a controller is attached
        if self.queue and self.switch_status:
            # Put start message in queue
            self.queue.put_nowait(core.QUEUE_MESSAGE_START)
            # put sensor type in queue
            self.queue.put_nowait(stype)
            # put HA server id in queue
            self.queue.put_nowait(self.queue_sid)
            # put on / off value(s) in queue
            self.queue.put_nowait(self.switch_status)
        # erase status
        self.switch_status = ""

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
    
