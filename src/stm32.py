#          
# Filename: stm32.py
# Version : 0.1
# Author  : Lisa Esselink
# Purpose : STM32 specific functions
# Usage   : STM32 specific functions to store pin and other data
#
# Copyright (c) Lisa Esselink. All rights reserved.  
# Licensend under the Creative Commons Attribution-NonCommercial 4.0 International License.
# See LICENSE file in the project root for full license information.  
#

from . import core
from . import utils
from . import db
from .db import _dbc

class board(object):

    def __init__(self) :
        #class network object, share among all instances!
        self._plugins   = core._plugins
        self._protocols = core._protocols
        self._nic       = core._nic
        self._log       = core._log
        self._hal       = core._hal
        self._utils     = core._utils

    def init_pindb(self, board):
        self._log.debug("STM32: init_pindb")
        #connect to database
        _dbc.connect()

        # create platform disabled pins
        if board == "PYBv3 with STM32F405RG":
            db.dxmapTable.create(count=31,d0="A0;PA0",d1="A1;PA1",d2="A2;PA2",d3="A3;PA3",d4="A4;PA4",d5="A5;PA5",d6="A6;PA6",d7="A7;PA7",d8="A13;PA13",d9="A14;PA14",d10="A15;PA15",d11="B0;PB0",d12="B1;PB1",d13="B3;PB3",d14="B4;PB4",d15="B6;PB6",d16="B7;PB7",d17="B8;PB8",d18="B9;PB9",d19="B10;PB10",d20="B11;PB11",d21="B12;PB12",d22="B13;PB13",d23="B14;PB14",d24="B15;PB15",d25="C0;PC0",d26="C1;PC1",d27="C2;PC2",d28="C3;PC3",d29="C6;PC6",d30="C7;PC7")        
        else:
            self._log.debug("Hal: dxpins_init pyboard failure")
         
        _dbc.close()
