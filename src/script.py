#          
# Filename: script.py
# Version : 0.1
# Author  : Lisa Esselink
# Purpose : Script class
# Usage   : Dynamic gateway to all script classes
#
# Copyright (c) 2018 - Lisa Esselink. All rights reserved.  
# Licensed under the Creative Commons Attribution-NonCommercial 4.0 International License.
# See LICENSE file in the project root for full license information.  
#
import gc, re, sys, os, utime, ujson, uasyncio as asyncio
from . import core, db, utils
from .app import app
from .hal import hal
from .scripts import *
from .db import _dbc
from asyn import Event

class scripts(object):

    def __init__(self) :
        self._protocols = core._protocols
        self._nic       = core._nic
        self._log       = core._log
        self._hal       = core._hal
        self._utils     = core._utils
        self._plugins   = core._plugins

        self._log.debug("Scripts: Load")
        self._script = {}
        self._script_class = {}
        self._mod = {}
        self._triggers = {}
        
    def init(self): 
        self._log.debug("Scripts: Init")
        
        # get plugins scriptqueue
        self._scriptqueue = self._plugins.getqueue()
        
        # put system boot message in queue!
        self._scriptqueue.put_nowait(core.QUEUE_MESSAGE_START)
        self._scriptqueue.put_nowait("System")
        self._scriptqueue.put_nowait("Boot")
        self._scriptqueue.put_nowait(True)
        
        # create all script records
        self.loadscripts()
        
        #create all rule records
        self.loadrules()

        self._log.debug("Scripts: Init script/rule records, run async loop")
        # get loop
        loop = asyncio.get_event_loop()
        # Reschedule coroutine every 100ms
        loop.call_later_ms(100, self.asyncscripts())

    def loadscripts(self):
        # get all filenames in scripts dir
        os.chdir('scripts')
        listdir = os.listdir()
        os.chdir('..')

        # delete scripts records
        self._log.debug("Scripts: init scripts records")
        scripts = db.scriptTable.public()
        for script in scripts:
            try:
                os.remove(db.scriptTable.fname(script['timestamp']))
            except KeyError:
                self._log.debug("Scripts: Script record delete failed!")

        cnt = 1
        advanced = db.advancedTable.getrow()
        # auto start or not?
        if advanced['scripts'] == 'on': autoscript = 'on'
        else: autoscript = 'off'
            
        # get all flash scripts
        for module in listdir:
            if module[-3:] != '.py':
                continue
            modname = module[:-3]
            # load script module
            self._log.debug("Scripts: Load script "+modname)
            self._mod[modname] = __import__('scripts/'+modname,globals(), locals(), [modname], 1)
            scriptname = self._mod[modname].name
            self._script_class[scriptname] = self._mod[modname]
            self._log.debug("Scripts: Create script Record: "+modname)

            #create script table record
            try:
                cid = db.scriptTable.create(id=cnt,name=scriptname, filename=module,pluginid=0,enable=autoscript, delay=self._mod[modname].delay)
            except OSError:
                self._log.debug("Scripts: Exception creating script record:"+modname)

            # init script!
            script = {}
            script['id'] = cnt
            script['name'] = scriptname
            script['filename'] = module
            script['pluginid'] = 0
            script['enable'] = "on"
            script['delay'] = self._mod[modname].delay
            self.initscript(script)
            
            # next script, if any
            cnt += 1

        # Clean up!
        gc.collect()
    
    def loadrules(self):
        # get all filenames in rules dir
        os.chdir('rules')
        listdir = os.listdir()
        os.chdir('..')

        # delete rules records
        self._log.debug("Scripts: init rules records")
        rules = db.ruleTable.public()
        for rule in rules:
            try:
                os.remove(db.ruleTable.fname(rule['timestamp']))
            except KeyError:
                self._log.debug("Scripts: Rule record delete failed!")

        cnt = 1
        advanced = db.advancedTable.getrow()
        # auto start or not?
        if advanced['rules'] == 'on': autorule = 'on'
        else: autorule = 'off'

        # get all flash rules
        for module in listdir:
            # get file/rule name
            if module[-5:] != '.rule':
                continue
            rulename = module[:-5]
            
            # load rule file
            self._log.debug("Scripts: Load rule "+rulename)
            rule_file = open("rules/{}".format(module), 'r')
            content = rule_file.read()
            rule_file.close()

            # parse file content and get event
            matchcontent = re.search( r'if (.*):', content)
            if matchcontent:
                # strip any comparison
                matchcomp = re.search( r'(.*)[<>=!]', matchcontent.group(1))
                if matchcomp: match = re.search( r'\'(.*)\'', matchcomp.group(1))
                else: match = re.search( r'\'(.*)\'', matchcontent.group(1))
                if match: 
                    ruleevent = match.group(1)
                    self._log.debug("Scripts: Rule: {}, event: {}".format(rulename,ruleevent))
                else:
                    self._log.debug("Scripts: Rule error, no event match: "+rulename)
                    continue                                
            else:
                self._log.debug("Scripts: Rule error, no event match: "+rulename)
                continue                
            
            # done, save rule
            self._log.debug("Scripts: Create rule Record: "+rulename)

            #create rule table record
            try:
                cid = db.ruleTable.create(id=cnt,name=rulename,event=ruleevent,filename=module,pluginid=0,enable=autorule)
            except OSError:
                self._log.debug("Scripts: Exception creating rule record:"+rulename)
           
            # next rule, if any
            cnt += 1
            
            # Clean up!
            gc.collect()

        # Clean up!
        gc.collect()
        
    def initscript(self, script): 
        self._log.debug("Scripts: Init script: "+script['name'])

        # find scriptname
        scriptname = script['name']
        queue      = None

        # instantiate script
        self._script[scriptname] = self._script_class[scriptname].script()
        self._log.debug("Scripts: Init script,instantiate script: "+scriptname)

        # init script
        script['client_id'] = core.__logname__+self._utils.get_upyeasy_name()
        if scriptname: self._triggers[scriptname] = self._script[scriptname].init(script)
        
        # Clean up!
        gc.collect()

    def timerSet(self, timer, delay):
        # max 10 timers!
        if timer in range(1,10):
            # get loop
            loop = asyncio.get_event_loop()
            
            # Reschedule timerX
            loop.call_later(delay, self.asynctimer(timer))
        else: self._log.debug("Rules: Run rule {}, incorrect timer number: {}".format(self._rulename,timer))

    def gpio(self, gpio, level):
        swpin = self._hal.pin(gpio, core.PIN_IN, core.PIN_PULL_UP)
        swpin(level)
        
    def runrule(self, rule, devicedata): 
        self._log.debug("Rules: Run rule: "+rule['name'])
        self._rulename = rule['name']
        # load rule file
        rule_file = open("rules/{}".format(rule['filename']), 'r')
        content = rule_file.read()
        rule_file.close()
        
        # setup rule environment
        event = {}
        event[devicedata['triggername']] = devicedata['value']

        try:
            exec(content, {}, {'gpio':self.gpio,'timerSet':self.timerSet,'event':event})
        except Exception as e:
            self._log.debug("Rules: Run rule: {}, exception: {}".format(rule['name'],repr(e)))
        
    async def asyncscripts(self):
        # Async coroutine to process all script work todo 
        self._log.debug("Scripts: Async processing scripts/rules")

        # get loop
        loop = asyncio.get_event_loop()

        while True:
            # get scriptqueue message
            devicedata = {}
            try:
                while await(self._scriptqueue.get()) != core.QUEUE_MESSAGE_START:
                    pass
                devicedata['name'] = self._scriptqueue.get_nowait()
                devicedata['valuename'] = self._scriptqueue.get_nowait()
                devicedata['value'] = self._scriptqueue.get_nowait()
            except Exception as e:
                self._log.debug("Protocol "+name+" proces Exception: "+repr(e))

            # Assemble triggername
            devicedata['triggername'] = devicedata['name']+'#'+devicedata['valuename']
            
            ### SCRIPTS
        
            # process all scripts
            scripts=db.scriptTable.public()
                    
            # Get all script values!
            for script in scripts:
                # skip not enabled scripts
                if script['enable'] == 'on' and devicedata['triggername'] in self._triggers[script['name']].values(): 
                    # get scripts
                    if not self._script[script['name']]._lock.locked:
                        self._log.debug("Scripts: Scheduling Async processing script: "+script['name'])
                        script_function = getattr(self._script[script['name']], 'asyncprocess')
                        if script_function: 
                            yield from self._script[script['name']]._lock.acquire()
                            if script['delay'] > 0: loop.call_later(script['delay'],script_function(devicedata))
                            else: loop.call_soon(script_function(devicedata))
                    await asyncio.sleep(0)

            # Give async a change to schedule something else
            await asyncio.sleep_ms(100)

            ### RULES
            
            # process all rules
            rules=db.ruleTable.public()

            # Get all rule values!
            for rule in rules:
                # skip not enabled rules
                if rule['enable'] == 'on' and devicedata['triggername'] == rule['event']: 
                    self._log.debug("Rules: Scheduling Async processing rule: "+rule['name'])
                    # run rule
                    self.runrule(rule, devicedata)
                    
        # Reschedule coroutine every 100ms
        loop.call_later_ms(100, self.asyncscripts())

    async def asynctimer(self, timer):
        # put timer1 message in queue!
        self._scriptqueue.put_nowait(core.QUEUE_MESSAGE_START)
        self._scriptqueue.put_nowait("Rules")
        self._scriptqueue.put_nowait("Timer")
        self._scriptqueue.put_nowait(timer)
                 