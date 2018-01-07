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
    import network as wifi
    # AP mode
    nic = wifi.WLAN(wifi.STA_IF)
    nic.active(True)

    print('Starting uPyEasy Webserver test...')
    # No ssid set yet, let's connect to the strongest unencrypted wifi ap possible
    wlan_list = nic.scan()
    # parse list, find the strongest open network
    strength = -500
    wlan_ap = None
    for wlan in wlan_list:
        print('SSID: ',str(wlan[0], 'utf8'),' Channel: ',str(wlan[2]), 'Strength: ', str(wlan[3]), ' Security type: ', str(wlan[4]) )
        if wlan[3] > strength and wlan[4] == 0:
            strength = wlan[3]
            wlan_ap = str(wlan[0], 'utf8')
    if wlan_ap == None:
        return False
    else:
        print("Trying to connect to AP: ", wlan_ap)
        #Activate station
        if not nic.isconnected():
            nic.connect(wlan_ap)
            while not nic.isconnected():
                pass
    ip_address_v4 = nic.ifconfig()[0]
    
    s = socket.socket()
    ai = socket.getaddrinfo(ip_address_v4, 80)
    print("Bind address info:", ai)
    addr = ai[0][-1]

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