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

#from xmlrpc.server import SimpleXMLRPCServer
#from xmlrpc.client import ServerProxy
import uuid
import logging
import configparser
import getpass

import seccure # py-seccure
import zmq

logging.basicConfig(level=logging.DEBUG)

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

# TODO - AT:
# I ported this straight from my own code base and adapted it for pyseccure. Hence, it may
# feel a bit ... shoddy at present. No worries, I'll improve it as we go along. First thing
# to note is that the secret key is read from a file, which is okay, but we should consider
# reading it once and caching it (it's not going to change mid-session). Perhaps here or in
# Configuration. Will get back to that later.
#
class Encryption(object):
    """Provides secure elliptic curve encryption.
       This is a convenience wrapper around py-seccure, which plays nice with our internal infra-structure.
    """

    __slots__ = [ "configuration", "logger", "curve", "mac", "public_key" ]

    def __init__(self, _configuration):
        self.configuration = _configuration
        self.logger = logging.getLogger("jodawg.encryption")

        self.curve = "secp521r1/nistp521"
        self.mac = 256
                
        self.public_key = self._generate_public_key()

    def _generate_public_key(self):
        secret_key_file = self.configuration.get_user_secret_key_file()
        secret_key = open(secret_key_file(), "rb").read()

        public_key = str(seccure.passphrase_to_pubkey(secret_key)) # priv -> pub
        self.logger.info("Public key derived: '" + public_key + "'")
        return public_key

    def encrypt(self, message, receiver_key):
        assert self.public_key is not None

        cipher = ssecure.encrypt(msg, receiver_key, mac_bytes=self.mac)
        self.logger.debug("Encrypted " + str(len(message)) + " bytes to '" + receiver_key + "'")
        return cipher

    def decrypt(self, cipher):
        secret_key_file = self.configuration.get_user_secret_key_file()
        secret_key = open(secret_key_file(), "rb").read()

        message = ssecure.decrypt(cipher, secret_key) # decrypt
        self.logger.debug("Decrypted " + str(len(message)) + " bytes for self")
        return message

    def sign(self, message):
        secret_key_file = self.configuration.get_user_secret_key_file()
        secret_key = open(secret_key_file(), "rb").read()

        signature = ssecure.sign(message, secret_key) # sign
        self.logger.debug("Signed " + str(len(message)) + " bytes with private key")
        return signature

    def verify(self, message, signature, public_key=None):
        if public_key is None:
            public_key = self.public_key # Verify against own public key by default

        authentic = ssecure.verify(message, signature, public_key)
        self.logger.debug("Verified " + str(len(message)) + " bytes against key '" + public_key + "', authentic = " + str(authentic))
        return authentic

#
# So, the downside of an unencrypted envelope
# is that anyone can see who was the sender
# and receiver. To mask that one could 
# encrypt the envelope as well, and always
# forward a message to a number of nodes
# only the node with the right private
# key can really decrypt the message.
#
# When store and forwarding, multiple peers
# must be specified as destination. 

# Storing profiles:
# So, profile information should not be visible
# to everyone, only to peers that have access
# to the information. Hence, the profile info
# must be encrypted. A private key to decrypt
# it can be given to those peers that you 
# have given permission. To block a person
# the profile info can be re-encrypted with
# a new key (the private part of which is
# handed out to those you still want to have
# access to your profile data). 

# Profile Data:
# 1) Account ID (a random number)
# 2) List of Associated Machines (Encrypted? Difficult to add someone then ...) 
#
# IDEA: Peer approved accounts - traceable account hierarchy.
# (i.e. you need to know someone to get in).

class MessageHeader(object):
    """A message header contains meta-data concerning
       the message, and is essentially a dictionary with named fields."""

    __slots__ = [  "identifier", "revision", "datetime", "fields" ]

    def __init__(self):
        self.identifier = uuid.uuid5(uuid.NAMESPACE_DNS, 'jodawg.org')
        self.revision = 0
        self.datetime = datetime.datetime.now()
        self.fields = {}

    def set_field(self, name, value):
        assert name is not None and len(name) > 0
        assert value is not None and len(value) > 0

        self.fields[name] = value
    
    def get_field(self, name):
        assert name is not None and len(name) > 0
        return self.fields[name]

class MessagePart(object):
    """A message part can be added to a message."""
    pass

class MessagePartText(MessagePart):
    """A specific message part consisting of only text data."""

    __slots__ = [ "content" ]

    def __init__(self, _content=""):
        self.content = _content

class Message(object):
    """A message consists of a header and
       one or more message parts. When a message needs to
       be revised. It must be cloned, then changed and re-added
       to a message log."""

    __slots__ = [ "header", "parts" ]

    def __init__(self, _header=None):
        if header is not None:
            self.header = _header
        else:
            self.header = MessageHeader()
        self.parts = []

    def add_part(self, message_part):
        self.parts.append(message_part)

    def clone_revision(self):
        """Clones the entire message to make a new revision
           of any of its contents."""
        # deepcopy
        # self.header.revision += 1

class SystemMessage(Message):
    pass

class MessageLog(object):
    """A message log is a collection of messages.
       intended for two or more participants. A message
       log must be synchronized between nodes associated
       with the specified participants."""

    __slots__ = [ "revision", "participants", "messages", "message_tracking" ]

    def __init__(self):
        self.participants = set([])
        self.messages = []
        self.message_tracking = set([])
        self.revision = 0

    def add_participant(self, user):
        """Adds a participant to the log.

           NOTE: The same participant may be added multiple times, this has
           no real effect, but it's not considered erroneous either.

           @param user The user to add.
        """

        self.participants.add(user)

        # Only output status message in group chat
        if len(self.participants) > 2:
            message = SystemMessage()
            message.add_part(MessagePartText("User " + str(user) + " was added"))
            self.add_message(message) # This also increases the revision, forcing everyone to sync
        else:
            self.revision += 1

    def remove_participant(self, user):
        """Removes a participant from this log.

           @param The user to remove.
        """

        self.participants.remove(user)
        assert len(self.participants) > 1 # at least two

        message = SystemMessage()
        message.add_part(MessagePartText("User " + str(user) + " was removed"))
        self.add_message(message) # This also increases the revision, forcing everyone to sync

    def append_message(self, message):
        """Appends a new message to the end of the log.
           
           NOTE: You can add a unique message + revision ONLY ONCE.
           In theory the same message could be appended to multiple logs.

           @param message The message to append.
        """

        # no point in adding messages if there's only one person
        assert len(self.participants) > 1 

        # Can't add the same message, same revision twice
        assert (message.header.identifier, message.header.revision) not in self.message_tracking

        self.messages.append(message)
        self.message_tracking.add((message.header.identifier, message.header.revision))
        self.revision += 1

class Roster(object):
    # User contact list abstraction
    pass

class User(object):
    __slots__ = [ "identifier", "nickname", "status" ]

    # status: chat, away, dnd, xa
    def __init__(self):
        self.status = "chat"
        self.identifier = 1
        self.nickname = "default"


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

#node = Node()
#node.run()

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
