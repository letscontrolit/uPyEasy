#          
# Filename: utils.py
# Author  : Lisa Esselink
# Purpose : uPyEasy util functions
# Usage   : Provide functions for the app
#
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

        #connect to database
        _dbc.connect()

        #Get network record key
        network = db.networkTable.getrow()

        # update network
        cid = db.networkTable.update({"timestamp":network['timestamp']},spi=spi_nr,pin_cs=cs, pin_rst=rst,ip=ip,gateway=gtw,subnet=mask,dns=dns)

        _dbc.close()

    def setwifi(self,ssid, key, ssid2, key2, wport):
        #self._log.debug("setwifi: "+ssid+"/"+key+"/"+ssid2+"/"+key2)
        #connect to database
        _dbc.connect()

        network = db.networkTable.getrow()

        # update network
        db.networkTable.update({"timestamp":network['timestamp']},ssid=ssid,key=key,fbssid=ssid2,fbkey=key2)
 
        #Get config record key
        config = db.configTable.getrow()
        db.configTable.update({"timestamp":network['timestamp']},port = wport)
        
        _dbc.close()
        
    def get_unit_nr(self):
        self._log.debug("Utils: Unit Number")
        #connect to database
        _dbc.connect()
        
        try:
            config = db.configTable.getrow()
        except OSError:
            pass
        
        _dbc.close()
        
        return config['unit']

    def get_upyeasy_name(self):
        self._log.debug("Utils: uPyEasy Name")
        #connect to database
        _dbc.connect()
        
        #init ONLY!
        try:
            #self._log.debug("Init Config Table")
            db.configTable.create_table()
        except OSError:
            pass

        config = db.configTable.getrow()

        _dbc.close()

        return config['name']
        
    def get_syslog_hostname(self):
        self._log.debug("Utils: Sys hostname")
        #connect to database
        _dbc.connect()
        
        #init ONLY!
        try:
            #self._log.debug("Init advanced Table")
            db.advancedTable.create_table()
        except OSError:
            pass

        advanced = db.advancedTable.getrow()

        _dbc.close()

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
     
        return platform
        
    def get_form_values(self,form):
        if form:
            # Get all form keys & values and put them in a cleaned dictionary
            form_values = [(v[0]) for k,v in form.items()]
            uform = dict(zip(form.keys(), form_values))
        else: 
            self._log.debug("Utils: No webform");
            uform = None
            
        return uform

    def map_form2db(self,dbtable, uform):
        # get db dict and form dict and map them so that db keys have right value from form
        #print(type(dbtable))
        #print(uform)
        #print(dbtable)

        if not dbtable or not uform:
           self._log.debug("Utils: map_form2db not all input available");
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
        #connect to database
        _dbc.connect()
        
        config = db.configTable.getrow()

        _dbc.close()
        return config["version"]
 
    def get_dxlabels(self):
        #connect to database
        _dbc.connect()
        
        # get dx map
        dxmap = db.dxmapTable.getrow()
        
        dx_label = {}
        # get dx labels
        for cnt in range(0,dxmap["count"]):
            dx_label['d'+str(cnt)] = dxmap['d'+str(cnt)].split(';')[1]
        # add count!
        dx_label["count"] = dxmap["count"]
        
        _dbc.close()
        return dx_label

    def pin_assignment(self, name, pin, count, dxpin):
        #connect to database
        _dbc.connect()

        # erase old assignment
        for cnt in range(0,count):
            if dxpin['d'+str(cnt)] == name:
                print(cnt)
                print (name)
                dxpin['d'+str(cnt)] = ''
                break
 
        # set new assignment
        dxpin[pin]=name

        _dbc.close()

    def plugin_senddata(self, queuedata):
        # no queue, no deal
        if not queuedata.scriptqueue: 
            self._log.debug("Utils: Senddata script queue empty!")
            return

        if queuedata.queue:
            # Put start message in protocol queue
            queuedata.queue.put_nowait(core.QUEUE_MESSAGE_START)
            # put sensor type in queue
            queuedata.queue.put_nowait(stype)
            # put HA server id in queue
            queuedata.queue.put_nowait(queuedata.queue_sid)

        # Put start message in script/rule queue
        queuedata.scriptqueue.put_nowait(core.QUEUE_MESSAGE_START)
        # Put device name in queue
        queuedata.scriptqueue.put_nowait(queuedata.devicename)
        # put valuename in queue
        queuedata.scriptqueue.put_nowait(queuedata.valuenames["valueN1"])

        while True:

            # case SENSOR_TYPE_SINGLE
            if queuedata.stype == core.SENSOR_TYPE_SINGLE:
                if queuedata.queue:
                    # put valuename in protocol queue
                    queuedata.queue.put_nowait(queuedata.valuenames["valueD1"])
                # put valuename in script/rule queue
                queuedata.scriptqueue.put_nowait(queuedata.valuenames["valueD1"])
                break

            # case SENSOR_TYPE_LONG
            if queuedata.stype == core.SENSOR_TYPE_LONG:
                break

            # case SENSOR_TYPE_DUAL
            if queuedata.stype == core.SENSOR_TYPE_DUAL:
                break

            # case SENSOR_TYPE_TEMP_HUM
            if queuedata.stype == core.SENSOR_TYPE_TEMP_HUM:
                if queuedata.queue:
                    # put valuenames in protocol queue
                    queuedata.queue.put_nowait(queuedata.valuenames["valueD1"])
                    queuedata.queue.put_nowait(queuedata.valuenames["valueD2"])
                # put valuename in script/rule queue
                queuedata.scriptqueue.put_nowait(queuedata.valuenames["valueD1"])
                # Put start message in script/rule queue
                queuedata.scriptqueue.put_nowait(core.QUEUE_MESSAGE_START)
                # Put device name in queue
                queuedata.scriptqueue.put_nowait(queuedata.devicename)
                # put valuename in queue
                queuedata.scriptqueue.put_nowait(queuedata.valuenames["valueN2"])
                # put valuename in script/rule queue
                queuedata.scriptqueue.put_nowait(queuedata.valuenames["valueD2"])
                break

            # case SENSOR_TYPE_TEMP_BARO
            if queuedata.stype == core.SENSOR_TYPE_TEMP_BARO:
                if queuedata.queue:
                    # put valuename in protocol queue
                    queuedata.queue.put_nowait(queuedata.valuenames["valueD1"])
                    queuedata.queue.put_nowait(queuedata.valuenames["valueD2"])
                # put valuename in script/rule queue
                queuedata.scriptqueue.put_nowait(queuedata.valuenames["valueD1"])
                # Put start message in script/rule queue
                queuedata.scriptqueue.put_nowait(core.QUEUE_MESSAGE_START)
                # Put device name in queue
                queuedata.scriptqueue.put_nowait(queuedata.devicename)
                # put valuename in queue
                queuedata.scriptqueue.put_nowait(queuedata.valuenames["valueN2"])
                # put valuename in script/rule queue
                queuedata.scriptqueue.put_nowait(queuedata.valuenames["valueD2"])
                break

            # case SENSOR_TYPE_TEMP_HUM_BARO
            if queuedata.stype == core.SENSOR_TYPE_TEMP_HUM_BARO:
                if queuedata.queue:
                    # put valuename in protocol queue
                    queuedata.queue.put_nowait(queuedata.valuenames["valueD1"])
                    queuedata.queue.put_nowait(queuedata.valuenames["valueD2"])
                    queuedata.queue.put_nowait(queuedata.valuenames["valueD3"])
                # put valuename in script/rule queue
                queuedata.scriptqueue.put_nowait(queuedata.valuenames["valueD1"])
                # Put start message in script/rule queue
                queuedata.scriptqueue.put_nowait(core.QUEUE_MESSAGE_START)
                # Put device name in queue
                queuedata.scriptqueue.put_nowait(queuedata.devicename)
                # put valuename in queue
                queuedata.scriptqueue.put_nowait(queuedata.valuenames["valueN2"])
                # put valuename in script/rule queue
                queuedata.scriptqueue.put_nowait(queuedata.valuenames["valueD2"])
                # Put start message in script/rule queue
                queuedata.scriptqueue.put_nowait(core.QUEUE_MESSAGE_START)
                # Put device name in queue
                queuedata.scriptqueue.put_nowait(queuedata.devicename)
                # put valuename in queue
                queuedata.scriptqueue.put_nowait(queuedata.valuenames["valueN3"])
                # put valuename in script/rule queue
                queuedata.scriptqueue.put_nowait(queuedata.valuenames["valueD3"])
                break

            # case SENSOR_TYPE_SWITCH
            if queuedata.stype == core.SENSOR_TYPE_SWITCH:
                if queuedata.queue:
                    # put valuename in protocol queue
                    queuedata.queue.put_nowait(queuedata.valuenames["valueD1"])
                # put valuename in script/rule queue
                queuedata.scriptqueue.put_nowait(queuedata.valuenames["valueD1"])
                break

            # case SENSOR_TYPE_DIMMER
            if queuedata.stype == core.SENSOR_TYPE_DIMMER:
                break

            # case SENSOR_TYPE_WIND
            if queuedata.stype == core.SENSOR_TYPE_WIND:
                break

            # else UNKNOWN
            self._log.debug("Utils: Senddata unknown sensor type!")
            break

    def plugin_initdata(self, data, plugin, device, queue, scriptqueue):
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
        data.queue_sid          = device["controllerid"]
        data.devicename         = device["name"]

    def plugin_loadform(self, data, plugindata):
        # generic
        plugindata['pincnt']    = data.pincnt
        plugindata['valuecnt']  = data.valuecnt
        plugindata['content']   = data.content
        # at least one value
        plugindata['valueN1']   = data.valuenames["valueN1"]
        plugindata['valueF1']   = data.valuenames["valueF1"]
        plugindata['valueD1']   = data.valuenames["valueD1"]
        # two values
        if data.valuecnt > 1:
            plugindata['valueN2']   = data.valuenames["valueN2"]
            plugindata['valueF2']   = data.valuenames["valueF2"]
            plugindata['valueD2']   = data.valuenames["valueD2"]
        # three values
        if data.valuecnt > 2:
            plugindata['valueN3']   = data.valuenames["valueN3"]
            plugindata['valueF3']   = data.valuenames["valueF3"]
            plugindata['valueD3']   = data.valuenames["valueD3"]
        
    def plugin_saveform(self, data, plugindata):
        # at least one value
        data.valuenames["valueN1"]  = plugindata['valueN1']
        data.valuenames["valueF1"]  = plugindata['valueF1']
        data.valuenames["valueD1"]  = plugindata['valueD1']
        # two values
        if data.valuecnt > 1:
            data.valuenames["valueN2"]  = plugindata['valueN2']
            data.valuenames["valueF2"]  = plugindata['valueF2']
            data.valuenames["valueD2"]  = plugindata['valueD2']
        # three values
        if data.valuecnt > 2:
            data.valuenames["valueN3"]  = plugindata['valueN3']
            data.valuenames["valueF3"]  = plugindata['valueF3']
            data.valuenames["valueD3"]  = plugindata['valueD3']
    
    
    
