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
import random
import string
import zlib
import json


import seccure # py-seccure

class KeyPair:
    __slots__ = [ "private_key", "public_key" ] 

    def __init__(self, _private_key=None, _public_key=None):
        """Generates a new keypair. This object can be serialized to store the pair generated."""

        assert (_private_key is None and _public_key is None) or (_private_key is not None and _public_key is not None)

        if _private_key is None:
            # Although the private key could be (a lot) shorter, I am sticking to a
            # private key with the byte length the same as the bit length of the curve for now.
            # This won't be easy to guess ...
            self.private_key = ''.join(random.choice(string.digits + string.ascii_letters + string.punctuation) for x in range(521)).encode("utf-8")
            self.public_key = str(seccure.passphrase_to_pubkey(self.private_key)).encode("utf-8")
        else:
            self.private_key = _private_key
            self.public_key = _public_key
        
class Encryption:
    """Provides secure elliptic curve encryption.
       This is a convenience wrapper around py-seccure, which plays nice with our internal infra-structure.
       Keys (where needed) are expected to be passed as byte strings.
    """

    # WB: Why use slots?
    __slots__ = [ "logger", "curve", "mac", "public_key" ]

    def __init__(self):
        self.logger = logging.getLogger("jodawg.encryption")
        self.curve = "secp521r1/nistp521"
        self.mac = 10 # FIXME: for some reason mac's different from 10 bytes do not work (at all), find out why, and find out if we need to do something about this - AT.
                
    def encrypt(self, message, public_key):
        cipher = seccure.encrypt(message.encode("utf-8"), public_key, mac_bytes=self.mac)
        self.logger.debug("Encrypted " + str(len(message)) + " bytes to '" + public_key.decode("utf-8") + "'")
        return cipher

    def encrypt_compress_json(self, dictionary, public_key):
        # Convenience method to jsonify a dictionary, encrypt it and compress it with zlib in one go.
        return self.encrypt(zlib.compress(json.dumps(dictionary, sort_keys=True), 9), public_key)

    def decrypt(self, cipher, private_key):
        message = seccure.decrypt(cipher, private_key) # decrypt
        self.logger.debug("Decrypted " + str(len(message)) + " bytes")
        return message.decode("utf-8")

    def decrypt_decompress_json(self, cipher, private_key):
        # Convenience method
        return json.loads(zlib.decompress(self.decrypt(cipher, private_key)))

    def sign(self, message, private_key):
        signature = seccure.sign(message, private_key) # sign
        self.logger.debug("Signed " + str(len(message)) + " bytes with private key")
        return signature

    def verify(self, message, signature, public_key):
        authentic = seccure.verify(message, signature, public_key)
        self.logger.debug("Verified " + str(len(message)) + " bytes against key '" + public_key.decode("utf-8") + "', authentic = " + str(authentic))
        return authentic

# TODO: Add some decent unit tests here ...
# WB: Check testencryption.py
