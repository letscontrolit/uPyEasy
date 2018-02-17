#          
# Filename: bme280.py
# Version : 0.1
# Author  : Lisa Esselink
# Purpose : Plugin BME280
# Usage   : Get BME280 sensor data
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
        # generic section
        self._log       = core._log
        self._log.debug("Plugin: bme280 contruction")
        self._utils     = core._utils
        self._plugins   = core._plugins
        self._lock      = Event()
        # plugin specific section
        self.valuenames["valueN1"]= "Temperature"
        self.valuenames["valueN2"]= "Humidity"
        self.valuenames["valueN3"]= "Pressure"
        self.valuenames["valueF1"]= ""
        self.valuenames["valueF2"]= ""
        self.valuenames["valueF3"]= ""
        self.valuenames["valueD1"]= 0
        self.valuenames["valueD2"]= 0
        self.valuenames["valueD3"]= 0
        # release lock, ready for next measurement
        self._lock.clear()
        
    def init(self, plugin, device, queue, scriptqueue):        
        self._log.debug("Plugin: bme280 init")
        # plugin generic section
        self._utils.plugin_initdata(self, plugin, device, queue, scriptqueue)
        self.content            = plugin.get('content',content)
        self.pincnt             = pincnt
        self.valuecnt           = valuecnt
        self.stype              = stype
        plugin['dtype']         = dtype
        plugin['stype']         = stype
        plugin['template']      = template
        datastore               = self._plugins.readstore(device["name"])
        # plugin specific section
        self.bme_elev           = bme_elev
        self.bme_i2c            = bme_i2c
        self.i2c                = core._hal.get_i2c(i2c)
        if self.i2c != None: 
            try:
                self.bme280_init(address=self.bme_i2c)
            except OSError as e:
                self._log.debug("Plugin: bme280 init OSError exception: "+repr(e))
        return True

    def loadform(self,plugindata):
        self._log.debug("Plugin: bme280 loadform")
        # generic section
        self._utils.plugin_loadform(self, plugindata)
        # plugin specific section
        plugindata['bme_i2c']   = self.bme_i2c
        plugindata['bme_elev']  = self.bme_elev
        
    def saveform(self,plugindata):
        self._log.debug("Plugin: bme280 saveform")
        # generic section
        self._utils.plugin_saveform(self, plugindata)
        # plugin specific section
        sf_bme_i2c                  = plugindata.get('bme_i2c',None)
        if sf_bme_i2c: self.bme_i2c = int(sf_bme_i2c)
        else: self.bme_i2c = None
        sf_bme_elev                 = plugindata.get('bme_elev',None)
        if sf_bme_elev: self.bme_elev = int(sf_bme_elev)
        else: self.bme_elev = None
        self.i2c                    = core._hal.get_i2c(i2c)
        if self.bme_i2c:
            try:
                if self.i2c != None: self.bme280_init(address=self.bme_i2c)
            except OSError as e:
                self._log.debug("Plugin: bme280 saveform OSError exception: "+repr(e))

    def read(self, values):
        self._log.debug("Plugin: bme280 read")
        # generic section
        values['valueN1'] = self.valuenames["valueN1"]
        values['valueN2'] = self.valuenames["valueN2"]
        values['valueN3'] = self.valuenames["valueN3"]
        # plugin specific section
        if self.i2c != None: 
            try:
                dvalues = self.bme280_values()
            except Exception as e:
                self._log.debug("Plugin: bme280 read exception: "+repr(e))
                values['valueV1'] = ''
                values['valueV2'] = ''
                values['valueV3'] = ''
                return values
            values["valueV1"] = dvalues[0]
            values["valueV2"] = dvalues[2]
            values["valueV3"] = dvalues[1]
        else:
            self._log.debug("Plugin: ds18 read, empty values")
            # empty values
            values['valueV1'] = ''
            values['valueV2'] = ''
            values['valueV3'] = ''
        return values
   
    def write(self):
        self._log.debug("Plugin: bme280 write")

    async def asyncprocess(self):
        # plugin specific section
        self._log.debug("Plugin: bme280 process")
        if self.i2c: 
            try:
                t, p, h = self.bme280_read_compensated_data()
            except Exception as e:
                self._log.debug("Plugin: bme280 process exception: "+repr(e))
                # release lock, ready for next measurement
                self._lock.clear()
                return
            # send data to protocol and script/rule queues
            self.valuenames["valueV1"] = t/100       
            self.valuenames["valueV2"] = h/1024        
            self.valuenames["valueV3"] = p/25600       
            self._utils.plugin_senddata(self)
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
        return ("{}c".format(t / 100), "{}.{:02d}hPa".format(pi, pd),
                "{}.{:02d}%".format(hi, hd))
