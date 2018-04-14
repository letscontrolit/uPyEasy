import socket
from machine import Pin

CONTENT = """\
HTTP/1.0 200 OK
Content-Type: text/html

<html>
  <head>
  </head>
  <body>
    <p>Hello #%d from uPyEasy!</p>
  </body>
</html>
"""

def main():
    import network,pyb
    nic = network.WIZNET5K(pyb.SPI(1), pyb.Pin.board.A3, pyb.Pin.board.A4)
    while not nic.isconnected():
        pass
    nic.active(1)
    nic.ifconfig(('192.168.178.135', '255.255.255.0', '192.168.178.1', '192.168.178.1'))
    ip_address_v4 = nic.ifconfig()[0]
    
    s = socket.socket()
    ai = socket.getaddrinfo(ip_address_v4, 80)
    print("Bind address info:", ai)
    addr = ai[0][-1]
    print("IP Address: ",addr)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(5)
    print("Listening, connect your browser to http://<this_host>:80/")

    counter = 0
    while True:
        sock, addr = s.accept()
        #s.setblocking(False)
        print("Client address:", addr)
        stream = sock.makefile("rwb")
        req = stream.readline().decode("ascii")
        method, path, protocol = req.split(" ")
        print("Got", method, "request for", path)
        while True:
            h = stream.readline().decode("ascii").strip()
            if h == "":
                break
            print("Got HTTP header:", h)
        stream.write((CONTENT % counter).encode("ascii"))
        stream.close()
        sock.close()
        counter += 1
        print()

main() # Press Ctrl-C to stop web server