#          
# Filename: db.py
# Version : 0.1
# Author  : Lisa Esselink
# Purpose : DB access functions
# Usage   : Database functions to store and retrieve data
#
# Copyright (c) Lisa Esselink. All rights reserved.  
# Licensend under the Creative Commons Attribution-NonCommercial 4.0 International License.
# See LICENSE file in the project root for full license information.  
#

import filedb as uorm, os, sys
from ucollections import OrderedDict
from . import core

_dbc = uorm.DB(core.working_dir+"config")

class configTable(uorm.Model):

    # Create config table
    __db__ = _dbc
    __table__ = "config"
    __schema__ = OrderedDict([
        ("timestamp", uorm.now),
        ("name", "uPyEasy"),
        ("unit",  0),
        ("port",  80),
        ("ssl",  "off"),
        ("password", ""),
        ("sleepenable", ""),
        ("sleeptime",  60),
        ("sleepfailure", ""),
        ("version", int(core.__build__)),
    ])

    @classmethod
    def mapkeys(cls, obj):
        return [obj.get(k) for k in cls.__schema__.keys()]

    @classmethod
    def public(cls):
        res = [x for x in cls.get()]
        return res

    @classmethod
    def getrow(cls):
        res = next(cls.get())
        return res

    @classmethod
    def list(cls):
        res = [x for x in cls.scan()]
        return res.values

class networkTable(uorm.Model):

    # Create network table
    __db__ = _dbc
    __table__ = "network"
    __schema__ = OrderedDict([
        ("timestamp", uorm.now),
        ("spi", 0),
        ("cs", ""),
        ("rst", ""),
        ("ssid", ""),
        ("key", ""),
        ("fbssid", ""),
        ("fbkey", ""),
        ("ip", ""),
        ("gateway", ""),
        ("subnet", ""),
        ("dns", ""),
        ("mode", "STA"),
    ])

    @classmethod
    def mapkeys(cls, obj):
        return [obj.get(k) for k in cls.__schema__.keys()]

    @classmethod
    def public(cls):
        res = [x for x in cls.get()]
        return res

    @classmethod
    def getrow(cls):
        res = next(cls.get())
        return res

    @classmethod
    def list(cls):
        res = [x for x in cls.scan()]
        return res.values

class controllerTable(uorm.Model):

    # Create controller table
    __db__ = _dbc
    __table__ = "controller"
    __schema__ = OrderedDict([
        ("timestamp", uorm.now),
        ("id",  1),
        ("usedns", ""),
        ("hostname", ""),
        ("port",  1883),
        ("user", ""),
        ("password", ""),
        ("subscribe", ""),
        ("publish", ""),
        ("enable",  ""),
        ("protocol", ""),        
    ])

    @classmethod
    def mapkeys(cls, obj):
        return [obj.get(k) for k in cls.__schema__.keys()]

    @classmethod
    def public(cls):
        res = [x for x in cls.get()]
        return res

    @classmethod
    def getrow(cls):
        res = next(cls.get())
        return res

    @classmethod
    def list(cls):
        res = [x for x in cls.scan()]
        return res.values

class protocolTable(uorm.Model):

    # Create protocol table
    __db__ = _dbc
    __table__ = "protocol"
    __schema__ = OrderedDict([
        ("timestamp", uorm.now),
        ("id",  1),
        ("name", ""),
        ("protocol", ""),
        ("template", ""),        
    ])

    @classmethod
    def mapkeys(cls, obj):
        return [obj.get(k) for k in cls.__schema__.keys()]

    @classmethod
    def public(cls):
        res = [x for x in cls.get()]
        return res

    @classmethod
    def getrow(cls):
        res = next(cls.get())
        return res

    @classmethod
    def list(cls):
        res = [x for x in cls.scan()]
        return res.values

class hardwareTable(uorm.Model):

    # Create hardware table
    __db__ = _dbc
    __table__ = "hardware"
    __schema__ = OrderedDict([
        ("timestamp", uorm.now),
        ("boardled", ""),
        ("boardled1", ""),
        ("boardled2", ""),
        ("boardled3", ""),
        ("boardled4", ""),
        ("boardled5", ""),
        ("boardled6", ""),
        ("switch1", ""),
        ("switch2", ""),       
        ("inverseled", ""),
        ("i2c", 0),
        ("spi", 0),
        ("uart", 0),
        ("i2s", 0),
        ("can", 0),
        ("sda", ""),
        ("scl", ""),
        ("mosi", ""),
        ("miso", ""),
        ("sck", ""),
        ("nss", ""),
        ("tx", ""),
        ("rx", ""),
        ("cts", ""),
        ("rts", ""),
        ("c-tx", ""),
        ("c-rx", ""),
        ("d0", 0),
        ("d1", 0),
        ("d2", 0),
        ("d3", 0),
        ("d4", 0),
        ("d5", 0),
        ("d6", 0),
        ("d7", 0),
        ("d8", 0),
        ("d9", 0),
        ("d10", 0),
        ("d11", 0),
        ("d12", 0),
        ("d13", 0),
        ("d14", 0),
        ("d15", 0),
        ("d16", 0),
        ("d17", 0),
        ("d18", 0),
        ("d19", 0),
        ("d20", 0),
        ("d21", 0),
        ("d22", 0),
        ("d23", 0),
        ("d24", 0),
        ("d25", 0),
        ("d26", 0),
        ("d27", 0),
        ("d28", 0),
        ("d29", 0),
        ("d30", 0),
        ("d31", 0),
        ("d32", 0),
        ("d33", 0),
        ("d34", 0),
        ("d35", 0),
        ("d36", 0),
        ("d37", 0),
        ("d38", 0),
        ("d39", 0),
        ("d40", 0),
    ])

    @classmethod
    def mapkeys(cls, obj):
        return [obj.get(k) for k in cls.__schema__.keys()]

    @classmethod
    def public(cls):
        res = [x for x in cls.get()]
        return res

    @classmethod
    def getrow(cls):
        res = next(cls.get())
        return res

    @classmethod
    def list(cls):
        res = [x for x in cls.scan()]
        return res.values

class dxpinTable(uorm.Model):

    # Create dxpin table
    __db__ = _dbc
    __table__ = "dxpin"
    __schema__ = OrderedDict([
        ("timestamp", uorm.now),
        ("d0", ""),
        ("d1", ""),
        ("d2", ""),
        ("d3", ""),
        ("d4", ""),
        ("d5", ""),
        ("d6", ""),
        ("d7", ""),
        ("d8", ""),
        ("d9", ""),
        ("d10", ""),
        ("d11", ""),
        ("d12", ""),
        ("d13", ""),
        ("d14", ""),
        ("d15", ""),
        ("d16", ""),
        ("d17", ""),
        ("d18", ""),
        ("d19", ""),
        ("d20", ""),
        ("d21", ""),
        ("d22", ""),
        ("d23", ""),
        ("d24", ""),
        ("d25", ""),
        ("d26", ""),
        ("d27", ""),
        ("d28", ""),
        ("d29", ""),
        ("d30", ""),
        ("d31", ""),
        ("d32", ""),
        ("d33", ""),
        ("d34", ""),
        ("d35", ""),
        ("d36", ""),
        ("d37", ""),
        ("d38", ""),
        ("d39", ""),
        ("d40", ""),
    ])

    @classmethod
    def mapkeys(cls, obj):
        return [obj.get(k) for k in cls.__schema__.keys()]

    @classmethod
    def public(cls):
        res = [x for x in cls.get()]
        return res

    @classmethod
    def getrow(cls):
        res = next(cls.get())
        return res

    @classmethod
    def list(cls):
        res = [x for x in cls.scan()]
        return res.values

class dxmapTable(uorm.Model):

    # Create dxpin table
    __db__ = _dbc
    __table__ = "dxmap"
    __schema__ = OrderedDict([
        ("timestamp", uorm.now),
        ("count", 0),
        ("d0", ""),
        ("d1", ""),
        ("d2", ""),
        ("d3", ""),
        ("d4", ""),
        ("d5", ""),
        ("d6", ""),
        ("d7", ""),
        ("d8", ""),
        ("d9", ""),
        ("d10", ""),
        ("d11", ""),
        ("d12", ""),
        ("d13", ""),
        ("d14", ""),
        ("d15", ""),
        ("d16", ""),
        ("d17", ""),
        ("d18", ""),
        ("d19", ""),
        ("d20", ""),
        ("d21", ""),
        ("d22", ""),
        ("d23", ""),
        ("d24", ""),
        ("d25", ""),
        ("d26", ""),
        ("d27", ""),
        ("d28", ""),
        ("d29", ""),
        ("d30", ""),
        ("d31", ""),
        ("d32", ""),
        ("d33", ""),
        ("d34", ""),
        ("d35", ""),
        ("d36", ""),
        ("d37", ""),
        ("d38", ""),
        ("d39", ""),
        ("d40", ""),
    ])

    @classmethod
    def mapkeys(cls, obj):
        return [obj.get(k) for k in cls.__schema__.keys()]

    @classmethod
    def public(cls):
        res = [x for x in cls.get()]
        return res

    @classmethod
    def getrow(cls):
        res = next(cls.get())
        return res

    @classmethod
    def list(cls):
        res = [x for x in cls.scan()]
        return res.values
        
class pluginTable(uorm.Model):

    # Create plugin table
    __db__ = _dbc
    __table__ = "plugin"
    __schema__ = OrderedDict([
        ("timestamp", uorm.now),
        ("id",  1),
        ("name", ""),
        ("dtype", ""),
        ("stype", ""),
        ("pincnt",  1),
        ("valuecnt",  1),
        ("senddata", ""),
        ("formula",  ""),
        ("sync",  ""),
        ("timer",  ""),
        ("pullup",  ""),
        ("inverse",  ""),
        ("port",  ""),
        ("template", ""),        
    ])

    @classmethod
    def mapkeys(cls, obj):
        return [obj.get(k) for k in cls.__schema__.keys()]

    @classmethod
    def public(cls):
        res = [x for x in cls.get()]
        return res
        
    @classmethod
    def getrow(cls):
        res = next(cls.get())
        return res

    @classmethod
    def list(cls):
        res = [x for x in cls.scan()]
        return res.values

class deviceTable(uorm.Model):

    # Create devices table
    __db__ = _dbc
    __table__ = "device"
    __schema__ = OrderedDict([
        ("timestamp", uorm.now),
        ("id",  1),
        ("enable", ""),
        ("pluginid",  0),
        ("name", ""),
        ("controller",  0),
        ("controllerid",  0),
        ("dxpin", "d0"),
        ("delay",  60),
        ("sync",  ""),
        ("i2c",  ""),
        ("bootstate", ""),
        ("pullup", ""),
        ("inverse", ""),
        ("port", ""),
        ("valuename", ""),
        ("valueformula", ""),
        ("valuedecimal", ""),
        ("valuesubscription", ""),
    ])

    @classmethod
    def mapkeys(cls, obj):
        return [obj.get(k) for k in cls.__schema__.keys()]

    @classmethod
    def public(cls):
        res = [x for x in cls.get()]
        return res

    @classmethod
    def getrow(cls):
        res = next(cls.get())
        return res

    @classmethod
    def list(cls):
        res = [x for x in cls.scan()]
        return res.values

class notificationTable(uorm.Model):

    # Create notification table
    __db__ = _dbc
    __table__ = "notification"
    __schema__ = OrderedDict([
        ("timestamp", uorm.now),
        ("id",  1),
        ("serviceid",  1),
        ("enable", ""),
    ])

    @classmethod
    def mapkeys(cls, obj):
        return [obj.get(k) for k in cls.__schema__.keys()]

    @classmethod
    def public(cls):
        res = [x for x in cls.get()]
        return res
        
    @classmethod
    def getrow(cls):
        res = next(cls.get())
        return res

    @classmethod
    def list(cls):
        res = [x for x in cls.scan()]
        return res

class serviceTable(uorm.Model):

    # Create service table
    __db__ = _dbc
    __table__ = "service"
    __schema__ = OrderedDict([
        ("timestamp", uorm.now),
        ("id",  1),
        ("name", ""),
        ("server", ""),
        ("port", ""),
        ("template", ""),        
    ])

    @classmethod
    def mapkeys(cls, obj):
        return [obj.get(k) for k in cls.__schema__.keys()]

    @classmethod
    def public(cls):
        res = [x for x in cls.get()]
        return res
        
    @classmethod
    def getrow(cls):
        res = next(cls.get())
        return res

    @classmethod
    def list(cls):
        res = [x for x in cls.scan()]
        return res

class advancedTable(uorm.Model):

    # Create advanced table
    __db__ = _dbc
    __table__ = "advanced"
    __schema__ = OrderedDict([
        ("timestamp", uorm.now),
        ("scripts", "off"),
        ("rules", "off"),
        ("notifications", "off"),
        ("mqttretain", ""),
        ("messagedelay",  0),
        ("ntphostname", "pool.ntp.org"),
        ("ntptimezone",  60),
        ("ntpdst", ""),
        ("sysloghostname", ""),
        ("sysloglevel",  0),
        ("serialloglevel",  1),
        ("webloglevel",  0),
        ("webloglines",  10),
        ("enablesdlog", ""),
        ("sdloglevel",  0),
        ("enableserial", ""),
        ("serialbaudrate",  115200),
        ("enablesync", ""),
        ("syncport",  8888),
        ("fixedipoctet",  0),
        ("wdi2caddress",  0),
        ("usessdp", ""),
        ("connectfailure",  0),
        ("i2cstretchlimit",  0),
    ])

    @classmethod
    def mapkeys(cls, obj):
        return [obj.get(k) for k in cls.__schema__.keys()]

    @classmethod
    def public(cls):
        res = [x for x in cls.get()]
        return res
        
    @classmethod
    def getrow(cls):
        res = next(cls.get())
        return res

    @classmethod
    def list(cls):
        res = [x for x in cls.scan()]
        return res

class pluginstoreTable(uorm.Model):

    # Create plugin table
    __db__ = _dbc
    __table__ = "pluginstore"
    __schema__ = OrderedDict([
        ("timestamp", uorm.now),
        ("name", ""),
        ("data", ""),        
    ])

    @classmethod
    def mapkeys(cls, obj):
        return [obj.get(k) for k in cls.__schema__.keys()]

    @classmethod
    def public(cls):
        res = [x for x in cls.get()]
        return res
        
    @classmethod
    def getrow(cls):
        res = next(cls.get())
        return res

    @classmethod
    def list(cls):
        res = [x for x in cls.scan()]
        return res.values

class scriptTable(uorm.Model):

    # Create script table
    __db__ = _dbc
    __table__ = "script"
    __schema__ = OrderedDict([
        ("timestamp", uorm.now),
        ("id",  1),
        ("enable", "off"),
        ("pluginid",  0),
        ("name", ""),
        ("filename", ""),
        ("delay",  60),
    ])

    @classmethod
    def mapkeys(cls, obj):
        return [obj.get(k) for k in cls.__schema__.keys()]

    @classmethod
    def public(cls):
        res = [x for x in cls.get()]
        return res

    @classmethod
    def getrow(cls):
        res = next(cls.get())
        return res

    @classmethod
    def list(cls):
        res = [x for x in cls.scan()]
        return res.values

class ruleTable(uorm.Model):

    # Create script table
    __db__ = _dbc
    __table__ = "rule"
    __schema__ = OrderedDict([
        ("timestamp", uorm.now),
        ("id",  1),
        ("enable", "off"),
        ("name", ""),
        ("filename", ""),
        ("delay",  60),
    ])

    @classmethod
    def mapkeys(cls, obj):
        return [obj.get(k) for k in cls.__schema__.keys()]

    @classmethod
    def public(cls):
        res = [x for x in cls.get()]
        return res

    @classmethod
    def getrow(cls):
        res = next(cls.get())
        return res

    @classmethod
    def list(cls):
        res = [x for x in cls.scan()]
        return res.values
                