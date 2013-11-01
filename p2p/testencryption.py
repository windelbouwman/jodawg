

from lib.encryption import Encryption, KeyPair

import unittest

class EncryptionTestCase(unittest.TestCase):
    def testEncrypt(self):
        kp = KeyPair()
        e = Encryption()
        msg = 'hello world'
        cipher = e.encrypt(msg, kp.public_key)
        msg2 = e.decrypt(cipher, kp.private_key)
        self.assertEqual(msg, msg2)



if __name__ == '__main__':
    unittest.main()


