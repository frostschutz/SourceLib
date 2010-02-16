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

# --- Imports: ---

from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor, defer
import struct

# --- Constants: ---

QUERY=0x31
REPLY='\xff\xff\xff\xff\x66\x0a'

US_EAST = 0x00
US_WEST = 0x01
SOUTH_AMERICA = 0x02
EUROPE = 0x03
ASIA = 0x04
AUSTRALIA = 0x05
MIDDLE_EAST = 0x06
AFRICA = 0x07
WORLD = 0xFF

# --- Twisted Protocol: ---

class MasterQueryProtocol(DatagramProtocol):
    # Init:
    def __init__(self, master, region=WORLD, filter={}, retries=10, timeout=1, deferred=None):
        # settings
        self.master = master
        self.region = region
        self.filter = filter
        self.timeout = timeout
        self.deferred = deferred

        # state
        self.retries = retries
        self.result = []
        self.callout = False
        self.done = False

    # Helpers:
    def success(self):
        self.done = True

        (d, self.deferred) = (self.deferred, None)

        if self.transport:
            self.transport.stopListening()

        if self.callout and self.callout.active():
            self.callout.cancel()

        if d:
            d.callback(self.result)

    def failure(self):
        self.done = True

        (d, self.deferred) = (self.deferred, None)

        if self.transport:
            self.transport.stopListening()

        if self.callout and self.callout.active():
            self.callout.cancel()

        if d:
            d.errback(Exception())

    def getFilterStr(self):
        result = ''

        for (key,value) in self.filter.iteritems():
            if value is True:
                result += '\\%s\\1' % (key,)

            elif isinstance(value, list) or isinstance(value, tuple):
                for e in value:
                    result += '\\%s\\%s' % (key,str(e))

            else:
                result += '\\%s\\%s' % (key,str(value))

        return result

    def sendRequest(self):
        # retry logic
        if not self.callout or not self.callout.active():
            self.callout = reactor.callLater(self.timeout, self.retryRequest)

        else:
            self.callout.reset(self.timeout)

        # send the last ip or 0.0.0.0:0 in the request
        if not len(self.result):
            addr = ('0.0.0.0', 0)
        else:
            addr = self.result[-1]

        # build the message
        addrstr = "%s:%d" % addr
        filterstr = self.getFilterStr()
        message = struct.pack('BB', QUERY, self.region)
        message = "%s%s\x00%s\x00" % (message, addrstr, filterstr)

        # send the message
        self.transport.write(message)

    def retryRequest(self):
        if not self.retries > 0:
            if not self.done:
                self.failure()
            return

        self.retries -= 1

        self.sendRequest()

    # Protocol:
    def startProtocol(self):
        self.transport.connect(self.master[0], self.master[1])
        self.sendRequest()

    def stopProtocol(self):
        if not self.done:
            self.failure()

    def connectionRefused(self):
        if not self.done:
            self.failure()

    def datagramReceived(self, data, addr):
        # ignore packets that do not come from our master
        # this shouldn't happen anyway but you never know
        if addr != self.master:
            return

        # ignore packets that do not have the correct header
        if not data.startswith(REPLY):
            return

        data = data[len(REPLY):]

        before = len(self.result)

        # add all new ips from this batch
        while len(data):
            (ip, port, data) = (data[0:4], data[4:6], data[6:])
            port = struct.unpack('!H', port)[0]
            ip = ".".join(map(str, struct.unpack('BBBB', ip)))
            server = (ip, port)

            # special case: ip is the terminator
            if server == ('0.0.0.0', 0):
                if not self.done:
                    self.success()
                return

            if not server in self.result:
                self.result.append(server)
                self.serverReceived(server)

        # request the next batch
        if len(self.result) > before:
            self.sendRequest()

    # Callbacks:
    def serverReceived(self, server):
        """This callback is called for every server we find."""
        pass

# --- Synchronous Interface: ---

class MasterQuery(object):
    # Init:
    def __init__(self, master, retries=10, timeout=1):
        self.master = master
        self.retries = retries
        self.timeout = timeout
        self.result = None

    # Callbacks:
    def success(self, servers):
        self.result = servers
        reactor.stop()

    def fail(self, e):
        self.result = None
        reactor.stop()
        return e

    # Query:
    def query(self, region=WORLD, filter={}):
        self.result = None
        d = defer.Deferred()
        d.addCallback(self.success)
        d.addErrback(self.fail)
        protocol = MasterQueryProtocol(self.master, region, filter, deferred=d)
        reactor.listenUDP(0, protocol)
        reactor.run()
        r = self.result
        self.result = None
        return r

# --- Main program: ---

if __name__ == "__main__":
    # TODO: command line parameters
    print MasterQuery(('69.28.140.247',27011)).query()
