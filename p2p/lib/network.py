#!/usr/bin/env python3
#
# Jodawg Peer-to-Peer Communicator
#
# network.py: peer-to-peer network services.
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

import logging
import zmq

# Thoughts on on-the-wire protocol:
# * protobuf has the disadvantage of not including the protocol
#   specification in the wire format (hence, it requires sender/receiver
#   to HAVE the full spec - and the same version of it as well). Though,
#   it is the most compact option. The default Python implementation is
#   slow.
# * XML is perhaps the most widely used solution (think XMPP), but is
#   slow and verbose. Though, it can be compressed, XML parsers have
#   numerous disadvantages (including security problems).
# * JSON is basically a lightweight XML-like format, though not
#   hampered by its verbosity, nor vulnerable to the same security
#   issues. Though more verbose than protobuf, it can be compressed
#   down to a reasonable size easily (either using zlib, or python-blosc
#   as much faster solution). ZMQ also offers easy object serialization
#   using JSON as carry format. So, it seems a good choice for now.
#
# See http://zeromq.github.io/pyzmq/serialization.html for some
# more thoughts on this.

# PROTOCOL MESSAGES

# Session Control:
#
# request: register_user <user-identifier> <public_key>
# request: login <user-identifier>
# request: logout <user-identifier>
# request: set_status <user-identifier> <status>
# request: set_profile <user-identifier> <vcard_data>

# Messaging:
# 
# request: message-log-join <user-identifier>
# request: message-log-leave <user-identifier>
# request: message-log-synchronize <user-identifier>
# request: message-log-append <user-identifier>
#

class Node(object):
    """A Node represents a peer in the network. A peer
       always has a (socket) address and a public_key
       for communication. A node may or may not have
       a user associated with it. Though, each node can
       have AT MOST one user.
    """

    __slots__ = [ "address", "public_key", "none" ]

    def __init__(self):
        self.address = None
        self.public_key = None
        self.user = None

class Node(object):
    __slots__ = [ "context", "super_peers_locations" ]

    def __init__(self):
        self.context = zmq.Context()
        self.super_peers_locations = [ "tcp://127.0.0.1:4363" ]

    def run(self):
        
        # AT: So, this is how a multi-poller would work in ZMQ. We need to set-up
        # some "maintenance" messaging on the supers which would probably work
        # with a (stateless) PUB/SUB system. This would involve assisting in
        # searching for other users for example. An other application of this
        # is chat synchronization. Though, I first want to look into a proper
        # way to "version" and synchronize MessageLogs, as that really is
        # the basis of the application. Both PUB/SUB as well as regular
        # sockets will be needed.

        poller = zmq.Poller()

        super_peers = []
        for location in self.super_peers_locations:
            super_peer = context.socket(zmq.SUB)
            super_peer.connect(location)
            super_peer.setsockopt_string(zmq.SUBSCRIBE, "SYSTEM")
            poller.register(super_peer, zmq.POLLIN)
            super_peers.append(super_peer)

        while True:
            socks = dict(poller.poll())

            for super_peer in super_peers:
                if super_peer in socks and socks[super_peer] == zmq.POLLIN:
                    message = receiver.recv()
                    # DO SOMETHING
