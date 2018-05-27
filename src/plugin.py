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
        from . import plugins 

        self._log.debug("Plugins: Init plugin records")
        # script queue
        self._scriptqueue = queues.Queue(maxsize=100)
        # rules queue
        self._rulequeue = queues.Queue(maxsize=100)
        # script queue
        self._valuequeue = queues.Queue(maxsize=100)
       
        # delete plugin record if plugin NOT present in frozen firmware!
        tplugins = db.pluginTable.public()
        cnt = 0
        for plugin in tplugins:
            # check if present in table
            if (not [modplugin for modplugin in plugins.plugins if plugin['name']+";{}".format(plugin['pincnt']) in plugins.plugins.values()]) and tplugins:
                if db.pluginTable.delete(plugin['timestamp']):
                    self._log.debug("Plugins: Record delete succeeded: "+db.pluginTable.fname(plugin['timestamp']))
                else:
                    self._log.error("Plugins: Record delete failed: "+db.pluginTable.fname(plugin['timestamp']))
            elif not tplugins: 
                self._log.warning("Plugins: No plugin records found!")
                cnt = 0
            else: 
                self._log.debug("Plugins: Plugin record found: {}".format(plugin['name']))
            if plugin['id'] > cnt: cnt = plugin['id']
        cnt+=1
        
        # get all frozen Plugins from __init__.py
        for modname, combi in plugins.plugins.items():
            # split name, pincnt
            name, pincnt = combi.split(';')
            template = modname+".html"
                
            # check if not present in table
            if not tplugins or (not [plugin for plugin in tplugins if name in plugin['name']]):
                #new Plugins found: create new plugin table record
                self._log.debug("Plugins: Create missing plugin record: "+modname)
                try:
                    cid = db.pluginTable.create(id=cnt,name=name,template=template, module=modname, pincnt=int(pincnt))
                except OSError:
                    self._log.error("Plugins: Exception creating plugin record:"+modname)
                cnt += 1
                                
    def initdevice(self, device): 
        self._log.debug("Plugins: Init device: "+device['name']+" with plugin: "+str(device['pluginid']))
        from . import plugins 

        _initcomplete = False
        # find plugin
        tplugins = db.pluginTable.public()
        pluginname = None
        for plugin in tplugins:
            if plugin['id'] == device['pluginid']:
                pluginname = plugin['name']
                devicename = device['name']
                queue      = None
                
                # only get controller in non-AP mode!
                if core.initial_upyeasywifi != core.NET_STA_AP:
                    # Get correct controller
                    controllers = db.controllerTable.public()
                    for controller in controllers:
                        if controller['id'] == device['controller']:
                           queue = self._protocols.getqueue(controller)
                           break

                # load plugin  
                modname = plugin['module']
                self._mod[pluginname] = __import__("upyeasy.plugins."+modname,globals(), locals(), 'plugin')
                self._plugin_class[pluginname] = getattr(self._mod[pluginname], modname+'_plugin')

                # update plugin?
                if plugin["dtype"] == "":
                    modplugin = self._mod[pluginname]
                    try:
                       self._log.debug("Plugins: Updating frozen plugin db record:"+pluginname)
                       db.pluginTable.update({"timestamp":plugin['timestamp']},dtype=modplugin.dtype,stype=modplugin.stype,valuecnt=modplugin.valuecnt,senddata=modplugin.senddata,formula=modplugin.formula,sync=modplugin.sync,timer=modplugin.timer,pullup=modplugin.pullup,inverse=modplugin.inverse,port=modplugin.port)
                    except OSError:
                        self._log.error("Plugins: Exception creating frozen plugin db record:"+pluginname)
                
                # instantiate plugin
                self._plugin[devicename] = self._plugin_class[pluginname]()
                self._log.debug("Plugins: Init device: "+devicename+" ,instantiate plugin: "+pluginname)

                # init plugin
                plugin['client_id'] = core.__logname__+self._utils.get_upyeasy_name()
                if devicename: 
                    try:
                        if not self._plugin[devicename].init(plugin, device, queue, self._scriptqueue, self._rulequeue, self._valuequeue):
                            self._log.debug("Plugins: Init device: "+device['name']+" with plugin: "+str(device['pluginid'])+" failed, disabling!")
                            # device init failed, disable!
                            db.deviceTable.update({"timestamp":device['timestamp']},enable="off")
                    except Exception as e:
                        self._log.error("Plugins: Init device: "+device['name']+" with plugin: "+str(device['pluginid'])+" failed, exception: "+repr(e))
                    else: 
                        _initcomplete = True
                
        if not _initcomplete: 
            self._log.debug("Plugins: Init device {} failed!".format(device['name']))
            # device init failed, disable!
            db.deviceTable.update({"timestamp":device['timestamp']},enable="off")
                                     
    def loadform(self, plugindata): 
        self._log.debug("Plugins: Loadform plugin "+plugindata['name'])

        try:
            self._plugin[plugindata['name']].loadform(plugindata)
        except Exception as e:
            self._log.error("Plugins: Loadform plugin Exception: {}".format(repr(e)))
        
    def saveform(self, plugindata): 
        self._log.debug("Plugins: Saveform plugin "+plugindata['name'])
        try:
            self._plugin[plugindata['name']].saveform(plugindata)
        except Exception as e:
            self._log.error("Plugins: Saveform plugin Exception: {}".format(repr(e)))
        
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
        # init done?
        plugins = db.pluginTable.public()
        for plugin in plugins:
            if plugin['id'] == device['pluginid'] and plugin["dtype"] == "":
                self.initdevice(device)
        # read plugin values  
        self._plugin[device['name']].read(values)

    def write(self, device, values): 
        self._log.debug("Plugins: Write device "+device['name'])
        # init done?
        plugins = db.pluginTable.public()
        for plugin in plugins:
            if plugin['id'] == device['pluginid'] and plugin["dtype"] == "":
                self.initdevice(device)
        # write plugin values  
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
 
    def getvaluequeue(self):
        self._log.debug("Plugins: GetValueQueue")

        return self._valuequeue

    def getscriptqueue(self):
        self._log.debug("Plugins: GetScriptQueue")

        return self._scriptqueue

    def getrulequeue(self):
        self._log.debug("Plugins: GetRuleQueue")

        return self._rulequeue

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
                            # init plugin?
                            try:
                               _mod = self._mod[plugin['name']]
                            except KeyError:
                                self.initdevice(device)
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
            await asyncio.sleep_ms(10)

    async def asyncvalues(self):
        # Async coroutine to process all script work todo 
        self._log.debug("Plugins: Async processing values")

        # get loop
        loop = asyncio.get_event_loop()

        while True:
            # get scriptqueue message
            devicedata = {}
            try:
                while await(self._valuequeue.get()) != core.QUEUE_MESSAGE_START:
                    # Give async a change to schedule something else
                    await asyncio.sleep_ms(100)
                devicedata['name'] = self._valuequeue.get_nowait()
                devicedata['valuename'] = self._valuequeue.get_nowait()
                devicedata['value'] = self._valuequeue.get_nowait()
            except Exception as e:
                self._log.error("Plugins: valuequeue proces Exception: "+repr(e))

            # Assemble triggername
            devicedata['triggername'] = devicedata['name']+'#'+devicedata['valuename']

            # process all devices
            devices=db.deviceTable.public()
                    
            # Get all device values!
            for device in devices:
                # skip not enabled devices
                if device['enable'] == 'on' and devicedata['triggername'] in device['valuesubscription']: 
                    plugin_function = getattr(self._plugin[device['name']], 'write')
                    if plugin_function: 
                        # Write data to plugin
                        self._plugin[device['name']].write(devicedata)
                await asyncio.sleep(0)
                    
            # Give async a change to schedule something else
            await asyncio.sleep_ms(100)
