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

import re
import socket
import asyncore

PACKETSIZE=1400

retype = re.compile('^(?P<type>RL|L) (?P<rest>.*)$', re.U)
redate = re.compile('^(?P<day>[0-9]{2})/(?P<month>[0-9]{2})/(?P<year>[0-9]{4}) - (?P<hour>[0-9]{2}):(?P<minute>[0-9]{2}):(?P<second>[0-9]{2}): (?P<rest>.*)$', re.U)
reproperty = re.compile('^(?P<rest>.*) \((?P<key>[^() ]+) "(?P<value>[^"]*)"\)$', re.U)

class SourceLogParser(object):
    def __init__(self):
        self.property = False
        self.remote = False
        self.date = False

    def parse(self, line):
        line = line.strip('\x00\xff\r\n\t ')
        print "parse", repr(line)

        typematch = retype.match(line)

        if not typematch:
            print "fail type"
            return

        if typematch.group('type') == 'RL':
            self.remote = True
        else:
            self.remote = False

        datematch = redate.match(typematch.group('rest'))

        if not datematch:
            print "fail date"
            return

        self.date = map(int, datematch.group('day', 'month', 'year', 'hour', 'minute', 'second'))

        line = datematch.group('rest')

        self.property = {}

        while propertymatch = reproperty.match(line):
            line = propertymatch.group('rest')
            self.property[propertymatch.group('key')] = propertymatch.group('value')

        print "parse", repr(self.remote), repr(self.date), repr(self.property), line

    def parse_file(self, filename):
        f = open(filename, 'r')

        for line in f:
            self.parse(line)

class SourceLogListenerError(Exception):
    pass

class SourceLogListener(asyncore.dispatcher):
    def __init__(self, local, remote, parser):
        asyncore.dispatcher.__init__(self)
        self.parser = parser
        self.create_socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.bind(local)
        self.connect(remote)

    def handle_connect(self):
        pass

    def handle_close(self):
        self.close()

    def handle_read(self):
        data = self.recv(PACKETSIZE)

        if data.startswith('\xff\xff\xff\xff') and data.endswith('\n\x00'):
            self.parser.parse(data)

        else:
            print "invalid packet", repr(data)
            raise SourceLogListenerError("Received invalid packet.")

    def writable(self):
        return False

    def handle_write(self):
        pass
