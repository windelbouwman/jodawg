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
    """Presents a simple shell for testing / interaction with the
       jodawg P2P network. This runs in its own thread."""

    __slots__ = [ "configuration", "node", "encryption", "auto_join" ]

    def __init__(self, _configuration, _node, _auto_join):
        """Creates a new shell.
        
           @param _configuration The global Configuration object to use.
           @param _node The Node to use for communication with the network.
        """

        threading.Thread.__init__(self)

        self.configuration = _configuration
        self.node = _node
        self.auto_join = _auto_join
        #self.encryption = Encryption()

    def command_help(self):
        """Lists all commands available."""

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

    def command_leave(self):
        self.node.get_service("overlay").leave()
        print("leave completed")

    def run(self):
        """Runs the interactive Shell.
           When the user exits the shell the thread terminates."""

        print('Jodawg (%s - %s - %s) [READY]' % (JODAWG_VERSION, JODAWG_VERSION_NAME, JODAWG_VERSION_STATUS))
        print('Your identity is %s' % (self.configuration.get_user_identifier()))
        print('Type "help" for more information')

        if self.auto_join:
            print("Executing Join")
            self.command_join()

        while True:
            try:
                s = input('>> ')
            except:
                break

            command = s.strip().lower()

            if command in ['x', 'exit', 'q', 'quit']: # Be flexible
                break
            elif command in ['j', 'join']:
                self.command_join()
            elif command in ['l', 'leave']:
                self.command_leave()
            elif command in [ 'h', 'help', '?' ]:
                self.command_help()
            else:
                print("Command not recognized. Type 'help' for a list of available commands")

        print("Exiting")
