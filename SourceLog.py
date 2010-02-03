#!/usr/bin/python
# -*- coding: utf-8 -*-

#------------------------------------------------------------------------------
# SourceLog - Python class for parsing logs of Source Dedicated Servers
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

# TODO:  Support games other than Team Fortress 2

"""http://developer.valvesoftware.com/wiki/HL_Log_Standard"""

import socket, asyncore

PACKETSIZE=1400

class SourceLogParser(object):
    def parse(self, line):
        line = line.strip('\x00\xff\r\n\t ')
        print "parse", repr(line)

    def parse_file(self, filename):
        f = open(filename, 'r')

        for line in f:
            self.parse(line)

class SourceLogListenerError(Exception):
    pass

class SourceLogListener(asyncore.dispatcher):
    def __init__(self, local, remote, parser)
        asyncore.dispatcher.__init__(self)
        self.parser = parser
        self.create_socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.bind(local)
        self.connect(remote)

    def handle_connect(self):
        print "handle_connect"
        pass

    def handle_close(self):
        print "handle_close"
        self.close()

    def handle_read(self):
        print "handle_read"
        data = self.recv(PACKETSIZE)

        if data.startswith('\xff\xff\xff\xff') and data.endswith('\n\x00'):
            self.parser.parse(data)

        else:
            print "invalid packet", repr(data)
            raise SourceLogListenerError("Received invalid packet.")

    def writable(self):
        print "writable"
        return False

    def handle_write(self):
        print "handle_write"
        pass
