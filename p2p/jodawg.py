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

from lib.encryption import Encryption
from lib.configuration import Configuration

import logging
logging.basicConfig(level=logging.DEBUG)

#node = Node()
#node.run()
