#!/usr/bin/env python3
#
# Jodawg Peer-to-Peer Communicator
#
# messaging.py: message encapsulation
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

class MessagingService():

    def __init__(self):
        pass

