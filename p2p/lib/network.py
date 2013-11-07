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

import threading
import logging
import zlib

import zmq

class Node(threading.Thread):
    """A Node represents a peer in the network. A peer
       always has a (socket) address and a public_key
       for communication. A node may or may not have
       a user associated with it. Though, each node can
       have AT MOST one user.
    """

    __slots__ = [ "logger", "address", "public_key", "user", "context", "handlers", "terminate_event" ]

    def __init__(self):
        threading.Thread.__init__(self)
        self.terminate_event = threading.Event()

        self.logger = logging.getLogger("jodawg.node")
        self.context = zmq.Context()
        self.address = "tcp://127.0.0.1:4363"
        self.user = None
        self.handlers = {}
        

    def add_service(self, name, handler):
        self.handlers[name] = handler
        self.logger.debug("Service '%s' was added" % (name))

    def get_service(self, name):
        return self.handlers[name]

    def terminate(self):
        self.terminate_event.set()

    def run(self):
        
        # NOTE: I use a poller here to be able to expand
        # easily to a multi-socket implementation later, just
        # using one socket for now.

        self.logger.debug("Starting node services")

        poller = zmq.Poller()
        
        # Main Socket
        main_socket = self.context.socket(zmq.REP)
        main_socket.bind(self.address)
        poller.register(main_socket, zmq.POLLIN)

        self.terminate_event.clear()
        while True:
            socks = dict(poller.poll(1000))

            if main_socket in socks and socks[main_socket] == zmq.POLLIN:
                self.logger.debug("Message received")
                message = main_socket.recv()
                
                for (handler_name, handler) in self.handlers.iteritems():
                    if handler.handle_message(message):
                        self.logger.debug("Message handled by '%s' service" % (handler_name))
                        break

            # Terminate request!
            if self.terminate_event.is_set():
                break
        
