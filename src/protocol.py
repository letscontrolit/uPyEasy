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

        # delete Protocols records
        self._log.debug("Protocols: Init protocol records")
        tprotocols = db.protocolTable.public()
        for tprotocol in tprotocols:
            try:
                os.remove(db.protocolTable.fname(tprotocol['timestamp']))
            except KeyError:
                self._log.debug("Protocols: Record delete failed!")

        cnt=1

        # get all frozen protcols
        for k, v in protocols.protocols.items():
            modname = k
            # load protocol module
            self._log.debug("Protocols: Load protocol "+modname)
            self._mod[modname] = __import__("upyeasy.protocols."+modname, None, None, v)
            protocol = self._mod[modname]
            self._mod[protocol.name] = self._mod[modname]
            self._protocol_class[protocol.name] = getattr(self._mod[modname],modname+'_protocol')

            self._log.debug("Protocols: Create protocol Record: "+modname)
            #create table record
            try:
                cid = db.protocolTable.create(id=cnt,name=protocol.name,protocol=protocol.protocol,template=protocol.template)
            except OSError:
                self._log.debug("Protocols: Exception creating protocol record:"+modname)
            cnt += 1

        self._log.debug("Protocols: Init protocol records, run async loop")
        # Reschedule coroutine
        loop = asyncio.get_event_loop()
        loop.call_later(1, self.asynccontrollers())

    def initcontroller(self, controller):
        self._log.debug("Protocols: Init controller "+controller["hostname"]+"-"+controller["protocol"]+"-"+str(controller["id"]))

        controllername = controller["hostname"]+"-"+str(controller["id"])
        # instantiate plugin
        self._protocol[controllername] = self._protocol_class[controller["protocol"]]()
            
        # init protocol
        controller['client_id'] = core.__logname__+self._utils.get_upyeasy_name()
        self._queue[controllername] = self._protocol[controllername].init(controller)
        
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
                           break
                    # process protocol
                    try:
                        if (not self._queue[controllername].empty()) and (not self._protocol[controllername]._lock.is_set()):
                            self._protocol[controllername]._lock.set()
                            protocol_function = getattr(self._protocol[controllername],'process')
                            if protocol_function: protocol_function()
                    except KeyError:
                        self._log.debug("Protocols: Async processing protocols KeyError exception, controller: "+controllername)
                        print(self._queue)
                        print(self._protocol)
                await asyncio.sleep(0)
            #self._hal.idle()  # Yield to underlying RTOS
            await asyncio.sleep(1)

        # Reschedule coroutine
        loop = asyncio.get_event_loop()
        loop.call_later(1, self.asynccontrollers())
