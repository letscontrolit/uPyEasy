#
# Copyright (c) dushin.net  All Rights Reserved
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of dushin.net nor the
#      names of its contributors may be used to endorse or promote products
#      derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY dushin.net ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL dushin.net BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

import usyslog
import ulog

# Facility constants
F_KERN = const(0)
F_USER = const(1)
F_MAIL = const(2)
F_DAEMON = const(3)
F_AUTH = const(4)
F_SYSLOG = const(5)
F_LPR = const(6)
F_NEWS = const(7)
F_UUCP = const(8)
F_CRON = const(9)
F_AUTHPRIV = const(10)
F_FTP = const(11)
F_NTP = const(12)
F_AUDIT = const(13)
F_ALERT = const(14)
F_CLOCK = const(15)
F_LOCAL0 = const(16)
F_LOCAL1 = const(17)
F_LOCAL2 = const(18)
F_LOCAL3 = const(19)
F_LOCAL4 = const(20)
F_LOCAL5 = const(21)
F_LOCAL6 = const(22)
F_LOCAL7 = const(23)

class Sink :
    
    def __init__(self, config, facility=F_DAEMON) :
        host = config['host']
        port = config['port']
        ## TODO add support for the facility
        self._client = usyslog.UDPClient(host, port, facility)

    def log(self, message) :
        level = message['level']
        text = "{} {}".format(
            message['name'], 
            #message['level'], 
            message['message']
        )
        if level == ulog.Log.DEBUG :
            self._client.debug(text)
        elif level == ulog.Log.INFO :
            self._client.info(text)
        elif level == ulog.Log.WARNING :
            self._client.warning(text)
        elif level == ulog.Log.ERROR :
            self._client.error(text)
        else :
            raise(Exception("Error: Unknown level: {}".format(level)))

