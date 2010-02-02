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
    def __init__(self, reqid=0, cmd=0, message=''):
        self.reqid = reqid
        self.cmd = cmd
        self.message = message

    def send(self, socket):
        data = struct.pack('<l', self.reqid) + struct.pack('<l', self.cmd) + self.message + '\x00\x00'
        socket.send(struct.pack('<l', len(data)) + data)

class SourceRconResponseError(Exception): pass

class SourceRconResponse(StringIO.StringIO):
    def receive(self, socket, reqid):
        print "receive", "socket", socket, "reqid", reqid

        # fetch all incoming data
        while 1:
            try:
                data = socket.recv(1024)
                self.write(data)
            except:
                self.seek(0)
                break

        result = ''
        length = self.read(4)

        while length:
            length = struct.unpack('<l', length)[0]
            (requestid, cmd) = struct.unpack('<2l', self.read(8))
            message = self.read(length-8)
            message = message[:message.index('\x00')]

            lengths = map(len, message.split("\n"))

            print min(lengths), max(lengths)

            if requestid != reqid:
                return False

            if cmd == SERVERDATA_AUTH_RESPONSE:
                return True

            if cmd == SERVERDATA_RESPONSE_VALUE:
                result += message

            else:
                return False

            length = self.read(4)


        return result

class SourceRcon(object):
    def __init__(self, host, port=27015, password='', timeout=1.0):
        self.host = host
        self.port = port
        self.password = password
        self.timeout = timeout
        self.tcp = False
        self.authed = False
        self.reqid = 0

    def disconnect(self):
        if self.tcp:
            self.tcp.close()
            self.tcp = False
            self.auth = False

    def connect(self):
        self.disconnect()
        self.tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp.settimeout(self.timeout)
        self.tcp.connect((self.host, self.port))
        self.auth()

    def auth(self):
        self.reqid += 1
        packet = SourceRconRequest(self.reqid,
                                   SERVERDATA_AUTH,
                                   self.password)
        packet.send(self.tcp)

        response = SourceRconResponse()

        if response.receive(self.tcp, self.reqid) == True:
            self.authed = True
        else:
            self.disconnect()

    def rcon(self, command):
        self.connect()

        self.reqid += 1

        packet = SourceRconRequest(self.reqid,
                                   SERVERDATA_EXECCOMMAND,
                                   command)
        packet.send(self.tcp)

        response = SourceRconResponse()

        return response.receive(self.tcp, self.reqid)

server = SourceRcon('intermud.de', password='chwanzuslongus')

server.rcon("cvarlist")
