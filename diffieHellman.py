import hashlib
import json
import random
import sys

""" Prime (p) and generator (g) are public
    Generator is typically 2 or 5
    Values of p and g are taken from:
    https://datatracker.ietf.org/doc/rfc3526/?include_text=1
    """
# Prime value
p = 0xFFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C62F356208552BB9ED529077096966D670C354E4ABC9804F1746C08CA18217C32905E462E36CE3BE39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9DE2BCBF6955817183995497CEA956AE515D2261898FA051015728E5A8AACAA68FFFFFFFFFFFFFFFF
print "The prime value is: " + str(p)

# Generator value
g = 2
print "The generator value is: " + str(g)

# TODO: Take out later
mode = "Client"

# Read user input values for K_AB
print "Please enter a secret value (K_AB):"
inputVal = sys.stdin.readline()
# Hash the entered value
m = hashlib.sha512()
m.update( inputVal )
k_ab = m.hexdigest()

def encrypt( data, key ):
    # TODO: Do stuff here
    return data

def decrypt( data, key ):
    # TODO: Do stuff here
    return data

def send( sendList ):
    # TODO: Do stuff here
    pass

def receive():
    # TODO: Do stuff here
    receivedMsg = []
    return receivedMsg

# Get half of Diffie-Hellman
def getHalfDiffieHellman():
    # Generate random pseudorandom number for a
    # Arbitrary values here (2^2500 gives a number with the number of digits > 618)
    a = random.randint( 2500, 50000 )

    # Generate half of the Diffie-Hellman exchange
    gaModP = ( g**a ) % p
    return ( a, gaModP )

# Function to establish mutual authentication
def mutualAuthentication():
    # Server and client should do different things
    # NOTE: mode is value in chat_app.py (adjust later)
    if mode is "Server":
        # Server node

        # Wait for request from client
        # None of this information will be encrypted
        recvMsg = receive()
        try:
            recvMsg, clientNonce = json.loads( recvMsg )
        except TypeError:
            # The loaded values were not correct
            print "The received values were not in the correct format"
            return

        # Check the initialization message
        if recvMsg is not "ClientInit":
            "Did not receive correct initialization message"
            return

        b, gbModP = getHalfDiffieHellman()

        # Generate nonce
        # Server always gets an even number
        myNonce = random.randrange( 0, 100000000, 2 )

        # Encrypt and send a challenge response
        sendVal = []
        sendVal.append( str( myNonce ) )

        # msg is the message to encrypt
        msg = []
        msg.append( "Server" )
        msg.append( str( clientNonce ) )
        msg.append( str( gbModP ) )
        # Dump the msg list into a json string
        msg = json.dumps( msg )
        sendVal.append( encrypt( msg, k_ab ) )

        # Send the entire message
        sendVal = json.dumps( sendVal )
        send( sendVal )

        # Wait for client's response
        recvMsg = receive()

        # TODO: Verify client's response
        recvMsg = decrypt( recvMsg, k_ab )
        try:
            msg, serverNonce, gaModP = json.loads( recvMsg )
        except TypeError:
            # The loaded values were not correct
            print "The received values were not in the correct format"
            return

        # Check the message contents. If values aren't what we expect
        # then stop the mutual authentication
        if msg is not "Client":
            print "Authentication failed"
            return

        if serverNonce is not myNonce:
            print "Authentication failed"
            return

        # Determine the session key
        k_s = ( gaModP ** b ) % p

        # "Forget" the value of "b" so that attackers can't find the value in the future
        b = None
    else:
        # Client Mode

        # Generate nonce
        # Client always gets an odd number
        myNonce = random.randrange( 1, 100000000, 2 )

        # Not sure what the message is to send or what's the best way
        # of putting the message and the nonce together. For the time
        # being, just concatenating the values together
        sendVal = []
        sendVal.append( "ClientInit" )
        sendVal.append( str( myNonce ) )
        sendVal = json.dumps( sendVal )
        send( sendVal )

        recvMsg = receive()
        try:
            serverNonce, encryptedData = json.loads( recvMsg )
        except TypeError:
            # The loaded values were not correct
            print "The received values were not in the correct format"
            return

        try:
            msg, clientNonce, gbModP = json.loads( decrypt( encryptedData, k_ab ) )
        except TypeError:
            # The loaded values were not correct
            print "The received values were not in the correct format"
            return

        # Check the message contents. If values aren't what we expect
        # then stop the mutual authentication
        # Check the sent message
        if msg is not "Server":
            print "Authentication failed"
            return

        # Check the received nonce
        if clientNonce is not myNonce:
            print "Authentication failed"
            return

        a, gaModP = getHalfDiffieHellman()
        print gaModP

        # Determine the session key
        k_s = ( gbModP ** a ) % p

        # "Forget" the value of "a" so that attackers can't find the value in the future
        a = None

        # Encrypt the different values
        msg = []
        msg.append( "Client" )
        msg.append( str( serverNonce ) )
        msg.append( str( gaModP ) )
        msg = json.dumps( msg )
        sendVal = []
        sendVal.append( encrypt( msg, k_ab ) )
        sendVal = json.dumps( sendVal )

        # Send the values
        send( sendVal )

# TODO (This functionality is currently in chat_app.py)
def normalOperation():
    # TODO Implement timeout value
    return

mutualAuthentication()
normalOperation()

# Don't use the same keypair for signing as you do encryption
# Session keys limit the amount of data encrypted with any particular key
# - Also limits the damage if one session key is compromised
# - Provides confidentiality and integrity protection
# TODO: Make it so that the session key changes every X messages or
# after a certain period of time
# Session key is just K_s = g^(ab) mod p
# Right after K_s is computed, Alice and Bob must forget about their values of a and b
#
# TODO: Destroy key once finished using it
#
# Shared key K_AB will be used to encrypt the diffie hellman exchange
#
# Timestamps can be used in place of a nonce
# Will not be using timestamps, but algorithm is below
"""
To use in place of nonce
T = timestamp
K = Key
"I'm Alice", [{T, K}_Bob]_Alice -->
<-- [T + 1]_Bob
"""
