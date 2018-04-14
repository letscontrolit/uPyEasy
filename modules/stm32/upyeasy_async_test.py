import picoweb, uasyncio as asyncio

CONTENT = """\
<html>
  <head>
  </head>
  <body>
    <p>Hello #%d from uPyEasy!</p>
  </body>
</html>
"""

app = picoweb.WebApp(__name__)

@app.route("/")
def index(req, resp):
    yield from picoweb.start_response(resp)
    yield from resp.awrite(CONTENT)

class plugins(object):
    def __init__(self) :
        print("init")
        
    async def asyncdevices(self):
        print("async")

import network,pyb
nic = network.WIZNET5K(pyb.SPI(1), pyb.Pin.board.A3, pyb.Pin.board.A4)
while not nic.isconnected():
    pass
nic.active(1)
nic.ifconfig(('192.168.178.100', '255.255.255.0', '192.168.178.1', '192.168.178.1'))

loop = asyncio.get_event_loop()
_plugins = plugins()
loop.create_task(_plugins.asyncdevices())
app.run(host="0.0.0.0", port=80,debug=False)
