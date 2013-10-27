#!/usr/bin/env python3
#
# Jodawg Peer-to-Peer Communicator
#
# account.py: persistent account data.
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
