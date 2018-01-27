#          
# Filename: test.py
# Version : 0.1
# Author  : Lisa Esselink
# Purpose : Process different Rules
# Usage   : Process different Rules, Event, etc
#
# Copyright (c) 2017 - Lisa Esselink. All rights reserved.  
# Licensend under the Creative Commons Attribution-NonCommercial 4.0 International License.
# See LICENSE file in the project root for full license information.  
#

from upyeasy import core
from asyn import Event
from uasyncio.synchro import Lock
import uasyncio

#
# CUSTOM SCRIPT GLOBALS
#

name                = "Test"
delay               = 0

class script:
    datastore           = None
    
    def __init__(self) :
        self._log       = core._log
        self._log.debug("Script: Test contruction")
        self._lock      = Lock()
        # release lock, ready for next run
        if self._lock.locked: self._lock.release()
        # get loop
        self._loop = uasyncio.get_event_loop()
        
    def init(self, script):        
        self._log.debug("Script: Test init")

        # Register all events you want to act on
        trigger = {}
        trigger['taskname1'] = 'BME280#Temperature'
        trigger['taskname2'] = 'BME280#Humidity'
        trigger['event1']    = 'System#Boot'
        trigger['event2']    = 'TurnOn'
        
        # set timer1 to expire 100 sec later
        self._loop.call_later(100, self.asynctimer1())
        
        return trigger

    async def asyncprocess(self, devicedata):
        # processing todo for script
        self._log.debug("Script: Test process")
        await uasyncio.sleep(10)
        # release lock, ready for next measurement
        self._lock.release()

    async def asynctimer1(self):
        # processing todo for script
        self._log.debug("Script: Test timer")
