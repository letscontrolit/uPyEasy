#          
# Filename: bme280.py
# Version : 0.1
# Author  : Lisa Esselink
# Purpose : Plugin BME280
# Usage   : Get BME280 sensor data
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

name                = "BME280"
dtype               = core.DEVICE_TYPE_I2C
stype               = core.SENSOR_TYPE_TEMP_HUM_BARO
template            = "bme.html"
pullup              = "off"
inverse             = "off"
port                = "off"
formula             = "off"
senddata            = "off"
timer               = "off"
sync                = "off"
delay               = 60
pincnt              = 0
valuecnt            = 3
i2c                 = 1
bme_i2c             = 118
bme_elev            = 0
content             = '<a class="button link" href="" target="_blank">?</a>'
 
import time
from ustruct import unpack, unpack_from
from array import array

# BME280 default address.
BME280_I2CADDR = 0x76

# Operating Modes
BME280_OSAMPLE_1 = 1
BME280_OSAMPLE_2 = 2
BME280_OSAMPLE_4 = 3
BME280_OSAMPLE_8 = 4
BME280_OSAMPLE_16 = 5

BME280_REGISTER_CONTROL_HUM = 0xF2
BME280_REGISTER_CONTROL = 0xF4

#
#
#

class bme280_plugin:
    valuenames          = {}
    datastore           = None
    
    def __init__(self) :
        self._log       = core._log
        self._log.debug("Plugin: bme280 contruction")
        self._lock      = Event()
        # release lock, ready for next measurement
        self._lock.clear()
        self.valuenames["valueN1"]= "Temperature"
        self.valuenames["valueN2"]= "Humidity"
        self.valuenames["valueN3"]= "Pressure"
        self.valuenames["valueF1"]= ""
        self.valuenames["valueF2"]= ""
        self.valuenames["valueF3"]= ""
        self.valuenames["valueD1"]= 0
        self.valuenames["valueD2"]= 0
        self.valuenames["valueD3"]= 0
        
    def init(self,plugin, device, queue):        
        self._log.debug("Plugin: bme280 init")
        self._plugins           = core._plugins
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
        self.bme_i2c            = bme_i2c
        self.pincnt             = pincnt
        self.valuecnt           = valuecnt
        self.bme_elev           = bme_elev
        self.stype              = stype
        plugin['dtype']         = dtype
        plugin['stype']         = stype
        plugin['template']      = template
        datastore               = self._plugins.readstore(device["name"])
        self.i2c                = core._hal.get_i2c(i2c)
        if self.i2c != None: 
            try:
                self.bme280_init(address=self.bme_i2c)
            except OSError as e:
                self._log.debug("Plugin: bme280 init OSError exception: "+repr(e))
        return True

    def loadform(self,plugindata):
        self._log.debug("Plugin: bme280 loadform")
        plugindata['pincnt']    = self.pincnt
        plugindata['valuecnt']  = self.valuecnt
        plugindata['bme_i2c']   = self.bme_i2c
        plugindata['bme_elev']  = self.bme_elev
        plugindata['valueN1']   = self.valuenames["valueN1"]
        plugindata['valueN2']   = self.valuenames["valueN2"]
        plugindata['valueN3']   = self.valuenames["valueN3"]
        plugindata['valueF1']   = self.valuenames["valueF1"]
        plugindata['valueF2']   = self.valuenames["valueF2"]
        plugindata['valueF3']   = self.valuenames["valueF3"]
        plugindata['valueD1']   = self.valuenames["valueD1"]
        plugindata['valueD2']   = self.valuenames["valueD2"]
        plugindata['valueD3']   = self.valuenames["valueD3"]
        plugindata['content']   = self.content
        
    def saveform(self,plugindata):
        self._log.debug("Plugin: bme280 saveform")
        sf_bme_i2c                  = plugindata.get('bme_i2c',None)
        if sf_bme_i2c: self.bme_i2c = int(sf_bme_i2c)
        else: self.bme_i2c = None
        sf_bme_elev                 = plugindata.get('bme_elev',None)
        if sf_bme_elev: self.bme_elev = int(sf_bme_elev)
        else: self.bme_elev = None
        self.valuenames["valueN1"]  = plugindata['valueN1']
        self.valuenames["valueN2"]  = plugindata['valueN2']
        self.valuenames["valueN3"]  = plugindata['valueN3']
        self.valuenames["valueF1"]  = plugindata['valueF1']
        self.valuenames["valueF2"]  = plugindata['valueF2']
        self.valuenames["valueF3"]  = plugindata['valueF3']
        self.valuenames["valueD1"]  = plugindata['valueD1']
        self.valuenames["valueD2"]  = plugindata['valueD2']
        self.valuenames["valueD3"]  = plugindata['valueD3']
        self.i2c                    = core._hal.get_i2c(i2c)
        if self.bme_i2c:
            try:
                if self.i2c != None: self.bme280_init(address=self.bme_i2c)
            except OSError as e:
                self._log.debug("Plugin: bme280 saveform OSError exception: "+repr(e))

    def read(self, values):
        self._log.debug("Plugin: bme280 read")
        #(hum, temp;, press) = bme280_read_compensated_data()
        if self.i2c != None: 
            try:
                dvalues = self.bme280_values()
            except Exception as e:
                self._log.debug("Plugin: bme280 read exception: "+repr(e))

            values['valueN1'] = self.valuenames["valueN1"]
            values["valueD1"] = dvalues[0]
            values['valueN2'] = self.valuenames["valueN2"]
            values["valueD2"] = dvalues[2]
            values['valueN3'] = self.valuenames["valueN3"]
            values["valueD3"] = dvalues[1]
        else:
            self._log.debug("Plugin: ds18 read, empty values")
            # dummy values
            values['valueN1'] = ''
            values["valueD1"] = ''
        return values
   
    def write(self):
        self._log.debug("Plugin: bme280 write")

    async def asyncprocess(self):
        # processing todo for plugin
        self._log.debug("Plugin: bme280 process")
        if self.queue and self.i2c: 
            try:
                values = self.bme280_values()
            except Exception as e:
                self._log.debug("Plugin: bme280 process exception: "+repr(e))
            # Put start message in queue
            self.queue.put_nowait(core.QUEUE_MESSAGE_START)
            # put sensor type in queue
            self.queue.put_nowait(self.stype)
            # put HA server id in queue
            self.queue.put_nowait(self.queue_sid)
            # put temperature value(s) in queue
            self.queue.put_nowait(values[0][:-1])
            # put humidity value(s) in queue
            self.queue.put_nowait(values[2][:-1])
            # put pressure value(s) in queue
            self.queue.put_nowait(values[1][:-3])
        # release lock, ready for next measurement
        self._lock.clear()
        
    #
    #CUSTOM SENSOR CODE...    
    #
    
    def bme280_init(self,
                 mode=BME280_OSAMPLE_1,
                 address=BME280_I2CADDR,
                 **kwargs):
        # Check that mode is valid.
        if mode not in [BME280_OSAMPLE_1, BME280_OSAMPLE_2, BME280_OSAMPLE_4,
                        BME280_OSAMPLE_8, BME280_OSAMPLE_16]:
            raise ValueError(
                'Unexpected mode value {0}. Set mode to one of '
                'BME280_ULTRALOWPOWER, BME280_STANDARD, BME280_HIGHRES, or '
                'BME280_ULTRAHIGHRES'.format(mode))
        self._mode = mode
        self.address = address

        # load calibration data
        dig_88_a1 = self.i2c.readfrom_mem(self.address, 0x88, 26)
        dig_e1_e7 = self.i2c.readfrom_mem(self.address, 0xE1, 7)
        self.dig_T1, self.dig_T2, self.dig_T3, self.dig_P1, \
            self.dig_P2, self.dig_P3, self.dig_P4, self.dig_P5, \
            self.dig_P6, self.dig_P7, self.dig_P8, self.dig_P9, \
            _, self.dig_H1 = unpack("<HhhHhhhhhhhhBB", dig_88_a1)

        self.dig_H2, self.dig_H3 = unpack("<hB", dig_e1_e7)
        e4_sign = unpack_from("<b", dig_e1_e7, 3)[0]
        self.dig_H4 = (e4_sign << 4) | (dig_e1_e7[4] & 0xF)

        e6_sign = unpack_from("<b", dig_e1_e7, 5)[0]
        self.dig_H5 = (e6_sign << 4) | (dig_e1_e7[4] >> 4)

        self.dig_H6 = unpack_from("<b", dig_e1_e7, 6)[0]

        self.i2c.writeto_mem(self.address, BME280_REGISTER_CONTROL,
                             bytearray([0x3F]))
        self.t_fine = 0

        # temporary data holders which stay allocated
        self._l1_barray = bytearray(1)
        self._l8_barray = bytearray(8)
        self._l3_resultarray = array("i", [0, 0, 0])

    def bme280_read_raw_data(self, result):
        """ Reads the raw (uncompensated) data from the sensor.

            Args:
                result: array of length 3 or alike where the result will be
                stored, in temperature, pressure, humidity order
            Returns:
                None
        """

        self._l1_barray[0] = self._mode
        self.i2c.writeto_mem(self.address, BME280_REGISTER_CONTROL_HUM,
                             self._l1_barray)
        self._l1_barray[0] = self._mode << 5 | self._mode << 2 | 1
        self.i2c.writeto_mem(self.address, BME280_REGISTER_CONTROL,
                             self._l1_barray)

        sleep_time = 1250 + 2300 * (1 << self._mode)
        sleep_time = sleep_time + 2300 * (1 << self._mode) + 575
        sleep_time = sleep_time + 2300 * (1 << self._mode) + 575
        time.sleep_us(sleep_time)  # Wait the required time

        # burst readout from 0xF7 to 0xFE, recommended by datasheet
        self.i2c.readfrom_mem_into(self.address, 0xF7, self._l8_barray)
        readout = self._l8_barray
        # pressure(0xF7): ((msb << 16) | (lsb << 8) | xlsb) >> 4
        raw_press = ((readout[0] << 16) | (readout[1] << 8) | readout[2]) >> 4
        # temperature(0xFA): ((msb << 16) | (lsb << 8) | xlsb) >> 4
        raw_temp = ((readout[3] << 16) | (readout[4] << 8) | readout[5]) >> 4
        # humidity(0xFD): (msb << 8) | lsb
        raw_hum = (readout[6] << 8) | readout[7]

        result[0] = raw_temp
        result[1] = raw_press
        result[2] = raw_hum

    def bme280_read_compensated_data(self, result=None):
        """ Reads the data from the sensor and returns the compensated data.

            Args:
                result: array of length 3 or alike where the result will be
                stored, in temperature, pressure, humidity order. You may use
                this to read out the sensor without allocating heap memory

            Returns:
                array with temperature, pressure, humidity. Will be the one from
                the result parameter if not None
        """
        self.bme280_read_raw_data(self._l3_resultarray)
        raw_temp, raw_press, raw_hum = self._l3_resultarray
        # temperature
        var1 = ((raw_temp >> 3) - (self.dig_T1 << 1)) * (self.dig_T2 >> 11)
        var2 = (((((raw_temp >> 4) - self.dig_T1) *
                  ((raw_temp >> 4) - self.dig_T1)) >> 12) * self.dig_T3) >> 14
        self.t_fine = var1 + var2
        temp = (self.t_fine * 5 + 128) >> 8

        # pressure
        var1 = self.t_fine - 128000
        var2 = var1 * var1 * self.dig_P6
        var2 = var2 + ((var1 * self.dig_P5) << 17)
        var2 = var2 + (self.dig_P4 << 35)
        var1 = (((var1 * var1 * self.dig_P3) >> 8) +
                ((var1 * self.dig_P2) << 12))
        var1 = (((1 << 47) + var1) * self.dig_P1) >> 33
        if var1 == 0:
            pressure = 0
        else:
            p = 1048576 - raw_press
            p = (((p << 31) - var2) * 3125) // var1
            var1 = (self.dig_P9 * (p >> 13) * (p >> 13)) >> 25
            var2 = (self.dig_P8 * p) >> 19
            pressure = ((p + var1 + var2) >> 8) + (self.dig_P7 << 4)

        # humidity
        h = self.t_fine - 76800
        h = (((((raw_hum << 14) - (self.dig_H4 << 20) -
                (self.dig_H5 * h)) + 16384)
              >> 15) * (((((((h * self.dig_H6) >> 10) *
                            (((h * self.dig_H3) >> 11) + 32768)) >> 10) +
                          2097152) * self.dig_H2 + 8192) >> 14))
        h = h - (((((h >> 15) * (h >> 15)) >> 7) * self.dig_H1) >> 4)
        h = 0 if h < 0 else h
        h = 419430400 if h > 419430400 else h
        humidity = h >> 12

        if result:
            result[0] = temp
            result[1] = pressure
            result[2] = humidity
            return result

        return array("i", (temp, pressure, humidity))

    def bme280_values(self):
        """ human readable values """

        t, p, h = self.bme280_read_compensated_data()

        p = p // 256
        pi = p // 100
        pd = p - pi * 100

        hi = h // 1024
        hd = h * 100 // 1024 - hi * 100
        return ("{}C".format(t / 100), "{}.{:02d}hPa".format(pi, pd),
                "{}.{:02d}%".format(hi, hd))
   