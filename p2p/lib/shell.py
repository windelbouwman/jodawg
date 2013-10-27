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

from lib.constants import *
from lib.configuration import Configuration
from lib.encryption import Encryption

class Shell(object):
    __slots__ = [ "configuration", "encryption" ]

    def __init__(self):
        self.configuration = Configuration()
        self.encryption = Encryption()

    def command_help(self):
        print('Available commands:')
        print('exit - terminate jodawg and return to the command-line')
        print('help - this overview')

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
            elif command == 'help' or command == '?':
                self.command_help()
