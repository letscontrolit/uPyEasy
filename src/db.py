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
_config = {}

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
    def getrow(cls):
        # if cached: return cached record
        if hasattr(cls,'_config'):  return cls._config
        # no cache: fetch it!
        try:
            cls._config = next(cls.get())
        except StopIteration:
            return None
        return cls._config

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
    def getrow(cls):
        try:
            res = next(cls.get())
        except StopIteration:
            return None
        return res

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
    def public(cls):
        # if cached: return cached table
        if hasattr(cls,'_controller'):  return cls._controller
        # no cache: fetch it!
        try:
            cls._controller = [x for x in cls.get()]
        except StopIteration:
            return None
        return cls._controller

    @classmethod
    def getrow(cls):
        try:
            res = next(cls.get())
        except StopIteration:
            return None           
        return res

    @classmethod
    def delete(cls, timestamp):
        # delete the table record
        try:
            os.remove(cls.fname(timestamp))
            # if cached: delete cached table
            if hasattr(cls,'_controller'):  del cls._controller
        except KeyError:
            return False
        return True

class protocolTable(uorm.Model):

    # Create protocol table
    __db__ = _dbc
    __table__ = "protocol"
    __schema__ = OrderedDict([
        ("timestamp", uorm.now),
        ("id",  1),
        ("name", ""),
        ("protocol", ""),
        ("module", ""),
        ("template", ""),        
    ])

    @classmethod
    def public(cls):
        try:
            res = [x for x in cls.get()]
        except StopIteration:
            return None
        return res

    @classmethod
    def getrow(cls):
        try:
            res = next(cls.get())
        except StopIteration:
            return None
        return res

    @classmethod
    def delete(cls, timestamp):
        # delete the table record
        try:
            os.remove(cls.fname(timestamp))
        except KeyError:
            return False
        return True

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
    def getrow(cls):
        try:
            res = next(cls.get())
        except StopIteration:
            return None
        return res

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
    def getrow(cls):
        try:
            res = next(cls.get())
        except StopIteration:
            return None
        return res

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
    def getrow(cls):
        try:
            res = next(cls.get())
        except StopIteration:
            return None
        return res

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
        ("module",  ""),
        ("template", ""),        
    ])

    @classmethod
    def public(cls):
        try:
            res = [x for x in cls.get()]
        except StopIteration:
            return None
        return res
        
    @classmethod
    def getrow(cls):
        try:
            res = next(cls.get())
        except StopIteration:
            return None
        return res

    @classmethod
    def delete(cls, timestamp):
        # delete the table record
        try:
            os.remove(cls.fname(timestamp))
        except KeyError:
            return False
        return True

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
        ("dxpin", ""),
        ("delay",  60),
        ("sync",  ""),
        ("i2c",  0),
        ("spi",  0),
        ("uart",  0),
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
    def public(cls):
        # if cached: return cached table
        if hasattr(cls,'_device'):  return cls._device
        # no cache: fetch it!
        try:
            cls._device = [x for x in cls.get()]
        except StopIteration:
            return None
        return cls._device

    @classmethod
    def getrow(cls):
        # if cached: return cached record
        if hasattr(cls,'_device'):  return cls._device
        # no cache: fetch it!
        try:
            cls._device = next(cls.get())
        except StopIteration:
            return None
        return cls._device

    @classmethod
    def delete(cls, timestamp):
        # delete the table record
        try:
            os.remove(cls.fname(timestamp))
            # if cached: delete cached table
            if hasattr(cls,'_device'):  del cls._device
        except KeyError:
            return False
        return True

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
    def public(cls):
        try:
            res = [x for x in cls.get()]
        except StopIteration:
            return None
        return res
        
    @classmethod
    def getrow(cls):
        try:
            res = next(cls.get())
        except StopIteration:
            return None
        return res

    @classmethod
    def delete(cls, timestamp):
        # delete the table record
        try:
            os.remove(cls.fname(timestamp))
        except KeyError:
            return False
        return True

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
    def public(cls):
        try:
            res = [x for x in cls.get()]
        except StopIteration:
            return None
        return res
        
    @classmethod
    def getrow(cls):
        try:
            res = next(cls.get())
        except StopIteration:
            return None
        return res

    @classmethod
    def delete(cls, timestamp):
        # delete the table record
        try:
            os.remove(cls.fname(timestamp))
        except KeyError:
            return False
        return True

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
        ("sysloglevel",  5),
        ("serialloglevel",  4),
        ("webloglevel",  5),
        ("webloglines",  25),
        ("enablesdlog", ""),
        ("sdloglevel",  5),
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
    def getrow(cls):
        try:
            res = next(cls.get())
        except StopIteration:
            return None
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
    def public(cls):
        try:
            res = [x for x in cls.get()]
        except StopIteration:
            return None
        return res
        
    @classmethod
    def getrow(cls):
        try:
            res = next(cls.get())
        except StopIteration:
            return None
        return res

    @classmethod
    def delete(cls, timestamp):
        # delete the table record
        try:
            os.remove(cls.fname(timestamp))
        except KeyError:
            return False
        return True

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
    def public(cls):
        # if cached: return cached table
        if hasattr(cls,'_script'):  return cls._script
        # no cache: fetch it!
        try:
            cls._script = [x for x in cls.get()]
        except StopIteration:
            return None
        return cls._script

    @classmethod
    def getrow(cls):
        try:
            res = next(cls.get())
        except StopIteration:
            return None
        return res

    @classmethod
    def delete(cls, timestamp):
        # delete the table record
        try:
            os.remove(cls.fname(timestamp))
            # if cached: delete cached table
            if hasattr(cls,'_script'):  del cls._script
        except KeyError:
            return False
        return True

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
    def public(cls):
        # if cached: return cached table
        if hasattr(cls,'_rule'):  return cls._rule
        # no cache: fetch it!
        try:
            cls._rule = [x for x in cls.get()]
        except StopIteration:
            return None
        return cls._rule

    @classmethod
    def getrow(cls):
        try:
            res = next(cls.get())
        except StopIteration:
            return None
        return res

    @classmethod
    def delete(cls, timestamp):
        # delete the table record
        try:
            os.remove(cls.fname(timestamp))
            # if cached: delete cached table
            if hasattr(cls,'_rule'):  del cls._rule
        except KeyError:
            return False
        return True
                