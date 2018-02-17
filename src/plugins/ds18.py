#          
# Filename: ds18.py
# Version : 0.1
# Author  : Lisa Esselink
# Purpose : Plugin DS18B20
# Usage   : Get DS18b20 sensor data
#
# Copyright (c) 2018 - Lisa Esselink. All rights reserved.  
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
        # generic section
        self._log       = core._log
        self._log.debug("Plugin: ds18 contruction")
        self._utils     = core._utils
        self._plugins   = core._plugins
        self._hal       = core._hal
        self._lock      = Event()
        # plugin specific section
        self.dxpin      = dxpin
        self.valuenames["valueN1"]= "Temperature"
        self.valuenames["valueF1"]= ""
        self.valuenames["valueD1"]= 0
        # release lock, ready for next measurement
        self._lock.clear()
        
    def init(self, plugin, device, queue, scriptqueue):        
        self._log.debug("Plugin: ds18 init")
        # generic section
        self._utils.plugin_initdata(self, plugin, device, queue, scriptqueue)
        self.pincnt             = pincnt
        self.valuecnt           = valuecnt
        self.stype              = stype
        self.content            = plugin.get('content',content)
        self.dxpin              = device.get('dxpin',dxpin)
        plugin['dtype']         = dtype
        plugin['stype']         = stype
        plugin['template']      = template
        datastore               = self._plugins.readstore(device["name"])
        # plugin specific section
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
        # generic section
        self._utils.plugin_loadform(self, plugindata)
        plugindata['dxpin0']    = self.dxpin
        # plugin specific section
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
        # generic section
        self._utils.plugin_saveform(self, plugindata)
        self.dxpin                  = plugindata['dxpin0']

        # plugin specific section
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
        # plugin specific section
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
                values["valueV1"] = "{}c".format(self.ds18.read_temp(rom))
        else:
            self._log.debug("Plugin: ds18 read, empty values")
            # dummy values
            values['valueN1'] = ''
            values["valueV1"] = ''
   
    def write(self, values):
        self._log.debug("Plugin: ds18 write")

    async def asyncprocess(self):
        self._log.debug("Plugin: ds18 process")
        # plugin specific section
        if not self.roms == None:
            for rom in self.roms:
                # Set convert on
                self.ds18.convert_temp()
                # wait 750ms for value to return
                await asyncio.sleep_ms(750)
                # put temperature value(s) in queue
                ds18temp = self.ds18.read_temp(rom)
                self._log.debug("Plugin: ds18 data read: "+str(ds18temp))
                # send data to protocol and script/rule queues
                self.valuenames["valueV1"] = ds18temp        
                self._utils.plugin_senddata(self)
        # release lock, ready for next measurement
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
    
