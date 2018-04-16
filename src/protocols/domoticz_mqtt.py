#          
# Filename: domoticz mqtt.py
# Version : 0.1
# Author  : Lisa Esselink
# Purpose : Controller Domoticz MQTT & HTTP
# Usage   : Send and receive messages from Domoticz using both MQTT and HTTP
#
# Copyright (c) 2017 - Lisa Esselink. All rights reserved.  
# Licensend under the Creative Commons Attribution-NonCommercial 4.0 International License.
# See LICENSE file in the project root for full license information.  
#

import ujson, uasyncio.queues as queues
from umqtt.robust import MQTTClient
from upyeasy import protocol as uprotocol, core
from asyn import Event

#
# CUSTOM PROTOCOL GLOBALS
#

name     = "Domoticz MQTT"
protocol = "MQTT"
template = "domoticz_mqtt.html"

#
#
#

class domoticz_mqtt_protocol:
    processcnt          = 1

    def __init__(self) :
        self._log   = core._log
        self._log.debug("Protocol: domoticz mqtt contruction")
        self._lock  = Event()
        # release lock, ready for next loop
        self._lock.clear()

    def init(self, protocol):        
        self._log.debug("Protocol "+name+": Init")
        self._client_id  = protocol['client_id']
        self._server     = protocol['hostname']
        self._port       = protocol['port']
        self._user       = protocol['user']
        self._password   = protocol['password']
        self._queue_out  = protocol['publish']
        self._queue_in   = protocol['subscribe']
        self._mq         = MQTTClient(self._client_id, self._server, self._port, self._user, self._password)
        # Print diagnostic messages when retries/reconnects happens
        #self._mq.DEBUG = True
        self._queue      = queues.Queue(maxsize=100)
        return self._queue
        
    def connect(self):
        self._log.debug("Protocol "+name+": connect")
        return self._mq.reconnect()

    def disconnect(self):
        self._log.debug("Protocol "+name+": disconnect")
        self._mq.disconnect()

    def check(self):
        self._log.debug("Protocol "+name+": check")
        self._mq.check_msg()
        
    def status(self):
        self._log.debug("Protocol "+name+": status")
        self._mq.ping()

    def recieve(self):
        self._log.debug("Protocol "+name+": recieve")
        self._mq.subscribe(self.queue_in)

    def send(self, devicedata):
        self._log.debug("Protocol "+name+": send "+devicedata["stype"])
        # connect or reconnect to mqtt server
        self.connect()
        mqttdata = None
        # case
        while True:
            mqttdata = None

            # case SENSOR_TYPE_SINGLE
            if devicedata["stype"] == core.SENSOR_TYPE_SINGLE:
                self._log.debug("Protocol "+name+": SENSOR_TYPE_SINGLE")
                # Get plugin values
                try:
                    devicedata['valueV1'] = self._queue.get_nowait()
                    devicedata['valueN1'] = self._queue.get_nowait()
                except Exception as e:
                    self._log.debug("Protocol "+name+" SENSOR_TYPE_SINGLE exception: "+repr(e))
                    break
                    
                # Assemble mqtt message
                mqttdata = {}
                mqttdata["idx"] = devicedata["serverid"]
                mqttdata["nvalue"] = 0
                mqttdata["svalue"] = str(devicedata["valueV1"])
                message = ujson.dumps(mqttdata)
                break


            # case SENSOR_TYPE_LONG
            if devicedata["stype"] == core.SENSOR_TYPE_LONG:
                self._log.debug("Protocol "+name+": SENSOR_TYPE_LONG")
                break

            # case SENSOR_TYPE_DUAL
            if devicedata["stype"] == core.SENSOR_TYPE_DUAL:
                self._log.debug("Protocol "+name+": SENSOR_TYPE_DUAL")
                break

            # case SENSOR_TYPE_TEMP_HUM
            if devicedata["stype"] == core.SENSOR_TYPE_TEMP_HUM:
                self._log.debug("Protocol "+name+": SENSOR_TYPE_TEMP_HUM")
                # Get plugin values
                try:
                    devicedata['valueV1'] = self._queue.get_nowait()
                    devicedata['valueN1'] = self._queue.get_nowait()
                    devicedata['valueV2'] = self._queue.get_nowait()
                    devicedata['valueN2'] = self._queue.get_nowait()
                except Exception as e:
                    self._log.debug("Protocol "+self._name+" SENSOR_TYPE_TEMP_HUM Exception: "+repr(e))
                    break
                # Assemble mqtt message
                mqttdata = {}
                mqttdata["idx"] = devicedata["serverid"]
                mqttdata["nvalue"] = 0
                mqttdata["svalue"] = str(devicedata["valueV1"])+";"+str(devicedata["valueV2"])+";0"
                message = ujson.dumps(mqttdata)
                break

            # case SENSOR_TYPE_TEMP_BARO
            if devicedata["stype"] == core.SENSOR_TYPE_TEMP_BARO:
                self._log.debug("Protocol "+name+": SENSOR_TYPE_TEMP_BARO")
                break

            # case SENSOR_TYPE_TEMP_HUM_BARO
            if devicedata["stype"] == core.SENSOR_TYPE_TEMP_HUM_BARO:
                self._log.debug("Protocol "+name+": SENSOR_TYPE_TEMP_HUM_BARO")
                # Get plugin values
                try:
                    devicedata['valueV1'] = self._queue.get_nowait()
                    devicedata['valueN1'] = self._queue.get_nowait()
                    devicedata['valueV2'] = self._queue.get_nowait()
                    devicedata['valueN2'] = self._queue.get_nowait()
                    devicedata['valueV3'] = self._queue.get_nowait()
                    devicedata['valueN3'] = self._queue.get_nowait()
                except Exception as e:
                    self._log.debug("Protocol "+self._name+" SENSOR_TYPE_TEMP_HUM_BARO Exception: "+repr(e))
                    break
                # Assemble mqtt message
                mqttdata = {}
                mqttdata["idx"] = devicedata["serverid"]
                mqttdata["nvalue"] = 0
                mqttdata["svalue"] = str(devicedata["valueV1"])+";"+str(devicedata["valueV2"])+";0;"+str(devicedata["valueV3"])+";0"
                message = ujson.dumps(mqttdata)
                break

            # case SENSOR_TYPE_SWITCH
            if devicedata["stype"] == core.SENSOR_TYPE_SWITCH:
                self._log.debug("Protocol "+name+": SENSOR_TYPE_SWITCH")
                # Get plugin values
                try:
                    devicedata['valueV1'] = self._queue.get_nowait()
                    devicedata['valueN1'] = self._queue.get_nowait()
                except Exception as e:
                    self._log.debug("Protocol "+self._name+" SENSOR_TYPE_SWITCH Exception: "+repr(e))
                    break

                # Switches can have many values, domoticz only two: on or off
                switch_on  = ['closed','press','double','long']
                switch_off = ['open','release']    
                
                if devicedata["valueV1"] in switch_on: devicedata["valueV1"] = 'On'
                elif devicedata["valueV1"] in switch_off: devicedata["valueV1"] = 'Off'
                else: break
                
                # Assemble mqtt message
                mqttdata = {}
                mqttdata["command"] = "switchlight"
                mqttdata["idx"] = devicedata["serverid"]
                mqttdata["switchcmd"] = devicedata["valueV1"]
                message = ujson.dumps(mqttdata)
                break

            # case SENSOR_TYPE_DIMMER
            if devicedata["stype"] == core.SENSOR_TYPE_DIMMER:
                self._log.debug("Protocol "+name+": SENSOR_TYPE_DIMMER")
                break

            # case SENSOR_TYPE_WIND
            if devicedata["stype"] == core.SENSOR_TYPE_WIND:
                self._log.debug("Protocol "+name+": SENSOR_TYPE_WIND")
                break

            # else UNKNOWN
            self._log.debug("Protocol "+name+": Unknown sensor type!")
            break

        if mqttdata != None: 
           self._log.debug("Protocol "+name+": Message: "+message)
           self._mq.publish(self._queue_out, message)

    def process(self):
        # processing todo for protocol
        self._log.debug("Protocol "+name+" Processing...")
        devicedata = {}
        try:
            while True:
                message = self._queue.get_nowait() 
                if message == core.QUEUE_MESSAGE_START:
                    break
            devicedata['stype'] = self._queue.get_nowait()
            devicedata['serverid'] = self._queue.get_nowait()
            devicedata['unitname'] = self._queue.get_nowait()
            devicedata['devicename'] = self._queue.get_nowait()
            self.send(devicedata)
        except Exception as e:
            self._log.debug("Protocol "+name+" process Exception: "+repr(e))

        # release lock, ready for next processing
        self._lock.clear()
