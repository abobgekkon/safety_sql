__author__= 'S.N. Pastuhov'
__copyright__= 'Copyright (c) 2019, S.N. Pastuhov'
__license__= 'Apache License, Version 2.0'

import rsa

class rsa_code:
    def get_new_keys(self):
        (pubkey, privkey) = rsa.newkeys(512)
        return pubkey, privkey

    def rsa_encode(self, data, pubkey):
        data = bytes(data, "UTF-8")
        data_enc = rsa.encrypt(data, pubkey)
        return data_enc

    def rsa_decode(self, data, privkey):
        data_dec = rsa.decrypt(data, privkey)
        return data_dec.decode("UTF-8")
