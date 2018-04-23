#          
# Filename: hal.py
#
# Author  : Lisa Esselink
#
# Purpose : HAL (Hardware Abstraction Layer)
#
# Usage   : Run HW specific commands
#
# Copyright (c) Lisa Esselink. All rights reserved.  
# Licensend under the Creative Commons Attribution-NonCommercial 4.0 International License.
# See LICENSE file in the project root for full license information.  
#

import gc
from operator import attrgetter
from . import core
from . import utils
from . import db
from .db import _dbc

class hal(object):

    def __init__(self) :
        #class network object, share among all instances!
        self._plugins   = core._plugins
        self._protocols = core._protocols
        self._nic       = core._nic
        self._log       = core._log
        self._hal       = core._hal
        self._utils     = core._utils

    def init_network(self, mode = "STA"):
        self._log.debug("Hal: Init")
        ip_address_v4 = None
        
        #connect to database
        _dbc.connect()

        #Get network record key
        try:
            network = db.networkTable.getrow()
        except (OSError, StopIteration):
            network = None
            self._log.debug("Hal: Network Table StopIteration")
 
        # check for network record
        if network:
            self._log.debug("Hal: init, network record present")
        else:
            self._log.debug("Hal: init, network record missing")
 
        _dbc.close()

        if self._utils.get_platform() == 'linux':
            self._log.debug("Hal: linux")
            if network: return True
            else: return False
        elif self._utils.get_platform() == 'pyboard': 
            self._log.debug("Hal: pyboard")
            import pyb, network as ethernet
            
            if network:
                board = self.board()
                if network['spi'] == 0:
                    self._log.debug("Hal: pyboard, spi is empty: trying default!")
                    if board == "PYBv3 with STM32F405RG":
                        # connect to default setup
                        core._nic = ethernet.WIZNET5K(pyb.SPI(1), pyb.Pin.board.A3, pyb.Pin.board.A4)
                        # wait to connect
                        import utime
                        cnt = 0
                        while not core._nic.isconnected():
                            if cnt > 10: break
                            cnt += 1
                            utime.sleep(1)
                        if not core._nic.isconnected():
                            self._log.debug("Hal: pyboard, spi is empty: no default setup!")
                            return False
                    else: 
                        self._log.debug("Hal: pyboard, spi is empty: unknown board: "+ board)
                        return False
                if not core._nic:
                    if board == "PYBv3 with STM32F405RG":
                        self._log.debug("Hal: Board: "+ board)
                        core._nic = ethernet.WIZNET5K(pyb.SPI(network['spi']), network['cs'], network['rst'])
                    else: 
                        self._log.debug("Hal: pyboard, unknown board: "+ board)
                        return False
                    while not core._nic.isconnected():
                        pass
                core._nic.active(1)
                self._nic = core._nic
                if network['ip']: 
                    self._nic.ifconfig((network['ip'], network['subnet'], network['gateway'], network['dns']))
                else: 
                    try:
                        self._nic.ifconfig('dhcp')
                    except (OSError, TypeError) as e:
                        self._log.debug("Hal: pyboard network init Error: "+repr(e))
                        return False
                ip_address_v4 = self._nic.ifconfig()[0]
                self._log.debug("Hal: pyboard, ip: "+ip_address_v4)
            else:
                self._log.debug("Hal: pyboard, network record empty")
                return False
        elif self._utils.get_platform() == 'esp32':
            self._log.debug("Hal: esp32")
            if network:
                import network as wifi
                # SSID already set?
                if not network['ssid']:
                    self._log.debug("Hal: esp32, ssid empty")
                    # No ssid set yet, goto AP mode!
                    self._log.debug("Hal: init esp32 network: AP mode")
                    self._nic = wifi.WLAN(wifi.AP_IF)
                    core._nic = self._nic
                    self._nic.active(True)
                    self._nic.config(essid="uPyEasy")
                    ip_address_v4 = self._nic.ifconfig()[0]
                    core.initial_upyeasywifi = "AP"
                else:
                    # STA mode
                    self._log.debug("Hal: init esp32 network: STA mode")
                    self._nic = wifi.WLAN(wifi.STA_IF)
                    core._nic = self._nic
                    self._nic.active(True)
                    #Activate station
                    if not self._nic.isconnected():
                        self._nic.connect(network['ssid'], network['key'])
                        # get start time
                        nicstart = self.get_time_sec()
                        import utime
                        # wait until connected or 30s timeout
                        while not self._nic.isconnected():
                            # wait 1sec
                            utime.sleep(1)
                            # get current sec time
                            nicnow = self.get_time_sec()
                            # timeout reached?
                            if nicnow > nicstart+30:
                                break
                    
                    if self._nic.isconnected():
                        # if ip address set: use it!
                        if network['ip']: 
                            self._nic.ifconfig((network['ip'], network['subnet'], network['gateway'], network['dns']))                    
                        # get ip address
                        ip_address_v4 = self._nic.ifconfig()[0]
                        # network mode STA+AP
                        if network['mode']=='STA+AP':
                            self._log.debug("Hal: init esp32 network: STA+AP mode")
                            self._apnic = wifi.WLAN(wifi.AP_IF)
                            self._apnic.active(True)
                            self._apnic.config(essid="uPyEasy")                    
                            core.initial_upyeasywifi = "STA+AP"
                        else:
                            core.initial_upyeasywifi = "STA"
                    else: 
                        self._log.debug("Hal: esp32, wifi not connected, going to STA+AP mode")
                        # goto STA+AP mode!
                        self._log.debug("Hal: init esp32 network: AP mode")
                        self._nic = wifi.WLAN(wifi.AP_IF)
                        core._nic = self._nic
                        self._nic.active(True)
                        self._nic.config(essid="uPyEasy")
                        ip_address_v4 = self._nic.ifconfig()[0]
                        core.initial_upyeasywifi = "STA+AP"
                
                self._log.debug("Hal: esp32, ip: "+ip_address_v4)
        elif self._utils.get_platform() == 'esp8266':
            if network:
                if not network['ssid']:
                    self._log.debug("Hal: esp8266, ssid empty")
                    return False
            import network as wifi
            
            #Activate station
            self._nic = wifi.WLAN(wifi.STA_IF)
            core._nic = self._nic
            if not self._nic.isconnected():
                self._nic.active(True)
                self._nic.connect(network['ssid'], network['key'])
                while not self._nic.isconnected():
                    pass
            ip_address_v4 = self._nic.ifconfig()[0]
            self._log.debug("Hal: esp8266, ip: "+ip_address_v4)
            
            #deactivate AP
            ap_if = wifi.WLAN(wifi.AP_IF)
            ap_if.active(False)
        else:
            self._log.debug("Hal: failure")
            self._nic = None
            return False
            
        if ip_address_v4: 
            self._log.debug("Hal: nic present")
            return True
        else: 
            self._log.debug("Hal: nic not present")
            return False

    def getntptime(self):
        self._log.debug("Hal: Entering GetNtpTime")

        #connect to database
        _dbc.connect()

        #init ONLY!
        try:
            self._log.debug("Hal: network Table")
            db.advancedTable.create_table()
        except OSError:
            pass

        #Get advanced record key
        advanced = db.advancedTable.getrow()

        _dbc.close()
        host = advanced['ntphostname']
        timezone = advanced['ntptimezone']
        dst = advanced['ntpdst']
        self._log.debug("Hal: Using NTP Hostname: " + host)
        self._log.debug("Hal: TimeZome offset: %d" % timezone)
        rtctime = None
 
        #no ntp hostname, no time
        if not host: return rtctime
 
        if self._utils.get_platform() == 'pyboard': 
            try:
                import usocket as socket
            except:
                import socket
            try:
                import ustruct as struct
            except:
                import struct

            # (date(2000, 1, 1) - date(1900, 1, 1)).days * 24*60*60
            NTP_DELTA = 3155673600
            
            NTP_QUERY = bytearray(48)
            NTP_QUERY[0] = 0x1b

            # collect socket
            gc.collect() 

            try:
                addr = socket.getaddrinfo(host, 123)[0][-1]
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.settimeout(1)
                res = s.sendto(NTP_QUERY, addr)
                msg = s.recv(48)
                s.close()
            except OSError as e:
                self._log.debug("Hal: NTP Time OSError exception: "+repr(e))
                return rtctime
                
            # collect socket
            gc.collect() 
            
            val = struct.unpack("!I", msg[40:44])[0]
            rtctime = val - NTP_DELTA
            self._log.debug("Hal: Received UTC NTP Time: %d" % rtctime)
        elif self._utils.get_platform() == 'esp32':
            try:
                import usocket as socket
            except:
                import socket
            try:
                import ustruct as struct
            except:
                import struct

            # (date(2000, 1, 1) - date(1900, 1, 1)).days * 24*60*60
            NTP_DELTA = 3155673600

            NTP_QUERY = bytearray(48)
            NTP_QUERY[0] = 0x1b
            
            # collect socket
            gc.collect() 

            try:
                addr = socket.getaddrinfo(host, 123)[0][-1]
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.settimeout(1)
                res = s.sendto(NTP_QUERY, addr)
                msg = s.recv(48)
                s.close()
            except (OSError,IndexError) as e:
                self._log.debug("Hal: NTP Time Error exception: "+repr(e))
                return rtctime
            
            # collect socket
            gc.collect() 

            val = struct.unpack("!I", msg[40:44])[0]
            rtctime = val - NTP_DELTA
            self._log.debug("Hal: Received UTC NTP Time: %d" % rtctime)

        elif self._utils.get_platform() == 'esp8266':
            try:
                import usocket as socket
            except:
                import socket
            try:
                import ustruct as struct
            except:
                import struct

            # (date(2000, 1, 1) - date(1900, 1, 1)).days * 24*60*60
            NTP_DELTA = 3155673600

            NTP_QUERY = bytearray(48)
            NTP_QUERY[0] = 0x1b

            # collect socket
            gc.collect() 

            try:
                addr = socket.getaddrinfo(host, 123)[0][-1]
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.settimeout(1)
                res = s.sendto(NTP_QUERY, addr)
                msg = s.recv(48)
                s.close()
            except OSError as e:
                self._log.debug("Hal: NTP Time OSError exception: "+repr(e))
                return rtctime
            
            # collect socket
            gc.collect() 

            val = struct.unpack("!I", msg[40:44])[0]
            rtctime = val - NTP_DELTA
            self._log.debug("Hal: Received UTC NTP Time: %d" % rtctime)

        #Add timezone
        rtctime+=(timezone*60)
        self._log.debug("Hal: Timezone corrected NTP Time: %d" % rtctime)
        #DST
        if dst == 'on': rtctime+=3600
        self._log.debug("Hal: DST corrected NTP Time: %d" % rtctime)

        return rtctime
            
    def settime(self):
        self._log.debug("Hal: Entering SetTime")
        
        if self._utils.get_platform() == 'linux': 
            import utime
            rtctime = utime.time()
            
            #Set start time
            core.upyeasy_starttime = rtctime
            
            return rtctime
        elif core._nic: rtctime = self.getntptime()
        else: return 
        #no ntp hostname, no time
        if rtctime:
            self._log.debug("Hal: Received NTP Time: %d" % rtctime)
        else: 
            self._log.debug("Hal: Received NTP Time: n.a.")
            return rtctime

        #store starttime
        core.upyeasy_starttime = rtctime
        self._log.debug("Hal: StartTime: %d" % core.upyeasy_starttime)

        if self._utils.get_platform() == 'pyboard': 
            import pyb, utime
            #convert unix to soc epoch
            #rtctime-=946684800
            tm = utime.localtime(rtctime)
            tm = tm[0:3] + (0,) + tm[3:6] + (0,)
            pyb.RTC().datetime(tm)
        elif self._utils.get_platform() == 'esp32':
            import machine,utime
            tm = utime.localtime(rtctime)
            tm = tm[0:3] + (0,) + tm[3:6] + (0,)

            # Set RTC time, if present
            if hasattr(machine,'RTC'):
                if hasattr(machine.RTC,'datetime'): machine.RTC().datetime(tm)
            else:
                self._log.debug("Hal: SetTime: NO RTC!")
                
            self._log.debug("Set time: "+"%04u-%02u-%02uT%02u:%02u:%02u" % utime.localtime()[0:6])
        elif self._utils.get_platform() == 'esp8266':
            import machine, utime

            year, month, day, hour, minute, second, millis, _tzinfo = utime.localtime(rtctime)
            self._log.debug("Hal: Set time: %d-%02d-%02d %02d:%02d:%02d.%03d" % (year, month, day, hour, minute, second, millis))
            rtc = machine.RTC()
            rtc.init((year, month, day, hour, minute, second, millis))
        
        return rtctime
        
    def get_time(self):
        import utime,time

        # NO LOGGING, Recursion!
        if self._utils.get_platform() == 'pyboard': 
            year, month, day, hour, minute, second, millis, _tzinfo = utime.localtime()
        elif self._utils.get_platform() == 'esp32':
            import machine
            if hasattr(machine,'RTC'):
                year, month, day, hour, minute, second, millis, _tzinfo = utime.localtime()
            else:
                year, month, day, hour, minute, second, millis, _tzinfo = utime.localtime(utime.mktime(utime.localtime()) + core.upyeasy_starttime)
        elif self._utils.get_platform() == 'esp8266':
             year, month, day, hour, minute, second, millis, _tzinfo = utime.localtime()
        elif self._utils.get_platform() == 'linux':
            year, month, day, hour, minute, second, millis, _tzinfo, dummy = utime.localtime()
        else:
             year, month, day, hour, minute, second, millis, _tzinfo, dummy = utime.localtime()
       
        #local_time = time.strftime("%Y-%m-%e %H:%M:%S", utime.localtime())

        return "%d-%02d-%02d %02d:%02d:%02d" % (year, month, day, hour, minute, second)

    def get_time_sec(self):
        import utime
        
        self._log.debug("Hal: Getting local time in seconds")
        if self._utils.get_platform() == 'pyboard': 
            sectime = utime.mktime(utime.localtime())
        elif self._utils.get_platform() == 'esp32':
            import machine
            if hasattr(machine,'RTC'):
                sectime = utime.mktime(utime.localtime())
            else:
                sectime = utime.mktime(utime.localtime()) + core.upyeasy_starttime
        elif self._utils.get_platform() == 'esp8266':
            sectime = utime.mktime(utime.localtime())
        elif self._utils.get_platform() == 'linux':
            import time
            sectime = time.mktime(utime.localtime())
        else:
            sectime = utime.mktime(utime.localtime())
       
        return sectime

    def get_ip_address(self):
        #get shared nic
        if not hasattr(self, '_nic'):
            self._nic = core._nic
    
        if self._utils.get_platform() == 'linux': 
            import os
            
            ifname = 'eth0'
            ip_address_v4 = os.popen('ip addr show '+ifname).read().split("inet ")[1].split("/")[0]
            ip_address_v6 = os.popen('ip addr show '+ifname).read().split("inet6 ")[1].split("/")[0]
            self._log.debug("Hal: get_ip_address linux, ip: "+ip_address_v4)
        elif self._utils.get_platform() == 'pyboard':
            #get ip address
            try:
                ip_address_v4 = self._nic.ifconfig()[0]
            except AttributeError:
                self._log.debug("Hal: get_ip_address AttributeError")
                #print(self._nic.ifconfig())
                ip_address_v4 = "0.0.0.0"
            self._log.debug("Hal: get_ip_address pyboard, ip: "+ip_address_v4)
        elif self._utils.get_platform() == 'esp32':
            #get ip address
            try:
                ip_address_v4 = self._nic.ifconfig()[0]
            except AttributeError:
                self._log.debug("Hal: get_ip_address AttributeError")
                #print(self._nic.ifconfig())
                ip_address_v4 = "0.0.0.0"
            self._log.debug("Hal: get_ip_address esp32, ip: "+ip_address_v4)
        elif self._utils.get_platform() == 'esp8266':
            #get ip address
            try:
                ip_address_v4 = self._nic.ifconfig()[0]
            except AttributeError:
                self._log.debug("Hal: get_ip_address AttributeError")
                #print(self._nic.ifconfig())
                ip_address_v4 = "0.0.0.0"
            self._log.debug("Hal: get_ip_address esp8266, ip: "+ip_address_v4)
        else:
            self._log.debug("Hal: get_ip_address failure")
            ip_address_v4 = ""
            
        return ip_address_v4

    def get_ip_gw(self):
        #get shared nic
        if not hasattr(self, '_nic'):
            self._nic = core._nic
        
        if self._utils.get_platform() == 'linux': 
            import os

            ip_gw = os.popen('route -n').read().split('0.0.0.0')[1].split()[0]
            self._log.debug("Hal: get_ip_gw linux, ip: "+ip_gw)
        elif self._utils.get_platform() == 'pyboard':
            #get ip address
            try:
                ip_gw = self._nic.ifconfig()[2]
            except AttributeError:
                self._log.debug("Hal: get_ip_gw AttributeError")
                ip_gw = "0.0.0.0"
            self._log.debug("Hal: get_ip_gw pyboard, ip: "+ip_gw)
        elif self._utils.get_platform() == 'esp32':
            #get ip address
            try:
                ip_gw = self._nic.ifconfig()[2]
            except AttributeError:
                self._log.debug("Hal: get_ip_gw AttributeError")
                ip_gw = "0.0.0.0"
            self._log.debug("Hal: get_ip_gw pyboard, ip: "+ip_gw)
        elif self._utils.get_platform() == 'esp8266':
            #get ip address
            try:
                ip_gw = self._nic.ifconfig()[2]
            except AttributeError:
                self._log.debug("Hal: get_ip_gw AttributeError")
                ip_gw = "0.0.0.0"
            self._log.debug("Hal: get_ip_gw pyboard, ip: "+ip_gw)
        else:
            self._log.debug("Hal: get_ip_gw failure")
            ip_gw = "invalid"

        return ip_gw
        
    def get_ip_netmask(self, ifname):
        #get shared nic
        if not hasattr(self, 'nic'):
            self._nic = core._nic
        
        if self._utils.get_platform() == 'linux': 
            import os

            ip_netmask = os.popen('ifconfig '+ifname).read().split("Mask:")[1].split()[0]
            self._log.debug("Hal: get_ip_netmask linux, ip: "+ip_netmask)
        elif self._utils.get_platform() == 'pyboard':
            #get ip address
            try:
                ip_netmask = self._nic.ifconfig()[1]
            except AttributeError:
                self._log.debug("Hal: get_ip_netmask AttributeError")
                #print(self._nic.ifconfig())
                ip_netmask = "0.0.0.0"
            self._log.debug("Hal: get_ip_netmask pyboard, ip: "+ip_netmask)
        elif self._utils.get_platform() == 'esp32':
            #get ip address
            try:
                ip_netmask = self._nic.ifconfig()[1]
            except AttributeError:
                self._log.debug("Hal: get_ip_netmask AttributeError")
                #print(self._nic.ifconfig())
                ip_netmask = "0.0.0.0"
            self._log.debug("Hal: get_ip_netmask pyboard, ip: "+ip_netmask)
        elif self._utils.get_platform() == 'esp8266':
            #get ip address
            try:
                ip_netmask = self._nic.ifconfig()[1]
            except AttributeError:
                self._log.debug("Hal: get_ip_netmask AttributeError")
                #print(self._nic.ifconfig())
                ip_netmask = "0.0.0.0"
            self._log.debug("Hal: get_ip_netmask pyboard, ip: "+ip_netmask)
        else:
            self._log.debug("Hal: get_ip_netmask failure")
            ip_netmask = "invalid"

        return ip_netmask

    def get_ip_dns(self, ifname):
        #get shared nic
        if not hasattr(self, '_nic'):
            self._nic = core._nic
        
        if self._utils.get_platform() == 'linux': 
            import os

            ip_dns = os.popen('nmcli device show '+ifname).read().split("IP4.DNS[1]:")[1].split()[0]
            self._log.debug("Hal: get_ip_dns linux, ip: "+ip_dns)
        elif self._utils.get_platform() == 'pyboard':
            #get ip address
            try:
                ip_dns = self._nic.ifconfig()[3]
            except AttributeError:
                self._log.debug("Hal: get_ip_dns AttributeError")
                #print(self._nic.ifconfig())
                ip_dns = "0.0.0.0"
            self._log.debug("Hal: get_ip_dns pyboard, ip: "+ip_dns)
        elif self._utils.get_platform() == 'esp32':
            #get ip address
            try:
                ip_dns = self._nic.ifconfig()[3]
            except AttributeError:
                self._log.debug("Hal: get_ip_dns AttributeError")
                #print(self._nic.ifconfig())
                ip_dns = "0.0.0.0"
            self._log.debug("Hal: get_ip_dns pyboard, ip: "+ip_dns)
        elif self._utils.get_platform() == 'esp8266':
            #get ip address
            try:
                ip_dns = self._nic.ifconfig()[3]
            except AttributeError:
                self._log.debug("Hal: get_ip_dns AttributeError")
                #print(self._nic.ifconfig())
                ip_dns = "0.0.0.0"
            self._log.debug("Hal: get_ip_dns pyboard, ip: "+ip_dns)
        else:
            self._log.debug("Hal: get_ip_dns failure")
            ip_dns = "invalid"

        return ip_dns

    def idle(self):
        if self._utils.get_platform() == 'linux': 
            pass
        elif self._utils.get_platform() == 'pyboard':
            pass
        elif self._utils.get_platform() == 'esp32':
            from utime import sleep_ms
            sleep_ms(20)
            #machine.idle()  # Yield to underlying RTOS
        elif self._utils.get_platform() == 'esp8266':
            import machine
            machine.idle()  # Yield to underlying RTOS
        else:
            pass

    def reboot(self):
        self._log.debug("Hal: reboot")
        if self._utils.get_platform() == 'linux': 
            import sys
            #reboot!
            sys.exit()
        elif self._utils.get_platform() == 'pyboard':
            pass
        elif self._utils.get_platform() == 'esp32':
            import machine
            machine.reset()
        elif self._utils.get_platform() == 'esp8266':
            import machine
            machine.reset()
        else:
            pass

    async def reboot_async(self):
        self._log.debug("Hal: Async reboot")
        if self._utils.get_platform() == 'linux': 
            import sys
            #reboot!
            sys.exit()
        elif self._utils.get_platform() == 'pyboard':
            pass
        elif self._utils.get_platform() == 'esp32':
            import machine
            machine.reset()
        elif self._utils.get_platform() == 'esp8266':
            import machine
            machine.reset()
        else:
            pass

    def wifiscan(self):
        self._log.debug("Hal: wifiscan")
        
        wifi_ap = []
        
        if self._utils.get_platform() == 'linux':
            self._log.debug("Hal: wifiscan linux")
        elif self._utils.get_platform() == 'pyboard': 
            self._log.debug("Hal: wifiscan pyboard")
        elif self._utils.get_platform() == 'esp32':
            self._log.debug("Hal: wifiscan esp32")
            # Get list of ssid's
            wifilist = self._nic.scan()
            # parse list, exchange encryption
            wifiaplist = []
            wifisec = ['Open','WEP','WPA-PSK','WPA2-PSK','WPA/WPA2-PSK']
            wifihide = ['Visible','Hidden']
            for wifi in wifilist:
                self._log.debug("Hal: esp32, Scan: Ssid found: "+str(wifi[0], 'utf8')+" Channel: "+str(wifi[2])+" Strength: "+str(wifi[3]) + ' dBm' + " Security: " + str(wifi[4])+ " Hidden: " + str(wifi[5]))
                info = {
                    "ssid":    str(wifi[0], 'utf8'),
                    "channel":    str(wifi[2]),
                    "strength":    str(wifi[3]),
                    "security":    wifisec[wifi[4]],
                    "hidden":    wifihide[wifi[5]],
                }
                wifiaplist.append(info)
            wifi_ap = sorted(wifiaplist, key=lambda k: (k['ssid'],k['strength'])) 
        elif self._utils.get_platform() == 'esp8266':
            self._log.debug("Hal: wifiscan esp8266")
            # Get list of ssid's
            wifilist = self._nic.scan()
            # parse list, exchange encryption
            wifiaplist = []
            wifisec = ['Open','WEP','WPA-PSK','WPA2-PSK','WPA/WPA2-PSK']
            wifihide = ['Visible','Hidden']
            for wifi in wifilist:
                self._log.debug("Hal: esp32, Scan: Ssid found: "+str(wifi[0], 'utf8')+" Channel: "+str(wifi[2])+" Strength: "+str(wifi[3]) + ' dBm' + " Security: " + str(wifi[4])+ " Hidden: " + str(wifi[5]))
                info = {
                    "ssid":    str(wifi[0], 'utf8'),
                    "channel":    str(wifi[2]),
                    "strength":    str(wifi[3]),
                    "security":    wifisec[wifi[4]],
                    "hidden":    wifihide[wifi[5]],
                }
                wifiaplist.append(info)
            wifi_ap = sorted(wifiaplist, key=lambda k: k['ssid']) 
        else:
            self._log.debug("Hal: wifiscan failure")
        
        return wifi_ap
 
    def hardwaredb_init(self):
        self._log.debug("Hal: hardwaredb init")
        
        #connect to database
        _dbc.connect()

        if self._utils.get_platform() == 'linux':
            self._log.debug("Hal: hardwaredb linux")
            # create hardwareTable
            db.hardwareTable.create(boardled1="")
        elif self._utils.get_platform() == 'pyboard': 
            self._log.debug("Hal: hardwaredb pyboard")
            # create hardwareTable
            board = self.board()
            if board == "PYBv3 with STM32F405RG":
                db.hardwareTable.create(boardled1="LED_G1",boardled2="LED_G2",boardled3="LED_R1",boardled4="LED_R2",switch1="SW")     
            else:
                self._log.debug("Hal: hardwaredb pyboard failure")
        elif self._utils.get_platform() == 'esp32':
            self._log.debug("Hal: hardwaredb esp32")
            # create hardwareTable
            db.hardwareTable.create(boardled1="")
        elif self._utils.get_platform() == 'esp8266':
            self._log.debug("Hal: hardwaredb esp82662")
            # create hardwareTable
            db.hardwareTable.create(boardled1="")
        else:
            self._log.debug("Hal: hardwaredb failure")
        
        _dbc.close()
        
 
    def pin(self, vpin, mode = None, pull = None):
        self._log.debug("Hal: pin = "+vpin)
        
        from machine import Pin
        
        pin = None

        # check if id is present
        if not vpin: 
            self._log.debug("Hal: vpin = None!")
            return pin
        
        # get dx map
        dxmap = db.dxmapTable.getrow()

        # received virtual pin, transforming to actual pin
        id = dxmap[vpin].split(';')[0]        
        
        if self._utils.get_platform() == 'linux':
            self._log.debug("Hal: pin linux: "+id)

            # Pin mode and pull are platform dependant
            pin_type = [None, None, Pin.IN, Pin.OUT, None, None, None]
            if mode: platform_mode = pin_type[mode]
            else: platform_mode = None
            if pull: platform_pull = pin_type[pull]
            else: platform_pull = None

            if platform_mode and platform_pull: pin = Pin(int(id), platform_mode, platform_pull)
            elif platform_mode: pin = Pin(int(id), platform_mode)
            else: pin = Pin(int(id))
        elif self._utils.get_platform() == 'pyboard': 
            self._log.debug("Hal: pin pyboard: "+id)

            # Pin mode and pull are platform dependant
            pin_type = [Pin.PULL_UP, Pin.PULL_DOWN, Pin.IN, Pin.OUT, Pin.OPEN_DRAIN, Pin.ALT, Pin.ALT_OPEN_DRAIN]
            if mode: platform_mode = pin_type[mode]
            else: platform_mode = None
            if pull: platform_pull = pin_type[pull]
            else: platform_pull = None

            if platform_mode and platform_pull: pin = Pin(id, platform_mode, platform_pull)
            elif platform_mode: pin = Pin(id, platform_mode)
            else: pin = Pin(id)
        elif self._utils.get_platform() == 'esp32':
            self._log.debug("Hal: pin esp32: "+id)

            # Pin mode and pull are platform dependant
            pin_type = [Pin.PULL_UP, Pin.PULL_DOWN, Pin.IN, Pin.OUT, Pin.OPEN_DRAIN, None, None]
            if mode: platform_mode = pin_type[mode]
            else: platform_mode = None
            if pull: platform_pull = pin_type[pull]
            else: platform_pull = None

            if platform_mode and platform_pull: pin = Pin(int(id), platform_mode, platform_pull)
            elif platform_mode: pin = Pin(int(id), platform_mode)
            else: pin = Pin(int(id))
        elif self._utils.get_platform() == 'esp8266':
            self._log.debug("Hal: pin esp8266: "+id)

            # Pin mode and pull are platform dependant
            pin_type = [Pin.PULL_UP, Pin.PULL_DOWN, Pin.IN, Pin.OUT, Pin.OPEN_DRAIN, None, None]
            if mode: platform_mode = pin_type[mode]
            else: platform_mode = None
            if pull: platform_pull = pin_type[pull]
            else: platform_pull = None

            if platform_mode and platform_pull: pin = Pin(int(id), platform_mode, platform_pull)
            elif platform_mode: pin = Pin(int(id), platform_mode)
            else: pin = Pin(int(id))
        else:
            self._log.debug("Hal: pin failure")

        return pin
        
    def dxpins_init(self):
        self._log.debug("Hal: dxpins_init")
        
        #connect to database
        _dbc.connect()

        if self._utils.get_platform() == 'linux':
            self._log.debug("Hal: dxpins_init linux")
            # Create pin mapping
            db.dxmapTable.create(count=20,d0="0;PA0",d1="1;PA1",d2="2;PA2",d3="3;PA3",d4="4;PA4",d5="5;PA5",d6="6;PA6",d7="7;PA7",d8="8;PA8",d9="9;PA9",d10="10;PA10",d11="11;PA11",d12="12;PA12",d13="13;PA13",d14="14;PA14",d15="15;PA15",d16="16;PA16",d17="17;PA17",d18="18;PA18",d19="19;PA19")        
        elif self._utils.get_platform() == 'pyboard': 
            self._log.debug("Hal: dxpins_init pyboard")
            # create platform disabled pins
            hwboard = self.board()
            from .stm32 import board
            stm32_pin = board()
            stm32_pin.init_pindb(hwboard)
        elif self._utils.get_platform() == 'esp32':
            self._log.debug("Hal: dxpins_init esp32")
            # create platform disabled pins
            db.dxmapTable.create(count=34,d0="0;GPIO0",d1="1;GPIO1",d2="2;GPIO2",d3="3;GPIO3",d4="4;GPIO4",d5="5;GPIO5",d6="6;GPIO6",d7="7;GPIO7",d8="8;GPIO8",d9="9;GPIO9",d10="10;GPIO10",d11="11;GPIO11",d12="12;GPIO12",d13="13;GPIO13",d14="14;GPIO14",d15="15;GPIO15",d16="16;GPIO16",d17="17;GPIO17",d18="18;GPIO18",d19="19;GPIO19",d20="21;GPIO21",d21="22;GPIO22",d22="23;GPIO23",d23="25;GPIO25",d24="26;GPIO26",d25="27;GPIO27",d26="32;GPIO32",d27="33;GPIO33",d28="34;GPIO34",d29="35;GPIO35",d30="36;GPIO35",d31="37;GPIO37",d32="38;GPIO38",d33="39;GPIO39")        
        elif self._utils.get_platform() == 'esp8266':
            self._log.debug("Hal: dxpins_init esp82662")
            # create platform disabled pins
            db.dxmapTable.create(count=12,d0="0;GPIO0",d1="1;GPIO1",d2="2;GPIO2",d3="3;GPIO3",d4="4;GPIO4",d5="5;GPIO5",d6="9;GPIO9",d7="10;GPIO10",d8="12;GPIO12",d9="13;GPIO13",d10="14;GPIO14",d11="15;GPIO15")        
        else:
            self._log.debug("Hal: dxpins_init failure")
        
        _dbc.close()

    def board(self):
        self._log.debug("Hal: board info")
        
        board = ""
        if self._utils.get_platform() == 'linux':
            self._log.debug("Hal: board linux")
            board = "Unknown"
        elif self._utils.get_platform() == 'pyboard': 
            self._log.debug("Hal: board pyboard")
            import os
            # get board version
            uname = os.uname()
            board = uname.machine
        elif self._utils.get_platform() == 'esp32':
            self._log.debug("Hal: board esp32")
            import os
            # get board version
            uname = os.uname()
            board = uname.machine
        elif self._utils.get_platform() == 'esp8266':
            self._log.debug("Hal: board esp8266")
            import os
            # get board version
            uname = os.uname()
            board = uname.machine
        else:
            self._log.debug("Hal: board failure")

        return board
        
    def python(self):
        self._log.debug("Hal: python info")
        
        python = ""
        if self._utils.get_platform() == 'linux':
            self._log.debug("Hal: python linux")
            import sys
            version = sys.implementation
            python = version.name +" "+str(version.version)
        elif self._utils.get_platform() == 'pyboard': 
            self._log.debug("Hal: python pyboard")
            import os
            # get python version
            uname = os.uname()
            python = uname.version
        elif self._utils.get_platform() == 'esp32':
            self._log.debug("Hal: python esp32")
            import os
            # get python version
            uname = os.uname()
            python = uname.version
        elif self._utils.get_platform() == 'esp8266':
            self._log.debug("Hal: python esp8266")
            import os
            # get python version
            uname = os.uname()
            python = uname.version
        else:
            self._log.debug("Hal: python failure")

        return python
        
    def get_i2c(self, id=1):
        self._log.debug("Hal: get i2c")

        # first time: create i2c storage
        if not hasattr(self,'_i2c'):
            self._log.debug("Hal: get i2c esp32, create i2c local storage")
            self._i2c = {}
        
        if self._utils.get_platform() == 'linux':
            self._log.debug("Hal: get i2c linux")
            return None
        elif self._utils.get_platform() == 'pyboard': 
            self._log.debug("Hal: get i2c pyboard")

            from machine import I2C
            # check boundaries
            if id > 2:
                self._log.debug("Hal: get i2c pyboard, id bigger then 2")
                return None

            # Create new or reuse existing
            if id not in self._i2c:
                self._log.debug("Hal: get i2c pyboard, create i2c object with id: "+str(id))
                self._i2c[id] = I2C(id)
                
            return self._i2c[id] 
        elif self._utils.get_platform() == 'esp32':
            self._log.debug("Hal: get i2c esp32")

            from machine import I2C
            # check boundaries
            if id > 1:
                self._log.debug("Hal: get i2c esp32, id bigger then 1")
                return None

            # Get SW I2C pins
            hardware = db.hardwareTable.getrow()

            # Create new or reuse existing
            if id not in self._i2c.keys():
                self._log.debug("Hal: get i2c esp32, create i2c object with id: "+str(id))
                try:
                    self._i2c[id] = I2C(sda=self.pin(hardware["sda"]), scl=self.pin(hardware["scl"]))
                except ValueError:
                    self._log.debug("Hal: get i2c esp32, exception valueerror")
                    return None

            return self._i2c[id] 
        elif self._utils.get_platform() == 'esp8266':
            self._log.debug("Hal: get i2c esp8266")

            from machine import I2C
            # check boundaries
            if id > 1:
                self._log.debug("Hal: get i2c esp8266, id bigger then 1")
                return None

            # Get SW I2C pins
            hardware = db.hardwareTable.getrow()
                
            # Create new or reuse existing
            if id not in self._i2c:
                self._log.debug("Hal: get i2c esp8266, create i2c object with id: "+str(id))
                self._i2c[id] = I2C(sda=self.pin(hardware["sda"]), scl=self.pin(hardware["scl"]))
                
            return self._i2c[id] 
        else:
            self._log.debug("Hal: get i2c failure")
            return None

    def get_spi(self, id=1):
        self._log.debug("Hal: get spi")

        # first time: create spi storage
        if not hasattr(self,'_spi'):
            self._log.debug("Hal: get spi esp32, create spi local storage")
            self._spi = {}
        
        if self._utils.get_platform() == 'linux':
            self._log.debug("Hal: get spi linux")
            return None
        elif self._utils.get_platform() == 'pyboard': 
            self._log.debug("Hal: get spi pyboard")

            from machine import SPI
            # check boundaries
            if id > 2:
                self._log.debug("Hal: get spi pyboard, id bigger then 2")
                return None

            # Create new or reuse existing
            if id not in self._spi:
                self._log.debug("Hal: get spi pyboard, create spi object with id: "+str(id))
                self._spi[id] = SPI(id)
                
            return self._spi[id] 
        elif self._utils.get_platform() == 'esp32':
            self._log.debug("Hal: get spi esp32")

            from machine import SPI
            # check boundaries
            if id > 1:
                self._log.debug("Hal: get spi esp32, id bigger then 1")
                return None

            # Get SW spi pins
            hardware = db.hardwareTable.getrow()

            # Create new or reuse existing
            if id not in self._spi.keys():
                self._log.debug("Hal: get spi esp32, create spi object with id: "+str(id))
                try:
                    self._spi[id] = SPI(miso=self.pin(hardware["miso"]), mosi=self.pin(hardware["mosi"]), sck=self.pin(hardware["sck"]), nss=self.pin(hardware["nss"]))
                except ValueError:
                    self._log.debug("Hal: get spi esp32, exception valueerror")
                    return None

            return self._spi[id] 
        elif self._utils.get_platform() == 'esp8266':
            self._log.debug("Hal: get spi esp8266")

            from machine import SPI
            # check boundaries
            if id > 1:
                self._log.debug("Hal: get spi esp8266, id bigger then 1")
                return None

            # Get SW spi pins
            hardware = db.hardwareTable.getrow()
                
            # Create new or reuse existing
            if id not in self._spi:
                self._log.debug("Hal: get spi esp8266, create spi object with id: "+str(id))
                self._spi[id] = SPI(miso=self.pin(hardware["miso"]), mosi=self.pin(hardware["mosi"]), sck=self.pin(hardware["sck"]), nss=self.pin(hardware["nss"]))
                
            return self._spi[id] 
        else:
            self._log.debug("Hal: get spi failure")
            return None

    def get_uart(self, id=1):
        self._log.debug("Hal: get uart")

        # first time: create uart storage
        if not hasattr(self,'_uart'):
            self._log.debug("Hal: get uart esp32, create uart local storage")
            self._uart = {}
        
        if self._utils.get_platform() == 'linux':
            self._log.debug("Hal: get uart linux")
            return None
        elif self._utils.get_platform() == 'pyboard': 
            self._log.debug("Hal: get uart pyboard")

            from machine import UART
            # check boundaries
            if id > 2:
                self._log.debug("Hal: get uart pyboard, id bigger then 2")
                return None

            # Create new or reuse existing
            if id not in self._uart:
                self._log.debug("Hal: get uart pyboard, create uart object with id: "+str(id))
                self._uart[id] = UART(id)
                
            return self._uart[id] 
        elif self._utils.get_platform() == 'esp32':
            self._log.debug("Hal: get uart esp32")

            from machine import UART
            # check boundaries
            if id > 2:
                self._log.debug("Hal: get uart esp32, id bigger then 2")
                return None

            # Get SW uart pins
            hardware = db.hardwareTable.getrow()

            # Create new or reuse existing
            if id not in self._uart.keys():
                self._log.debug("Hal: get uart esp32, create uart object with id: "+str(id))
                try:
                    self._uart[id] = UART(id, tx=int(hardware["tx"][1:]), rx=int(hardware["rx"][1:]))
                except ValueError:
                    self._log.debug("Hal: get uart esp32, exception valueerror")
                    return None

            return self._uart[id] 
        elif self._utils.get_platform() == 'esp8266':
            self._log.debug("Hal: get uart esp8266")

            from machine import UART
            # check boundaries
            if id > 2:
                self._log.debug("Hal: get uart esp8266, id bigger then 2")
                return None

            # Get SW uart pins
            hardware = db.hardwareTable.getrow()
                
            # Create new or reuse existing
            if id not in self._uart:
                self._log.debug("Hal: get uart esp8266, create uart object with id: "+str(id))
                self._uart[id] = UART(tx=self.pin(hardware["tx"]), rx=self.pin(hardware["rx"]))
                
            return self._uart[id] 
        else:
            self._log.debug("Hal: get uart failure")
            return None
                    