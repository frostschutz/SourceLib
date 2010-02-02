#!/usr/bin/python
# -*- coding: utf-8 -*-

#------------------------------------------------------------------------------
# SourceRcon - Python class for executing commands on Source Dedicated Servers
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

"""http://developer.valvesoftware.com/wiki/Source_RCON_Protocol"""

import socket, struct
import StringIO

SERVERDATA_AUTH = 3
SERVERDATA_AUTH_RESPONSE = 2

SERVERDATA_EXECCOMMAND = 2
SERVERDATA_RESPONSE_VALUE = 0

class SourceRconRequest(object):
    def __init__(self, id=0, type=0, string=''):
        self.id = 0
        self.type = 0
        self.string = ''

    def send(self, socket):
        data = struct.pack('<l', self.id) + struct.pack('<l', self.type) + self.string + '\x00\x00'
        socket.send(struct.pack('<l', len(data)) + data)

class SourceRconResponse(object):
    pass

class SourceRcon(object):
    def __init__(self, host, port=27015, password='', timeout=1.0):
        self.host = host
        self.port = port
        self.password = password
        self.timeout = timeout
        self.tcp = False
        self.requestid = 0

    def disconnect(self):
        if self.tcp:
            self.tcp.close()
            self.tcp = False

    def connect(self):
        self.disconnect()
        self.tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp.settimeout(self.timeout)
        self.tcp.connect((self.host, self.port))
        self.auth()

    def auth(self):
        self.requestid += 1
        packet = SourceRconRequest(SERVERDATA_AUTH, self.password)

        packet.setId(self.make_requestid())
        packet.setType(SERVERDATA_AUTH)
        packet.setString(self.password)

        print repr(packet.getvalue())
        self.tcp.send(packet.getvalue())
        response = self.tcp.recv(8192)
        print repr(response)

server = SourceRcon('intermud.de', password='chwanzuslongus')

server.connect()
