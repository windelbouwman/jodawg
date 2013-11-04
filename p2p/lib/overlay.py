#!/usr/bin/env python3
#
# Jodawg Peer-to-Peer Communicator
#
# overlay.py: network overlay service.
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

import zlib
import json
import zmq

class OverlayNode:

    def __init__(self, _address, _public_key, _capabilities):
        self.address = _address
        self.public_key = _public_key
        self.capabilities = _capabilities

class OverlayUser:
    """A user in overlay context is really just an identifier, public key
       and a list of known associated nodes and keys."""

    def __init__(self, _identifier, _public_key):
        self.identifier = _identifier
        self.public_key = _public_key
        self.nodes = {}
        self.signatures = []

    def register_node(self, node_address, node_key):
        self.nodes[node_address] = node_key

    def add_signature(self, signature):
        self.signatures.append(signature)

class OverlayStore:

    def __init__(self):
        self.users = {}

    def login_user(self, user_id, user_key, node_key):
        if user_id in self.users:
            self.users[user_id]

    def authorize_user(self, user_id):
        pass

class OverlayService:
    
    def __init__(self, _configuration, _encryption):
        self.configuration = _configuration
        self.encryption = _encryption
        self.store = OverlayStore()
        self.neighbours = []

    def _handle_join(self, message):
        if m.user_id in self.store.users: # Known user
            user = self.store.users[m.user_id]
        else: # Unknown user
            user = OverlayUser(m.user_id, m.user_key)
            user.register_node()

        return True

    def handle_message(self, message):
        m = self.encryption.decrypt_decompress_json(message)

        if m[command] == "node_join":
            return self._handle_join(message)
        else:
            print("Unrecognized command: " + m[command])

    def join(self):

        for (node_address, node_public_key) in self.configuration.get_bootstrap_peer_addresses():
            socket = self.context.socket(zmq.REQ)
            sock.connect(node_address)

            user_id = configuration.get_user_identifier()
            user_key = configuration.get_user_keypair().public_key
            node_key = configuration.get_node_keypair().public_key

            m = { "command" : "node_join", "user_id" : user_id, "user_key" : user_key, "node_key" : node_key, "parent_user_id" : "x", "parent_user_key" : "y" }
            sock.send(self.encryption.encrypt_compress_json(m, node_public_key))

            bootstrap_message = sock.recv()

    def leave(self):
        
        pass



        
