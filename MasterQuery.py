#!/usr/bin/python
# -*- coding: utf-8 -*-

#------------------------------------------------------------------------------
# MasterQuery - Python class for querying info from Source Master Servers
# Copyright (c) 2010 Andreas Klauer <Andreas.Klauer@metamorpher.de>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#------------------------------------------------------------------------------

"""http://developer.valvesoftware.com/wiki/Master_Server_Query_Protocol"""

from twisted.internet.protocol import DatagramProtocol
import struct

class MasterQuery(DatagramProtocol):
    def startProtocol(self):
        self.transport.connect('69.28.140.247', 27011)
        self.transport.write(struct.pack('B', 0x31)+struct.pack('B', 0xFF)+"0.0.0.0:0\x00"+"\x00")

    def datagramReceived(self, data, (host, port)):
        ips = []

        if data.startswith('\xff\xff\xff\xff\x66\x0a'):
            data = data[6:]

            while len(data):
                (ip, port, data) = (data[0:4], data[4:6], data[6:])

                ip = ".".join(map(str, struct.unpack('BBBB', ip)))
                port = struct.unpack('!H', port)[0]
                ips.append((ip,port))

        # get the next batch of ips
        print ips

        if ips[-1] != ('0.0.0.0', 0):
            print "requesting", ips[-1]
            self.transport.write(struct.pack('B', 0x31)+struct.pack('B', 0xFF)+ips[-1][0]+":"+str(ips[-1][1])+"\x00"+"\x00")

            # this doesn't work too well - the server simply does not always send an answer back
            # unreliable UDP protocol, so we need a timeout & re-request facility here...

if __name__ == "__main__":
    from twisted.internet import reactor
    reactor.listenUDP(0, MasterQuery())
    reactor.run()
