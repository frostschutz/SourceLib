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
from twisted.internet import reactor, defer

US_EAST_COAST = 0x00
US_WEST_COAST = 0x01
SOUTH_AMERICA = 0x02
EUROPE = 0x03
ASIA = 0x04
AUSTRALIA = 0x05
MIDDLE_EAST = 0x06
AFRICA = 0x07
WORLD = 0xFF

class MasterQueryProtocol(DatagramProtocol):
    def __init__(self, master=('69.28.140.247',27011), region=WORLD, filter={}, retries=10, timeout=1):
        # settings
        self.master = master
        self.region = region
        self.filter = filter
        self.retries = retries
        self.timeout = timeout

        # state
        self.call = False
        self.request = False
        self.response = []

    def startProtocol(self):
        self.transport.connect(self.master)
        self.sendRequest(('0.0.0.0',0))

    def datagramReceived(self, data, addr):
        # ignore packets that do not come from our master
        if addr != self.master:
            return

        print "received %r from %s:%d" % (data, host, port)

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

        if ips[-1] != self.nextip:
            self.nextip = ips[-1]

        if self.nextip == ('0.0.0.0', 0):
            self.retry.cancel()

        else:
            self.requestIp(False)

    def sendRequest(self, addr):


    def requestIp(self, later):
        if self.nextip:
            print "requesting", later, self.nextip
            self.transport.write(struct.pack('B', 0x31)+struct.pack('B', 0xFF)+self.nextip[0]+":"+str(self.nextip[1])+"\x00"+"\x00")

        if later or not self.retry:
            self.retry = reactor.callLater(0.1, self.requestIp, True)

        elif self.retry.active():
            self.retry.reset(0.1)

if __name__ == "__main__":
    from twisted.internet import reactor
    reactor.listenUDP(0, MasterQueryProtocol())
    reactor.run()
