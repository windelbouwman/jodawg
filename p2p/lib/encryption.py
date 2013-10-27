#!/usr/bin/env python3
#
# Jodawg Peer-to-Peer Communicator
#
# encryption.py: data encryption services
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
import seccure # py-seccure

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

# TODO: Add some decent unit tests here ...
