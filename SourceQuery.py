#!/usr/bin/python
# -*- coding: utf-8 -*-

#------------------------------------------------------------------------------
# SourceQuery - Python class for talking to Source Dedicated Servers
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

import socket, struct, time

PACKETSIZE = 1400
MAXSPLITSIZE = 1248
MINSPLITSIZE = 564
WHOLE = struct.pack("<l", -1)
SPLIT = struct.pack("<l", -2)

A2A_PING = 'i'
A2A_PING_REPLY = 'j'

class SourceQueryError(Exception): pass

class SourceQuery(object):
    """http://developer.valvesoftware.com/wiki/Server_Queries"""

    def __init__(self, host, port=27015, timeout=1.0):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.socket = False
        self.connected = False
        self.challenge = False
        self.sendid = 0
        self.recvid = 0

    def connect(self):
        if not self.connected:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.settimeout(self.timeout)
            self.socket.connect((self.host, self.port))
            self.connected = True
            self.challenge = False

    def disconnect(self):
        if self.connected:
            self.socket.close()
            self.socket = False
            self.connected = False

    def send(self, message, splitsize=MAXSPLITSIZE):
        # prepare the message
        data = WHOLE+message

        # check if we have to split this packet
        splitsize = min(splitsize, MAXSPLITSIZE)
        splitsize = max(splitsize, MINSPLITSIZE)
        total = len(message) / splitsize
        if len(message) % splitsize:
            total += 1

        if total == 1:
            self.socket.send(data)

        #
        else:
            print "fooogfofo"
            self.sendid += 1
            for x in xrange(total):
                header = SPLIT + struct.pack("<l", self.sendid) + struct.pack("<b", total) + struct.pack("<b", x) + struct.pack("<h", splitsize)
                self.socket.send(header+data[:splitsize])
                data = data[splitsize:]

    def receive(self):
        chunk = self.socket.recv(PACKETSIZE)

        if chunk.startswith(WHOLE):
            return chunk[len(WHOLE):]

    def communicate(self, message):
        # In theory we should split the message here if it's too long.
        # In practice we don't issue queries longer than 1400 bytes,
        # so we can always send the whole message.
        self.send(message, 16)

        # However, the reply we receive may be split.
        chunk = self.socket.recv(1400)
        if chunk.startswith(WHOLE):
            return chunk[len(WHOLE):]

    def ping(self):
        ping = time.time()
        reply = self.communicate(A2A_PING)
        print repr(reply)
        pong = time.time()
        return pong - ping

    def info(self):
        reply = self.communicate("TSource Engine Query")
        print repr(reply)

server = SourceQuery('intermud.de')

server.connect()
server.info()
