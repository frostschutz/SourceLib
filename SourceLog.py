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

# replayer breaks most easily because the log doesn't escape player names.
# There is nothing we can do about malicious players, but we are restrictive
# anyway in order to avoid random breakage when someone uses "<> in a name.
replayerpattern = '(?P<name>.*?)<(?P<uid>[0-9]{1,3}?)><(?P<steamid>(Console|BOT|STEAM_[01]:[01]:[0-9]{1,12}))><(?P<team>[^<>"]*)>'
replayer = re.compile('^"'+replayerpattern+'" (?P<rest>.*)$', re.U)
repureplayer = re.compile('^'+replayerpattern+'$', re.U)
retype = re.compile('^(?P<type>RL|L) (?P<rest>.*)$', re.U)
redate = re.compile('^(?P<month>[0-9]{2})/(?P<day>[0-9]{2})/(?P<year>[0-9]{4}) - (?P<hour>[0-9]{2}):(?P<minute>[0-9]{2}):(?P<second>[0-9]{2}): (?P<rest>.*)$', re.U)
reproperty = re.compile('^(?P<rest>.*) \((?P<key>[^() ]+) "(?P<value>[^"]*)"\)$', re.U)
recoordinates = re.compile('^(?P<x>-?[0-9]+) (?P<y>-?[0-9]+) (?P<z>-?[0-9]+)$', re.U)

# There is nothing we can do about malicious players, but we are restrictive
class SourceLogParser(object):
    def __init__(self):
        self.property = False
        self.remote = False
        self.date = False
        self.player = False

    def parse_value(self, key, value):
        # if value is a player...
        playermatch = repureplayer.match(value)

        if playermatch:
            value = (playermatch.group('name'),
                     int(playermatch.group('uid')),
                     playermatch.group('steamid'),
                     playermatch.group('team'))

        # if value is a x y z coordinate...
        coordinatesmatch = recoordinates.match(value)

        if coordinatesmatch:
            value = map(int, coordinatesmatch.group('x', 'y', 'z'))

        # TODO: parse other values?

        self.property[key] = value

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

        self.date = map(int, datematch.group('year', 'month', 'day', 'hour', 'minute', 'second'))

        line = datematch.group('rest')

        self.property = {}

        while 1:
            propertymatch = reproperty.match(line)

            if not propertymatch:
                break

            line = propertymatch.group('rest')
            key = propertymatch.group('key')
            value = propertymatch.group('value')
            self.parse_value(key, value)

        self.player = False

        playermatch = replayer.match(line)

        if playermatch:
            line = playermatch.group('rest')
            self.player = (playermatch.group('name'),
                           int(playermatch.group('uid')),
                           playermatch.group('steamid'),
                           playermatch.group('team'))

        print "parse", repr(self.remote), repr(self.date), repr(self.property), repr(self.player), repr(line)

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
