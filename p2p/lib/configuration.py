#!/usr/bin/env python3
#
# Jodawg Peer-to-Peer Communicator
#
# configuration.py: peer/user configuration services
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

import os
import uuid
import logging
import configparser
import getpass
import random

# NOTE - AT:
# Ported from my own code, this object is intended to hold onto configuration settings
# specific for this peer/user. Should work just fine, but ideally i'd like to decouple the
# two things (i.e. having a separate destination for peer and user specific things, so the
# user's settings can be synchronized across peers ...). Future work :)
#
class Configuration(object):
    """Holds global configuration settings"""

    __slots__ = [ "CONFIG_FILE", "KEY_FILE", "config", "logger" ]

    def __init__(self):
        self.logger = logging.getLogger("jodawg.config")
        self.CONFIG_FILE="/home/almer/.jodawg.cfg" # FIXME: This should not be hard-coded, will change this to homedir later.
        self.KEY_FILE="/home/almer/.jodawg.key" # FIXME: This should not be hard-coded, will change this to homedir later.

        self.config = configparser.ConfigParser()
        if os.path.isfile(self.CONFIG_FILE):
            self.logger.debug("Using existing configuration file " + self.CONFIG_FILE)
            self.config.read(self.CONFIG_FILE)
        else:
            self.logger.debug("Creating new configuration file " + self.CONFIG_FILE)
            # Initialize configuration groups
            self.config["identity"] = {}

    def _flush(self):
        self.logger.debug("Flushing configuration file to disk")
        self.config.write(open(self.CONFIG_FILE, "w"))

    def get_user_name(self):
        return getpass.getuser() # NOTE: could be made more configurable (e.g. firstname.lastname would be better)

    def get_user_fullname(self):
        return getpass.getuser() # Should be the whole name including spacing

    def get_user_identifier(self):
        value = self.config.get("identity", "identifier", fallback=None)
        if value is None:
            value = str(random.randint(1000, 9999)) + "-" + str(random.randint(100, 999)) + "-" + str(random.randint(10, 99))
            self.set_user_identifier(value)
            self.logger.info("No user identifier stored, generated new identifier: " + value)
        return value
    
    def get_user_secret_key_file(self):
        # TODO: Make sure the keyfile rights are "600"
        if os.path.isfile(self.KEY_FILE):
            return self.KEY_FILE
        else:
            # Although the private key could be (a lot) shorter, I am sticking to a
            # private key with the byte length the same as the bit length of the curve for now.
            # This won't be easy to guess ...
            value = ''.join(random.choice(string.digits + string.ascii_letters + string.punctuation) for x in range(521)) + "\n"
            self.logger.info("No secret key stored. Generated a new key as " + self.KEY_FILE)
            f = open(self.KEY_FILE, "w")
            f.write(value)
            f.close()

    def set_user_identifier(self, identifier):
        self.config["identity"]["identifier"] = identifier
        self._flush()
