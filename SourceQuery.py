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

"""http://developer.valvesoftware.com/wiki/Server_Queries"""

import socket, struct, time
import StringIO

class SourceQueryPacket(StringIO.StringIO):
    # putting and getting values
    def putByte(self, val):
        """Put a unsigned 8bit value into the packet."""
        self.write(struct.pack('<B', val))

    def getByte(self):
        """Get a unsigned 8bit value from the packet."""
        return struct.unpack('<B', self.read(1))[0]

    def putShort(self, val):
        """Put a signed 16bit value into the packet."""
        self.write(struct.pack('<h', val))

    def getShort(self):
        """Get a signed 16bit value from the packet."""
        return struct.unpack('<h', self.read(2))[0]

    def putLong(self, val):
        """Put a signed 32bit value into the packet."""
        self.write(struct.pack('<l', val))

    def getLong(self):
        """Get a signed 32bit value from the packet."""
        return struct.unpack('<l', self.read(4))[0]

    def putFloat(self, val):
        """Put a floating point value into the packet."""
        self.write(struct.pack('<f', val))

    def getFloat(self):
        """Get a floating point value from the packet."""
        return struct.unpack('<f', self.read(4))[0]

    def putString(self, val):
        """Put a variable length string into the packet."""
        self.write(val + '\x00')

    def getString(self):
        """Get a variable length string from the packet."""
        val = self.getvalue()
        start = self.tell()
        end = val.index('\0', start)
        val = val[start:end]
        self.seek(end+1)
        return val

class SourceQuery(object):
    def __init__(self, host, port=27015, timeout=1.0):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.udp = False

    def disconnect(self):
        if self.udp:
            self.udp.close()
            self.udp = False

    def connect(self):
        self.disconnect()
        self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp.settimeout(self.timeout)
        self.udp.connect((self.host, self.port))

    def ping(self):
        packet = SourceQueryPacket()
        packet.putLong(-1)
        packet.putByte(0x69)
        self.connect()
        self.udp.send(packet.getvalue())
        packet = SourceQueryPacket(self.udp.recv(1400))
        print repr([packet.getLong(),packet.getByte(),packet.getString()])

    def info(self):
        packet = SourceQueryPacket()
        packet.putLong(-1)
        packet.putByte(ord('T'))
        packet.putString("Source Engine Query")
        self.connect()
        self.udp.send(packet.getvalue())
        packet = SourceQueryPacket(self.udp.recv(1400))
        print repr([packet.getLong(),packet.getByte(),packet.getByte(),packet.getString(),packet.getString(),packet.getString(),packet.getString(),packet.getShort(),packet.getByte(),packet.getByte(),packet.getByte(),packet.getByte(),packet.getByte(),packet.getByte(),packet.getByte(),packet.getString(),packet.getByte(),packet.getShort(),packet.getString()])

server = SourceQuery('intermud.de')
server.ping()
server.info()
