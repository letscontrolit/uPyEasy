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
    # set debug value
    _debug=2
    for param, value in params.items():
        if param == "loglevel":
            _debug=value
        
    # auto collect garbage
    gc.enable()
    # Max 1/4 heap used: start auto collect
    gc.threshold((gc.mem_free() + gc.mem_alloc()) // 4)
    
    #Start init
    init_ok = init(_debug)
    
    if init_ok.init():
        # load pages
        from . import pages
        
        # get loop
        loop = asyncio.get_event_loop()

        # Run only in STA, STA+AP or ETH mode!
        if core.initial_upyeasywifi == core.NET_STA or core.initial_upyeasywifi == core.NET_STA_AP or core.initial_upyeasywifi == core.NET_ETH:
            if core.initial_upyeasywifi == core.NET_STA:
                core._log.info("Main: uPyEasy running in Station mode")
            elif core.initial_upyeasywifi == core.NET_STA_AP:
                core._log.info("Main: uPyEasy running in Station_Access Point mode")
            elif core.initial_upyeasywifi == core.NET_ETH:
                core._log.info("Main: uPyEasy running in Ethernet mode")
           
            #get ip address
            ip_address = core._hal.get_ip_address()
            config = db.configTable.getrow()
            port=config["port"]
            # Schedule plugin/protocol async coro's!
            core._log.debug("Main: Schedule async loops")
            # Create async controller tasks
            loop.create_task(core._protocols.asynccontrollers())
        else:
            # WIFI AP mode
            core._log.info("Main: uPyEasy running in Access Point mode")
            ip_address = "0.0.0.0"
            port = 80

        # Create async tasks
        loop.create_task(core._plugins.asyncdevices())
        loop.create_task(core._plugins.asyncvalues())
        # check if rules/scripts are needed!
        advanced = db.advancedTable.getrow()
        if advanced["scripts"] == "on": loop.create_task(core._scripts.asyncscripts())
        if advanced["rules"] == "on": loop.create_task(core._scripts.asyncrules())

        # Run main loop
        core._log.info("Main: uPyEasy Main Async Loop on IP adress: "+ip_address+":"+str(port))
        while True:
            if _debug < 2: app.run(host=ip_address, port=port, debug=False, log=core._log)
            else:
                try:
                    app.run(host=ip_address, port=port, debug=False, log=core._log)
                except Exception as e:
                    core._log.debug("Main: Async loop exception: {}".format(repr(e)))
                    import sys
                    sys.print_exception(e)
            #app.run(host=ip_address, port=config["port"],debug=True, key=ssl.key, cert=ssl.cert)   # SSL version
    else:
        #No network, exit!
        print("Exiting: Network not available, set network values!")
        
if __name__ == '__main__':
   main()
elif __name__ == '__setnet__':
   setnet()
elif __name__ == '__setwifi__':
   setwifi()