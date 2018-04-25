#          
# Filename: plugin.py
# Version : 0.1
# Author  : Lisa Esselink
# Purpose : Plugin class
# Usage   : Dynamic gateway to all plugin classes
#
# Copyright (c) 2017 - Lisa Esselink. All rights reserved.  
# Licensed under the Creative Commons Attribution-NonCommercial 4.0 International License.
# See LICENSE file in the project root for full license information.  
#
import gc, sys, os, utime, ujson, uasyncio as asyncio, uasyncio.queues as queues
from asyn import Event
from . import core, db, utils
from .app import app
from .hal import hal
from .plugins import *
from .db import _dbc

class plugins(object):

    def __init__(self) :
        self._protocols = core._protocols
        self._nic       = core._nic
        self._log       = core._log
        self._hal       = core._hal
        self._utils     = core._utils

        self._log.debug("Plugins: Load")
        self._plugin = {}
        self._plugin_class = {}
        self._mod = {}
        
    def init(self): 
        # Load all plugins
        import sys
        from . import plugins 

        # script queue
        self._scriptqueue = queues.Queue(maxsize=100)
       
        # delete plugins records
        self._log.debug("Plugins: init plugin records")
        tplugins = db.pluginTable.public()
        for tplugin in tplugins:
            if db.pluginTable.delete(tplugin['timestamp']):
                self._log.debug("DB: Plugin record delete succeeded: "+db.pluginTable.fname(tplugin['timestamp']))
            else:
                self._log.debug("DB: Plugin record delete failed: "+db.pluginTable.fname(tplugin['timestamp']))

        cnt=1
        
        # get all frozen plugins
        for k, v in plugins.plugins.items():
            # load plugin module
            #print(k)
            #print(v)
            modname = k
            self._log.debug("Plugins: Register frozen plugin "+modname)
            self._mod[modname] = __import__("upyeasy.plugins."+modname,globals(), locals(), v)
            plugin = self._mod[modname]
            
            self._log.debug("Plugins: Create frozen plugin Record: "+modname)
            #create table record
            try:
                cid = db.pluginTable.create(id=cnt,name=plugin.name,dtype=plugin.dtype,stype=plugin.stype,valuecnt=plugin.valuecnt,senddata=plugin.senddata,formula=plugin.formula,sync=plugin.sync,timer=plugin.timer,pullup=plugin.pullup,inverse=plugin.inverse,port=plugin.port,template=plugin.template, pincnt=plugin.pincnt)
            except OSError:
                self._log.debug("Plugins: Exception creating frozen plugin record:"+modname)
            cnt += 1

            # unload plugin to save memory
            self._mod[plugin.name] = modname
            del plugin
            del self._mod[modname]
            del sys.modules["upyeasy.plugins."+modname]
                    
    def initdevice(self, device): 
        self._log.debug("Plugins: Init device: "+device['name']+" with plugin: "+str(device['pluginid']))
        from . import plugins 

        # find plugin
        tplugins = db.pluginTable.public()
        pluginname = None
        for plugin in tplugins:
            if plugin['id'] == device['pluginid']:
                pluginname = plugin['name']
                devicename = device['name']
                queue      = None
                
                # Get correct controller
                controllers = db.controllerTable.public()
                for controller in controllers:
                    if controller['id'] == device['controller']:
                       queue = self._protocols.getqueue(controller)
                       break

                # load plugin  
                #print(self._mod)
                #print(pluginname)
                modname = self._mod[pluginname]
                #print(modname)
                mod = __import__("upyeasy.plugins."+modname,globals(), locals(), 'plugin')
                #self._mod[pluginname] = self._mod[modname]
                self._plugin_class[pluginname] = getattr(mod, modname+'_plugin')
                       
                # instantiate plugin
                self._plugin[devicename] = self._plugin_class[pluginname]()
                self._log.debug("Plugins: Init device: "+devicename+" ,instantiate plugin: "+pluginname)

                # init plugin
                plugin['client_id'] = core.__logname__+self._utils.get_upyeasy_name()
                if devicename: 
                    try:
                        if not self._plugin[devicename].init(plugin, device, queue, self._scriptqueue):
                            self._log.debug("Plugins: Init device: "+device['name']+" with plugin: "+str(device['pluginid'])+" failed, disabling!")
                            # device init failed, disable!
                            db.deviceTable.update({"timestamp":device['timestamp']},enable="off")
                    except Exception as e:
                        self._log.debug("Plugins: Init device: "+device['name']+" with plugin: "+str(device['pluginid'])+" failed, exception: "+repr(e))
                            
    def loadform(self, plugindata): 
        self._log.debug("Plugins: Loadform plugin "+plugindata['name'])

        try:
            self._plugin[plugindata['name']].loadform(plugindata)
        except KeyError:
            self._log.debug("Plugins: Loadform plugin KeyError Exception: "+plugindata['name'])
        
    def saveform(self, plugindata): 
        self._log.debug("Plugins: Saveform plugin "+plugindata['name'])
        self._plugin[plugindata['name']].saveform(plugindata)

    def loadvalues(self, device, valuenames): 
        self._log.debug("Plugins: Loadvalues plugin")

        # load values
        devices=db.deviceTable.public()
        # Get right device!
        for devicedb in devices:
            if devicedb['name'] == device['name']:
                valuenames["valueN1"],valuenames["valueN2"],valuenames["valueN3"]=devicedb['valuename']
                valuenames["valueF1"],valuenames["valueF2"],valuenames["valueF3"]=devicedb['valueformula']
                valuenames["valueD1"],valuenames["valueD2"],valuenames["valueD3"]=devicedb['valuedecimal']

    def savevalues(self, device, valuenames): 
        self._log.debug("Plugins: Savevalues plugin")

        # process values
        devices=db.deviceTable.public()
        # Get right device!
        for devicedb in devices:
            if devicedb['name'] == device['name']:
                namelist = valuenames["valueN1"]+';'+valuenames["valueN2"]+';'+valuenames["valueN3"]
                formulalist = valuenames["valueF1"]+';'+valuenames["valueF2"]+';'+valuenames["valueF3"]
                decimallist = valuenames["valueD1"]+';'+valuenames["valueD2"]+';'+valuenames["valueD3"]
                db.deviceTable.update({"timestamp":devicedb['timestamp']},valuename=namelist, valueformula=formulalist , valuedecimal=decimallist)
                return

    def read(self, device, values): 
        self._log.debug("Plugins: Read device "+device['name'])
        self._plugin[device['name']].read(values)

    def write(self, device, values): 
        self._log.debug("Plugins: Write device "+device['name'])
        self._plugin[device['name']].write(values)

    def triggers(self, device, triggers):
        self._log.debug("Plugins: Triggers device "+device['name'])
        # process triggers
        devices=db.deviceTable.public()
        # Get right device!
        for devicedb in devices:
            if devicedb['name'] == device['name']:
                db.deviceTable.update({"timestamp":devicedb['timestamp']},valuesubscription=triggers)
                return
        
    def readstore(self, pname):
        self._log.debug("Plugins: Read device store: "+pname)
        datastores = db.pluginstoreTable.public()
        data = None
        # read plugin data
        for datastore in datastores:
            if datastore['name'] == pname:
                data = ujson.loads(datastore['data'])
                break
            
        return data

    def writestore(self, pname, pdata):
        self._log.debug("Plugins: Write device store: "+pname)
        data = ujson.dumps(pdata)
        # if exists: get timestamp
        datastores = db.pluginstoreTable.public()
        for datastore in datastores:
            if datastore['name'] == pname:
                db.pluginstoreTable.update({"timestamp":datastore['timestamp']},name=pname,data=data)
                return

        # create/update datastore entry
        db.pluginstoreTable.create(name=pname,data=data)
 
    def getqueue(self):
        self._log.debug("Plugins: GetQueue")

        return self._scriptqueue

    async def asyncdevices(self):
        # Async coroutine to process all plugin work todo 
        self._log.debug("Plugins: Async processing plugins")

        # get loop
        loop = asyncio.get_event_loop()
        
        # Get all (frozen) plugins
        plugins = db.pluginTable.public()

        while True:
            # process all devices
            devices=db.deviceTable.public()
                    
            # Get all plugin values!
            for device in devices:
                # skip not enabled devices
                if device['enable'] == 'on': 
                    pluginname = None
                    # get plugin data from plugin
                    for plugin in plugins:
                        # get devices
                        if plugin['id'] == device['pluginid']:
                            # process plugin
                            #self._plugin[plugin['name']].process()
                            if not self._plugin[device['name']]._lock.is_set():
                                self._log.debug("Plugins: Scheduling Async processing plugin: "+plugin['name'])
                                plugin_function = getattr(self._plugin[device['name']], 'asyncprocess')
                                if plugin_function: 
                                    if device['delay'] > 0: loop.call_later(device['delay'],plugin_function())
                                    else: loop.call_soon(plugin_function())
                                self._plugin[device['name']]._lock.set()
                        await asyncio.sleep(0)
            #self._hal.idle()  # Yield to underlying RTOS
            await asyncio.sleep_ms(10)
