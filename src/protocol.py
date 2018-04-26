#          
# Filename: plugin.py
# Version : 0.1
# Author  : Lisa Esselink
# Purpose : Plugin class
# Usage   : Dynamic gateway to all plugin classes
#
# Copyright (c) 2017 - Lisa Esselink. All rights reserved.  
# Licensend under the Creative Commons Attribution-NonCommercial 4.0 International License.
# See LICENSE file in the project root for full license information.  
#
import gc, sys, os, utime, uasyncio as asyncio
from . import core, db, utils
from .app  import app
from .hal import hal
from .db import _dbc

class protocol(object):

    def __init__(self):
        self._plugins   = core._plugins
        self._nic       = core._nic
        self._log       = core._log
        self._hal       = core._hal
        self._utils     = core._utils

        self._log.debug("Protocols: Load")
        self._protocol = {}
        self._protocol_class = {}
        self._mod = {}
        self._queue = {}
        
    def init(self):
        # Load all protocols
        from . import protocols 

        self._log.debug("Protocols: Init protocol records")
        # delete protocol record if protocol NOT present in frozen firmware!
        tprotocols = db.protocolTable.public()
        cnt = 0
        for protocol in tprotocols:
            # check if present in table
            if (not [modprotocol for modprotocol in protocols.protocols if protocol['name']+";"+protocol['protocol'] in protocols.protocols.values()]) and tprotocols:
                if db.protocolTable.delete(protocol['timestamp']):
                    self._log.debug("Protocols: Record delete succeeded: "+db.protocolTable.fname(protocol['timestamp']))
                else:
                    self._log.debug("Protocols: Record delete failed: "+db.protocolTable.fname(protocol['timestamp']))
            elif not tprotocols: 
                self._log.debug("Protocols: No protocol records found!")
                cnt = 0
            else: 
                self._log.debug("Protocols: Protocol record found: {}".format(protocol['name']))
            if protocol['id'] > cnt: cnt = protocol['id']
        cnt+=1
        
        # get all frozen protocols from __init__.py
        for modname, combi in protocols.protocols.items():
            # split name, protocol
            name, protocol = combi.split(';')
            template = modname+".html"
                
            # check if not present in table
            if not tprotocols or (not [protocol for protocol in tprotocols if name in protocol['name']]):
                #new protocols found: create new protocol table records
                self._log.debug("Protocols: Create missing protocol record: "+modname)
                try:
                    cid = db.protocolTable.create(id=cnt,name=name,protocol=protocol,template=template, module=modname)
                except OSError:
                    self._log.debug("Protocols: Exception creating protocol record:"+modname)
                cnt += 1
            
    def initcontroller(self, controller):
        self._log.debug("Protocols: Init controller "+controller["hostname"]+"-"+controller["protocol"]+"-"+str(controller["id"]))

        _initcomplete = False
        protocols = db.protocolTable.public()
        for protocol in protocols:
            if protocol['name'] == controller['protocol']:
                controllername = controller["hostname"]+"-"+str(controller["id"])
                modname = protocol['module']
                
                # load frozen protocol module
                self._log.debug("Protocols: Load protocol "+modname)
                self._mod[modname] = __import__("upyeasy.protocols."+modname, None, None, 'protocol')
                self._mod[protocol['name']] = self._mod[modname]
                self._protocol_class[protocol['name']] = getattr(self._mod[modname],modname+'_protocol')

                # instantiate plugin
                self._protocol[controllername] = self._protocol_class[controller["protocol"]]()
                    
                # init protocol
                controller['client_id'] = core.__logname__+self._utils.get_upyeasy_name()
                self._queue[controllername] = self._protocol[controllername].init(controller)
                
                _initcomplete = True
                
        if not _initcomplete: 
            self._log.debug("Protocols: Init controller {} failed!".format(controller['protocol']))
        
    def getqueue(self,controller):
        self._log.debug("Protocols: GetQueue controller "+controller["hostname"]+"-"+controller["protocol"]+"-"+str(controller["id"]))

        controllername = controller["hostname"]+"-"+str(controller["id"])
        return self._queue[controllername]
        
    async def asynccontrollers(self):
        # Async coroutine to process all protocol work todo 
        self._log.debug("Protocols: Async processing protocols")
        # Get list of protocols
        protocols = db.protocolTable.public()
        # Run forever
        while True:
            # Get correct controller
            controllers = db.controllerTable.public()
            for controller in controllers:
                # only run active controllers!
                if controller['enable'] == 'on':
                    controllername = controller["hostname"]+"-"+str(controller["id"])
                    for protocol in protocols:
                        if protocol['name'] == controller['protocol']:
                            # init controller?
                            try:
                               _mod = self._mod[protocol['name']]
                            except KeyError:
                                self.initcontroller(controller)
                            # process protocol
                            try:
                                if (not self._queue[controllername].empty()) and (not self._protocol[controllername]._lock.is_set()):
                                    self._protocol[controllername]._lock.set()
                                    protocol_function = getattr(self._protocol[controllername],'process')
                                    if protocol_function: protocol_function()
                            except KeyError:
                                self._log.debug("Protocols: Async processing protocols KeyError exception, controller: "+controllername)
                await asyncio.sleep(0)
            await asyncio.sleep(1)
