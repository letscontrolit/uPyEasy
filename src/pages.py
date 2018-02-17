#          
# Filename: pages.py
# Version : 0.1
# Author  : Lisa Esselink
# Purpose : Server webpages to webclients
# Usage   : Retrieve webtemplates, fill in the content and send them to the webclients
#
# Copyright (c) Lisa Esselink. All rights reserved.  
# Licensed under the Creative Commons Attribution-NonCommercial 4.0 International License.
# See LICENSE file in the project root for full license information.  
#

import picoweb, gc, ustruct, ujson
from . import core, db, utils
from .app  import app
from .hal import hal
from .db import _dbc

_plugins    = core._plugins
_protocols  = core._protocols
_nic        = core._nic
_log        = core._log
_hal        = core._hal
_utils      = core._utils
_scripts    = core._scripts

def auth_page(request, response):
    # Are you authorized to use uPyEasy?
    _log.debug("Pages: Authorize User!?")

    # Get admin password if any
    config = db.configTable.getrow()
    if config["password"]:
        _log.debug("Pages: Authorize User is set, verifying password")

        # get password cookie if any
        password = request.headers.get(b"Cookie", None)

        # same password = ok, no password -> password page redirect
        if password:
            import uhashlib
            password = password.decode().split('=')[1]
            configpw = config["password"]
            hash = str(uhashlib.sha256(configpw).digest())
            if hash == password:
                return True

        _log.debug("Pages: Authorize User is set, password failed or not given")
        return False
    else: return True
        
@app.route("/password", methods=['GET','POST'])
def authenticate_page(request, response):
    _log.debug("Pages: Entering Authentication Page")

    if request.method == 'GET':
        info={}

        info['name']        = _utils.get_upyeasy_name()
        info['copyright']   = core.__copyright__
        info['holder']      = core.__author__
        info['message']     = ""

        # menu settings
        menu = 1
        advanced = db.advancedTable.getrow()
        gc.collect()

        yield from picoweb.start_response(response)
        yield from app.render_template(response, "header.html",(info, menu, advanced))
        yield from app.render_template(response, "password.html",(info,))
        yield from app.render_template(response, "footer.html",(info,))
    elif request.method == 'POST':
         #Auth password
        _log.debug("Pages: Authenticatie password")

        # Get all form values in a dict
        yield from request.read_form_data()
        uform = _utils.get_form_values(request.form)
        # same password = ok, no password -> password page redirect
        if uform["password"]:
            print (uform["password"])
            # Get admin password if any
            config = db.configTable.getrow()
            print(config["password"])
            if config["password"] == uform["password"]:
                import uhashlib
                configpw = config["password"]
                hash = str(uhashlib.sha256(configpw).digest())
                print(hash)
                # same password, send the cookie and redirect to homepage
                yield from response.awrite("HTTP/1.0 301 Moved Permanently\r\n")
                yield from response.awrite("Set-Cookie: upyeasy="+hash+"\r\n")
                yield from response.awrite("Location: /\r\n")
                yield from response.awrite("Content-Type: text/html\r\n")
                yield from response.awrite("<html><head><title>Moved</title></head><body><h1>Moved</h1></body></html>\r\n")
                return
            else:

                info={}
                info['name']        = _utils.get_upyeasy_name()
                info['copyright']   = core.__copyright__
                info['holder']      = core.__author__
                info['message']     = "Authentication Failed!"
                
                # menu settings
                menu = 1
                advanced = db.advancedTable.getrow()
                gc.collect()

                yield from picoweb.start_response(response)
                yield from app.render_template(response, "header.html",(info, menu, advanced))
                yield from app.render_template(response, "password.html",(info,))
                yield from app.render_template(response, "footer.html",(info,))
    
@app.route("/", methods=['GET'])
def homepage(request, response):
    if not auth_page(request, response): 
        #send to password page
        yield from response.awrite("HTTP/1.0 301 Moved Permanently\r\nLocation: /password\r\nContent-Type: text/html\r\n<html><head><title>Moved</title></head><body><h1>Moved</h1></body></html>\r\n")
        return
    
    #Display home page
    _log.debug("Pages: Entering Home Page")

    info={}

    info['name'] = _utils.get_upyeasy_name()
    info['copyright']=core.__copyright__
    info['holder']= core.__author__
    info['unit'] = _utils.get_unit_nr()
    info['version'] = core.__version__
    info['time'] = _hal.get_time()
    info['platform'] = _utils.get_platform()
    info['uptime'] = _utils.get_uptime()
    info['heap'] = _utils.get_mem()
    info['ip'] = _hal.get_ip_address()    
    info['stack'] = _utils.get_stack_current()
    _log.debug("Pages: Home Page Data collected")
    
    nodes = {}
    
    # menu settings
    menu = 1
    advanced = db.advancedTable.getrow()
    gc.collect()

    yield from picoweb.start_response(response)
    yield from app.render_template(response, "header.html",(info, menu, advanced))
    yield from app.render_template(response, "homepage.html",(info,nodes,))
    yield from app.render_template(response, "footer.html",(info,))

@app.route("/config", methods=['GET','POST'])
def configpage(request, response):
    if not auth_page(request, response): 
        #send to password page
        yield from response.awrite("HTTP/1.0 301 Moved Permanently\r\nLocation: /password\r\nContent-Type: text/html\r\n<html><head><title>Moved</title></head><body><h1>Moved</h1></body></html>\r\n")
        return

    #Edit Config
    
    if request.method == 'GET':
        _log.debug("Pages: Display Config Page")
        
        #init ONLY!
        try:
            _log.debug("Pages: Init Config Table")
            db.configTable.create_table()
        except OSError:
            pass

        config = db.configTable.getrow()
        
        #Get network record key
        network = db.networkTable.getrow()

        info={}

        info['name'] = config['name']
        info['copyright']=core.__copyright__
        info['holder']= core.__author__
        info['unit'] = config['unit']
        info['port']=config['port']
        info['password'] = config['password']
        if network['ssid']: info['ssid'] = network['ssid']
        else: info['ssid'] = '' 
        if network['key']: info['key'] = network['key']
        else: info['key'] = '' 
        if network['fbssid']: info['fbssid'] = network['fbssid']
        else: info['fbssid'] = '' 
        if network['fbkey']: info['fbkey'] = network['fbkey']
        else: info['fbkey'] = '' 
        if network['ip']: info['ip'] = network['ip']
        else: info['ip'] = ''  
        if network['gateway']: info['gateway'] = network['gateway']
        else: info['gateway'] = ''
        if network['subnet']: info['subnet'] = network['subnet']
        else: info['subnet'] = ''
        if network['dns']: info['dns'] = network['dns']
        else: info['dns'] = ''
        info['sleepenable'] = config['sleepenable']
        info['sleeptime'] = config['sleeptime']
        info['sleepfailure'] = config['sleepfailure']
        if _utils.get_platform() == 'linux':
           info['wifi'] = "disabled"
           info['ethernet'] = "disabled"
           info['sleep'] = ""
        elif _utils.get_platform() == 'pyboard':
           info['wifi'] = "disabled"
           info['ethernet'] = ""
           info['sleep'] = ""
        elif _utils.get_platform() == 'esp32':
           info['wifi'] = ""
           info['ethernet'] = "disabled"
           info['sleep'] = ""
        elif _utils.get_platform() == 'esp8266':
           info['wifi'] = ""
           info['ethernet'] = "disabled"
           info['sleep'] = ""
        else:
           info['wifi'] = ""
           info['ethernet'] = ""
           info['sleep'] = ""

        # menu settings
        menu = 2
        advanced = db.advancedTable.getrow()
        gc.collect()

        yield from picoweb.start_response(response)
        yield from app.render_template(response, "header.html",(info, menu, advanced))
        yield from app.render_template(response, "config.html",(info,))
        yield from app.render_template(response, "footer.html",(info,))

    elif request.method == 'POST':
         #Update config
        _log.debug("Pages: Update config")
        
        #init ONLY!
        try:
            db.configTable.create_table()
        except OSError:
            pass

        #Get config record key
        _dbconfig = db.configTable.getrow()

        #Get network record key
        dbnetwork = db.networkTable.getrow()

        # Get all form values in a dict
        yield from request.read_form_data()
        uform = _utils.get_form_values(request.form)

        # map form values to db records
        config = _utils.map_form2db(_dbconfig, uform)
        network = _utils.map_form2db(dbnetwork, uform)

        # Update config
        cid = db.configTable.update({"timestamp":config['timestamp']},name=config['name'],unit=config['unit'],password=config['password'],sleepenable=config['sleepenable'],sleeptime=config['sleeptime'],sleepfailure=config['sleepfailure'],port=config['port'])

        # update network
        cid = db.networkTable.update({"timestamp":network['timestamp']},ssid=network['ssid'],key=network['key'],fbssid=network['fbssid'],fbkey=network['fbkey'],ip=network['ip'],gateway=network['gateway'],subnet=network['subnet'],dns=network['dns'])

        #return to controllers page
        yield from response.awrite("HTTP/1.0 301 Moved Permanently\r\n")
        yield from response.awrite("Location: /config\r\n")
        yield from response.awrite("Content-Type: text/html\r\n")
        yield from response.awrite("<html><head><title>Moved</title></head><body><h1>Moved</h1></body></html>\r\n")
    
@app.route("/controllers", methods=['GET'])
def controllerspage(request, response):
    if not auth_page(request, response): 
        #send to password page
        yield from response.awrite("HTTP/1.0 301 Moved Permanently\r\nLocation: /password\r\nContent-Type: text/html\r\n<html><head><title>Moved</title></head><body><h1>Moved</h1></body></html>\r\n")
        return

    #Display controllers overview page
    _log.debug("Pages: Entering Controllers Page")

    info={}
    info['name'] = _utils.get_upyeasy_name()
    info['copyright']=core.__copyright__
    info['holder']= core.__author__

    # Get list of controllers
    controllers=db.controllerTable.public()
    
    # menu settings
    menu = 3
    advanced = db.advancedTable.getrow()
    gc.collect()

    yield from picoweb.start_response(response)
    yield from app.render_template(response, "header.html",(info, menu, advanced))
    yield from app.render_template(response, "controllers.html",(info,controllers,))
    yield from app.render_template(response, "footer.html",(info,))

@app.route("/controller_setting", methods=['GET','POST'])
def controllersettingpage(request, response):
    if not auth_page(request, response): 
        #send to password page
        yield from response.awrite("HTTP/1.0 301 Moved Permanently\r\nLocation: /password\r\nContent-Type: text/html\r\n<html><head><title>Moved</title></head><body><h1>Moved</h1></body></html>\r\n")
        return

    #Display controller settings page
    _log.debug("Pages: Entering Controller Settings Page")

    if request.method == 'GET' and request.qs != "":
        _log.debug("Pages: GET")
        parsed_qs = picoweb.utils.parse_qs(request.qs)
        _log.debug(''.join(list(parsed_qs)))
        qs_id = parsed_qs.get("id")
        _log.debug(''.join(qs_id))
        id = int(qs_id[0])
        _log.debug(str(id))
        qs_oper = parsed_qs.get("oper")
        if qs_oper: 
            oper = qs_oper[0] 
            _log.debug(oper)
        else: oper = None
        
        if id > 0 and not oper:
            #Edit controller
            _log.debug("Pages: Edit Controller: "+str(id))
            
            #connect to database
            _dbc.connect()
            
            #init ONLY!
            try:
                db.protocolTable.create_table()
            except OSError:
                pass
            try:
                db.controllerTable.create_table()  
            except OSError:
                pass
                    
            info={}
            info['name'] = _utils.get_upyeasy_name()
            info['copyright']=core.__copyright__
            info['holder']= core.__author__

            # Get correct controller
            controllers = db.controllerTable.public()
            for controller in controllers:
                if controller['id'] == id:
                   break
            
            # Get list of protocols
            protocols = db.protocolTable.public()
            for protocol in protocols:
                if protocol['name'] == controller['protocol']:
                   break
            info['id'] = protocol['id']
            info['protocolname']=protocol['name']
            
            _dbc.close()
           
            # menu settings
            menu = 3
            advanced = db.advancedTable.getrow()
            gc.collect()

            yield from picoweb.start_response(response)
            yield from app.render_template(response, "header.html",(info, menu, advanced))
            yield from app.render_template(response, protocol['template'],(info,protocols,controller,))
            yield from app.render_template(response, "footer.html",(info,))
        elif id > 0 and oper == 'del':
            # delete controller
            import os

            _log.debug("Pages: Delete Controller: "+str(id))
            
            #connect to database
            _dbc.connect()
            
            try:
                db.controllerTable.create_table()  
            except OSError:
                pass

            # Get correct controller
            controllers = db.controllerTable.public()
            for controller in controllers:
                if controller['id'] == id:
                   break
            _log.debug("Pages: remove record file: "+db.controllerTable.fname(controller['timestamp']))
            os.remove(db.controllerTable.fname(controller['timestamp']))
            
            _dbc.close()
            
            #gc.collect()
            #deleted, return to controllers page
            yield from response.awrite("HTTP/1.0 301 Moved Permanently\r\n")
            yield from response.awrite("Location: /controllers\r\n")
            yield from response.awrite("Content-Type: text/html\r\n")
            yield from response.awrite("<html><head><title>Moved</title></head><body><h1>Moved</h1></body></html>\r\n")

        elif id == 0:
            #New controller
            _log.debug("Pages: New Controller: "+str(id))
            
            #connect to database
            _dbc.connect()
            
            #init ONLY!
            try:
                db.protocolTable.create_table()
            except OSError:
                pass
                    
            # Get list of protocols
            protocols = db.protocolTable.public()
            protocol = db.protocolTable.getrow()

            _dbc.close()

            info={}
            info['name']=_utils.get_upyeasy_name()
            info['copyright']=core.__copyright__
            info['holder']= core.__author__
            info['id']=protocol['id']
            info['protocolname']=protocol['name']

            # empty controller
            controller = db.controllerTable.__schema__
            
            # menu settings
            menu = 3
            advanced = db.advancedTable.getrow()
            gc.collect()

            yield from picoweb.start_response(response)
            yield from app.render_template(response, "header.html",(info, menu, advanced))
            yield from app.render_template(response, protocol['template'],(info,protocols,controller,))
            yield from app.render_template(response, "footer.html",(info,))

    elif request.method == 'POST' and request.qs != "":
        _log.debug("Pages: POST")
        parsed_qs = picoweb.utils.parse_qs(request.qs)
        _log.debug(''.join(list(parsed_qs)))
        id = int(''.join(parsed_qs.get("id")))
        _log.debug(str(id))
        qs_oper = parsed_qs.get("oper")
        if qs_oper: 
            oper = qs_oper[0] 
            _log.debug(oper)
        else: oper = None
        # Get all form values in a dict
        yield from request.read_form_data()
        uform = _utils.get_form_values(request.form)
        
        if uform['currentprotocol'] != uform['protocol']:
            protocolchange = True
        else: protocolchange = False
        _log.debug('Current Protocol: '+ uform['currentprotocol'])
        _log.debug('New Protocol: '+ uform['protocol'])

        if id > 0:
            #Update controller
            _log.debug("Pages: Update Controller: "+str(id))
            
            if not protocolchange:
                # Same  protocol, update controller!
                _log.debug("Pages: Update controller: Same  protocol")
                #connect to database
                _dbc.connect()

                #init ONLY!
                try:
                    db.protocolTable.create_table()
                except OSError:
                    pass
                try:
                    db.controllerTable.create_table()  
                except OSError:
                    pass

                # Get list of protocols
                protocols = db.protocolTable.public()
                for protocol in protocols:
                    if protocol['name'] == uform['protocol']:
                       break
                _log.debug('Protocol: %s', protocol['name'])

                # Get correct controller
                controllers = db.controllerTable.public()
                for _dbcontroller in controllers:
                    if _dbcontroller['id'] == id:
                       break

                controller = _utils.map_form2db(_dbcontroller, uform)
                
                # Verify mandatory fields!
                if controller['hostname']:
                    cid = db.controllerTable.update({"timestamp":controller['timestamp']},id=controller['id'],usedns=controller['usedns'],hostname=controller['hostname'],port=controller['port'],user=controller['user'],password=controller['password'],subscribe=controller['subscribe'],publish=controller['publish'], enable=controller['enable'], protocol=controller['protocol'])
                else:
                    _log.debug("Failed to update controller entry: not all fields are filled")

                _dbc.close()

                #return to controllers page
                yield from response.awrite("HTTP/1.0 301 Moved Permanently\r\n")
                yield from response.awrite("Location: /controllers\r\n")
                yield from response.awrite("Content-Type: text/html\r\n")
                yield from response.awrite("<html><head><title>Moved</title></head><body><h1>Moved</h1></body></html>\r\n")
            else:
                # Different  protocol, empty controller!
                _log.debug("Pages: Update controller: different protocol")
                
                # Get list of protocols
                protocols = db.protocolTable.public()
                for protocol in protocols:
                    if protocol['name'] == uform['protocol']:
                       break
                _log.debug('Protocol: %s', protocol['name'])
                
                _dbc.close()

                info={}
                info['name'] = _utils.get_upyeasy_name()
                info['copyright']=core.__copyright__
                info['holder']= core.__author__
                info['id'] = protocol['id']
                info['protocolname'] = protocol['name']

                # Empty controller
                controller = db.controllerTable.__schema__
                
                # menu settings
                menu = 3
                advanced = db.advancedTable.getrow()
                gc.collect()

                yield from picoweb.start_response(response)
                yield from app.render_template(response, "header.html",(info, menu, advanced))
                yield from app.render_template(response, protocol['template'],(info,protocols,controller,))
                yield from app.render_template(response, "footer.html",(info,))
                
        elif id == 0:
            #Create controller
            _log.debug("Pages: Create Controller")

            controllerhostname = uform['hostname']
            _log.debug("Pages: Controller hostname: %s",controllerhostname)
            
            #Controller creation/protocol change
            if not controllerhostname and not protocolchange:
                #empty: return to controllers page
                _log.debug("Pages: Empty new Controller")
                yield from response.awrite("HTTP/1.0 301 Moved Permanently\r\n")
                yield from response.awrite("Location: /controllers\r\n")
                yield from response.awrite("Content-Type: text/html\r\n")
                yield from response.awrite("<html><head><title>Moved</title></head><body><h1>Moved</h1></body></html>\r\n")
            elif not controllerhostname and protocolchange:
                #Protocol change
                _log.debug("Pages: Empty controller protocol change, new protocol: "+uform['protocol'])
                #connect to database
                _dbc.connect()
                
                #init ONLY!
                try:
                    db.protocolTable.create_table()
                except OSError:
                    pass
                        
                # Get list of protocols
                protocols = db.protocolTable.public()
                for protocol in protocols:
                    if protocol['name'] == uform['protocol']:
                       break
                _log.debug('Protocol: %s', protocol['name'])
                
                _dbc.close()

                info={}
                info['name'] = _utils.get_upyeasy_name()
                info['copyright']=core.__copyright__
                info['holder']= core.__author__
                info['id'] = protocol['id']
                info['protocolname'] = protocol['name']

                # Empty controller
                controller = db.controllerTable.__schema__
                
                # menu settings
                menu = 3
                advanced = db.advancedTable.getrow()
                gc.collect()

                yield from picoweb.start_response(response)
                yield from app.render_template(response, "header.html",(info, menu, advanced))
                yield from app.render_template(response, protocol['template'],(info,protocols,controller,))
                yield from app.render_template(response, "footer.html",(info,))
            else:
                #Controller creation
                _log.debug("Pages: Create new Controller")
                #connect to database
                _dbc.connect()
                
                try:
                    db.controllerTable.create_table()  
                except OSError:
                    pass

                 #init ONLY!
                try:
                    db.protocolTable.create_table()
                except OSError:
                    pass

                # Get correct controller max count
                controllers = db.controllerTable.public()
                cnt = 0
                for controller in controllers:
                    if controller['id'] > cnt:
                       cnt = controller['id']
                _log.debug("Pages: Controller Count: %i",cnt)
                 
                # Empty controller
                _dbcontroller = db.controllerTable.__schema__

                controller = _utils.map_form2db(_dbcontroller, uform)
 
                # Verify mandatory fields!
                if controller['hostname']:
                    cid = db.controllerTable.create(id=cnt+1,usedns=controller['usedns'],hostname=controller['hostname'],port=controller['port'],user=controller['user'],password=controller['password'],subscribe=controller['subscribe'],publish=controller['publish'], enable=controller['enable'], protocol=controller['protocol'])
                else:
                    _log.debug("Failed to create controller entry: not all fields are filled")
                       
                _dbc.close()

                #init controller!
                _protocols.initcontroller(controller)
                
                #return to controllers page
                yield from response.awrite("HTTP/1.0 301 Moved Permanently\r\n")
                yield from response.awrite("Location: /controllers\r\n")
                yield from response.awrite("Content-Type: text/html\r\n")
                yield from response.awrite("<html><head><title>Moved</title></head><body><h1>Moved</h1></body></html>\r\n")
                    
@app.route("/hardware", methods=['GET','POST'])
def hardwarepage(request, response):
    if not auth_page(request, response): 
        #send to password page
        yield from response.awrite("HTTP/1.0 301 Moved Permanently\r\nLocation: /password\r\nContent-Type: text/html\r\n<html><head><title>Moved</title></head><body><h1>Moved</h1></body></html>\r\n")
        return

    #Display hardware page
    _log.debug("Pages: Entering Hardware Page")
    if request.method == 'GET':
        _log.debug("Pages: Display hardware Page")

        #connect to database
        _dbc.connect()
        
        # Get hardware config
        hardware = db.hardwareTable.getrow()

        # Get dxpin config
        dxpin = db.dxpinTable.getrow()

        _dbc.close()

        #General info
        info = {}
        info['name'] = _utils.get_upyeasy_name()
        info['copyright']=core.__copyright__
        info['holder']= core.__author__

        # Get dx labels
        dx_label = _utils.get_dxlabels()
        #_log.debug("Pages: dx_label: "+"-".join(dx_label))

        # menu settings
        menu = 4
        advanced = db.advancedTable.getrow()
        gc.collect()

        yield from picoweb.start_response(response)
        yield from app.render_template(response, "header.html",(info, menu, advanced))
        yield from app.render_template(response, "hardware.html",(info, hardware, dx_label, dxpin,))
        yield from app.render_template(response, "footer.html",(info,))
    elif request.method == 'POST':
         #Update config
        _log.debug("Pages: Update hardware")
        
        #connect to database
        _dbc.connect()
        
        # Get dxpin config, but it's a generator!
        dxpin = db.dxpinTable.getrow()
        # convert namedtuple to list which can be muted

        # Get hardware config, but it's a generator!
        dbhardware = db.hardwareTable.getrow()

        # get dx map
        dxmap = db.dxmapTable.getrow()
        
        # Get all form values in a dict
        yield from request.read_form_data()
        uform = _utils.get_form_values(request.form)

        hardware = _utils.map_form2db(dbhardware, uform)

        # New/reassigned/delete pin assignment
        _utils.pin_assignment('boardled',hardware['boardled'],dxmap["count"],dxpin)
        _utils.pin_assignment('sda',hardware['sda'],dxmap["count"],dxpin)
        _utils.pin_assignment('scl',hardware['scl'],dxmap["count"],dxpin)
        _utils.pin_assignment('mosi',hardware['mosi'],dxmap["count"],dxpin)
        _utils.pin_assignment('miso',hardware['miso'],dxmap["count"],dxpin)
        _utils.pin_assignment('sck',hardware['sck'],dxmap["count"],dxpin)
        _utils.pin_assignment('nss',hardware['nss'],dxmap["count"],dxpin)
        _utils.pin_assignment('tx',hardware['tx'],dxmap["count"],dxpin)
        _utils.pin_assignment('rx',hardware['rx'],dxmap["count"],dxpin)

        # Verify mandatory fields!
        cid = db.hardwareTable.update({"timestamp":hardware['timestamp']},boardled=hardware['boardled'],inverseled=hardware['inverseled'],sda=hardware['sda'],scl=hardware['scl'],mosi=hardware['mosi'],miso=hardware['miso'],sck=hardware['sck'],nss=hardware['nss'],tx=hardware['tx'],rx=hardware['rx'],d0=hardware['d0'],d1=hardware['d1'],d2=hardware['d2'],d3=hardware['d3'],d4=hardware['d4'],d5=hardware['d5'],d6=hardware['d6'],d7=hardware['d7'],d8=hardware['d8'],d9=hardware['d9'],d10=hardware['d10'],d11=hardware['d11'],d12=hardware['d12'],d13=hardware['d13'],d14=hardware['d14'],d15=hardware['d15'],d16=dxpin['d16'],d17=dxpin['d17'],d18=dxpin['d18'],d19=dxpin['d19'],d20=dxpin['d20'],d21=dxpin['d21'],d22=dxpin['d22'],d23=dxpin['d23'],d24=dxpin['d24'],d25=dxpin['d25'],d26=dxpin['d26'],d27=dxpin['d27'],d28=dxpin['d28'],d29=dxpin['d29'],d30=dxpin['d30'],d31=dxpin['d31'],d32=dxpin['d32'],d33=dxpin['d33'],d34=dxpin['d34'],d35=dxpin['d35'],d36=dxpin['d36'],d37=dxpin['d37'],d38=dxpin['d38'],d39=dxpin['d39'])

        cid = db.dxpinTable.update({"timestamp":dxpin['timestamp']},d0=dxpin['d0'],d1=dxpin['d1'],d2=dxpin['d2'],d3=dxpin['d3'],d4=dxpin['d4'],d5=dxpin['d5'],d6=dxpin['d6'],d7=dxpin['d7'],d8=dxpin['d8'],d9=dxpin['d9'],d10=dxpin['d10'],d11=dxpin['d11'],d12=dxpin['d12'],d13=dxpin['d13'],d14=dxpin['d14'],d15=dxpin['d15'],d16=dxpin['d16'],d17=dxpin['d17'],d18=dxpin['d18'],d19=dxpin['d19'],d20=dxpin['d20'],d21=dxpin['d21'],d22=dxpin['d22'],d23=dxpin['d23'],d24=dxpin['d24'],d25=dxpin['d25'],d26=dxpin['d26'],d27=dxpin['d27'],d28=dxpin['d28'],d29=dxpin['d29'],d30=dxpin['d30'],d31=dxpin['d31'],d32=dxpin['d32'],d33=dxpin['d33'],d34=dxpin['d34'],d35=dxpin['d35'],d36=dxpin['d36'],d37=dxpin['d37'],d38=dxpin['d38'],d39=dxpin['d39'])
        
        _dbc.close()
 
        #return to hardwares page
        yield from response.awrite("HTTP/1.0 301 Moved Permanently\r\n")
        yield from response.awrite("Location: /hardware\r\n")
        yield from response.awrite("Content-Type: text/html\r\n")
        yield from response.awrite("<html><head><title>Moved</title></head><body><h1>Moved</h1></body></html>\r\n")
 
@app.route("/devices", methods=['GET,POST'])
def devicespage(request, response):
    if not auth_page(request, response): 
        #send to password page
        yield from response.awrite("HTTP/1.0 301 Moved Permanently\r\nLocation: /password\r\nContent-Type: text/html\r\n<html><head><title>Moved</title></head><body><h1>Moved</h1></body></html>\r\n")
        return

    #Display devices overview page
    _log.debug("Pages: Entering Devices Page")

    #connect to database
    _dbc.connect()
    
    info={}
    info['name'] = _utils.get_upyeasy_name()
    info['copyright']=core.__copyright__
    info['holder']= core.__author__
       
    # Get list of plugins
    plugins = db.pluginTable.public()

    #devices
    devices=db.deviceTable.public()
    
    # Get current plugin values
    plugindata = {}
    
    # Get all plugin values!
    for device in devices:
        if device['enable'] == 'on':
            # get plugin data from plugin
            values={}
            _plugins.read(device, values)
            for plugin in plugins:
                if plugin['id'] == device['pluginid']:
                    break
            deval = ''
            if values:
                deval += "<table>"
                for cnt in range(1,plugin['valuecnt']+1):
                    deval += "<TR><TD><div class='div_l'>"+values['valueN'+str(cnt)]+"</div>:</TD><TD><div class='div_r'>"+str(values['valueV'+str(cnt)])+"</div></TD></TR>"
                deval += "</table>"
            device['values'] = deval
        else:
            device['values'] = ''
        
    # Get all controllers
    controllers = db.controllerTable.public()

    _dbc.close()
    
    # menu settings
    menu = 5
    advanced = db.advancedTable.getrow()
    gc.collect()

    yield from picoweb.start_response(response)
    yield from app.render_template(response, "header.html",(info, menu, advanced))
    yield from app.render_template(response, "devices.html",(info,devices,plugins, controllers,))
    yield from app.render_template(response, "footer.html",(info,))

@app.route("/device_setting", methods=['GET,POST'])
def devicesettingpage(request, response):
    if not auth_page(request, response): 
        #send to password page
        yield from response.awrite("HTTP/1.0 301 Moved Permanently\r\nLocation: /password\r\nContent-Type: text/html\r\n<html><head><title>Moved</title></head><body><h1>Moved</h1></body></html>\r\n")
        return

    #Display device settings page
    _log.debug("Pages: Entering Device Settings Page")
    if request.method == 'GET' and request.qs != "":
        _log.debug("Pages: GET")
        parsed_qs = picoweb.utils.parse_qs(request.qs)
        _log.debug('Parsed qs: '.join(list(parsed_qs)))
        qs_id = parsed_qs.get("id")
        _log.debug('Parsed id: '.join(qs_id))
        id = int(qs_id[0])
        _log.debug("Pages: id: %i",id)
        qs_oper = parsed_qs.get("oper")
        if qs_oper: 
            oper = qs_oper[0] 
            _log.debug("Pages: Oper: "+oper)
        else: oper = None
        
        if id > 0 and not oper:
            #Edit controller
            _log.debug("Pages: Edit Device: "+str(id))
            
            #connect to database
            _dbc.connect()
            
            #init ONLY!
            try:
                db.controllerTable.create_table()
            except OSError:
                pass
            try:
                db.deviceTable.create_table()  
            except OSError:
                pass
            try:
                db.pluginTable.create_table()  
            except OSError:
                pass

            # Get correct device
            devices = db.deviceTable.public()
            for device in devices:
                if device['id'] == id:
                   break
            
            # Get all controllers
            controllers = db.controllerTable.public()

            # Get list of plugins
            plugins = db.pluginTable.public()
            for plugin in plugins:
                if plugin['id'] == device['pluginid']:
                   break
            
            _dbc.close()
           
            info={}
            info['name'] = _utils.get_upyeasy_name()
            info['copyright']=core.__copyright__
            info['holder']= core.__author__
            #get plugin id or default
            info['pluginid'] = device['pluginid']
            info['pluginname'] = plugin['name']

            plugindata = {}
            plugindata['name'] = device['name']
            # get plugin data from plugin
            _plugins.loadform(plugindata)
 
            # Get dxpin config
            dxpin = db.dxpinTable.getrow()

            # Get dx labels
            dx_label = _utils.get_dxlabels()
            #_log.debug("Pages: dx_label: "+"-".join(dx_label))
            
            # Get hardware config
            hardware = db.hardwareTable.getrow()


            # Convert pin settings
            dxpins = device["dxpin"].split(';')
            for cnt in range(0,plugindata["pincnt"]):
                device['dxpin'+str(cnt)] = dxpins[cnt]

            _log.debug("Pages: Loading plugin page: "+plugin['template'])

            # menu settings
            menu = 5
            advanced = db.advancedTable.getrow()
            gc.collect()

            yield from picoweb.start_response(response)
            yield from app.render_template(response, "header.html",(info, menu, advanced))
            yield from app.render_template(response, "plugin_header.html",(info, controllers, plugins, plugindata, device, dxpin, dx_label, hardware,))
            yield from app.render_template(response, plugin['template'],(info, plugindata,))
            yield from app.render_template(response, "plugin_footer.html",(info, plugindata,))
            yield from app.render_template(response, "footer.html",(info,))
        elif id > 0 and oper == 'del':
            # delete device
            import os

            _log.debug("Pages: Delete Device: "+str(id))
            
            #connect to database
            _dbc.connect()
            
            try:
                db.deviceTable.create_table()  
            except OSError:
                pass

            # Get correct device
            devices = db.deviceTable.public()
            for device in devices:
                if device['id'] == id:
                   break

            # Get list of plugins
            plugins = db.pluginTable.public()
            for plugin in plugins:
                if plugin['id'] == device['pluginid']:
                   break

            _log.debug("Pages: remove record file: "+db.deviceTable.fname(device['timestamp']))
            os.remove(db.deviceTable.fname(device['timestamp']))
            
            _dbc.close()
            
            # Get dxpin config
            dxpin = db.dxpinTable.getrow()

            # Convert pin settings
            dxpins = device["dxpin"].split(';')
            for cnt in range(0,plugin["pincnt"]):
                _log.debug("Pages: delete plugin, free pin: "+dxpins[cnt])
                dxpin[dxpins[cnt]] = ''

            # Updated deleted pins
            cid = db.dxpinTable.update({"timestamp":dxpin['timestamp']},d0=dxpin['d0'],d1=dxpin['d1'],d2=dxpin['d2'],d3=dxpin['d3'],d4=dxpin['d4'],d5=dxpin['d5'],d6=dxpin['d6'],d7=dxpin['d7'],d8=dxpin['d8'],d9=dxpin['d9'],d10=dxpin['d10'],d11=dxpin['d11'],d12=dxpin['d12'],d13=dxpin['d13'],d14=dxpin['d14'],d15=dxpin['d15'],d16=dxpin['d16'],d17=dxpin['d17'],d18=dxpin['d18'],d19=dxpin['d19'],d20=dxpin['d20'],d21=dxpin['d21'],d22=dxpin['d22'],d23=dxpin['d23'],d24=dxpin['d24'],d25=dxpin['d25'],d26=dxpin['d26'],d27=dxpin['d27'],d28=dxpin['d28'],d29=dxpin['d29'],d30=dxpin['d30'],d31=dxpin['d31'],d32=dxpin['d32'],d33=dxpin['d33'],d34=dxpin['d34'],d35=dxpin['d35'],d36=dxpin['d36'],d37=dxpin['d37'],d38=dxpin['d38'],d39=dxpin['d39'])

            # clean up!
            gc.collect()

            #deleted, return to controllers page
            yield from response.awrite("HTTP/1.0 301 Moved Permanently\r\n")
            yield from response.awrite("Location: /devices\r\n")
            yield from response.awrite("Content-Type: text/html\r\n")
            yield from response.awrite("<html><head><title>Moved</title></head><body><h1>Moved</h1></body></html>\r\n")

        elif id == 0:
            #New device
            _log.debug("Pages: New Device, choose plugin")
            
            #connect to database
            _dbc.connect()
            
            # Get list of plugins
            plugins = db.pluginTable.public()
            plugins = sorted(plugins, key=lambda k: k['name'])

            _dbc.close()

            info={}
            info['name'] = _utils.get_upyeasy_name()
            info['copyright']=core.__copyright__
            info['holder']= core.__author__

            # menu settings
            menu = 5
            advanced = db.advancedTable.getrow()
            gc.collect()
            
            yield from picoweb.start_response(response)
            yield from app.render_template(response, "header.html",(info, menu, advanced))
            yield from app.render_template(response, "plugin.html",(info, plugins,))
            yield from app.render_template(response, "footer.html",(info,))
    elif request.method == 'POST' and request.qs != "":
        _log.debug("Pages: POST")
        parsed_qs = picoweb.utils.parse_qs(request.qs)
        _log.debug(''.join(list(parsed_qs)))
        id = int(''.join(parsed_qs.get("id")))
        _log.debug(str(id))
        qs_oper = parsed_qs.get("oper")
        if qs_oper: 
            oper = qs_oper[0] 
            _log.debug(oper)
        else: oper = None

        # Get all form values in a dict
        yield from request.read_form_data()
        uform = _utils.get_form_values(request.form)
 
        if 'currentpluginid' in uform: 
            _log.debug('Current Plugin: %s', uform['currentpluginid'])
            if uform['currentpluginid'] != uform['pluginid']:
                pluginchange = True
            else: pluginchange = False
        else: pluginchange = False

        if 'pluginid' in uform: 
            #get new plugin id
            pluginid = int(uform['pluginid'])
            _log.debug('New Plugin: %s', uform['pluginid'])
        else: 
            pluginid = None
            
        if id > 0:
            #Update Device
            _log.debug("Pages: Update Device: "+str(id))
            
            if not pluginchange:
                # Same  plugin, update Device!
                _log.debug("Pages: Update Device: Same  plugin")
                #connect to database
                _dbc.connect()

                #init ONLY!
                try:
                    db.deviceTable.create_table()
                except OSError:
                    pass

                # Get correct device
                dbdevices = db.deviceTable.public()
                for dbdevice in dbdevices:
                    if dbdevice['id'] == id:
                       break

                # Get list of plugins
                plugins = db.pluginTable.public()
                for plugin in plugins:
                    if plugin['id'] == dbdevice['pluginid']:
                       break

                # Get dxpin config
                dxpin = db.dxpinTable.getrow()

                #contract dxpin fields
                dbdevice['dxpin'] = ""
                for dxcnt in range(0,plugin['pincnt']):
                    dxpin[uform['dxpin'+str(dxcnt)]] = dbdevice['name']
                    dbdevice['dxpin'] += str(uform['dxpin'+str(dxcnt)])
                    if dxcnt < plugin['pincnt']-1: dbdevice['dxpin'] += ";"
                    
                # exchange values from form to device
                device = _utils.map_form2db(dbdevice, uform)

                # Verify mandatory fields!
                if device['id']:
                    cid = db.deviceTable.update({"timestamp":device['timestamp']},id=device['id'],enable=device['enable'],pluginid=device['pluginid'],name=device['name'],controller=device['controller'],controllerid=device['controllerid'],dxpin=device['dxpin'],delay=device['delay'], sync=device['sync'], i2c=device['i2c'], bootstate=device['bootstate'], pullup=device['pullup'],inverse=device['inverse'],port=device['port'])
                else:
                    _log.debug("Pages: Failed to update device entry: not all fields are filled")

                _dbc.close()

                # init device!
                _plugins.initdevice(device)
                
                # call saveform device!
                uform['name'] = device['name']
                _plugins.saveform(uform)

                #return to devices page
                yield from response.awrite("HTTP/1.0 301 Moved Permanently\r\n")
                yield from response.awrite("Location: /devices\r\n")
                yield from response.awrite("Content-Type: text/html\r\n")
                yield from response.awrite("<html><head><title>Moved</title></head><body><h1>Moved</h1></body></html>\r\n")
            else:
                # Different  plugin, empty device!
                _log.debug("Pages: Update device: different plugin")
                
                #connect to database
                _dbc.connect()
                
                # Get correct device
                devices = db.deviceTable.public()
                for device in devices:
                    if device['id'] == id:
                       break
                
                # Get list of plugins
                plugins = db.pluginTable.public()
                for plugin in plugins:
                    if plugin['id'] == pluginid:
                       break
                
                # Get correct controller
                controllers=db.controllerTable.public()

                _dbc.close()

                info={}
                info['name'] = _utils.get_upyeasy_name()
                info['copyright']=core.__copyright__
                info['holder']= core.__author__
                info['id'] = 1
                info['pluginname'] = plugin['name']

                # Get dx labels
                dx_label = _utils.get_dxlabels()
                #_log.debug("Pages: dx_label: "+"-".join(dx_label))
                
                # Get hardware config
                hardware = db.hardwareTable.getrow()

                # Get dxpin config
                dxpin = db.dxpinTable.getrow()

                # Empty device, dict converted to list
                device = db.deviceTable.__schema__
                
                plugindata = {}
                plugindata['name'] = plugin['name']
                # get plugin data from plugin
                _plugins.loadform(plugindata)


                # Convert pin settings
                for cnt in range(0,plugindata["pincnt"]):
                    device['dxpin'+str(cnt)] = 0

                _log.debug("Pages: Loading plugin page: "+plugin['template'])

                # menu settings
                menu = 5
                advanced = db.advancedTable.getrow()
                gc.collect()

                yield from picoweb.start_response(response)
                yield from app.render_template(response, "header.html",(info, menu, advanced))
                yield from app.render_template(response, "plugin_header.html",(info, controllers, plugins, plugindata, device, dxpin, dx_label, hardware,))
                yield from app.render_template(response, plugin['template'],(info, plugindata,))
                yield from app.render_template(response, "plugin_footer.html",(info, plugindata,))
                yield from app.render_template(response, "footer.html",(info,))
        elif id == 0:
            #Create Device
            _log.debug("Pages: Create Device")

            if 'name' in uform: 
                devicename = uform['name']
                _log.debug("Pages: Device name: %s",devicename)
            else: devicename = None
            
            #Device creation/plugin change
            if not devicename and not pluginchange and not pluginid:
                #empty: return to devices page
                _log.debug("Pages: Empty new Device")
                yield from response.awrite("HTTP/1.0 301 Moved Permanently\r\n")
                yield from response.awrite("Location: /devices\r\n")
                yield from response.awrite("Content-Type: text/html\r\n")
                yield from response.awrite("<html><head><title>Moved</title></head><body><h1>Moved</h1></body></html>\r\n")
            elif pluginchange:
                #Plugin change
                _log.debug("Pages: Empty device plugin change, new plugin")
                #connect to database
                _dbc.connect()
                
                # Get list of plugins
                plugins = db.pluginTable.public()
                for plugin in plugins:
                    if plugin['id'] == pluginid:
                       break
                        
                _dbc.close()

                info={}
                info['name'] = _utils.get_upyeasy_name()
                info['copyright']=core.__copyright__
                info['holder']= core.__author__
                info['pluginid'] = pluginid
                info['pluginname'] = plugin['name']

                # Get dx labels
                dx_label = _utils.get_dxlabels()
                #_log.debug("Pages: dx_label: "+"-".join(dx_label))
                
                # Get hardware config
                hardware = db.hardwareTable.getrow()

                # Get correct controller
                controllers=db.controllerTable.public()

                # Empty device, dict converted to list
                device = db.deviceTable.__schema__
                
                # Get dxpin config
                dxpin = db.dxpinTable.getrow()

                plugindata = {}
                plugindata['name'] = plugin['name']
                # get plugin data from plugin
                _plugins.loadform(plugindata)

                # Convert pin settings
                for cnt in range(0,plugindata["pincnt"]):
                    device['dxpin'+str(cnt)] = 0

                _log.debug("Pages: Loading plugin page: "+plugin['template'])

                # menu settings
                menu = 5
                advanced = db.advancedTable.getrow()
                gc.collect()

                yield from picoweb.start_response(response)
                yield from app.render_template(response, "header.html",(info, menu, advanced))
                yield from app.render_template(response, "plugin_header.html",(info, controllers, plugins, plugindata, device, dxpin, dx_label, hardware,))
                yield from app.render_template(response, plugin['template'],(info, plugindata,))
                yield from app.render_template(response, "plugin_footer.html",(info, plugindata, ))
                yield from app.render_template(response, "footer.html",(info,))
            elif pluginid and not devicename:
                #New device
                _log.debug("Pages: New Device and plugin choosen: "+str(pluginid))
                
                #connect to database
                _dbc.connect()
                
                # Get correct controller
                controllers=db.controllerTable.public()
                
                # Get list of plugins
                plugins = db.pluginTable.public()
                for plugin in plugins:
                    if plugin['id'] == pluginid:
                        break

                _dbc.close()

                info={}
                info['name'] = _utils.get_upyeasy_name()
                info['copyright']=core.__copyright__
                info['holder']= core.__author__
                info['pluginid'] = plugin['id']
                info['pluginname'] = plugin['name']

                # Get dx labels
                dx_label = _utils.get_dxlabels()
                #_log.debug("Pages: dx_label: "+"-".join(dx_label))
                
                # Get hardware config
                hardware = db.hardwareTable.getrow()

                # Empty device, dict converted to list
                device = db.deviceTable.__schema__


                # init temp device!
                device['name'] = 'dummy'
                device['pluginid'] = pluginid
                _plugins.initdevice(device)

                # Get dxpin config
                dxpin = db.dxpinTable.getrow()

                plugindata = {}
                # use dummy instead of devicename which we don't have yet.
                plugindata['name'] = device['name']
                # get plugin data from plugin
                _plugins.loadform(plugindata)
                
                # clear devicename
                device['name'] = ''

                # Convert pin settings
                for cnt in range(0,plugindata["pincnt"]):
                    device['dxpin'+str(cnt)] = "d0"
                
                _log.debug("Pages: Loading plugin page: "+plugin['template'])

                # menu settings
                menu = 5
                advanced = db.advancedTable.getrow()
                gc.collect()

                yield from picoweb.start_response(response)
                yield from app.render_template(response, "header.html",(info, menu, advanced))
                yield from app.render_template(response, "plugin_header.html",(info, controllers, plugins, plugindata, device, dxpin, dx_label, hardware,))
                yield from app.render_template(response, plugin['template'],(info, plugindata,))
                yield from app.render_template(response, "plugin_footer.html",(info, plugindata,))
                yield from app.render_template(response, "footer.html",(info,))

            else:
                # Same  plugin, new Device!
                _log.debug("Pages: New Device: Same  plugin")
                #connect to database
                _dbc.connect()

                #init ONLY!
                try:
                    db.deviceTable.create_table()
                except OSError:
                    pass

                # Get correct device max count
                devices = db.deviceTable.public()
                cnt = 0
                for device in devices:
                    if device['id'] > cnt:
                       cnt = device['id']
                _log.debug("Pages: Device max Count: %i",cnt)
                    
                # set form values
                # Empty device, dict converted to list
                db_device = db.deviceTable.__schema__
                device = _utils.map_form2db(db_device, uform)
                
                # Get list of plugins
                plugins = db.pluginTable.public()
                for plugin in plugins:
                    if plugin['id'] == device['pluginid']:
                       break

                # Get dxpin config
                dxpin = db.dxpinTable.getrow()

                #contract dxpin fields
                device['dxpin'] = ""
                for dxcnt in range(0,plugin['pincnt']):
                    dxpin["d"+str(device['dxpin'+str(dxcnt)])] = device['name']
                    device['dxpin'] += str(device['dxpin'+str(dxcnt)])
                    if dxcnt < plugin['pincnt']-1: device['dxpin'] += ";"
                
                # Update pins
                cid = db.dxpinTable.update({"timestamp":dxpin['timestamp']},d0=dxpin['d0'],d1=dxpin['d1'],d2=dxpin['d2'],d3=dxpin['d3'],d4=dxpin['d4'],d5=dxpin['d5'],d6=dxpin['d6'],d7=dxpin['d7'],d8=dxpin['d8'],d9=dxpin['d9'],d10=dxpin['d10'],d11=dxpin['d11'],d12=dxpin['d12'],d13=dxpin['d13'],d14=dxpin['d14'],d15=dxpin['d15'],d16=dxpin['d16'],d17=dxpin['d17'],d18=dxpin['d18'],d19=dxpin['d19'],d20=dxpin['d20'],d21=dxpin['d21'],d22=dxpin['d22'],d23=dxpin['d23'],d24=dxpin['d24'],d25=dxpin['d25'],d26=dxpin['d26'],d27=dxpin['d27'],d28=dxpin['d28'],d29=dxpin['d29'],d30=dxpin['d30'],d31=dxpin['d31'],d32=dxpin['d32'],d33=dxpin['d33'],d34=dxpin['d34'],d35=dxpin['d35'],d36=dxpin['d36'],d37=dxpin['d37'],d38=dxpin['d38'],d39=dxpin['d39'])

                # Verify mandatory fields!
                if device['name']:
                    cid = db.deviceTable.create(id=cnt+1,enable=device['enable'],pluginid=device['pluginid'],name=device['name'],controller=device['controller'],controllerid=device['controllerid'],dxpin=device['dxpin'],delay=device['delay'], sync=device['sync'], i2c=device['i2c'], bootstate=device['bootstate'], pullup=device['pullup'],inverse=device['inverse'],port=device['port'])
                else:
                    _log.debug("Pages: Failed to create device entry: not all fields are filled")

                _dbc.close()
                
                # init device!
                _plugins.initdevice(device)

                # call saveform device!
                uform['name'] = device['name']
                _plugins.saveform(uform)

                #return to devices page
                yield from response.awrite("HTTP/1.0 301 Moved Permanently\r\n")
                yield from response.awrite("Location: /devices\r\n")
                yield from response.awrite("Content-Type: text/html\r\n")
                yield from response.awrite("<html><head><title>Moved</title></head><body><h1>Moved</h1></body></html>\r\n")

@app.route("/rules", methods=['GET','POST'])
def rulepage(request, response):
    if not auth_page(request, response): 
        #send to password page
        yield from response.awrite("HTTP/1.0 301 Moved Permanently\r\nLocation: /password\r\nContent-Type: text/html\r\n<html><head><title>Moved</title></head><body><h1>Moved</h1></body></html>\r\n")
        return

    #Edit Config
    
    if request.method == 'GET':
        _log.debug("Pages: Display Rules Page")

        info = {}
        info['name'] = _utils.get_upyeasy_name()
        info['copyright']=core.__copyright__
        info['holder']= core.__author__
        info['id']=6
        
        # Get list of Rules
        rules = db.ruleTable.public()
        rules = sorted(rules, key=lambda k: k['name'])
        
        # menu settings
        menu = 6
        advanced = db.advancedTable.getrow()
        gc.collect()

        yield from picoweb.start_response(response)
        yield from app.render_template(response, "header.html",(info, menu, advanced))
        yield from app.render_template(response, "rules.html",(info,rules))
        yield from app.render_template(response, "footer.html",(info,))

@app.route("/rule_setting", methods=['GET,POST'])
def rulesettingpage(request, response):
    if not auth_page(request, response): 
        #send to password page
        yield from response.awrite("HTTP/1.0 301 Moved Permanently\r\nLocation: /password\r\nContent-Type: text/html\r\n<html><head><title>Moved</title></head><body><h1>Moved</h1></body></html>\r\n")
        return

    #Display device settings page
    _log.debug("Pages: Entering rule Settings Page")
    if request.method == 'GET' and request.qs != "":
        _log.debug("Pages: GET")
        parsed_qs = picoweb.utils.parse_qs(request.qs)
        _log.debug('Parsed qs: '.join(list(parsed_qs)))
        # get id
        qs_id = parsed_qs.get("id")
        if qs_id: 
            _log.debug('Parsed id: {}'.format(qs_id))
            id = int(qs_id[0])
        else: id = None
        # get operation
        qs_oper = parsed_qs.get("oper")
        if qs_oper: 
            oper = qs_oper[0] 
            _log.debug("Pages: Oper: "+oper)
        else: oper = None
        
        if id and oper == "edit":
            #Edit rule
            _log.debug("Pages: Edit rule: "+str(id))
            
            info = {}
            info['name'] = _utils.get_upyeasy_name()
            info['copyright']=core.__copyright__
            info['holder']= core.__author__
            
            # Get rule from table
            rules = db.ruleTable.public()
            for rule in rules:
                if rule['id'] == id:
                   break
            
            filename = 'rules/'+rule['filename']
            _log.debug("Pages: rule filename: "+filename)
            rule_file = open(filename, 'r')
            rule['content'] = rule_file.read()
            rule_file.close() 
            rule['size'] = len(rule['content'])
            rule['operation'] = 'edit'

            # menu settings
            menu = 7
            advanced = db.advancedTable.getrow()
            gc.collect()

            yield from picoweb.start_response(response)
            yield from app.render_template(response, "header.html",(info, menu, advanced))
            yield from app.render_template(response, "rule_edit.html",(info,rule))
            yield from app.render_template(response, "footer.html",(info,))
        elif id and oper == 'enable':
            # enable rule
            _log.debug("Pages: Enable/Disable rule: "+str(id))
            
            # Get rule from table
            rules = db.ruleTable.public()
            for rule in rules:
                if rule['id'] == id:
                   break

            # toggle enable
            if rule["enable"] == 'on': rule["enable"] = 'off'
            else: rule["enable"] = 'on'
                   
            #change rule table record
            try:
                cid = db.ruleTable.update({"timestamp":rule['timestamp']},enable=rule["enable"])
            except OSError:
                self._log.debug("Rules: Exception creating  rule record: "+modname)

            #gc.collect()
            #deleted, return to rules page
            yield from response.awrite("HTTP/1.0 301 Moved Permanently\r\n")
            yield from response.awrite("Location: /rules\r\n")
            yield from response.awrite("Content-Type: text/html\r\n")
            yield from response.awrite("<html><head><title>Moved</title></head><body><h1>Moved</h1></body></html>\r\n")
        elif id and oper == 'del':
            # Get rule from table
            rules = db.ruleTable.public()
            for rule in rules:
                if rule['id'] == id:
                   break
            
            # get filename
            filename = 'rules/'+rule['filename']

            # delete device
            import os

            _log.debug("Pages: Delete rule: "+filename)
            os.remove(filename)
            
            #gc.collect()
            #deleted, return to rule page
            yield from response.awrite("HTTP/1.0 301 Moved Permanently\r\n")
            yield from response.awrite("Location: /rules\r\n")
            yield from response.awrite("Content-Type: text/html\r\n")
            yield from response.awrite("<html><head><title>Moved</title></head><body><h1>Moved</h1></body></html>\r\n")
        elif oper == 'refresh':
            # enable rule
            _log.debug("Pages: refresh rules")
            
            gc.collect()
            #deleted, return to rules page
            yield from response.awrite("HTTP/1.0 301 Moved Permanently\r\n")
            yield from response.awrite("Location: /rules\r\n")
            yield from response.awrite("Content-Type: text/html\r\n")
            yield from response.awrite("<html><head><title>Moved</title></head><body><h1>Moved</h1></body></html>\r\n")
        elif oper == 'add':
            #New device
            _log.debug("Pages: Add rule")
            
            info = {}
            info['name'] = _utils.get_upyeasy_name()
            info['copyright']=core.__copyright__
            info['holder']= core.__author__
            rule = {}
            rule['scriptname'] = ""
            rule['content'] = ""
            rule['size'] = 0
            rule['operation'] = 'add'
            rule['id'] = 0
            
            # menu settings
            menu = 7
            advanced = db.advancedTable.getrow()
            gc.collect()

            yield from picoweb.start_response(response)
            yield from app.render_template(response, "header.html",(info, menu,advanced))
            yield from app.render_template(response, "rule_edit.html",(info,rule))
            yield from app.render_template(response, "footer.html",(info,))

    elif request.method == 'POST':
        _log.debug("Pages: POST")
        # Get all form values in a dict
        parsed_qs = picoweb.utils.parse_qs(request.qs)
        yield from request.read_form_data()
        uform = _utils.get_form_values(request.form)

        if uform['filename']:
            #Create rule
            _log.debug("Pages: Create rule: {}".format(uform['filename']))
            
            try:
                content = uform['content']
            except TypeError:
                content = ""
                        
            # get filename
            filename = 'rules/'+uform['filename']

            _log.debug("Pages: rule filename: "+filename)
            try:
                rule_file = open(filename, 'w')
                rule_file.write(content)
                rule_file.close() 
            except TypeError:
                _log.debug("Pages: Exception getting rule creation from data!")

            # reload all rules
            _scripts.loadrules()
                
            #return to devices page
            yield from response.awrite("HTTP/1.0 301 Moved Permanently\r\n")
            yield from response.awrite("Location: /rules\r\n")
            yield from response.awrite("Content-Type: text/html\r\n")
            yield from response.awrite("<html><head><title>Moved</title></head><body><h1>Moved</h1></body></html>\r\n")
        
@app.route("/scripts", methods=['GET','POST'])
def scriptpage(request, response):
    if not auth_page(request, response): 
        #send to password page
        yield from response.awrite("HTTP/1.0 301 Moved Permanently\r\nLocation: /password\r\nContent-Type: text/html\r\n<html><head><title>Moved</title></head><body><h1>Moved</h1></body></html>\r\n")
        return

    #Edit Config
    
    if request.method == 'GET':
        _log.debug("Pages: Display Scripts Page")

        info = {}
        info['name'] = _utils.get_upyeasy_name()
        info['copyright']=core.__copyright__
        info['holder']= core.__author__
        info['id']=7
        
        # Get list of scripts
        scripts = db.scriptTable.public()
        scripts = sorted(scripts, key=lambda k: k['name'])
        
        # menu settings
        menu = 7
        advanced = db.advancedTable.getrow()
        gc.collect()

        yield from picoweb.start_response(response)
        yield from app.render_template(response, "header.html",(info, menu, advanced))
        yield from app.render_template(response, "scripts.html",(info,scripts))
        yield from app.render_template(response, "footer.html",(info,))

@app.route("/script_setting", methods=['GET,POST'])
def scriptsettingpage(request, response):
    if not auth_page(request, response): 
        #send to password page
        yield from response.awrite("HTTP/1.0 301 Moved Permanently\r\nLocation: /password\r\nContent-Type: text/html\r\n<html><head><title>Moved</title></head><body><h1>Moved</h1></body></html>\r\n")
        return

    #Display device settings page
    _log.debug("Pages: Entering Script Settings Page")
    if request.method == 'GET' and request.qs != "":
        _log.debug("Pages: GET")
        parsed_qs = picoweb.utils.parse_qs(request.qs)
        _log.debug('Parsed qs: '.join(list(parsed_qs)))
        # get id
        qs_id = parsed_qs.get("id")
        if qs_id:
            _log.debug('Parsed id: '.join(qs_id))
            id = int(qs_id[0])
        else: id = None
        # get operation
        qs_oper = parsed_qs.get("oper")
        if qs_oper: 
            oper = qs_oper[0] 
            _log.debug("Pages: Oper: "+oper)
        else: oper = None
        
        if id and oper == "edit":
            #Edit script
            _log.debug("Pages: Edit script: "+str(id))
            
            info = {}
            info['name'] = _utils.get_upyeasy_name()
            info['copyright']=core.__copyright__
            info['holder']= core.__author__
            
            # Get script from table
            scripts = db.scriptTable.public()
            for script in scripts:
                if script['id'] == id:
                   break
            
            filename = 'scripts/'+script['filename']
            _log.debug("Pages: Script filename: "+filename)
            script_file = open(filename, 'r')
            script['content'] = script_file.read()
            script_file.close() 
            script['size'] = len(script['content'])
            script['operation'] = 'edit'

            # menu settings
            menu = 7
            advanced = db.advancedTable.getrow()
            gc.collect()

            yield from picoweb.start_response(response)
            yield from app.render_template(response, "header.html",(info, menu,advanced))
            yield from app.render_template(response, "script_edit.html",(info,script))
            yield from app.render_template(response, "footer.html",(info,))
        elif id and oper == 'enable':
            # enable script
            _log.debug("Pages: Enable/Disable Script: "+str(id))
            
            # Get script from table
            scripts = db.scriptTable.public()
            for script in scripts:
                if script['id'] == id:
                   break

            _scripts.initscript(script)       
                   
            # toggle enable
            if script["enable"] == 'on': script["enable"] = 'off'
            else: script["enable"] = 'on'
                   
            #change script table record
            try:
                cid = db.scriptTable.update({"timestamp":script['timestamp']},enable=script["enable"])
            except OSError:
                self._log.debug("Scripts: Exception creating  script record: "+modname)

            #gc.collect()
            #deleted, return to scripts page
            yield from response.awrite("HTTP/1.0 301 Moved Permanently\r\n")
            yield from response.awrite("Location: /scripts\r\n")
            yield from response.awrite("Content-Type: text/html\r\n")
            yield from response.awrite("<html><head><title>Moved</title></head><body><h1>Moved</h1></body></html>\r\n")
        elif id and oper == 'del':
            # Get script from table
            scripts = db.scriptTable.public()
            for script in scripts:
                if script['id'] == id:
                   break
            
            # get filename
            filename = 'scripts/'+script['filename']

            # delete device
            import os

            _log.debug("Pages: Delete Script: "+filename)
            os.remove(filename)
            
            #gc.collect()
            #deleted, return to scripts page
            yield from response.awrite("HTTP/1.0 301 Moved Permanently\r\n")
            yield from response.awrite("Location: /scripts\r\n")
            yield from response.awrite("Content-Type: text/html\r\n")
            yield from response.awrite("<html><head><title>Moved</title></head><body><h1>Moved</h1></body></html>\r\n")
        elif oper == 'refresh':
            # refresh script
            _log.debug("Pages: refresh Script")
            
            gc.collect()
            #deleted, return to scripts page
            yield from response.awrite("HTTP/1.0 301 Moved Permanently\r\n")
            yield from response.awrite("Location: /scripts\r\n")
            yield from response.awrite("Content-Type: text/html\r\n")
            yield from response.awrite("<html><head><title>Moved</title></head><body><h1>Moved</h1></body></html>\r\n")
        elif oper == 'add':
            #New device
            _log.debug("Pages: Add script")
            
            info = {}
            info['name'] = _utils.get_upyeasy_name()
            info['copyright']=core.__copyright__
            info['holder']= core.__author__
            script = {}
            script['scriptname'] = ""
            script['content'] = ""
            script['size'] = 0
            script['operation'] = 'add'
            script['id'] = 0
            
            # menu settings
            menu = 7
            advanced = db.advancedTable.getrow()
            gc.collect()

            yield from picoweb.start_response(response)
            yield from app.render_template(response, "header.html",(info, menu,advanced))
            yield from app.render_template(response, "script_edit.html",(info,script))
            yield from app.render_template(response, "footer.html",(info,))

    elif request.method == 'POST':
        _log.debug("Pages: POST")
        parsed_qs = picoweb.utils.parse_qs(request.qs)
        # Get all form values in a dict
        yield from request.read_form_data()
        uform = _utils.get_form_values(request.form)

        if uform['filename']:
            #Create Script
            _log.debug("Pages: Create Script: {} ".format(uform['filename']))
            
            try:
                content = uform['content']
            except TypeError:
                content = ""
            
            # get filename
            filename = 'scripts/'+uform['filename']

            _log.debug("Pages: Script filename: "+filename)
            try:
                script_file = open(filename, 'w')
                script_file.write(content)
                script_file.close() 
            except TypeError:
                _log.debug("Pages: Exception getting script creation from data!")

            # reload all scripts
            _scripts.loadscripts()
                
            #return to devices page
            yield from response.awrite("HTTP/1.0 301 Moved Permanently\r\n")
            yield from response.awrite("Location: /scripts\r\n")
            yield from response.awrite("Content-Type: text/html\r\n")
            yield from response.awrite("<html><head><title>Moved</title></head><body><h1>Moved</h1></body></html>\r\n")

@app.route("/notifications", methods=['GET','POST'])
def notificationpage(request, response):
    if not auth_page(request, response): 
        #send to password page
        yield from response.awrite("HTTP/1.0 301 Moved Permanently\r\nLocation: /password\r\nContent-Type: text/html\r\n<html><head><title>Moved</title></head><body><h1>Moved</h1></body></html>\r\n")
        return

    #Edit notifications
    
    if request.method == 'GET':
        _log.debug("Pages: Display Notifications Page")

        info = {}
        info['name'] = _utils.get_upyeasy_name
        info['copyright']=core.__copyright__
        info['holder']= core.__author__

        
        # Get notifications
        notifications = db.notificationTable.public()

        # Get services
        services = db.serviceTable.public()
       
        # menu settings
        menu = 8
        advanced = db.advancedTable.getrow()
        gc.collect()

        yield from picoweb.start_response(response)
        yield from app.render_template(response, "header.html",(info, menu,advanced))
        yield from app.render_template(response, "notifications.html",(info,services,notifications))
        yield from app.render_template(response, "footer.html",(info,))

@app.route("/notification_setting", methods=['GET,POST'])
def notificationsettingpage(request, response):
    if not auth_page(request, response): 
        #send to password page
        yield from response.awrite("HTTP/1.0 301 Moved Permanently\r\nLocation: /password\r\nContent-Type: text/html\r\n<html><head><title>Moved</title></head><body><h1>Moved</h1></body></html>\r\n")
        return

    #Display notification settings page
    _log.debug("Pages: Entering notification Settings Page")
    if request.method == 'GET' and request.qs != "":
        _log.debug("Pages: GET")
        parsed_qs = picoweb.utils.parse_qs(request.qs)
        _log.debug('Parsed qs: '.join(list(parsed_qs)))
        qs_id = parsed_qs.get("id")
        _log.debug('Parsed id: '.join(qs_id))
        id = int(qs_id[0])
        _log.debug("Pages: id: %i",id)
        qs_oper = parsed_qs.get("oper")
        if qs_oper: 
            oper = qs_oper[0] 
            _log.debug("Pages: Oper: "+oper)
        else: oper = None
        
        if id > 0 and not oper:
            #Edit controller
            _log.debug("Pages: Edit notification: "+str(id))
            
            #connect to database
            _dbc.connect()
            
            info = {}
            info['name'] = _utils.get_upyeasy_name()
            info['copyright']=core.__copyright__
            info['holder']= core.__author__

            # Get services
            services = db.serviceTable.public()

            # Get correct notification
            notifications = db.notificationTable.public()
            for notification in notifications:
                if notification['id'] == id:
                   break

            # Get correct service
            services = db.serviceTable.public()
            for service in services:
                if service['id'] == notification['serviceid']:
                   break
                   
            _dbc.close()

            # menu settings
            menu = 8
            advanced = db.advancedTable.getrow()
            gc.collect()

            yield from picoweb.start_response(response)
            yield from app.render_template(response, "header.html",(info, menu, advanced))
            yield from app.render_template(response, service['template'],(info,services,notification,))
            yield from app.render_template(response, "footer.html",(info,))
        elif id > 0 and oper == 'del':
            # delete notification
            import os

            _log.debug("Pages: Delete notification: "+str(id))
            
            #connect to database
            _dbc.connect()
            
            # Get correct notification
            notifications = db.notificationTable.public()
            for notification in notifications:
                if notification['id'] == id:
                   break
            _log.debug("Pages: remove record file: "+db.notificationTable.fname(notification['timestamp']))
            os.remove(db.notificationTable.fname(notification['timestamp']))
            
            _dbc.close()
            
            #gc.collect()
            #deleted, return to controllers page
            yield from response.awrite("HTTP/1.0 301 Moved Permanently\r\n")
            yield from response.awrite("Location: /notifications\r\n")
            yield from response.awrite("Content-Type: text/html\r\n")
            yield from response.awrite("<html><head><title>Moved</title></head><body><h1>Moved</h1></body></html>\r\n")
        elif id == 0:
            #New notification
            _log.debug("Pages: New notification")
            
            #connect to database
            _dbc.connect()
            
            # Get services
            services = db.serviceTable.public()
            if services: service = services[0]
            else: 
                yield from response.awrite("HTTP/1.0 301 Moved Permanently\r\n")
                yield from response.awrite("Location: /notifications\r\n")
                yield from response.awrite("Content-Type: text/html\r\n")
                yield from response.awrite("<html><head><title>Moved</title></head><body><h1>Moved</h1></body></html>\r\n")
                return 

            _dbc.close()

            info={}
            info['name'] = _utils.get_upyeasy_name()
            info['copyright']=core.__copyright__
            info['holder']= core.__author__
            #get max notification id or default
            info['id'] = 0

            
            # Empty notification
            notification = db.notificationTable.__schema__
            notification['id'] = info ['id']
            
            # menu settings
            menu = 8
            advanced = db.advancedTable.getrow()
            gc.collect()

            yield from picoweb.start_response(response)
            yield from app.render_template(response, "header.html",(info, menu, advanced))
            yield from app.render_template(response, service['template'],(info,services,notification,))
            yield from app.render_template(response, "footer.html",(info,))

    elif request.method == 'POST' and request.qs != "":
        _log.debug("Pages: POST")
        parsed_qs = picoweb.utils.parse_qs(request.qs)
        _log.debug(''.join(list(parsed_qs)))
        id = int(''.join(parsed_qs.get("id")))
        _log.debug(str(id))
        qs_oper = parsed_qs.get("oper")
        if qs_oper: 
            oper = qs_oper[0] 
            _log.debug(oper)
        else: oper = None

        # Get all form values in a dict
        yield from request.read_form_data()
        uform = _utils.get_form_values(request.form)

        if uform['currentserviceid'] != uform['serviceid']:
            notificationchange = True
        else: notificationchange = False
        _log.debug('Current service id: %s', uform['currentserviceid'])
        _log.debug('New service id: %s', uform['serviceid'])

        if id > 0:
            #Update notification
            _log.debug("Pages: Update notification: "+str(id))
            
            if not notificationchange:
                # Same  service, update notification!
                _log.debug("Pages: Update notification: Same  service")
                #connect to database
                _dbc.connect()

                # Get correct notification
                notifications = db.notificationTable.public()
                for dbnotification in notifications:
                    if dbnotification['id'] == id:
                       break
                    
                # set form values
                notification = _utils.map_form2db(dbnotification, uform)

                # Verify mandatory fields!
                if notification['id'] != 0:
                    cid = db.notificationTable.update({"timestamp":notification['timestamp']},id=notification['id'],serviceid=notification['serviceid'],enable=notification['enable'])
                else:
                    _log.debug("Pages: Failed to create notification entry: not all fields are filled")
                
                _dbc.close()

                #return to notifications page
                yield from response.awrite("HTTP/1.0 301 Moved Permanently\r\n")
                yield from response.awrite("Location: /notifications\r\n")
                yield from response.awrite("Content-Type: text/html\r\n")
                yield from response.awrite("<html><head><title>Moved</title></head><body><h1>Moved</h1></body></html>\r\n")
            else:
                # Different  service, empty notification!
                _log.debug("Pages: Update notification: different service")
                
                #connect to database
                _dbc.connect()
                
                # Get correct notification
                notifications = db.notificationTable.public()
                for notification in notifications:
                    if notification['id'] == id:
                       break
                
                #get new plugin id
                pluginid = uform['pluginid']
                
                # Get list of plugins
                plugins = db.pluginTable.public()
                for plugin in plugins:
                    if plugin['id'] == plugini:
                       break
                
                # Get correct controller
                controllers=db.controllerTable.public()

                _dbc.close()

                info={}
                info['name'] = _utils.get_upyeasy_name()
                info['copyright']=core.__copyright__
                info['holder']= core.__author__
                info['id'] = 1

                # Get dx labels
                dx_label = _utils.get_dxlabels()
                #_log.debug("Pages: dx_label: "+"-".join(dx_label))
                
                # Get hardware config
                hardware = db.hardwareTable.getrow()

                # Empty notification
                notification = db.notificationTable.__schema__
                notification['id'] = info ['id']

                # menu settings
                menu = 8
                advanced = db.advancedTable.getrow()
                gc.collect()

                yield from picoweb.start_response(response)
                yield from app.render_template(response, "header.html",(info, menu, advanced,))
                yield from app.render_template(response, notification['template'],(info,controllers, plugins, notification, dx_label, hardware,))
                yield from app.render_template(response, "footer.html",(info,))
                
        elif id == 0:
            #Create notification
            _log.debug("Pages: Create notification")

            serviceid = uform['serviceid']
            _log.debug("Pages: service id: %s",serviceid)
            
            #serviceid creation/serviceid change
            if serviceid == 0 and not notificationchange:
                #empty: return to notifications page
                _log.debug("Pages: Empty new notification")
                yield from response.awrite("HTTP/1.0 301 Moved Permanently\r\n")
                yield from response.awrite("Location: /notifications\r\n")
                yield from response.awrite("Content-Type: text/html\r\n")
                yield from response.awrite("<html><head><title>Moved</title></head><body><h1>Moved</h1></body></html>\r\n")
            elif serviceid != 0 and notificationchange:
                #Plugin change
                _log.debug("Pages: Empty notification service change, new service id: %i",serviceid)
                
                #connect to database
                _dbc.connect()
                
                info = {}
                info['name'] = _utils.get_upyeasy_name()
                info['copyright']=core.__copyright__
                info['holder']= core.__author__
                # Get correct service
                services = db.serviceTable.public()
                for service in services:
                    if service['id'] == serviceid:
                       break
                       
                _dbc.close()

                # Empty notification
                notification = db.notificationTable.__schema__

                # menu settings
                menu = 8
                advanced = db.advancedTable.getrow()
                gc.collect()

                yield from picoweb.start_response(response)
                yield from app.render_template(response, "header.html",(info, menu, advanced))
                yield from app.render_template(response, service['template'],(info,services,notification,))
                yield from app.render_template(response, "footer.html",(info,))
            else:
                # Same  plugin, new notification!
                _log.debug("Pages: New notification: Same  plugin")
                #connect to database
                _dbc.connect()

                # Get correct notification max count
                notifications = db.notificationTable.public()
                cnt = 0
                for dbnotification in notifications:
                    if notification['id'] > cnt:
                       cnt = notification_org['id']
                _log.debug("Pages: notification max Count: %i",cnt)
                    
                # set form values
                notification = _utils.map_form2db(dbnotification, uform)
                
                # Verify mandatory fields!
                if serviceid != 0:
                    cid = db.notificationTable.create(id=cnt+1,serviceid=notification['serviceid'],enable=notification['enable'],custom1=notification['custom1'],custom2=notification['custom2'],custom3=notification['custom3'],custom4=notification['custom4'],custom5=notification['custom5'],custom6=notification['custom6'],custom7=notification['custom7'],custom8=notification['custom8'],custom9=notification['custom9'],custom10=notification['custom10'])
                else:
                    _log.debug("Pages: Failed to create notification entry: not all fields are filled")

                _dbc.close()

                #return to notifications page
                yield from response.awrite("HTTP/1.0 301 Moved Permanently\r\n")
                yield from response.awrite("Location: /notifications\r\n")
                yield from response.awrite("Content-Type: text/html\r\n")
                yield from response.awrite("<html><head><title>Moved</title></head><body><h1>Moved</h1></body></html>\r\n")

@app.route("/tools", methods=['GET', 'POST'])
def toolpage(request, response):
    if not auth_page(request, response): 
        #send to password page
        yield from response.awrite("HTTP/1.0 301 Moved Permanently\r\nLocation: /password\r\nContent-Type: text/html\r\n<html><head><title>Moved</title></head><body><h1>Moved</h1></body></html>\r\n")
        return

    _log.debug("Pages: Entering Tools Page")

    if request.method == 'GET':

        parsed_qs = picoweb.utils.parse_qs(request.qs)
        _log.debug('Parsed qs: '.join(list(parsed_qs)))
        qs_cmd = parsed_qs.get("ucmd")
        if qs_cmd: 
            cmd = qs_cmd[0] 
            _log.debug("Pages: cmd: "+cmd)
        else: cmd = None
        
        if not cmd:
            _log.debug("Pages: Display Tools Page")
            info = {}
            info['name'] = _utils.get_upyeasy_name()
            info['copyright']=core.__copyright__
            info['holder']= core.__author__
            info['id'] = 9
            if _utils.get_platform() == 'esp32' or _utils.get_platform() == 'esp8266':
                info['wifi'] = True
            else: info['wifi'] = False
            
            # menu settings
            menu = 9
            advanced = db.advancedTable.getrow()
            gc.collect()

            yield from picoweb.start_response(response)
            yield from app.render_template(response, "header.html",(info, menu, advanced))
            yield from app.render_template(response, "tools.html",(info,))
            yield from app.render_template(response, "footer.html",(info,))
        elif cmd == "reboot":
            _log.debug("Pages: Reboot command given")
            _hal.reboot()
        elif cmd == "log":
            _log.debug("Pages: Log command given")
            info = {}
            info['name'] = _utils.get_upyeasy_name()
            info['copyright']=core.__copyright__
            info['holder']= core.__author__
            info['id'] = 9

            logger  = {}
            logger['content'] = _log.readlog()
            
            # menu settings
            menu = 9
            advanced = db.advancedTable.getrow()
            gc.collect()

            yield from picoweb.start_response(response)
            yield from app.render_template(response, "header.html",(info, menu, advanced))
            yield from app.render_template(response, "log.html",(logger,))
            yield from app.render_template(response, "footer.html",(info,))
        elif cmd == "wifiscanner":
            _log.debug("Pages: wifiscanner command given")
            info = {}
            info['name'] = _utils.get_upyeasy_name()
            info['copyright']=core.__copyright__
            info['holder']= core.__author__
            info['id'] = 9

            wifilist = _hal.wifiscan()
            
            # menu settings
            menu = 9
            advanced = db.advancedTable.getrow()
            gc.collect()

            yield from picoweb.start_response(response)
            yield from app.render_template(response, "header.html",(info, menu, advanced))
            yield from app.render_template(response, "wifi.html",(wifilist,))
            yield from app.render_template(response, "footer.html",(info,))
        elif cmd == "i2cscanner":
            _log.debug("Pages: i2cscanner command given")
            info = {}
            info['name'] = _utils.get_upyeasy_name()
            info['copyright']=core.__copyright__
            info['holder']= core.__author__
            info['id'] = 9

            i2c_hw = _hal.get_i2c()
            if i2c_hw: i2clist = i2c_hw.scan()
            else: i2clist = []
            
            # menu settings
            menu = 9
            advanced = db.advancedTable.getrow()
            gc.collect()

            yield from picoweb.start_response(response)
            yield from app.render_template(response, "header.html",(info, menu, advanced))
            yield from app.render_template(response, "i2c.html",(i2clist,))
            yield from app.render_template(response, "footer.html",(info,))
        elif cmd == "savesettings":
            _log.debug("Pages: savesettings command given")
            info = {}
            info['name'] = _utils.get_upyeasy_name()
            info['copyright']=core.__copyright__
            info['holder']= core.__author__
            info['id'] = 9
            
            # totals config file backup data
            backupfilename = "upyeasy_settings.bak"
            backupfilesize = 0
            
            # Return to root!
            import os
            os.chdir(core.working_dir)
            
            # start html transfer
            yield from picoweb.start_response(response,content_type="text/plain\r\nContent-Disposition: attachment; filename=%s\r\n"%backupfilename)
            
            # get all config file names
            import uos 
            
            # get all config dirs
            try:
                dirs = sorted(uos.ilistdir('config'))
            except OSError as e:
               _log.debug("Pages: savesettings dir exception: "+repr(e))
               return False
            
            # get all config files
            for dir in dirs: 
                if dir[0] != '.' and dir[0] != '..':
                    fulldir = 'config/'+dir[0]
                    _log.debug("Pages: savesettings fulldir: "+fulldir)
                    try:
                        files = sorted(uos.ilistdir(fulldir))
                    except OSError as e:
                        _log.debug("Pages: savesettings file exception: "+repr(e))
                        return False
                    for file in files:
                        if file[0] != '.' and file[0] != '..':
                            fullfile = fulldir +'/'+ file[0]
                            gc.collect()
                            file_desc = open(fullfile, 'r')
                            content = ujson.dumps(file_desc.read())
                            file_desc.close()
                            filedata = fullfile+"\r\n"+content+"\r\n"
                            yield from response.awrite(filedata)
                            backupfilesize += len(filedata)
            
            # end file with filename and size
            filedata = "Backup Filename: "+backupfilename+"\r\nBackup File Size: "
            backupfilesize += len(filedata) + len(str(backupfilesize))
            filedata += str(backupfilesize)
            yield from response.awrite(filedata)
                            
        elif cmd == "loadsettings":
            _log.debug("Pages: loadsettings command given")
            info = {}
            info['name'] = _utils.get_upyeasy_name()
            info['copyright']=core.__copyright__
            info['holder']= core.__author__
            info['id'] = 9

            # menu settings
            menu = 9
            advanced = db.advancedTable.getrow()
            gc.collect()

            yield from picoweb.start_response(response)
            yield from app.render_template(response, "header.html",(info, menu, advanced))
            yield from app.render_template(response, "loadsettings.html",(info,))
            yield from app.render_template(response, "footer.html",(info,))
        else:
            #return to tools page
            yield from response.awrite("HTTP/1.0 301 Moved Permanently\r\n")
            yield from response.awrite("Location: /tools\r\n")
            yield from response.awrite("Content-Type: text/html\r\n")
            yield from response.awrite("<html><head><title>Moved</title></head><body><h1>Moved</h1></body></html>\r\n")
    elif request.method == 'POST':
        _log.debug("Pages: tools POST")

        # get data and size of return backup file
        size = int(request.headers[b"Content-Length"])
        data = yield from request.reader.read(size)
        # We're cutting off the boundary part
        size -= 214

        # Get all data in a string
        content = data.decode("utf-8").split("octet-stream")[1].split("------")[0].replace("\\","").strip().splitlines()
        
        # save all files
        for cnt in range(0, len(content), 2):
            # don't import backup file data
            if content[cnt][:16] != 'Backup Filename:':
                # don't import protocol/plugin data which are regenerated everytime upyeasy starts!
                if content[cnt][:15] != 'config/protocol' and content[cnt][:13] != 'config/plugin':
                    gc.collect()
                    _log.debug("Pages: Loadsettings: Loading Filename: "+content[cnt])
                    _log.debug("Pages: Loadsettings: Filename content: "+content[cnt+1][1:20]+"...")
                    try:
                        file_desc = open(content[cnt], 'w')
                        file_desc.write(content[cnt+1][1:-1])
                        file_desc.close() 
                    except TypeError:
                        _log.debug("Pages: Loadsettings: Exception writing settings file!")
                    _log.debug("Pages: Loadsettings: Settingsfile "+content[cnt]+" processed")
            else:
                _log.debug("Pages: Loadsettings: Loaded backupfile: "+content[cnt])
                _log.debug("Pages: Loadsettings: Loaded backupfilesize: "+content[cnt+1])
                _log.debug("Pages: Loadsettings: original backupfilesize: "+str(size))

        #return to tools page
        yield from response.awrite("HTTP/1.0 301 Moved Permanently\r\n")
        yield from response.awrite("Location: /tools\r\n")
        yield from response.awrite("Content-Type: text/html\r\n")
        yield from response.awrite("<html><head><title>Moved</title></head><body><h1>Moved</h1></body></html>\r\n")
        
@app.route("/files", methods=['GET','POST'])
def filespage(request, response):
    if not auth_page(request, response): 
        #send to password page
        yield from response.awrite("HTTP/1.0 301 Moved Permanently\r\nLocation: /password\r\nContent-Type: text/html\r\n<html><head><title>Moved</title></head><body><h1>Moved</h1></body></html>\r\n")
        return

    #Edit Config
    
    if request.method == 'GET':
        import os
        _log.debug("Pages: Display files Page")

        parsed_qs = picoweb.utils.parse_qs(request.qs)
        _log.debug('Parsed qs: '.join(list(parsed_qs)))
        qs_name = ""
        try:
            qs_name = parsed_qs.get("name")[0]
        except TypeError:
            pass
        _log.debug('Parsed name: '.join(qs_name))

        info = {}
        info['name'] = _utils.get_upyeasy_name()
        info['copyright']=core.__copyright__
        info['holder']= core.__author__
        info['id']=9
        
        # change dir if needed
        if qs_name: 
            try:
                _log.debug('Changing directory: '+qs_name)
                if qs_name != '..': os.chdir(qs_name)
                else: os.chdir('..')
            except OSError as e:
                _log.debug('Changing directory error: '+repr(e))
        
        # get all file names
        import uos
        try:
            files = sorted(uos.ilistdir())
        except OSError:
            files = []
            
        # display higher dir?
        fworking_dir = os.getcwd()
        if os.getcwd() != '/': fworking_dir+="/"
        if core.working_dir == fworking_dir: info['rootdir']='Y'
        else: info['rootdir']='N'

        # menu settings
        menu = 9
        advanced = db.advancedTable.getrow()
        gc.collect()

        yield from picoweb.start_response(response)
        yield from app.render_template(response, "header.html",(info, menu, advanced))
        yield from app.render_template(response, "files.html",(info,files))
        yield from app.render_template(response, "footer.html",(info,))

@app.route("/file_setting", methods=['GET,POST'])
def filesettingpage(request, response):
    if not auth_page(request, response): 
        #send to password page
        yield from response.awrite("HTTP/1.0 301 Moved Permanently\r\nLocation: /password\r\nContent-Type: text/html\r\n<html><head><title>Moved</title></head><body><h1>Moved</h1></body></html>\r\n")
        return

    #Display device settings page
    _log.debug("Pages: Entering file settings Page")
    if request.method == 'GET' and request.qs != "":
        _log.debug("Pages: GET")
        parsed_qs = picoweb.utils.parse_qs(request.qs)
        _log.debug('Parsed qs: '.join(list(parsed_qs)))
        try:
            qs_name = parsed_qs.get("name")[0]
        except TypeError:
            qs_name = ""
        _log.debug('Parsed name: '.join(qs_name))
        qs_oper = parsed_qs.get("oper")
        if qs_oper: 
            oper = qs_oper[0] 
            _log.debug("Pages: Oper: "+oper)
        else: oper = None
        
        if qs_name and oper == "edit":
            #Edit script
            _log.debug("Pages: Edit file: "+qs_name)
            
            info = {}
            info['name'] = _utils.get_upyeasy_name()
            info['copyright']=core.__copyright__
            info['holder']= core.__author__
            file = {}
            file['filename'] = qs_name
            filename = ''.join(qs_name)
            _log.debug("Pages: Filename: "+filename)
            file_desc = open(filename, 'r')
            file['content'] = file_desc.read()
            file_desc.close() 
            file['size'] = len(file['content'])
            file['operation'] = 'edit'

            # menu settings
            menu = 9
            advanced = db.advancedTable.getrow()
            gc.collect()

            yield from picoweb.start_response(response)
            yield from app.render_template(response, "header.html",(info, menu))
            yield from app.render_template(response, "file_edit.html",(info,file))
            yield from app.render_template(response, "footer.html",(info,))
            
        elif qs_name and oper == 'download':
            # download file
            _log.debug("Pages: download file: "+qs_name)

            file_desc = open(qs_name, 'r')
            content = file_desc.read()
            file_desc.close() 

            yield from picoweb.start_response(response,content_type="text/plain\r\nContent-Disposition: attachment; filename=%s\r\n"% qs_name)
            yield from response.awrite(content)

        elif qs_name and oper == 'del':
            # delete device
            import os
            qs_type = parsed_qs.get("ftype")[0]
            _log.debug("Pages: Delete file/dir: "+qs_type)

            if qs_type == 'file':
                _log.debug("Pages: Delete file: "+qs_name)
                os.remove(''.join(qs_name))
            elif qs_type == 'dir':
                _log.debug("Pages: Delete directory: "+qs_name)
                os.rmdir(''.join(qs_name))
            else: 
                _log.debug("Pages: Delete file error: "+qs_name)

            #gc.collect()
            #deleted, return to scripts page
            yield from response.awrite("HTTP/1.0 301 Moved Permanently\r\n")
            yield from response.awrite("Location: /files\r\n")
            yield from response.awrite("Content-Type: text/html\r\n")
            yield from response.awrite("<html><head><title>Moved</title></head><body><h1>Moved</h1></body></html>\r\n")

        elif oper == 'add':
            #New device
            _log.debug("Pages: Add file: "+qs_name)
            
            #Edit file
            _log.debug("Pages: Edit file: "+qs_name)
            
            info = {}
            info['name'] = _utils.get_upyeasy_name()
            info['copyright']=core.__copyright__
            info['holder']= core.__author__
            file = {}
            file['filetname'] = qs_name
            file['content'] = ""
            file['size'] = 0
            file['operation'] = 'add'
            
            # menu settings
            menu = 9
            advanced = db.advancedTable.getrow()
            gc.collect()

            yield from picoweb.start_response(response)
            yield from app.render_template(response, "header.html",(info, menu))
            yield from app.render_template(response, "file_edit.html",(info,file))
            yield from app.render_template(response, "footer.html",(info,))

    elif request.method == 'POST':
        _log.debug("Pages: Filesettings POST")
        # Get all form values in a dict
        yield from request.read_form_data()
        uform = _utils.get_form_values(request.form)

        try:
            qs_name = uform["filename"]
        except TypeError:
            qs_name = ""
        _log.debug('Parsed name: %s',qs_name)

        if qs_name:
            #Create Script
            _log.debug("Pages: Create file: "+qs_name)
            
            try:
                content = uform['content']
            except TypeError:
                content = ""
            
            filename = ''.join(qs_name)
            _log.debug("Pages: File name: "+filename)
            try:
                file_desc = open(filename, 'w')
                file_desc.write(content)
                file_desc.close() 
            except TypeError:
                _log.debug("Pages: Exception getting file creation form data!")

            #return to devices page
            yield from response.awrite("HTTP/1.0 301 Moved Permanently\r\n")
            yield from response.awrite("Location: /files\r\n")
            yield from response.awrite("Content-Type: text/html\r\n")
            yield from response.awrite("<html><head><title>Moved</title></head><body><h1>Moved</h1></body></html>\r\n")
        
@app.route("/advanced", methods=['GET, POST'])
def advancedpage(request, response):
    if not auth_page(request, response): 
        #send to password page
        yield from response.awrite("HTTP/1.0 301 Moved Permanently\r\nLocation: /password\r\nContent-Type: text/html\r\n<html><head><title>Moved</title></head><body><h1>Moved</h1></body></html>\r\n")
        return

    _log.debug("Pages: Entering Advanced Page")
    
    if request.method == 'GET':
        _log.debug("Pages: Display Advanced Page")
        info = {}
        info['name'] = _utils.get_upyeasy_name()
        info['copyright']=core.__copyright__
        info['holder']= core.__author__
        info['id'] = 10

        # menu settings
        menu = 10
        advanced = db.advancedTable.getrow()
        gc.collect()

        yield from picoweb.start_response(response)
        yield from app.render_template(response, "header.html",(info, menu, advanced))
        yield from app.render_template(response, "advanced.html",(info, advanced,))
        yield from app.render_template(response, "footer.html",(info,))

    elif request.method == 'POST':
         #Update Advanced
        _log.debug("Pages: Update Advanced")
        
        # Get all form values in a dict
        yield from request.read_form_data()
        uform = _utils.get_form_values(request.form)

        #connect to database
        _dbc.connect()

        #init ONLY!
        try:
            db.advancedTable.create_table()
        except OSError:
            pass

        #Get advanced record key
        dbadvanced = db.advancedTable.getrow()

        # get form values
        advanced = _utils.map_form2db(dbadvanced, uform)

        # new ntp server = run settime
        if advanced['ntphostname'] != dbadvanced['ntphostname']: _hal.settime()
        
        # Update advanced
        cid = db.advancedTable.update({"timestamp":advanced['timestamp']},scripts=advanced['scripts'],rules=advanced['rules'],notifications=advanced['notifications'],mqttretain=advanced['mqttretain'],messagedelay=advanced['messagedelay'],ntphostname=advanced['ntphostname'],ntptimezone=advanced['ntptimezone'],ntpdst=advanced['ntpdst'],sysloghostname=advanced['sysloghostname'],sysloglevel=advanced['sysloglevel'],serialloglevel=advanced['serialloglevel'],webloglevel=advanced['webloglevel'],webloglines=advanced['webloglines'],enablesdlog=advanced['enablesdlog'],sdloglevel=advanced['sdloglevel'],enableserial=advanced['enableserial'],serialbaudrate=advanced['serialbaudrate'],enablesync=advanced['enablesync'],syncport=advanced['syncport'],fixedipoctet=advanced['fixedipoctet'],wdi2caddress=advanced['wdi2caddress'],usessdp=advanced['usessdp'],connectfailure=advanced['connectfailure'],i2cstretchlimit=advanced['i2cstretchlimit'])
       
        _dbc.close()

        #Set right syslog hostname
        _log.changehost(core.__logname__+"-"+_utils.get_upyeasy_name(),advanced['sysloghostname'])

        #return to controllers page
        yield from response.awrite("HTTP/1.0 301 Moved Permanently\r\n")
        yield from response.awrite("Location: /advanced\r\n")
        yield from response.awrite("Content-Type: text/html\r\n")
        yield from response.awrite("<html><head><title>Moved</title></head><body><h1>Moved</h1></body></html>\r\n") 

@app.route("/dxpins", methods=['GET'])
def dxpinspage(request, response):
    if not auth_page(request, response): 
        #send to password page
        yield from response.awrite("HTTP/1.0 301 Moved Permanently\r\nLocation: /password\r\nContent-Type: text/html\r\n<html><head><title>Moved</title></head><body><h1>Moved</h1></body></html>\r\n")
        return

    _log.debug("Pages: Entering Dxpins Page")

    info = {}
    info['name'] = _utils.get_upyeasy_name()
    info['copyright']=core.__copyright__
    info['holder']= core.__author__
    info['id'] = 9

    # Get dxpin config
    dxpin = db.dxpinTable.getrow()

    # Get hardware config
    hardware = db.hardwareTable.getrow()
    dx_label = _utils.get_dxlabels()
    
    # menu settings
    menu = 9
    advanced = db.advancedTable.getrow()
    gc.collect()

    yield from picoweb.start_response(response)
    yield from app.render_template(response, "header.html",(info, menu, advanced))
    yield from app.render_template(response, "dxpins.html",(info, dxpin, hardware,dx_label))
    yield from app.render_template(response, "footer.html",(info,))
 
@app.route("/info", methods=['GET'])
def infopage(request, response):
    if not auth_page(request, response): 
        #send to password page
        yield from response.awrite("HTTP/1.0 301 Moved Permanently\r\nLocation: /password\r\nContent-Type: text/html\r\n<html><head><title>Moved</title></head><body><h1>Moved</h1></body></html>\r\n")
        return

    _log.debug("Pages: Entering info Page")

    info = {}
    info['name'] = _utils.get_upyeasy_name()
    info['copyright']=core.__copyright__
    info['holder']= core.__author__
    info['unit'] = _utils.get_unit_nr()
    info['version'] = core.__version__
    info['buildstatus']= core.__status__
    info['buildversion']= core.__build__
    info['dbversion']= _utils.get_dbversion()
    info["micropython"] = _hal.python()
    info["board"] = _hal.board()
    import machine
    if hasattr(machine,'unique_id'): 
        try:
            info['unique'] = str(machine.unique_id(), 'utf8')
        except UnicodeError as e:
            _log.debug("Pages: Entering info Page unicode machine id error: "+repr(e))
            info['unique'] = str(machine.unique_id())
    else: info['unique'] = '-'
    #if hasattr(machine,'freq'): info['freq'] = str(machine.freq())
    info['freq'] = '-'
    info['time'] = _hal.get_time()
    info['platform'] = _utils.get_platform()
    info['uptime'] = _utils.get_uptime()
    info['free'] = _utils.get_mem_free()
    info['total'] = _utils.get_mem_total()
    info['stack'] = _utils.get_stack_current()
    info['peak'] = _utils.get_mem_peak ()
    info['current'] = _utils.get_mem_current ()
    import micropython
    info['memorymap'] = micropython.mem_info(1)
    info['ip'] = _hal.get_ip_address()    
    info['gateway'] = _hal.get_ip_gw()    
    info['subnet'] = _hal.get_ip_netmask('eth0')    
    info['dns'] = _hal.get_ip_dns('eth0')    

    # menu settings
    menu = 9
    advanced = db.advancedTable.getrow()
    gc.collect()

    yield from picoweb.start_response(response)
    yield from app.render_template(response, "header.html",(info, menu, advanced))
    yield from app.render_template(response, "info.html",(info,))
    yield from app.render_template(response, "footer.html",(info,))
         