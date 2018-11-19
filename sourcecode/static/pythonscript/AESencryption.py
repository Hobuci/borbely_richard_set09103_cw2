from Crypto.Cipher import AES
import base64

BLOCK_SIZE = 16

def encrypt(key, string):
    PADDING = '{'

    pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING
    EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))


    cipher = AES.new(key)
    encrypted = EncodeAES(cipher, string)

    return encrypted


def decrypt(key, encryptedString):
    PADDING = '{'

    DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)

    cipher = AES.new(key)
    decrypted = DecodeAES(cipher, encryptedString)

    return decrypted
