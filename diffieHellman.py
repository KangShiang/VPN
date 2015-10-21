import hashlib
import random
import sys

""" Prime and generator are public
Generator is typically 2 or 5"""
""" Values of p and g are taken from:
   https://datatracker.ietf.org/doc/rfc3526/?include_text=1 """

# Prime value
p = 0xFFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C62F356208552BB9ED529077096966D670C354E4ABC9804F1746C08CA18217C32905E462E36CE3BE39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9DE2BCBF6955817183995497CEA956AE515D2261898FA051015728E5A8AACAA68FFFFFFFFFFFFFFFF
print "The prime value is: " + str(p)

# Generator value
g = 2
print "The generator value is: " + str(g)

# Generate random pseudorandom number for A/B
# Arbitrary values here (2^2500 gives a number with the number of digits > 618)
a = random.randint( 2500, 50000 )

# Read user input values for K_AB
print "Please enter a value for K_AB:"
inputVal = sys.stdin.readline()
m = hashlib.sha512()
m.update( inputVal )
k_ab = m.hexdigest()

print "Please enter a value for A/B:"

"""inputVal = sys.stdin.readline()
m = hashlib.sha512()
m.update( inputVal )
val = m.hexdigest()"""

"""isInteger = False
while not isInteger:
   inputVal = sys.stdin.readline()
   try:
      val = long( inputVal )
      isInteger = True
   except ValueError:
      print "The value you entered is not an integer. Please try again:"

print val
print int( val, 16 )
"""

# Generate value to send
sendVal = ( g**a ) % p
print sendVal

# Generate nonce
# Choose a random odd number
# TODO: Add check so that clients will always get odd numbers and
# servers will always get an even number
nonce = random.randrange( 0, 100000000, 2 )
nonce = random.randrange( 1, 100000000, 2 )

# TODO: Get message (i.e. the IP)


# TODO: Send value to other computer

# TODO: Receive value from other computer


