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

    print('Starting uPyEasy Webclient test...')
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
    
    # now use usocket as usual
    import usocket as socket
    addr = socket.getaddrinfo('www.micropython.org', 80)[0][-1]
    s = socket.socket()
    #s.setblocking(False)
    s.connect(addr)
    s.send(b'GET / HTTP/1.1\r\nHost: www.micropython.org\r\n\r\n')
    data = s.recv(10000)
    print(data)
    s.close()

main() # Press Ctrl-C to stop web server