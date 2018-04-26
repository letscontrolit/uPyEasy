##          
# Filename: __init__.py
# Version : 0.1
# Author  : Lisa Esselink
# Purpose : App to control and read SOC's
# Usage   : Runs the app
#
# Copyright (c) Lisa Esselink. All rights reserved.  
# Licensend under the Creative Commons Attribution-NonCommercial 4.0 International License.
# See LICENSE file in the project root for full license information.  
#

plugins             = {}
plugins["bme280"]   = "BME280;0"
plugins["ds18"]     = "DS18B20;1"
plugins["switch"]   = "SSD1306;0"
plugins["test"]     = "Test;1"
