#!/usr/bin/env python3
#
# Jodawg Peer-to-Peer Communicator
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
# Dependencies:
# - python3 (obviously :D)
# - seccure (https://github.com/bwesterb/py-seccure)
# - zmq (http://zeromq.org/)
#

import logging

from lib.encryption import Encryption
from lib.configuration import Configuration
from lib.shell import Shell

from lib.network import Node
from lib.overlay import OverlayService

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger("jodawg.main")

logger.debug("Initializing Configuration")
configuration = Configuration()

logger.debug("Initializing Encryption")
encryption = Encryption()

# Create the network node, register appropriate handlers for
# the various network services. The node runs in its own thread.

logger.debug("Initializing Node")
node = Node()
node.add_service("overlay", OverlayService(configuration, encryption))
# node.register_handler(PresenceService())
# node.register_handler(MessagingService())
# etc.

logger.debug("Starting Node")
node.start()

# START SHELL (also in its own thread)
logger.debug("Starting Shell")
shell = Shell(configuration, node)
shell.start()

shell.join()
logger.debug("Shell Stopped")

logger.debug("Shutting Down Node")
node.terminate()
node.join()

logger.debug("Terminated")

#import logging
#logging.basicConfig(level=logging.DEBUG)

# configuration = Configuration()
# print(configuration.get_user_identifier())
# kp = configuration.get_user_keypair()

# e = Encryption()
# m = e.encrypt("Test", kp.public_key)
# print(m)
# print(e.decrypt(m, kp.private_key))

#node = Node()
#node.run()
