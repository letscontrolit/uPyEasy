#          
# Filename: init.py
# Version : 0.1
# Author  : Lisa Esselink
# Purpose : Init App to control and read SOC's
# Usage   : Initialize the app
#
# Copyright (c) Lisa Esselink. All rights reserved.  
# Licensend under the Creative Commons Attribution-NonCommercial 4.0 International License.
# See LICENSE file in the project root for full license information.  
#

import uos, gc, ulog
from . import core
from . import db
from .utils import utils
from .db import _dbc
from .hal import hal
from .plugin import plugins
from .protocol import protocol
from .script import scripts

class init (object):
    
    def __init__(self):
        logger              = ulog.get_config()
        logger['name']      = core.initial_upyeasyname
        self._log           = ulog.Log(logger)
        core._log           = self._log

        #Set log levels
        self._log.changelevel('syslog',0)
        self._log.changelevel('console',1, True)
        self._log.changelevel('log',0)
        
        core._log.debug("Init: Init constructor")
        
    def init(self):
        # Init Config
        self._log.debug("Init: Entering init")
        
        # Init utils
        core._utils = utils()
\
        # init hal
        self._hal = hal()
        core._hal = self._hal
        self._log.changehal(self._hal)
        
        # create dir structure
        root_dir = ""
        try:
            self._log.debug("Init: Create directory config")
            uos.mkdir(root_dir+"config")
        except OSError as e:
            self._log.debug("Init: Create directory config exception: "+repr(e))
        # create dir structure
        root_dir = ""
        try:
            self._log.debug("Init: Create directory plugins")
            uos.mkdir(root_dir+"plugins")
        except OSError as e:
            self._log.debug("Init: Create directory plugins exception: "+repr(e))
        try:
            self._log.debug("Init: Create directory protocols")
            uos.mkdir(root_dir+"protocols")
        except OSError as e:
            self._log.debug("Init: Create directory protocols exception: "+repr(e))
        try:
            self._log.debug("Init: Create directory scripts")
            uos.mkdir(root_dir+"scripts")
        except OSError as e:
            self._log.debug("Init: Create directory scripts exception: "+repr(e))
        try:
            self._log.debug("Init: Create directory rules")
            uos.mkdir(root_dir+"rules")
        except OSError as e:
            self._log.debug("Init: Create directory rules exception: "+repr(e))
        
        gc.collect()
        #connect to database
        _dbc.connect()
        
        #init ONLY!
        try:
            self._log.debug("Init: config Table")
            db.configTable.create_table(True)
        except OSError as e:
            self._log.debug("Init: config Table exception: "+repr(e))
        try:
            self._log.debug("Init: network Table")
            db.networkTable.create_table(True)
        except OSError as e:
            self._log.debug("Init: network Table exception: "+repr(e))
        try:
            self._log.debug("Init: protocol Table")
            db.protocolTable.create_table(True)
        except OSError as e:
            self._log.debug("Init: protocol Table exception: "+repr(e))
        try:
            self._log.debug("Init: controller Table")
            db.controllerTable.create_table(True)
        except OSError as e:
            self._log.debug("Init: controller Table exception: "+repr(e))
        try:
            self._log.debug("Init: hardware Table")
            db.hardwareTable.create_table(True)
        except OSError as e:
            self._log.debug("Init: hardware Table exception: "+repr(e))
        try:
            self._log.debug("Init: dxpin Table")
            db.dxpinTable.create_table(True)
        except OSError as e:
            self._log.debug("Init: dxpin Table exception: "+repr(e))
        try:
            self._log.debug("Init: dxmap Table")
            db.dxmapTable.create_table(True)
        except OSError as e:
            self._log.debug("Init: dxmap Table exception: "+repr(e))
        try:
            self._log.debug("Init: plugin Table")
            db.pluginTable.create_table(True)
        except OSError as e:
            self._log.debug("Init: plugin Table exception: "+repr(e))
        try:
            self._log.debug("Init: pluginstore Table")
            db.pluginstoreTable.create_table(True)
        except OSError as e:
            self._log.debug("Init: pluginstore Table exception: "+repr(e))
        try:
            self._log.debug("Init: device Table")
            db.deviceTable.create_table(True)
        except OSError as e:
            self._log.debug("Init: device Table exception: "+repr(e))
        try:
            self._log.debug("Init: service Table")
            db.serviceTable.create_table(True)
        except OSError as e:
            self._log.debug("Init: service Table exception: "+repr(e))
        try:
            self._log.debug("Init: notification Table")
            db.notificationTable.create_table(True)
        except OSError as e:
            self._log.debug("Init: notification Table exception: "+repr(e))
        try:
            self._log.debug("Init: advanced Table")
            db.advancedTable.create_table(True)
        except OSError as e:
            self._log.debug("Init: advanced Table exception: "+repr(e))
        try:
            self._log.debug("Init: script Table")
            db.scriptTable.create_table(True)
        except OSError as e:
            self._log.debug("Init: script Table exception: "+repr(e))
        try:
            self._log.debug("Init: rule Table")
            db.ruleTable.create_table(True)
        except OSError as e:
            self._log.debug("Init: rule Table exception: "+repr(e))

        gc.collect()

        #Config table init
        config = db.configTable.public()
        
        #Test is config table = empty, if so create initial record
        if not config:
            self._log.debug("Init: Create Config Record")
            #create table
            cid = db.configTable.create(name=core.initial_upyeasyname)

        #Network table init
        network = db.networkTable.public()
        #Test is network table = empty, if so create initial record
        if not network:
            self._log.debug("Init: Create Network Record")
            #create table
            cid = db.networkTable.create(ssid="")

        #Hardware table init
        hardware = db.hardwareTable.public()
        #Test is hardware table = empty, if so create initial record
        if not hardware:
            self._log.debug("Init: Create Hardware Record")
            #create platform dependent hardware table
            self._hal.hardwaredb_init()
            
        #dxpin table init
        dxpin = db.dxpinTable.public()
        #Test is dxpin table = empty, if so create initial record
        if not dxpin:
            self._log.debug("Init: Create dxpin Record")
            # create pin record
            db.dxpinTable.create(d0="")
            #create pin mapping
            self._hal.dxpins_init()
            
        #advanced table init
        advanced = db.advancedTable.public()
        #Test is advanced table = empty, if so create initial record
        if not advanced:
            self._log.debug("Init: Create advanced Record")
            #create table
            cid = db.advancedTable.create(mqttretain=0)

        # Init network!
        netconnected = self._hal.init_network()
            
        # return in AP mode!
        #if core.initial_upyeasywifi == "AP" : return netconnected
            
        # Init all protocols
        self._protocols = protocol()
        core._protocols = self._protocols
        self._protocols.init()
           
        # Init all plugins
        self._plugins = plugins()
        core._plugins = self._plugins
        self._plugins.init()
        
        # Init all scripts
        self._scripts = scripts()
        core._scripts = self._scripts
        self._scripts.init()

        #Get advanced record key
        advanced = db.advancedTable.getrow()
       
        #Set right syslog hostname
        if core._utils.get_syslog_hostname():
            self._log.changehost(core.__logname__+"-"+core._utils.get_upyeasy_name(),core._utils.get_syslog_hostname())
        else:
            self._log.changehost(core.__logname__+"-"+core._utils.get_upyeasy_name(),'0.0.0.0')
        
        #Set the right time!
        self._hal.settime()
        
        gc.collect()
       
        return netconnected
