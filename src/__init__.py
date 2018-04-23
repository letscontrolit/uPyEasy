#          
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

import gc, uasyncio as asyncio
from . import core, db, ssl
from .init import init
from .hal import hal
from .app import app

def setnet(spi, cs, rst, ip='',gtw='',mask='',dns=''):
    #Set ethernet values
    from .utils import utils
    net = utils()
    net.setnet(spi,cs,rst,ip,gtw,mask,dns)
    
def setwifi(ssid,key,ssid2='',key2='', port=80):
    #set wifi values
    from .utils import utils
    wifi = utils()
    wifi.setwifi(ssid, key, ssid2, key2, port)
	
def main(**params):
    # auto collect garbage
    gc.enable()
    # Max 1/4 heap used: start auto collect
    gc.threshold((gc.mem_free() + gc.mem_alloc()) // 4)
    
    #Start init
    init_ok = init()
    
    if init_ok.init():
        # load pages
        from . import pages
        
        #We have a network!
        core._log.debug("Main: Pre-loading home page")
        # Preload templates to avoid memory fragmentation issues
        gc.collect()
        app._load_template('homepage.html')
        gc.collect()

        # Run only in STA mode!
        if core.initial_upyeasywifi == "STA" or core.initial_upyeasywifi == "STA+AP":
            #get ip address
            if core.initial_upyeasywifi == "STA":
               core._log.debug("Main: uPyEasy running in Station mode")
               ip_address = core._hal.get_ip_address()
            else: 
               core._log.debug("Main: uPyEasy running in Station+Access Point mode")
               ip_address = "0.0.0.0"
            config = db.configTable.getrow()
            port=config["port"]
            # Schedule plugin/protocol async coro's!
            core._log.debug("Main: Schedule async loops")
            # get loop
            loop = asyncio.get_event_loop()
            # Create async tasks
            loop.create_task(core._plugins.asyncdevices())
            loop.create_task(core._protocols.asynccontrollers())
            loop.create_task(core._scripts.asyncscripts())
        else:
            # WIFI AP mode
            core._log.debug("Main: uPyEasy running in Access Point mode")
            ip_address = "0.0.0.0"
            port = 80
        
        core._log.debug("Main: uPyEasy Main Async Loop on IP adress: "+ip_address+":"+str(port))
        app.run(host=ip_address, port=port, debug=False, log=core._log, **params)
        #app.run(host=ip_address, port=config["port"],debug=True, key=ssl.key, cert=ssl.cert, **params)   # SSL version
    else:
        #No network, exit!
        print("Exiting: Network not available, set network values!")
        
if __name__ == '__main__':
   main()
elif __name__ == '__setnet__':
   setnet()
elif __name__ == '__setwifi__':
   setwifi()