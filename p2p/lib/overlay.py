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

import json
import zmq
import logging
import datetime
from lib.encryption import Key, KeyPair


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


class OverlayNode:

    OVERLAY_NODE_STATUS_UNKNOWN = 0
    OVERLAY_NODE_STATUS_ONLINE = 1
    OVERLAY_NODE_STATUS_DANGLING = 2 # Indicated wants to leave, but can't verify signature
    OVERLAY_NODE_STATUS_OFFLINE = 3

    def __init__(self, _address, _public_key, _joined=None):
        self.address = _address
        self.public_key = _public_key
        if _joined is None:
            self.joined = datetime.utcnow()
        else:
            self.joined = _joined
        self.status = self.OVERLAY_NODE_STATUS_UNKNOWN


class OverlayStore:

    def __init__(self):
        self.nodes = {}
    #     self.users = {}

    # def login_user(self, user_id, user_key, node_key):
    #     if user_id in self.users:
    #         self.users[user_id]

    # def authorize_user(self, user_id):
    #     pass

    def update_node(self, node):
        # TODO: Overwrites existing object, should be no problem per se. However,
        # we do need to check this better to protect against an "overwriting" attack,
        # which would render nodes useless. Note entirely sure what would be a good approach here,
        # have to think about it - AT.
        self.nodes[node.address] = node 

    def get_node(self, node_address, node_public_key):
        if node_address in self.nodes:
            return self.nodes[node_address]
        else:
            return None

    def get_nodes(self, n=100):
        # This returns a list of 100 nodes which are ON-LINE the longest.
	# TODO: To prevent the network on converging to a list of 100 completely
	# static nodes, which are then on-line for the longest amount of time,
	# there should be some variation in this. Perhaps a 50/50 mix between the longest
	# on-line nodes and a random set, or picking 100 nodes randomly from maximally 1000 nodes
	# with the highest uptime. Or 33/33/33 where nodes with long, medium and short uptimes are
	# equally represented.
        for node in sorted(filter(lambda x: x.status == self.OVERLAY_STATUS_ONLINE, self.nodes.itervalues()), key=lambda x: x.joined)[:n]:
            return node


class OverlayService:

    def __init__(self, _configuration, _encryption):
        self.logger = logging.getLogger("jodawg.overlay")
        self.configuration = _configuration
        self.encryption = _encryption
        self.store = OverlayStore()
        self.neighbours = []
        self.context = zmq.Context()

    def _handle_node_join(self, message):

        # Check fields
        if (not "node_address" in message) or (not "node_public_key" in message) or (not "signature" in message):
            m = { "response" : "node_join_denied", "reason" : "missing mandatory fields!" } # Don't know node's pkey, so can't do this
            return json.dumps(m, sort_keys=True) # UNENCRYPTED! (don't know other node's pkey yet!)

        # Verify signature
        if not self.encryption.verify(Key(message["node_public_key"]).raw_key, message["signature"], Key(message["node_public_key"]).raw_key):
            m = { "response" : "node_join_denied", "reason" : "invalid signature!" }
            return self.encryption.encrypt_compress_json(m, Key(message["node_public_key"]).raw_key)
            
        # Build response + send.
        # Response includes at most 100 known nodes.
        m = { "response" : "node_join_approved" }
        for no in self.overlay.get_nodes():
            m[n.address] = (n.public_key.b64_key, n.status)

        # Register that we've seen this peer for bootstrapping purposes later on
        self.configuration_add_known_node(message["node_address"], Key(message["node_public_key"]))

        # Register node in the overlay (as active)
        # TODO: Ideally, we would also include a signature, so that
        # others can verify that the addition to the "overlaystore" is
        # a genuine one ...
        node = OverlayNode(node_address, Key(node_public_key))
        node.status = OverlayNode.OVERLAY_NODE_STATUS_ONLINE
        self.overlay.update_node(node)

        return self.encryption.encrypt_compress_json(m, Key(message["node_public_key"]).raw_key)

    def _handle_node_leave(self, message):

        # Check fields
        if (not "node_address" in message) or (not "signature" in message):
            m = { "response" : "node_leave_denied", "reason" : "missing mandatory fields!" }
            return json.dumps(m, sort_keys=True) # UNENCRYPTED! (don't know other node's pkey yet!)

        node = self.overlay.get_node(message["node_address"])

        # Is the node joined?
        if node is None or node.status == OVERLAY_NODE_STATUS_OFFLINE:
            m = { "response" : "node_leave_denied", "reason" : "Node is not part of the network or off-line" }
            return self.encryption.encrypt_compress_json(m, node.raw_public_key)

        # Verify signature
        if not self.encryption.verify(message["node_address"], message["signature"], message["node_address"]):
            m = { "response" : "node_leave_denied", "reason" : "invalid signature!" }
            node.status = OVERLAY_NODE_STATUS_DANGLING
            return self.encryption.encrypt_compress_json(m, node.raw_public_key)
        
        m = { "response" : "node_leave_approved" }
        return self.encryption.encrypt_compress_json(m, node.raw_public_key)

    def handle_message(self, message):
        try:
            m = self.encryption.decrypt_decompress_json(message, self.configuration.get_node_keypair().raw_private_key)
        except:
            self.logger.warning('Error decoding message')
            raise
            return json.dumps({ "response" : "protocol_error", "reason" : "format_or_encryption_error" }, sort_keys=True) # UNENCRYPTED! (don't know other node's pkey yet!)

        if m['request'] == "node_join":
            return self._handle_node_join(m)
        elif m['request'] == "node_leave":
            return self._handle_node_leave(m)

        return False # Someone else should handle this

    # def authorize_user(self, user_id, user_public_key):
    #     signature = self.encryption.sign(user_public_key, self.configuration.get_user_keypair().private_key)
    #     user = OverlayUser(user_id, user_public_key)
    #     user.add_signature(signature)
    #     self.store.users[m.user_id] = user

    def join(self):
        self.logger.debug("Joining the Network")

        bootstrap_peer_addresses = self.configuration.get_known_nodes()
        if len(bootstrap_peer_addresses) == 0:
            self.logger.debug("No known bootstrap peers, assuming disjunct operation")
            self.configuration.get_node_keypair() # but DO generate a keypair for interactions with new peers ...
            return True

        for (bootstrap_node_address, bootstrap_node_public_key) in bootstrap_peer_addresses:
            self.logger.debug("Trying %s for bootstrap" % (bootstrap_node_address))

            socket = self.context.socket(zmq.REQ)
            socket.connect(bootstrap_node_address)

            node_address = self.configuration.get_node_address()
            node_keypair = self.configuration.get_node_keypair()
            signature = self.encryption.sign(node_keypair.raw_public_key, node_keypair.raw_private_key)

            m = { "request" : "node_join", "node_address" : node_address, "node_public_key" : node_keypair.b64_public_key, "signature" : signature }
            socket.send(self.encryption.encrypt_compress_json(m, bootstrap_node_public_key.raw_key))

            response = socket.recv()
            try:
                r = self.encryption.decrypt_decompress_json(response, node_keypair.raw_private_key)
            except:
                try:
                    # Assume the response is not encrypted. This is ALWAYS an error
                    r = json.loads(response) 
                    self.logger.debug("Failed to bootstrap via %s: %s - %s" % (bootstrap_node_address, r["response"], r["reason"]))
                    continue # Next node ...
                except:
                    self.logger.debug("Failed to bootstrap via %s: unknown data returned")
                    continue # Give up, next node ...

            if "response" in r and r["response"] == "node_join_denied":
                self.logger.debug("Failed to bootstrap via %s: %s - %s" % (bootstrap_node_address, r["response"], r["reason"]))
                continue # Try next node ...

            # Retrieve list of nodes (+ status)
            for (k, v) in r.iteritems():
                if k == "response":
                    assert v == "node_join_approved" # Something fishy going on otherwise ....
            
                node = OverlayNode(k, v[0])
                node.status = v[1]
                self.store.update_node(node)

            # TODO: Perhaps update the list with bootstrap peers here as well ..
                
            return True

        self.logger.error("Could not bootstrap into the network!")
        return False

    # TODO: I am doubting as to whether we want an actual leave protocol for the nodes. On the one hand it's nice
    # as it would allow us to keep better track of which nodes are still alive. On the other hand, there are so many
    # ways in which this can go wrong (nodes failing to send leave messages). Perhaps ONLY a keep-alive is a better
    # idea. This could be done with a separate PUB/SUB socket.

    def leave(self):
        self.logger.debug("Leaving the Network")
        return True

