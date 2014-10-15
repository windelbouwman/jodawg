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
import base64

import seccure # py-seccure


class Key:
    __slots__ = ["_key"]

    def __init__(self, key, raw=False):
        """Stores a private or public key.

           @param key The key to store.
           @param raw If true the key is assumed to be in unencoded bytestring format, if False (default)
                      it is assumed that it's a base64 encoded version instead.
        """
        if raw:
            self._key = key
        else:
            self.b64_key = key

    @property
    def b64_key(self):
        return base64.b64encode(self._key).decode('utf-8')

    @b64_key.setter
    def b64_key(self, key):
        self._key = base64.b64decode(key.encode('utf-8'))

    @property
    def raw_key(self):
        return self._key

    @raw_key.setter
    def raw_key(self, key):
        self._key = key


class KeyPair:
    """KeyPair holds a public/private keypair as byte strings, and can also generate new keypairs easily.

       Internally keys are stored as byte strings. However, they can also be get/set using base64 encoding.
       (reason for this is that keys can contain weird characters which can clash with wrapping them in text-based
        carrying format, base64 handles that. See the Key class for details).
    """

    __slots__ = [ "_private_key", "_public_key" ] 

    def __init__(self, _private_key=None, _public_key=None):
        """Generates a new keypair. This object can be serialized to store the pair generated.
        
           To generate a NEW key, set both parameters to None (simply invoke the constructor
           w/o arguments). To load/use an existing pair pass them as parameter. You can not
           use this object to store ONLY a private or public key.

           You may read out the 'private_key' and 'public_key' properties directly.

           @param _private_key An existing private key (or None). Should be in base64 format.
           @param _public_key An existing public key (or None). Should be in base64 format.
        """

        assert (_private_key is None and _public_key is None) or (_private_key is not None and _public_key is not None)

        if _private_key is None:
            # Although the private key could be (a lot) shorter, I am sticking to a
            # private key with the byte length the same as the bit length of the curve for now.
            # This won't be easy to guess ...
            self._private_key = Key(''.join(random.choice(string.digits + string.ascii_letters + string.punctuation) for x in range(521)).encode("utf-8"), True)
            self._public_key = Key(str(seccure.passphrase_to_pubkey(self.raw_private_key)).encode("utf-8"), True)
        else:
            self._private_key = Key(_private_key)
            self._public_key = Key(_public_key)

    @property
    def b64_public_key(self):
        return self._public_key.b64_key

    @property
    def b64_private_key(self):
        return self._private_key.b64_key

    @property
    def raw_public_key(self):
        return self._public_key.raw_key

    @property
    def raw_private_key(self):
        return self._private_key.raw_key


class Encryption:
    """Provides secure elliptic curve encryption.

       This is a convenience wrapper around py-seccure, which plays nice with our
       internal infra-structure. Though this object can be instantiated and passed
       around. Apart from logging, it is essentially stateless and could be regarded
       as a singleton. Though, For future compatibility it is recommended to instantiate 
       and pass around Encryption objects like any other object.

       NOTE: Keys (where needed) are expected to be passed as byte strings.
    """

    # WB: Why use slots? AT: They are useful in cases where you want the class to
    # have no other members than those specified in slots. This takes up fewer
    # resources (one less dict) and eliminates run-time errors due to typos.
    # Though, it's probably useful only for objects that have (more or less)
    # crystallized in terms of their interface.
    #

    __slots__ = ["logger", "curve", "mac", "public_key"]

    def __init__(self):
        """Initializes a new Encryption object."""

        self.logger = logging.getLogger("jodawg.encryption")
        self.curve = "secp521r1/nistp521"

        # FIXME: for some reason mac's different from 10 bytes do not work
        # (at all), find out why, and find out if we need to do something
        # about this - AT.
        self.mac = 10

    def encrypt(self, message, public_key):
        """Encrypts the given message with the provided public key.

           @param message The message to encrypt.
           @param public_key The public key to use.
           @return An encrypted version of @message.
        """
        assert type(message) is bytes
        cipher = seccure.encrypt(message, public_key, mac_bytes=self.mac)
        self.logger.debug("Encrypted " + str(len(message)) + " bytes to '" + public_key.decode("utf-8") + "'")
        return cipher

    def encrypt_compress_json(self, dictionary, public_key):
        """Encrypts and compresses the given dictionary.
           This is a convenience function which automatically builds a json representation of
           the dictionary provided, compresses it, and then encrypts the compressed representation.

           @param dictionary The Python dictionary to encrypt/compress.
           @param public_key The public key to use.
        """
        assert type(dictionary) is dict
        msg = json.dumps(dictionary, sort_keys=True).encode('utf-8')
        return self.encrypt(zlib.compress(msg, 9), public_key)

    def decrypt(self, cipher, private_key):
        """Decrypts a message with the provide private key.
        
           @param cipher The encrypted message.
           @param private_key The key to use for decryption.
           @return The decrypted message.
        """
        assert type(cipher) is bytes
        # TODO: This should probably raise some type of exception when decryption fails ...
        message = seccure.decrypt(cipher, private_key)
        self.logger.debug("Decrypted " + str(len(message)) + " bytes")
        return message

    def decrypt_decompress_json(self, cipher, private_key):
        """Decrypts and decompresses a message.
           See encrypt_compress_json() for details.

           @param cipher The message to decrypt.
           @param private_key The private key to use for decryption.
           @return A Python dictionary.
        """
        # Convenience method
        raw_txt = zlib.decompress(self.decrypt(cipher, private_key))
        return json.loads(raw_txt.decode('utf-8'))

    def sign(self, message, private_key):
        """Signs a message with a private_key.

           @param message The message to sign.
           @param private_key The private key to use for signing.
           @return A signature which can be verified with the public key
                   that pairs with @private_key.
        """
        # sign:
        signature = seccure.sign(message, private_key).decode('utf-8')
        self.logger.debug("Signed " + str(len(message)) + " bytes with private key")
        return signature

    def verify(self, message, signature, public_key):
        """Verifies a signature.
           
           @param message The message that was signed.
           @param signature The signature.
           @param public_key The key to use to verify the signature.
        """

        authentic = seccure.verify(message, signature, public_key)
        self.logger.debug("Verified " + str(len(message)) + " bytes against key '" + public_key.decode("utf-8") + "', authentic = " + str(authentic))
        return authentic

# TODO: Add some decent unit tests here ...
# WB: Check testencryption.py
# AT: Cool :) Let's extend that with some tests and perhaps build a UnitTest suite around this.
#     also for other (future) components.
#
