#!/usr/bin/python

#
# This example script listens to a TF2 server log
# and records matches using Source TV
# and makes finished demos available for download
#
# Record starts on match start and ends on match end.
#
# Doesn't handle never ending matches (timelimit 0 stopwatch).
#

import SourceLib
import asyncore
import subprocess

from datetime import datetime

rcon = SourceLib.SourceRcon.SourceRcon('1.2.3.4', 27015, 'rconpw')
query = SourceLib.SourceQuery.SourceQuery('1.2.3.4', 27015)

currentdemo = False
directory = '/var/www/server/sourcetv/'
demodirectory = '/home/tf2/srcds/orangebox/tf/'

# create a text log file
def logfile(message):
    global rcon, query, currentdemo, directory, demodirectory

    if currentdemo:
        fh = open(directory + currentdemo + '.txt', 'a')
        fh.write(str(message) + '\n')
        fh.close()

# create a sourcelogparser
class MyLogParser(SourceLib.SourceLog.SourceLogParser):
    def action(self, remote, timestamp, key, value, properties):
        try:
            self.my_action(remote, timestamp, key, value, properties)
        except:
            pass

    def my_action(self, remote, timestamp, key, value, properties):
        global currentdemo, directory, demodirectory, rcon, query

        if key == 'trigger_world' and value['trigger'] == 'Round_Start':
            # fetch info from server
            info = query.info()
            #print info
            if info['numplayers'] > 0:            
                demoname = datetime(*timestamp)
                demoname = demoname.strftime('TV-%Y-%m-%d-%a-%H-%M-%S-'+info['map'])

                record = rcon.rcon('tv_record '+demoname)

                if record.find('Recording SourceTV demo to '+demoname) >= 0:
                    currentdemo = demoname
                    status = rcon.rcon('status')
                    logfile(status + "="*75)

            elif currentdemo:
                rcon.rcon("tv_stoprecord");
                subprocess.call(['/home/tf2/bin/sourcetv.sh'])

        if currentdemo:
            if key == 'trigger_world_reason' and value['trigger'] == 'Game_Over':
                rcon.rcon("tv_stoprecord");
                # sourcetv.sh syncs the www directory
                subprocess.call(['/home/tf2/bin/sourcetv.sh'])

            if key == 'map_start':
                subprocess.call(['/home/tf2/bin/sourcetv.sh'])
                currentdemo = False

            if key == 'score': # score numplayers team
                logfile('score %(score)s numplayers %(numplayers)s team %(team)s' % value)

            if key == 'score_final': # score numplayers team
                logfile('final score %(score)s numplayers %(numplayers)s team %(team)s' % value)

                # save another, final status at the end of the map
                if value['team'] == 'Blue':
                    status = rcon.rcon("status");
                    logfile("="*75 + "\n" + status)

            # additional info

            if key == 'say':
                logfile('[%(player_steamid)s] %(player_name)s (%(player_team)s): "%(message)s"' % value)

        print remote, timestamp, key, value, properties

# Listen for log on port 17015
# use logaddress_add 1.2.3.4:17015 in the server config
server = SourceLib.SourceLog.SourceLogListener(('1.2.3.4', 17015), ('1.2.3.4', 27015), MyLogParser())

asyncore.loop()
