#          
# Filename: ds18.py
# Version : 0.1
# Author  : Lisa Esselink
# Purpose : Plugin DS18B20
# Usage   : Get DS18b20 sensor data
#
# Copyright (c) 2017 - Lisa Esselink. All rights reserved.  
# Licensend under the Creative Commons Attribution-NonCommercial 4.0 International License.
# See LICENSE file in the project root for full license information.  
#

import uasyncio as asyncio
from upyeasy import core
from asyn import Event

#
# CUSTOM SENSOR GLOBALS
#

import onewire, ds18x20

name                = "DS18B20"
dtype               = core.DEVICE_TYPE_SINGLE
stype               = core.SENSOR_TYPE_SINGLE
template            = "ds18.html"
pullup              = "off"
inverse             = "off"
port                = "off"
formula             = "off"
senddata            = "off"
timer               = "off"
sync                = "off"
delay               = 60
pincnt              = 1
valuecnt            = 1
dxpin               = "d0"
resolution          = 9
content             = '<a class="button link" href="" target="_blank">?</a>'

#
#
#

class ds18_plugin:
    valuenames          = {}
    datastore           = None
    roms                = None
    
    def __init__(self) :
        self._log       = core._log
        self._log.debug("Plugin: ds18 contruction")
        self._lock      = Event()
        self.dxpin      = dxpin
        # release lock, ready for next measurement
        self._lock.clear()
        self.valuenames["valueN1"]= "Temperature"
        self.valuenames["valueF1"]= ""
        self.valuenames["valueD1"]= 0
        
    def init(self, plugin, device, queue):        
        self._log.debug("Plugin: ds18 init")
        self._plugins           = core._plugins
        self._hal               = core._hal
        self.pullup             = plugin['pullup'] # 0=false, 1=true
        self.inverse            = plugin['inverse']
        self.port               = plugin['port']
        self.formula            = plugin['formula']
        self.senddata           = plugin['senddata']
        self.timer              = plugin['timer']
        self.sync               = plugin['sync']
        self.valuecnt           = plugin['valuecnt']
        self.content            = plugin.get('content',content)
        self.queue              = queue
        self.queue_sid          = device["controllerid"]
        self.devicename         = device["name"]
        self.dxpin              = device.get('dxpin',dxpin)
        plugin['dtype']         = dtype
        plugin['stype']         = stype
        plugin['template']      = template
        datastore               = self._plugins.readstore(device["name"])
        self._log.debug("Plugin: ds18 init, pin used: "+str(self.dxpin))
        # the device is on Dx
        self.mPin                   = self._hal.pin(self.dxpin)
        # create the onewire object
        self.ds18                   = ds18x20.DS18X20(onewire.OneWire(self.mPin))
        # scan for devices on the bus
        roms                        = self.ds18.scan()
        # scan for devices on the bus
        self.roms                   = self.ds18.scan()

        return True

    def loadform(self,plugindata):
        self._log.debug("Plugin: ds18 loadform")
        plugindata['pincnt']    = pincnt
        plugindata['dxpin0']    = self.dxpin
        plugindata['valuecnt']  = valuecnt
        plugindata['valueN1']   = self.valuenames["valueN1"]
        plugindata['valueF1']   = self.valuenames["valueF1"]
        plugindata['valueD1']   = self.valuenames["valueD1"]
        plugindata['content']   = content
        plugindata['resolution']= resolution
        romcnt = 0
        if not self.roms == None:
            for rom in self.roms:
                plugindata['rom'+str(romcnt)] = ''.join('{:02x}-'.format(x) for x in rom)[:-1]
                self._log.debug("Plugin: ds18 loadform, rom: "+plugindata['rom'+str(romcnt)])
                romcnt+=1
        else:
            self._log.debug("Plugin: ds18 loadform, no roms!")
        plugindata['romcnt']    = romcnt
        
    def saveform(self,plugindata):
        self._log.debug("Plugin: ds18 saveform")
        self.dxpin                  = plugindata['dxpin0']
        self.valuenames["valueN1"]  = plugindata['valueN1']
        self.valuenames["valueF1"]  = plugindata['valueF1']
        self.valuenames["valueD1"]  = plugindata['valueD1']
        self.romid                  = plugindata.get('deviceid','')
        self.resolution             = plugindata['resolution']

        # store values
        data = {}
        data["romid"]       = self.romid
        data["dxpin"]       = self.dxpin
        data["resolution"]  = self.resolution
        data["valueN1"]     = self.valuenames["valueN1"]
        data["valueF1"]     = self.valuenames["valueF1"] 
        data["valueD1"]     = self.valuenames["valueD1"]
        self._plugins.writestore(self.devicename, data)

        # the device is on Dx
        self.mPin                   = self._hal.pin(self.dxpin)
        self._log.debug("Plugin: ds18 saveform, pin used: "+str(self.dxpin))
        # create the onewire object
        self.ds18                   = ds18x20.DS18X20(onewire.OneWire(self.mPin))
        # scan for devices on the bus
        roms                        = self.ds18.scan()
        # scan for devices on the bus
        self.roms                   = self.ds18.scan()
        
    def read(self, values):
        self._log.debug("Plugin: ds18 read")
        if not self.roms == None:
            for rom in self.roms:
                # Set convert on
                self.ds18.convert_temp()
                # wait 750ms for value to return
                #await asyncio.sleep_ms(750)
                import utime
                utime.sleep_ms(750)
                # Read temp
                values['valueN1'] = ''.join('{:02x}-'.format(x) for x in rom)[:-1]
                values["valueD1"] = self.ds18.read_temp(rom)
        else:
            self._log.debug("Plugin: ds18 read, empty values")
            # dummy values
            values['valueN1'] = ''
            values["valueD1"] = ''
   
    def write(self, values):
        self._log.debug("Plugin: ds18 write")

    async def asyncprocess(self):
        # processing todo for plugin
        self._log.debug("Plugin: ds18 process")
        if not self.roms == None:
            for rom in self.roms:
                # If a controller is attached
                if self.queue:
                    # Set convert on
                    self.ds18.convert_temp()
                    # wait 750ms for value to return
                    await asyncio.sleep_ms(750)
                    # Put start message in queue
                    self.queue.put_nowait(core.QUEUE_MESSAGE_START)
                    # put sensor type in queue
                    self.queue.put_nowait(stype)
                    # put HA server id in queue
                    self.queue.put_nowait(self.queue_sid)
                    # put temperature value(s) in queue
                    ds18temp = self.ds18.read_temp(rom)
                    self._log.debug("Plugin: ds18 data read: "+str(ds18temp))
                    self.queue.put_nowait(ds18temp)
        # put humidity value(s) in queue
        self._lock.clear()

#
#Module Code...    
#

ds18 = ds18_plugin()

def loadform(plugindata):
    ds18.loadform(plugindata)
        
#
#CUSTOM SENSOR CODE...    
#
    
