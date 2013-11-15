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
import stat
import uuid
import logging
import configparser
import getpass
import random
import base64

from lib.encryption import KeyPair

# NOTE - AT:
# Ported from my own code, this object is intended to hold onto configuration settings
# specific for this peer/user. Should work just fine, but ideally i'd like to decouple the
# two things (i.e. having a separate destination for peer and user specific things, so the
# user's settings can be synchronized across peers ...). Future work :)
#
class Configuration(object):
    """Holds global configuration settings.
    
       NOTE: public/private keys are stored as base64 encoded strings. This is to prevent parsing
       problems with Python's configparser module.
    """

    __slots__ = [ "CONFIG_FILE", "config", "logger" ]

    def __init__(self, location=None):
        """Initializes this configuration.
        
           @param location The configuration file location. If None is provided, this
                           is derived from the user's home directory, and defaults to
                           ~/.jodawg.cfg
        """

        self.logger = logging.getLogger("jodawg.config")

        if location is None:
            self.CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".jodawg.cfg")
        else:
            self.CONFIG_FILE = location

        self.config = configparser.ConfigParser()
        if os.path.isfile(self.CONFIG_FILE):
            self.logger.debug("Using existing configuration file " + self.CONFIG_FILE)
            self.config.read(self.CONFIG_FILE)
        else:
            self.logger.debug("Creating new configuration file " + self.CONFIG_FILE)
            # Initialize configuration groups
            self.config["user"] = {}
            self.config["node"] = {}
            self._flush()
            # os.chmod(self.CONFIG_FILE, stat.S_IRUSR | stat.S_IWUSR) # TODO: Correctly, set file permissions

    def _flush(self):
        """Writes the configuration to the disk."""

        self.logger.debug("Flushing configuration file to disk")
        self.config.write(open(self.CONFIG_FILE, "w"))

    def get_user_name(self):
        return getpass.getuser() # NOTE: could be made more configurable (e.g. firstname.lastname would be better)

    def get_user_fullname(self):
        return getpass.getuser() # Should be the whole name including spacing

    def get_user_identifier(self):
        """Retrieves this user's unique identifier. If none exists, one is generated.

           @return Unique identifier (a string).
        """
        value = self.config.get("user", "identifier", fallback=None)
        if value is None:
            value = str(random.randint(1000, 9999)) + "-" + str(random.randint(100, 999)) + "-" + str(random.randint(10, 99))
            self.config["user"]["identifier"] = value
            self._flush()
            self.logger.info("No user identifier stored, generated new identifier: " + value)
        return value

    def get_user_keypair(self):
        """Retrieves the user's public/private keypair.
           If none exists, one is generated.

           @return A KeyPair object.
        """

        value = self.config.get("user", "private_key", fallback=None)
        if value is None:
            keypair = KeyPair() # generate new
            self.config["user"]["private_key"] = base64.b64encode(keypair.private_key).decode("utf-8")
            self.config["user"]["public_key"] = base64.b64encode(keypair.public_key).decode("utf-8")
            self._flush()
            self.logger.info("No user keypair stored, generated new pair")
        else:
            keypair = KeyPair(base64.b64decode(self.config.get("user", "private_key").encode("utf-8")), base64.b64decode(self.config.get("user", "public_key").encode("utf-8")))
        return keypair

    def get_node_keypair(self):
        value = self.config.get("node", "private_key", fallback=None)
        if value is None:
            keypair = KeyPair() # generate new
            self.config["node"]["private_key"] = base64.b64encode(keypair.private_key).decode("utf-8")
            self.config["node"]["public_key"] = base64.b64encode(keypair.public_key).decode("utf-8")
            self._flush()
            self.logger.info("No node keypair stored, generated new pair")
        else:
            keypair = KeyPair(base64.b64decode(self.config.get("node", "private_key").encode("utf-8")), base64.b64decode(self.config.get("node", "public_key").encode("utf-8")))
        return keypair

    def get_node_address(self):
        return self.config.get("node", "address", fallback="tcp://127.0.0.1:4363")

    def get_known_nodes(self):
        try:
            return [ (node_address, base64.b64decode(node_public_key.encode("utf-8"))) for (node_address, node_public_key) in self.config.items("known_nodes") ]
        except:
            return []

    def has_known_node(self, node_address):
        return self.config.has_section("known_nodes", node_address)

    def add_known_node(self, node_address, node_public_key):
        self.config["known_nodes"][node_address] = base64.b64encode(node_public_key).decode("utf-8")
        self._flush()

    def remove_known_node(self, node_address):
        self.config.remove_option("known_nodes", node_address)
        self._flush()

