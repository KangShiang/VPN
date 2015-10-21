from Crypto.Cipher import AES
import Crypto.Random

# relevant urls
# http://eli.thegreenplace.net/2010/06/25/aes-encryption-of-files-in-python-with-pycrypto/
# http://stackoverflow.com/questions/14716338/pycrypto-how-does-the-initialization-vector-work
#  

key = '0123456789abcdef'
mode = AES.MODE_CBC
text = 'j' * 64 + 'i' * 128

def encrypt(msg, key):
  iv = Crypto.Random.OSRNG.posix.new().read(AES.block_size)
  mode = AES.MODE_CBC
  encryptor = AES.new(key, mode, iv)
  ciphertext = encryptor.encrypt(msg)
  return ciphertext

#TODO: padding, prefix ciphertext with IV, encode as hex?
print(encrypt(text, key))

def decrypt(msg, key):
  # get iv from first part of msg
  iv = Crypto.Random.OSRNG.posix.new().read(AES.block_size) 
  decryptor = AES.new(key, mode, iv)
  plaintext = decryptor.decrypt(msg)
  return plaintext

print(decrypt(encrypt(text, key), key))


