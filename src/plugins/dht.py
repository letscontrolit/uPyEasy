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

#import uasyncio.queues as queues
from machine import Pin
from upyeasy import core
from asyn import Event

#
# CUSTOM SENSOR GLOBALS
#

# We need to use global properties here as any allocation of a memory (aka declaration of a variable)
# during the read cycle causes non-acceptable delay and we are loosing data than
nc = None
gnd = None
vcc = None
data = None
timer = None
micros = None

FALL_EDGES = 42 # we have 42 falling edges during data receive

times = list(range(FALL_EDGES))
index = 0

#
#
#

class dht_plugin:
    name                = "DHT 11/12/22"
    dtype               = core.DEVICE_TYPE_SINGLE
    stype               = core.SENSOR_TYPE_TEMP_HUM
    template            = "dht.html"
    pullup              = "off"
    inverse             = "off"
    port                = "off"
    formula             = "off"
    senddata            = "off"
    timer               = "off"
    sync                = "off"
    delay               = 0
    pincnt              = 2
    valuecnt            = 2
    dxpin0              = 0
    dxpin1              = 1
    dhttype             = "11"
    valuenames          = {}
    content             = '<a class="button link" href="" target="_blank">?</a>'
    datastore           = None
    
    def __init__(self) :
        self._log       = core._log
        self._log.debug("Plugin: dht contruction")
        self._lock      = Event()
        # release lock, ready for next measurement
        self._lock.clear()
        self.valuenames["valueN1"]= "Temperature"
        self.valuenames["valueN2"]= "Humidity"
        self.valuenames["valueF1"]= ""
        self.valuenames["valueF2"]= ""
        self.valuenames["valueD1"]= 0
        self.valuenames["valueD2"]= 0
        
    def init(self, plugin, device, queue):        
        self._log.debug("Plugin: dht init")
        self._plugins           = core._plugins
        self.pullup             = plugin['pullup'] # 0=false, 1=true
        self.inverse            = plugin['inverse']
        self.port               = plugin['port']
        self.formula            = plugin['formula']
        self.senddata           = plugin['senddata']
        self.timer              = plugin['timer']
        self.sync               = plugin['sync']
        self.valuecnt           = plugin['valuecnt']
        self.content            = plugin.get('content',self.content)
        self.queue              = queue
        self.queue_sid          = device["controllerid"]
        plugin['dtype']         = self.dtype
        plugin['stype']         = self.stype
        plugin['template']      = self.template
        datastore               = self._plugins.readstore(self.name)
        #DHT.init()
        return True

    def loadform(self,plugindata):
        self._log.debug("Plugin: dht loadform")
        plugindata['dhttype']   = self.dhttype
        plugindata['pincnt']    = self.pincnt
        plugindata['valuecnt']  = self.valuecnt
        plugindata['valueN1']   = self.valuenames["valueN1"]
        plugindata['valueN2']   = self.valuenames["valueN2"]
        plugindata['valueF1']   = self.valuenames["valueF1"]
        plugindata['valueF2']   = self.valuenames["valueF2"]
        plugindata['valueD1']   = self.valuenames["valueD1"]
        plugindata['valueD2']   = self.valuenames["valueD2"]
        plugindata['content']   = self.content
        
    def saveform(self,plugindata):
        self._log.debug("Plugin: dht saveform")
        self.dhttype                = plugindata['dhttype']
        self.dxpin0                 = plugindata['dxpin0']
        self.dxpin1                 = plugindata['dxpin1']
        self.valuenames["valueN1"]  = plugindata['valueN1']
        self.valuenames["valueN2"]  = plugindata['valueN2']
        self.valuenames["valueF1"]  = plugindata['valueF1']
        self.valuenames["valueF2"]  = plugindata['valueF2']
        self.valuenames["valueD1"]  = plugindata['valueD1']
        self.valuenames["valueD2"]  = plugindata['valueD2']

    def read(self):
        self._log.debug("Plugin: dht read")
        #(hum, temp) = DHT.measure()
        values={}
        values['valueN1'] = self.valuenames["valueN1"]
        values["valueD1"] = self.valuenames["valueD1"]
        values['valueN2'] = self.valuenames["valueN2"]
        values["valueD2"] = self.valuenames["valueD2"]
        return values
   
    def write(self):
        self._log.debug("Plugin: dht write")

    async def asyncprocess(self):
        # processing todo for plugin
        self._log.debug("Plugin: dht process")
        # put sensor type in queue
        self.queue.put_nowait(self.stype)
        # put HA server id in queue
        self.queue.put_nowait(self.queue_sid)
        # put temperature value(s) in queue
        self.queue.put_nowait(25)
        # put humidity value(s) in queue
        self.queue.put_nowait(55)
        # release lock, ready for next measurement
        self._lock.clear()

    #
    #CUSTOM SENSOR CODE...    
    #
    
    # The interrupt handler
''''    def edge(line):
        global index
        global times
        global micros
        times[index] = micros.counter()
        if index < (FALL_EDGES - 1): # Avoid overflow of the buffer in case of any noise on the line
            index += 1

    def init(timer_id = 2, nc_pin = 'Y3', gnd_pin = 'Y4', vcc_pin = 'Y1', data_pin = 'Y2'):
        global nc
        global gnd
        global vcc
        global data
        global micros
        global timer
        # Leave the pin unconnected
        if nc_pin is not None:
            nc = Pin(nc_pin)
            nc.init(Pin.OUT_OD)
            nc.high()
        # Make the pin work as GND
        if gnd_pin is not None:
            gnd = Pin(gnd_pin)
            gnd.init(Pin.OUT_PP)
            gnd.low()
        # Make the pin work as power supply
        if vcc_pin is not None:
            vcc = Pin(vcc_pin)
            vcc.init(Pin.OUT_PP)
            vcc.high()
        # Configure the pid for data communication
        data = Pin(data_pin)
        # Save the ID of the timer we are going to use
        timer = timer_id
        # setup the 1uS timer
        micros = pyb.Timer(timer, prescaler=83, period=0x3fffffff) # 1MHz ~ 1uS
        # Prepare interrupt handler
        ExtInt(data, ExtInt.IRQ_FALLING, Pin.PULL_UP, None)
        ExtInt(data, ExtInt.IRQ_FALLING, Pin.PULL_UP, edge)

    # Start signal
    def do_measurement():
        global nc
        global gnd
        global vcc
        global data
        global micros
        global timer
        global index
        # Send the START signal
        data.init(Pin.OUT_PP)
        data.low()
        micros.counter(0)
        while micros.counter() < 25000:
            pass
        data.high()
        micros.counter(0)
        while micros.counter() < 20:
            pass
        # Activate reading on the data pin
        index = 0
        data.init(Pin.IN, Pin.PULL_UP)
        # Till 5mS the measurement must be over
        pyb.delay(5)

    # Parse the data read from the sensor
    def process_data():
        global times
        i = 2 # We ignore the first two falling edges as it is a respomse on the start signal
        result_i = 0
        result = list([0, 0, 0, 0, 0])
        while i < FALL_EDGES:
            result[result_i] <<= 1
            if times[i] - times[i - 1] > 100:
                result[result_i] += 1
            if (i % 8) == 1:
                result_i += 1
            i += 1
        [int_rh, dec_rh, int_t, dec_t, csum] = result
        humidity = ((int_rh * 256) + dec_rh)/10
        temperature = (((int_t & 0x7F) * 256) + dec_t)/10
        if (int_t & 0x80) > 0:
            temperature *= -1
        comp_sum = int_rh + dec_rh + int_t + dec_t
        if (comp_sum & 0xFF) != csum:
            raise ValueError('Checksum does not match')
        return (humidity, temperature)

    def measure():
        do_measurement()
        if index != (FALL_EDGES -1):
            raise ValueError('Data transfer failed: %s falling edges only' % str(index))
        return process_data()        
 '''           
