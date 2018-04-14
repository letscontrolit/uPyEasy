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

try:
    import uio as io
except ImportError:
    import io

class Sink :
    _logbuffer = None
    _logbuffersize = 0
    _logbufferlinecnt = 0

    def __init__(self, config) :
        self._logbuffersize = config['buffersize']
        self._logbuffer = io.StringIO()

    def log(self, message) :
        if self._logbufferlinecnt > self._logbuffersize:
            #Delete oldest entry
            buffer = self._logbuffer.getvalue()
            self._logbuffer.close()
            old, new = buffer.split("<BR>",1)
            
            self._logbuffer = io.StringIO(new)
            self._logbuffer.seek(len(new))
            self._logbufferlinecnt -= 1
        self._logbuffer.write("{} [{}] {}: {}<BR>".format(
            message['datetime'], 
            message['level'], 
            message['name'], 
            message['message'])
        )
        self._logbufferlinecnt += 1

    def read(self) :
        return self._logbuffer.getvalue()
