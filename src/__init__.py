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

import gc
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

        #get ip address
        ip_address = core._hal.get_ip_address()
        config = db.configTable.getrow()
        
        core._log.debug("Main: uPyEasy Main Async Loop")
        app.run(host=ip_address, port=config["port"],debug=True, **params)
        #app.run(host=ip_address, port=config["port"],debug=True, key=ssl.key, cert=ssl.cert, **params)   # SSL version
    else:
        #No network, exit!
        print("Exiting: Network not available, set network values!")
        return 
        
if __name__ == '__main__':
   main()
elif __name__ == '__setnet__':
   setnet()
elif __name__ == '__setwifi__':
   setwifi()