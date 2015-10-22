from Crypto.Cipher import AES
import Crypto.Random
import base64

# relevant urls
# http://eli.thegreenplace.net/2010/06/25/aes-encryption-of-files-in-python-with-pycrypto/
# http://stackoverflow.com/questions/14716338/pycrypto-how-does-the-initialization-vector-work
# http://stackoverflow.com/questions/12524994/encrypt-decrypt-using-pycrypto-aes-256 

key = '0123456789abcdef'
mode = AES.MODE_CBC
text = 'python does some weird string comparison'

# pads the string s to make its length a multiple of 16
# how the padding works:
def pad(s):
  return s + (16 - len(s) % 16) * chr(16 - len(s) % 16)

# undoes the padding
def unpad(s):
  return s[:-ord(s[len(s)-1:])]

def encrypt(msg, key):
  msg2 = pad(msg)
  iv = Crypto.Random.OSRNG.posix.new().read(AES.block_size)
  print("iv: " + iv )
  mode = AES.MODE_CBC
  encryptor = AES.new(key, mode, iv)
  ciphertext = encryptor.encrypt(msg2)
  print("ctext: " + ciphertext)
  return base64.b64encode(iv + ciphertext)


print(encrypt(text, key))

def decrypt(msg, key):
  msg2 = base64.b64decode(msg)
  # get iv from first part of msg
  iv = msg2[:16] 
  print("iv: " + iv)
  decryptor = AES.new(key, mode, iv)
  plaintext = decryptor.decrypt(msg2[16:])
  print("ptext: " + plaintext)
  return unpad(plaintext)

print("decrypting: ")

print(decrypt(encrypt(text, key), key))


