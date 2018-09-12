from Crypto.PublicKey import RSA 
from Crypto.Hash import SHA256 

class Authentication():
    def __init__(self, cfg):
        self._key = RSA.generate(2048)
        self._passphrase = "passphrase"
        self._private_key = self._key.exportKey(passphrase=self._passphrase, pkcs=8)
        self.public_key = self._key.publickey().exportKey()

    def sign_msg(self, msg):
        #hash = SHA256.new(msg.encode()).digest()
        hash = SHA256.new(msg).digest()
        return self._key.sign(hash, self._private_key)

def verify_signature(pub_key, signature, data):
    rsakey = RSA.importKey(pub_key) 
    hash = SHA256.new()  
    hash.update(data)
    return rsakey.verify(hash.digest(), signature)
