#          
# Filename: openhab mqtt.py
# Version : 0.12 (includes latest changes from valueD1 to valueV1)
# Author  : Andrew Jackson (based on domoticz_mqtt.py by Lisa Esselink)
# Purpose : Controller OpenHAB MQTT
# Usage   : Send and receive messages from OpenHAB and compatible controllers, using both MQTT and HTTP
# Status  : ALPHA: first version using topic in style Unitname/Devicename/Valuename. Currently, only SINGLE sensor case.
#         : Publish only.
# Copyright (c) 2018 - Andrew Jackson/Lisa Esselink. All rights reserved.  
# Licensed under the Creative Commons Attribution-NonCommercial 4.0 International License.
# See LICENSE file in the project root for full license information.  
#         : code simplified to reduce duplication in send()

import ujson, uasyncio.queues as queues  # replaced ujson by json (?) # uasyncio gives not found error (in Pycharm console)!
from umqtt.robust import MQTTClient
from upyeasy import protocol as uprotocol, core
from asyn import Event

#
# CUSTOM PROTOCOL GLOBALS
#

name     = "OpenHAB MQTT"
protocol = "MQTT"
template = "openhab_mqtt.html"

#
#
#

class openhab_mqtt_protocol:
    processcnt          = 1

    def __init__(self) :
        self._log   = core._log
        self._log.debug("Protocol: openhab mqtt contruction")
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
        self._queue_out1  = {}
        self._queue_out2  = {}
        self._queue_out3  = {}
        self._queue_out  = protocol['publish'] #### was commented out AJ, now back in
        self._pubstr     = protocol['publish'] #### added AJ
        self._queue_in   = protocol['subscribe']
        self._mq         = MQTTClient(self._client_id, self._server, self._port, self._user, self._password)
        # Print diagnostic messages when retries/reconnects happens
        self._mq.DEBUG = True
        self._queue      = queues.Queue(maxsize=100)
        return self._queue
        
    def connect(self):
        self._log.debug("Protocol: "+name+": connect")
        return self._mq.reconnect()

    def disconnect(self):
        self._log.debug("Protocol: "+name+": disconnect")
        self._mq.disconnect()

    def check(self):
        self._log.debug("Protocol: "+name+": check")
        self._mq.check_msg()
        
    def status(self):
        self._log.debug("Protocol: "+name+": status")
        self._mq.ping()

    def recieve(self):
        self._log.debug("Protocol: "+name+": recieve")
        self._mq.subscribe(self.queue_in)

    def send(self, devicedata):
        self._log.debug("Protocol: "+name+": send "+devicedata["stype"])
        # connect or reconnect to mqtt server
        self.connect()
        mqttdata1 = None
        mqttdata2 = None
        mqttdata3 = None
        
        # case - all sensor types
        while True:
            mqttdata1 = None  # looks like duplication of above!
            mqttdata1 = {}
            mqttdata2 = {}
            mqttdata3 = {}
            self._queue_out1 = ''
            self._queue_out2 = ''
            self._queue_out3 = ''
            message1 = ''
            message2 = ''
            message3 = ''

            # Get next plugin datavalues from utils.py, plugin_senddata(self, queuedata)
            try:
                devicedata['unitname'] = self._queue.get_nowait()
                devicedata['devicename'] = self._queue.get_nowait()
            except Exception as e:
                self._log.debug("Protocol: "+name+" SENSOR_TYPE_SINGLE exception: "+repr(e))
                break
            
            # case SENSOR_TYPE_SINGLE
            if devicedata["stype"] == core.SENSOR_TYPE_SINGLE:
                # get plugin values
                devicedata['valueV1'] = self._queue.get_nowait()
                devicedata['valueN1'] = self._queue.get_nowait()
                # Assemble mqtt message
                mqttdata1 = {}
                mqttdata1['topic'] = devicedata['unitname']+"/"+devicedata['devicename']+"/"+devicedata['valueN1']
                mqttdata1['msg'] = str(devicedata["valueV1"])
                message1 = str(devicedata["valueV1"])
                break

            # case SENSOR_TYPE_LONG
            if devicedata["stype"] == core.SENSOR_TYPE_LONG:
                self._log.debug("Protocol: "+name+": SENSOR_TYPE_LONG")
                break
            
            # case SENSOR_TYPE_DUAL
            if devicedata["stype"] == core.SENSOR_TYPE_DUAL:
                self._log.debug("Protocol: "+name+": SENSOR_TYPE_DUAL")
                break

            # case SENSOR_TYPE_TEMP_HUM
            if devicedata["stype"] == core.SENSOR_TYPE_TEMP_HUM :
                self._log.debug("Protocol: "+name+": SENSOR_TYPE_TEMP_HUM")
                # Get plugin values
                try:
                    devicedata['valueV1'] = self._queue.get_nowait()
                    devicedata['valueN1'] = self._queue.get_nowait()
                    devicedata['valueV2'] = self._queue.get_nowait()
                    devicedata['valueN2'] = self._queue.get_nowait()
                except Exception as e:
                    self._log.debug("Protocol: "+self._name+" SENSOR_TYPE_TEMP_HUM Exception: "+repr(e))
                    break
                
                # Assemble mqtt messages
                mqttdata1 = {}
                mqttdata1['topic'] = devicedata['unitname']+"/"+devicedata['devicename']+"/"+devicedata['valueN1']
                mqttdata1['msg'] = str(devicedata["valueV1"])
                message1 = str(devicedata["valueV1"])
                mqttdata2 = {}
                mqttdata2['topic'] = devicedata['unitname']+"/"+devicedata['devicename']+"/"+devicedata['valueN2']
                mqttdata2['msg'] = str(devicedata["valueV2"])
                message1 = str(devicedata["valueV2"])
                break

            # case SENSOR_TYPE_TEMP_BARO
            if devicedata["stype"] == core.SENSOR_TYPE_TEMP_BARO:
                self._log.debug("Protocol: "+name+": SENSOR_TYPE_TEMP_BARO")
                break

            # case SENSOR_TYPE_TEMP_HUM_BARO
            if devicedata["stype"] == core.SENSOR_TYPE_TEMP_HUM_BARO:
                #self._log.debug("Protocol: "+name+": SENSOR_TYPE_TEMP_HUM_BARO")
                # Get plugin values
                try:
                    devicedata['valueV1'] = self._queue.get_nowait()
                    devicedata['valueN1'] = self._queue.get_nowait()
                    devicedata['valueV2'] = self._queue.get_nowait()
                    devicedata['valueN2'] = self._queue.get_nowait()
                    devicedata['valueV3'] = self._queue.get_nowait()
                    devicedata['valueN3'] = self._queue.get_nowait()
                except Exception as e:
                    self._log.debug("Protocol: "+self._name+" SENSOR_TYPE_TEMP_HUM_BARO Exception: "+repr(e))
                    break
                # Assemble mqtt topics for valueV1, V2, V3
                mqttdata1 = {}
                mqttdata1['topic'] = devicedata['unitname']+"/"+devicedata['devicename']+"/"+devicedata['valueN1']
                mqttdata1['msg'] = str(devicedata["valueV1"])
                message1 = str(devicedata["valueV1"])
                mqttdata2 = {}
                mqttdata2['topic'] = devicedata['unitname']+"/"+devicedata['devicename']+"/"+devicedata['valueN2']
                mqttdata2['msg'] = str(devicedata["valueV2"])
                message2 = str(devicedata["valueV2"])
                mqttdata3 = {}
                mqttdata3['topic'] = devicedata['unitname']+"/"+devicedata['devicename']+"/"+devicedata['valueN3']
                mqttdata3['msg'] = str(devicedata["valueV3"])
                message3 = str(devicedata["valueV3"])
                break

            # case SENSOR_TYPE_SWITCH
            if devicedata["stype"] == core.SENSOR_TYPE_SWITCH:
                self._log.debug("Protocol: "+name+": SENSOR_TYPE_SWITCH")
                # Get plugin values
                try:
                    devicedata['valueV1'] = self._queue.get_nowait()
                    devicedata['valueN1'] = self._queue.get_nowait()
                except Exception as e:
                    self._log.debug("Protocol: "+self._name+" SENSOR_TYPE_SWITCH Exception: "+repr(e))
                    break
                # Switches can have many values, OpenHAB (usually) only two: 1 (=on) or 0 (=off)
                switch_on  = ['closed','press','double','long', 'on']
                switch_off = ['open','release', 'off']    
                
                if devicedata["valueV1"] in switch_on: devicedata["valueV1"] = 1
                elif devicedata["valueV1"] in switch_off: devicedata["valueV1"] = 0
                else: break

                # Assemble mqtt message
                mqttdata1 = {}
                mqttdata1['topic'] = devicedata['unitname']+"/"+devicedata['devicename']+"/"+devicedata['valueN1']
                mqttdata1['msg'] = str(devicedata["valueV1"])
                message1 = str(devicedata["valueV1"])
                break

            # case SENSOR_TYPE_DIMMER
            if devicedata["stype"] == core.SENSOR_TYPE_DIMMER:
                self._log.debug("Protocol: "+name+": SENSOR_TYPE_DIMMER")
                break

            # case SENSOR_TYPE_WIND
            if devicedata["stype"] == core.SENSOR_TYPE_WIND:
                self._log.debug("Protocol: "+name+": SENSOR_TYPE_WIND")
                break

            # else UNKNOWN
            self._log.debug("Protocol "+name+": Unknown sensor type!")
            break

        # Now publish the data to the MQTT broker/server
            
        # test for a user entry in webform protocol 'Publish' field; use it if it exists
        if self._pubstr != '': # entry exists in Publish field
            self._queue_out1 = self._pubstr
            self._queue_out2 = self._pubstr
            self._queue_out3 = self._pubstr
        else: # use "standard" format (unitname/devicename/valuename)...
            self._log.debug('Protocol: '+name+': "standard" topic format')
            self._queue_out1 = str(mqttdata1['topic'])
            if devicedata.get('valueN2') != None:
                self._queue_out2 = devicedata['unitname']+"/"+devicedata['devicename']+"/"+devicedata['valueN2']
            if devicedata.get('valueN3') != None:
                self._queue_out3 = devicedata['unitname']+"/"+devicedata['devicename']+"/"+devicedata['valueN3']
        
        # Whichever the sensor type, check if we have mqtt data to send, and if so publish it
        
        # publish datavalue1...
        if message1 != None:
            self._log.debug("Protocol: "+name+" Publish: Topic: "+self._queue_out1+", Message: "+message1 )
            self._mq.publish(self._queue_out1, message1 )
            
        # publish datavalue2 (if it exists)
        if devicedata.get('valueN2') != None:
            if message2 != None: 
                self._log.debug("Protocol: "+name+" Publish: Topic: "+self._queue_out2+", Message: "+message2 )
                self._mq.publish(self._queue_out2, message2 )

        # publish datavalue3 (if it exists)
        if devicedata.get('valueN3') != None:
            if mqttdata3['msg'] != None: 
                self._log.debug("Protocol: "+name+" Publish: Topic: "+self._queue_out3+", Message: "+message3 )
                self._mq.publish(self._queue_out3, message3 )
        
        # we may eventually need more, for example for Dummy device (4 values)...
        # End of send #

    def process(self):
        # processing todo for protocol (main loop of protocol)
        self._log.debug("Protocol: "+name+" Processing...")
        devicedata = {}
        try:
            while True:
                message1 = self._queue.get_nowait() # keep reading from the protocol queue
                if message1 == core.QUEUE_MESSAGE_START: # found "start" message
                    break  # ready to read devicedata values
            devicedata['stype'] = self._queue.get_nowait() # get sensor type
            devicedata['serverid'] = self._queue.get_nowait() # get server id
            #print("OHmqtt l 266: devicedata = ", devicedata)
            self.send(devicedata) # go and get other datavalues as needed, and publish them to MQTT ...
        except Exception as e:
            self._log.debug("Protocol: "+name+" process Exception: "+repr(e))

        # release lock, ready for next processing
        self._lock.clear()
