#          
# Filename: utils.py
# Author  : Lisa Esselink, with mods for Openhab MQTT by AJ
# Purpose : uPyEasy util functions
# Usage   : Provide functions for the app
# Version : 0.13 (send unitname direct from utils)
# Copyright (c) Lisa Esselink. All rights reserved.  
# Licensend under the Creative Commons Attribution-NonCommercial 4.0 International License.
# See LICENSE file in the project root for full license information.  
#

from . import core, db
from .db import _dbc

class utils(object):

    def __init__(self):
        self._log = core._log
        
    def setnet(self, spi_nr, cs, rst, ip, gtw, mask, dns):
        #self._log.debug("setnet: "+ip+"/"+gtw+"/"+mask+"/"+dns)

        #Get network record key
        network = db.networkTable.getrow()

        # update network
        cid = db.networkTable.update({"timestamp":network['timestamp']},spi=spi_nr,cs=cs, rst=rst,ip=ip,gateway=gtw,subnet=mask,dns=dns)

    def setwifi(self,ssid, key, ssid2, key2, wport):
        #self._log.debug("setwifi: "+ssid+"/"+key+"/"+ssid2+"/"+key2)

        network = db.networkTable.getrow()

        # update network
        db.networkTable.update({"timestamp":network['timestamp']},ssid=ssid,key=key,fbssid=ssid2,fbkey=key2)
 
        #Get config record key
        config = db.configTable.getrow()
        db.configTable.update({"timestamp":config['timestamp']},port = wport)
        
    def get_unit_nr(self):
        self._log.debug("Utils: Unit Number")
        
        try:
            config = db.configTable.getrow()
        except OSError:
            pass
        
        return config['unit']

    def get_upyeasy_name(self):
        self._log.debug("Utils: uPyEasy Name")
        
        config = db.configTable.getrow()

        return config['name']
        
    def get_syslog_hostname(self):
        self._log.debug("Utils: Sys hostname")
        
        #init ONLY!
        try:
            #self._log.debug("Init advanced Table")
            db.advancedTable.create_table()
        except OSError:
            pass

        advanced = db.advancedTable.getrow()

        return advanced['sysloghostname']
        
    def get_uptime(self):	

        diff_time_sec = core._hal.get_time_sec() - core.upyeasy_starttime
        days, rest = divmod(diff_time_sec,86400)    
        hours, rest = divmod(rest,3600)
        minutes, seconds = divmod(rest, 60)
        diff_time = '{} days {} hours {} minutes'.format(round(days),round(hours),round(minutes))
        
        return diff_time

    def get_mem_total(self):
        import gc
        
        mem_total = gc.mem_alloc() + gc.mem_free()
        
        return mem_total	
            
    def get_mem_free(self):
        import gc
        
        gc.collect()
        mem_free = gc.mem_free()
        
        return mem_free	

    def get_mem_current(self):
        import micropython
        
        # these functions are not always available
        if not hasattr(micropython, 'mem_current'):
           mem_current = -1
        else:
           mem_current = micropython.mem_current()
        
        return mem_current	

    def get_mem_peak(self):
        import micropython
        
        # these functions are not always available
        if not hasattr(micropython, 'mem_peak'):
           mem_peak = -1
        else:
           mem_peak = micropython.mem_peak()
        
        return mem_peak	

    def get_mem(self):
        mem = '{}/{}'.format(self.get_mem_free(),self.get_mem_total())
        
        return mem
        
    def get_stack_current(self):
        import micropython

        stack_mem = micropython.stack_use()
        
        return stack_mem	
        
    #def get_stack_total():
    #    import micropython

    #    stack_mem = micropython.mem_info()
    #    stack_mem.split(" out of ")[1].split("\n")[0]
        
    #    return stack_mem	

    #def get_stack_mem():
    #    mem = '{}/{}'.format(get_stack_current(),get_stack_total())

    #    return mem
        
    def get_platform(self):
        import sys

        platform = sys.platform
        if platform[:5] == 'esp32': platform = platform[:5]
     
        return platform
        
    def get_machine_id(self):
        import machine, ubinascii

        if hasattr(machine,'unique_id'): 
            try:
                return str(ubinascii.hexlify(machine.unique_id()), 'utf-8')
            except UnicodeError as e:
                self._log.error("Pages: Entering info Page unicode machine id error: "+repr(e))
                return '-'
        else: return '-'

    def get_form_values(self,form):
        if form:
            # Get all form keys & values and put them in a cleaned dictionary
            form_values = [(v[0]) for k,v in form.items()]
            uform = dict(zip(form.keys(), form_values))
        else: 
            self._log.warning("Utils: No webform");
            uform = None
            
        return uform

    def map_form2db(self,dbtable, uform):
        # get db dict and form dict and map them so that db keys have right value from form
        #print(type(dbtable))
        #print(uform)
        #print(dbtable)

        if not dbtable or not uform:
           self._log.warning("Utils: map_form2db not all input available");
           return None
        
        # compare keys and if they match: copy value over
        for key in dbtable:
            # DB Key in form?
            if key in uform:
                # String or not?
                if type(uform[key]) is str:
                    # Positive Number ?
                    if uform[key].isdigit():
                        dbtable[key] = int(uform[key])
                    elif uform[key].lstrip("-").isdigit():
                        # Negative number
                        dbtable[key] = int(uform[key])
                    elif uform[key].replace('.','',1).isdigit():
                        # Float!
                        dbtable[key] = float(uform[key])
                    else: 
                        # No number or float
                        dbtable[key] = uform[key]
                else: dbtable[key] = uform[key]
        
        #print(dbtable)
        
        return dbtable

    def get_dbversion(self):
        config = db.configTable.getrow()
        return config["version"]
 
    def get_dxlabels(self):
        # get dx map
        dxmap = db.dxmapTable.getrow()
        
        dx_label = {}
        # get dx labels
        for cnt in range(0,dxmap["count"]):
            dx_label['d'+str(cnt)] = dxmap['d'+str(cnt)].split(';')[1]
        # add count!
        dx_label["count"] = dxmap["count"]
        return dx_label

    def pin_assignment(self, name, pin, count, dxpin):

        # erase old assignment
        for cnt in range(0,count):
            if dxpin['d'+str(cnt)] == name:
                #print(cnt)
                #print (name)
                dxpin['d'+str(cnt)] = ''
                break
 
        # set new assignment
        dxpin[pin]=name

    def plugin_senddata(self, queuedata):
        # no queue, no deal
        if not queuedata.valuequeue:  # Value queue
            self._log.warning("Utils: Senddata value queue not existing!")
            return

        # full queue, no deal
        if queuedata.valuequeue.full():  # Value queue
            self._log.warning("Utils: Senddata value queue full!")
            return

        # check if rules/scripts are needed!
        advanced = db.advancedTable.getrow()

        # General section for all sensor types..
        # Read unitname and put into queuedata
        queuedata.valuenames['unitname'] = self.get_upyeasy_name() # AJ added for OHmqtt

        # Value queue...
        # Put start message in value queue
        queuedata.valuequeue.put_nowait(core.QUEUE_MESSAGE_START)
        # Put device/plugin name in value queue
        queuedata.valuequeue.put_nowait(queuedata.devicename)
        # put  first valuename datavalue into value queue
        queuedata.valuequeue.put_nowait(queuedata.valuenames['valueN1'])

        # Protocol queue...
        if queuedata.queue: # Protocol queue for Domoticz, Openhab etc
            # Put start message in protocol queue
            queuedata.queue.put_nowait(core.QUEUE_MESSAGE_START)
            # put sensor type in protocol queue
            queuedata.queue.put_nowait(queuedata.stype)
            # put HA server id in protocol queue
            queuedata.queue.put_nowait(queuedata.queue_sid)
            
            # Additional parameters for use by Openhab MQTT protocol (for all sensor types) (AJ)
            queuedata.queue.put_nowait(queuedata.valuenames['unitname']) # aka upyeasyname
            queuedata.queue.put_nowait(queuedata.valuenames['devicename']) # given name of device/plugin

        if advanced["scripts"] == "on": 
            # Scrip queue...
            # Put start message in script queue
            queuedata.scriptqueue.put_nowait(core.QUEUE_MESSAGE_START)
            # Put device/plugin name in script queue
            queuedata.scriptqueue.put_nowait(queuedata.devicename)
            # put  first valuename datavalue into script queue
            queuedata.scriptqueue.put_nowait(queuedata.valuenames['valueN1'])

        if advanced["rules"] == "on": 
            # Rule queue...
            # Put start message in Rule queue
            queuedata.rulequeue.put_nowait(core.QUEUE_MESSAGE_START)
            # Put device/plugin name in Rule queue
            queuedata.rulequeue.put_nowait(queuedata.devicename)
            # put  first valuename datavalue into Rule queue
            queuedata.rulequeue.put_nowait(queuedata.valuenames['valueN1'])
        
        # Start of code for specific sensor types...
        while True:
            # case SENSOR_TYPE_SINGLE
            if queuedata.stype == core.SENSOR_TYPE_SINGLE:
                # put first data value in value queue (order to match script.py)
                queuedata.valuequeue.put_nowait(queuedata.valuenames["valueV1"]) # (name done in general section)

                if queuedata.queue:
                    # put valuedata and name in protocol queue
                    queuedata.queue.put_nowait(queuedata.valuenames['valueV1'])
                    queuedata.queue.put_nowait(queuedata.valuenames["valueN1"])

                if advanced["scripts"] == "on": 
                    # put first data value in script queue (order to match script.py)
                    queuedata.scriptqueue.put_nowait(queuedata.valuenames["valueV1"]) # (name done in general section)

                if advanced["rules"] == "on": 
                    # put first data value in rule queue (order to match script.py)
                    queuedata.rulequeue.put_nowait(queuedata.valuenames["valueV1"]) # (name done in general section)

                break

            # case SENSOR_TYPE_LONG
            if queuedata.stype == core.SENSOR_TYPE_LONG:
                break

            # case SENSOR_TYPE_DUAL
            if queuedata.stype == core.SENSOR_TYPE_DUAL:
                # put valuenames and valuees in value queue
                queuedata.valuequeue.put_nowait(queuedata.valuenames["valueV1"]) # (name done in general section)
                # start second block of data
                queuedata.valuequeue.put_nowait(core.QUEUE_MESSAGE_START)
                queuedata.valuequeue.put_nowait(queuedata.devicename)
                queuedata.valuequeue.put_nowait(queuedata.valuenames["valueN2"])
                queuedata.valuequeue.put_nowait(queuedata.valuenames["valueV2"])
                
                if queuedata.queue:
                    # put valuedata and names in protocol queue
                    queuedata.queue.put_nowait(queuedata.valuenames["valueV1"])
                    queuedata.queue.put_nowait(queuedata.valuenames["valueN1"])
                    queuedata.queue.put_nowait(queuedata.valuenames["valueV2"])
                    queuedata.queue.put_nowait(queuedata.valuenames["valueN2"])
                
                if advanced["scripts"] == "on": 
                    # put valuenames and valuees in script queue
                    queuedata.scriptqueue.put_nowait(queuedata.valuenames["valueV1"]) # (name done in general section)
                    # start second block of data
                    queuedata.scriptqueue.put_nowait(core.QUEUE_MESSAGE_START)
                    queuedata.scriptqueue.put_nowait(queuedata.devicename)
                    queuedata.scriptqueue.put_nowait(queuedata.valuenames["valueN2"])
                    queuedata.scriptqueue.put_nowait(queuedata.valuenames["valueV2"])
                
                if advanced["rules"] == "on": 
                    # put valuenames and valuees in rule queue
                    queuedata.rulequeue.put_nowait(queuedata.valuenames["valueV1"]) # (name done in general section)
                    # start second block of data
                    queuedata.rulequeue.put_nowait(core.QUEUE_MESSAGE_START)
                    queuedata.rulequeue.put_nowait(queuedata.devicename)
                    queuedata.rulequeue.put_nowait(queuedata.valuenames["valueN2"])
                    queuedata.rulequeue.put_nowait(queuedata.valuenames["valueV2"])
                
                break

            # case SENSOR_TYPE_TRIPLE
            if queuedata.stype == core.SENSOR_TYPE_TRIPLE:
                # put first value in value queue
                queuedata.valuequeue.put_nowait(queuedata.valuenames["valueV1"]) # (name done in general section)
                # second block of data for value queue
                queuedata.valuequeue.put_nowait(core.QUEUE_MESSAGE_START)
                queuedata.valuequeue.put_nowait(queuedata.devicename)
                queuedata.valuequeue.put_nowait(queuedata.valuenames["valueN2"])
                queuedata.valuequeue.put_nowait(queuedata.valuenames["valueV2"])
                # third block of data for value queue
                queuedata.valuequeue.put_nowait(core.QUEUE_MESSAGE_START)
                queuedata.valuequeue.put_nowait(queuedata.devicename)
                queuedata.valuequeue.put_nowait(queuedata.valuenames["valueN3"])
                queuedata.valuequeue.put_nowait(queuedata.valuenames["valueV3"])
                
                if queuedata.queue:
                    # put valuedata and names in protocol queue
                    queuedata.queue.put_nowait(queuedata.valuenames["valueV1"])
                    queuedata.queue.put_nowait(queuedata.valuenames["valueN1"])
                    queuedata.queue.put_nowait(queuedata.valuenames["valueV2"])
                    queuedata.queue.put_nowait(queuedata.valuenames["valueN2"])
                    queuedata.queue.put_nowait(queuedata.valuenames["valueV3"])
                    queuedata.queue.put_nowait(queuedata.valuenames["valueN3"])
                    
                if advanced["scripts"] == "on": 
                    # put first value in script queue
                    queuedata.scriptqueue.put_nowait(queuedata.valuenames["valueV1"]) # (name done in general section)
                    # second block of data for script queue
                    queuedata.scriptqueue.put_nowait(core.QUEUE_MESSAGE_START)
                    queuedata.scriptqueue.put_nowait(queuedata.devicename)
                    queuedata.scriptqueue.put_nowait(queuedata.valuenames["valueN2"])
                    queuedata.scriptqueue.put_nowait(queuedata.valuenames["valueV2"])
                    # third block of data for script queue
                    queuedata.scriptqueue.put_nowait(core.QUEUE_MESSAGE_START)
                    queuedata.scriptqueue.put_nowait(queuedata.devicename)
                    queuedata.scriptqueue.put_nowait(queuedata.valuenames["valueN3"])
                    queuedata.scriptqueue.put_nowait(queuedata.valuenames["valueV3"])
                
                if advanced["rules"] == "on": 
                    # put first value in rule queue
                    queuedata.rulequeue.put_nowait(queuedata.valuenames["valueV1"]) # (name done in general section)
                    # second block of data for rule queue
                    queuedata.rulequeue.put_nowait(core.QUEUE_MESSAGE_START)
                    queuedata.rulequeue.put_nowait(queuedata.devicename)
                    queuedata.rulequeue.put_nowait(queuedata.valuenames["valueN2"])
                    queuedata.rulequeue.put_nowait(queuedata.valuenames["valueV2"])
                    # third block of data for rule queue
                    queuedata.rulequeue.put_nowait(core.QUEUE_MESSAGE_START)
                    queuedata.rulequeue.put_nowait(queuedata.devicename)
                    queuedata.rulequeue.put_nowait(queuedata.valuenames["valueN3"])
                    queuedata.rulequeue.put_nowait(queuedata.valuenames["valueV3"])
                
                break

            # case SENSOR_TYPE_TEMP_HUM
            if queuedata.stype == core.SENSOR_TYPE_TEMP_HUM:
                # put valuenames and valuees in value queue
                queuedata.valuequeue.put_nowait(queuedata.valuenames["valueV1"]) # (name done in general section)
                # start second block of data
                queuedata.valuequeue.put_nowait(core.QUEUE_MESSAGE_START)
                queuedata.valuequeue.put_nowait(queuedata.devicename)
                queuedata.valuequeue.put_nowait(queuedata.valuenames["valueN2"])
                queuedata.valuequeue.put_nowait(queuedata.valuenames["valueV2"])
                
                if queuedata.queue:
                    # put valuedata and names in protocol queue
                    queuedata.queue.put_nowait(queuedata.valuenames["valueV1"])
                    queuedata.queue.put_nowait(queuedata.valuenames["valueN1"])
                    queuedata.queue.put_nowait(queuedata.valuenames["valueV2"])
                    queuedata.queue.put_nowait(queuedata.valuenames["valueN2"])
                
                if advanced["scripts"] == "on": 
                    # put valuenames and valuees in script queue
                    queuedata.scriptqueue.put_nowait(queuedata.valuenames["valueV1"]) # (name done in general section)
                    # start second block of data
                    queuedata.scriptqueue.put_nowait(core.QUEUE_MESSAGE_START)
                    queuedata.scriptqueue.put_nowait(queuedata.devicename)
                    queuedata.scriptqueue.put_nowait(queuedata.valuenames["valueN2"])
                    queuedata.scriptqueue.put_nowait(queuedata.valuenames["valueV2"])
                
                if advanced["rules"] == "on": 
                    # put valuenames and valuees in rule queue
                    queuedata.rulequeue.put_nowait(queuedata.valuenames["valueV1"]) # (name done in general section)
                    # start second block of data
                    queuedata.rulequeue.put_nowait(core.QUEUE_MESSAGE_START)
                    queuedata.rulequeue.put_nowait(queuedata.devicename)
                    queuedata.rulequeue.put_nowait(queuedata.valuenames["valueN2"])
                    queuedata.rulequeue.put_nowait(queuedata.valuenames["valueV2"])
                
                break

            # case SENSOR_TYPE_TEMP_BARO
            if queuedata.stype == core.SENSOR_TYPE_TEMP_BARO:
                # put first value in value queue
                queuedata.valuequeue.put_nowait(queuedata.valuenames["valueV1"]) # (name done in general section)
                # second block of data for value queue
                queuedata.valuequeue.put_nowait(core.QUEUE_MESSAGE_START)
                queuedata.valuequeue.put_nowait(queuedata.devicename)
                queuedata.valuequeue.put_nowait(queuedata.valuenames["valueN2"])
                queuedata.valuequeue.put_nowait(queuedata.valuenames["valueV2"])
                
                if queuedata.queue:
                    # put valuedata and names in protocol queue
                    queuedata.queue.put_nowait(queuedata.valuenames["valueV1"])
                    queuedata.queue.put_nowait(queuedata.valuenames["valueN1"])
                    queuedata.queue.put_nowait(queuedata.valuenames["valueV2"])
                    queuedata.queue.put_nowait(queuedata.valuenames["valueN2"])
               
                if advanced["scripts"] == "on": 
                    # put first value in script queue
                    queuedata.scriptqueue.put_nowait(queuedata.valuenames["valueV1"]) # (name done in general section)
                    # second block of data for script queue
                    queuedata.scriptqueue.put_nowait(core.QUEUE_MESSAGE_START)
                    queuedata.scriptqueue.put_nowait(queuedata.devicename)
                    queuedata.scriptqueue.put_nowait(queuedata.valuenames["valueN2"])
                    queuedata.scriptqueue.put_nowait(queuedata.valuenames["valueV2"])
                
                if advanced["rules"] == "on": 
                    # put first value in rule queue
                    queuedata.rulequeue.put_nowait(queuedata.valuenames["valueV1"]) # (name done in general section)
                    # second block of data for rule queue
                    queuedata.rulequeue.put_nowait(core.QUEUE_MESSAGE_START)
                    queuedata.rulequeue.put_nowait(queuedata.devicename)
                    queuedata.rulequeue.put_nowait(queuedata.valuenames["valueN2"])
                    queuedata.rulequeue.put_nowait(queuedata.valuenames["valueV2"])
                
                break

            # case SENSOR_TYPE_TEMP_HUM_BARO
            if queuedata.stype == core.SENSOR_TYPE_TEMP_HUM_BARO:
                # put first value in value queue
                queuedata.valuequeue.put_nowait(queuedata.valuenames["valueV1"]) # (name done in general section)
                # second block of data for value queue
                queuedata.valuequeue.put_nowait(core.QUEUE_MESSAGE_START)
                queuedata.valuequeue.put_nowait(queuedata.devicename)
                queuedata.valuequeue.put_nowait(queuedata.valuenames["valueN2"])
                queuedata.valuequeue.put_nowait(queuedata.valuenames["valueV2"])
                # third block of data for value queue
                queuedata.valuequeue.put_nowait(core.QUEUE_MESSAGE_START)
                queuedata.valuequeue.put_nowait(queuedata.devicename)
                queuedata.valuequeue.put_nowait(queuedata.valuenames["valueN3"])
                queuedata.valuequeue.put_nowait(queuedata.valuenames["valueV3"])
                
                if queuedata.queue:
                    # put valuedata and names in protocol queue
                    queuedata.queue.put_nowait(queuedata.valuenames["valueV1"])
                    queuedata.queue.put_nowait(queuedata.valuenames["valueN1"])
                    queuedata.queue.put_nowait(queuedata.valuenames["valueV2"])
                    queuedata.queue.put_nowait(queuedata.valuenames["valueN2"])
                    queuedata.queue.put_nowait(queuedata.valuenames["valueV3"])
                    queuedata.queue.put_nowait(queuedata.valuenames["valueN3"])
                    
                if advanced["scripts"] == "on": 
                    # put first value in script queue
                    queuedata.scriptqueue.put_nowait(queuedata.valuenames["valueV1"]) # (name done in general section)
                    # second block of data for script queue
                    queuedata.scriptqueue.put_nowait(core.QUEUE_MESSAGE_START)
                    queuedata.scriptqueue.put_nowait(queuedata.devicename)
                    queuedata.scriptqueue.put_nowait(queuedata.valuenames["valueN2"])
                    queuedata.scriptqueue.put_nowait(queuedata.valuenames["valueV2"])
                    # third block of data for script queue
                    queuedata.scriptqueue.put_nowait(core.QUEUE_MESSAGE_START)
                    queuedata.scriptqueue.put_nowait(queuedata.devicename)
                    queuedata.scriptqueue.put_nowait(queuedata.valuenames["valueN3"])
                    queuedata.scriptqueue.put_nowait(queuedata.valuenames["valueV3"])
                
                if advanced["rules"] == "on": 
                    # put first value in rule queue
                    queuedata.rulequeue.put_nowait(queuedata.valuenames["valueV1"]) # (name done in general section)
                    # second block of data for rule queue
                    queuedata.rulequeue.put_nowait(core.QUEUE_MESSAGE_START)
                    queuedata.rulequeue.put_nowait(queuedata.devicename)
                    queuedata.rulequeue.put_nowait(queuedata.valuenames["valueN2"])
                    queuedata.rulequeue.put_nowait(queuedata.valuenames["valueV2"])
                    # third block of data for rule queue
                    queuedata.rulequeue.put_nowait(core.QUEUE_MESSAGE_START)
                    queuedata.rulequeue.put_nowait(queuedata.devicename)
                    queuedata.rulequeue.put_nowait(queuedata.valuenames["valueN3"])
                    queuedata.rulequeue.put_nowait(queuedata.valuenames["valueV3"])
                
                break

            # case SENSOR_TYPE_SWITCH
            if queuedata.stype == core.SENSOR_TYPE_SWITCH:
                # put valuename and value in value queue
                queuedata.valuequeue.put_nowait(queuedata.valuenames["valueV1"])

                if queuedata.queue:
                    # put valuedata and name in protocol queue
                    queuedata.queue.put_nowait(queuedata.valuenames["valueV1"])
                    queuedata.queue.put_nowait(queuedata.valuenames["valueN1"])

                if advanced["scripts"] == "on": 
                    # put valuename and value in script queue
                    queuedata.scriptqueue.put_nowait(queuedata.valuenames["valueV1"])

                if advanced["rules"] == "on": 
                    # put valuename and value in rule queue
                    queuedata.rulequeue.put_nowait(queuedata.valuenames["valueV1"])

                break

            # case SENSOR_TYPE_DIMMER
            if queuedata.stype == core.SENSOR_TYPE_DIMMER:
                break

            # case SENSOR_TYPE_WIND
            if queuedata.stype == core.SENSOR_TYPE_WIND:
                break

            # else UNKNOWN
            self._log.error("Utils: Senddata unknown sensor type!")
            break

    def plugin_initdata(self, data, plugin, device, queue, scriptqueue, rulequeue, valuequeue):
        data.pullup             = plugin['pullup'] # 0=false, 1=true
        data.inverse            = plugin['inverse']
        data.port               = plugin['port']
        data.formula            = plugin['formula']
        data.senddata           = plugin['senddata']
        data.timer              = plugin['timer']
        data.sync               = plugin['sync']
        data.valuecnt           = plugin['valuecnt']
        data.queue              = queue
        data.scriptqueue        = scriptqueue
        data.rulequeue          = rulequeue
        data.valuequeue         = valuequeue
        data.queue_sid          = device["controllerid"]
        data.devicename         = device["name"] # added AJ for Openhab mqtt
        data.unitname           = utils.get_upyeasy_name(self) # added AJ for Openhab mqtt

    def plugin_loadform(self, data, plugindata):
        # generic
        plugindata['pincnt']    = data.pincnt
        plugindata['valuecnt']  = data.valuecnt
        plugindata['content']   = data.content
        
        # at least one value
        plugindata['valueN1']   = data.valuenames["valueN1"]
        plugindata['valueF1']   = data.valuenames["valueF1"]
        plugindata['valueD1']   = data.valuenames["valueD1"]
        
        # two values or more
        if data.valuecnt > 1:
            plugindata['valueN2']   = data.valuenames["valueN2"]
            plugindata['valueF2']   = data.valuenames["valueF2"]
            plugindata['valueD2']   = data.valuenames["valueD2"]
        # three values or more
        if data.valuecnt > 2:
            plugindata['valueN3']   = data.valuenames["valueN3"]
            plugindata['valueF3']   = data.valuenames["valueF3"]
            plugindata['valueD3']   = data.valuenames["valueD3"]
            
        # we'll need to add more values to cover valuecnt = 4 (for Dummy plugin)
        
        
    def plugin_saveform(self, data, plugindata):
        # at least one value
        data.valuenames["valueN1"]  = plugindata['valueN1']
        data.valuenames["valueF1"]  = plugindata['valueF1']
        data.valuenames["valueD1"]  = plugindata['valueD1']
        
        # two values or more
        if data.valuecnt > 1:
            data.valuenames["valueN2"]  = plugindata['valueN2']
            data.valuenames["valueF2"]  = plugindata['valueF2']
            data.valuenames["valueD2"]  = plugindata['valueD2']
            
        # three values
        if data.valuecnt > 2:
            data.valuenames["valueN3"]  = plugindata['valueN3']
            data.valuenames["valueF3"]  = plugindata['valueF3']
            data.valuenames["valueD3"]  = plugindata['valueD3']
            
        # we'll need to add more values to cover valuecnt = 4 (for Dummy plugin)