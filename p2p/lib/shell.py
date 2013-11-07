#!/usr/bin/env python3
#
# Jodawg Peer-to-Peer Communicator
#
# shell.py: interactive shell
#
# Copyright (C) 2013 Almer S. Tigelaar & Windel Bouwman
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import threading

from lib.constants import *
from lib.configuration import Configuration
from lib.encryption import Encryption

class Shell(threading.Thread):
    __slots__ = [ "configuration", "node", "encryption" ]

    def __init__(self, _configuration, _node):
        threading.Thread.__init__(self)

        self.configuration = _configuration
        self.node = _node
        #self.encryption = Encryption()

    def command_help(self):
        print('Available commands:')
        print('join - join the network with this machine')
        print('leave - leave the network with this machine [TODO]')
        print('login - login to the network [TODO]')
        print('logout - logout from the network [TODO]')
        print('exit - terminate jodawg and return to the command-line')
        print('help - this overview')

    def command_join(self):
        self.node.get_service("overlay").join()
        print("join completed")

    def run(self):
        print('Jodawg (%s - %s - %s) [READY]' % (JODAWG_VERSION, JODAWG_VERSION_NAME, JODAWG_VERSION_STATUS))
        print('Your identity is %s' % (self.configuration.get_user_identifier()))
        print('Type "help" for more information')

        while True:
            try:
                s = input('>> ')
            except:
                break

            command = s.strip().lower()

            if command == 'exit':
                break
            if command == 'join':
                self.command_join()
            if command == 'leave':
                break
            elif command == 'help' or command == '?':
                self.command_help()

        print("Exiting")
