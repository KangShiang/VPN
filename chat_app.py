import hashlib
import json
import random
import sys
import aes
from datetime import datetime
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

inputVal = None

# Calls the encrypt function in the aes.py file
def encrypt_auth( data, key ):
    return aes.encrypt(msg=data, key=key)

# Calls the decrypt function in the aes.py file
def decrypt_auth( data, key ):
    return aes.decrypt(msg=data, key=key)

scheduled_loss = False
timer_connection = None
def timer_callback(dt):
    global timer_connection
    global scheduled_loss
    scheduled_loss = True
    print "KILL CONNECTION"
    timer_connection.loseConnection()
    Clock.unschedule(timer_callback)

# Get half of Diffie-Hellman
def getHalfDiffieHellman():
    # Generate random pseudorandom number for a
    # Arbitrary values here (2^2500 gives a number with the number of digits > 618)
    a = random.randint( 4800, 5000 )

    # Generate half of the Diffie-Hellman exchange
    gaModP = ( g**a ) % p
    return ( a, gaModP )

# Initiates the first message from client to server
def client_initiate(conn):
    global myNonce
    myNonce = int(random.randrange( 1, 100000000, 2 ))
    # Not sure what the message is to send or what's the best way
    # of putting the message and the nonce together. For the time
    # being, just concatenating the values together
    sendVal = []
    sendVal.append( "ClientInit" )
    sendVal.append( str( myNonce ) )
    sendVal = json.dumps( sendVal )
    conn.write(sendVal)
    print str(datetime.utcnow()) + " -- Sending Nounce to Server"
    print sendVal
    print ""
    return

# The server challenge response message to the client
def server_reply(conn, recvMsg):
    print str(datetime.utcnow()) + " -- Input From Client:"
    print recvMsg
    print ""
    try:
        recvMsg, recvNonce = json.loads( recvMsg )
        #obj = json.loads( recvMsg )
    except TypeError:
        # The loaded values were not correct
        print "The received values were not in the correct format"
        return

    # Check the initialization message
    if recvMsg != "ClientInit":
        "Did not receive correct initialization message"
        return
    b, gbModP = getHalfDiffieHellman()

    # Generate nonce
    # Server always gets an even number
    global server_Nounce
    global temp_b 
    temp_b = b
    serverNonce = random.randrange( 0, 100000000, 2 )
    server_Nounce = serverNonce
    # Encrypt and send a challenge response
    sendVal = []
    sendVal.append( str( serverNonce ) )

    # msg is the message to encrypt
    msg = []
    msg.append( "Server" )
    msg.append( str( recvNonce ) )
    msg.append( str( gbModP ) )
    # Dump the msg list into a json string
    msg = json.dumps( msg )
    sendVal.append( encrypt_auth( data=msg, key=k_ab ) )
    # Send the entire message
    sendVal = json.dumps( sendVal )
    print str(datetime.utcnow()) + " -- Sending E{\"Server\", ClientNounce, g^b mod p, K_ab}, ServerNounc"
    print sendVal
    print ""
    return sendVal

# The client's reply message to the server's challenge request
def client_reply(recvMsg):
    print str(datetime.utcnow()) + " -- Receiving E{\"Server\", ClientNounce, g^b mod p, K_ab}, ServerNounc"
    print recvMsg
    print ""
    client = ""
    my = ""
    serverNonce = ""
    try:
        s_Nonce, encryptedData = json.loads( recvMsg )
        serverNonce = str(s_Nonce)
    except TypeError:
        # The loaded values were not correct
        print "The received values were not in the correct format"
        return

    try:
        msg, clientNonce, gbModP = json.loads( decrypt_auth( encryptedData, k_ab ) )
        print "Checking..."
        print msg
        client = str(clientNonce)
        my = str(myNonce)
        print client == my
    except TypeError:
        # The loaded values were not correct
        print "The received values were not in the correct format"
        return

    # Check the message contents. If values aren't what we expect
    # then stop the mutual authentication
    # Check the sent message
    if msg != "Server":
        print "Authentication failed, msg is not Server"
        return

    # Check the received nonce
    if client != my:
        print "Authentication failed, clientNonce != myNonce"
        return

    a, gaModP = getHalfDiffieHellman()
    # Determine the session key
    global k_s
    k_s = ( int(gbModP) ** a ) % p
    m = hashlib.md5()
    m.update(str(k_s))
    k_s = m.hexdigest()
    # "Forget" the value of "a" so that attackers can't find the value in the future
    a = None
    print k_ab
    print inputVal
    # Encrypt the different values
    msg = []
    msg.append( "Client" )
    msg.append( serverNonce )
    msg.append( str( gaModP ) )
    msg = json.dumps( msg )
    sendVal = []
    sendVal.append( encrypt_auth( data=msg, key=k_ab ) )
    sendVal = json.dumps( sendVal )
    print sendVal
    # Send the values
    return sendVal

def server_recv(recvMsg):
    global k_s
    recvMsg = decrypt_auth( recvMsg, k_ab )
    try:
        msg, serverNonce, gaModP = json.loads( recvMsg )
    except TypeError:
        # The loaded values were not correct
        print "The received values were not in the correct format"
        return
    print msg
    print 
    # Check the message contents. If values aren't what we expect
    # then stop the mutual authentication
    if msg != "Client":
        print "Authentication failed"
        return

    if str(serverNonce) != str(server_Nounce):
        print "Authentication failed, serverNonce"
        return

    # Determine the session key
    k_s = ( int(gaModP) ** temp_b ) % p
    m = hashlib.md5()
    m.update(str(k_s))
    k_s = m.hexdigest()
    global temp_b
    temp_b = ""
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

#######################################################################################################

#install_twisted_rector must be called before importing the reactor
from kivy.support import install_twisted_reactor
install_twisted_reactor()
from kivy.lang import Builder
from kivy.uix.scrollview import ScrollView
from kivy.properties import StringProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
#A simple Client that send messages to the echo server
from twisted.internet import reactor, protocol
from twisted.internet.error import CannotListenError
from kivy.clock import Clock

# Variables for connection establishment
G_connection = ""
address = "127.0.0.1"
port = "8080"
secret = ""
mode = "Server"
connector = None
connected = False
received = False
is_authenticated = False
is_client_initializing = False
myNonce = ""
k_s = ""
server_Nounce =""
temp_b = ""
next_button = False

class EchoClient(protocol.Protocol):

    def connectionMade(self):
        self.factory.app.on_connection(self.transport)

    def dataReceived(self, data):
        global is_authenticated
        if is_authenticated:
            data = aes.decrypt(data, str(k_s))
            
            print "Decrypted Message:"
            print data
            print str(k_s)
            
            self.factory.app.print_message("Other: " + data)
        else:
            if mode == "Server":
                global is_client_initializing
                if is_client_initializing == False:
                    connection = self.factory.app.connection
                    rslt = server_reply(conn=connection,recvMsg=data)
                    is_client_initializing = True;
                    self.factory.app.print_message(str(datetime.utcnow()) + " -- Received \"ClientInit\",ClientNounce from client")
                    connection.write(rslt)
                else:
                    self.factory.app.print_message(str(datetime.utcnow()) + " -- Authentication is done")    
                    server_recv(data)
                    is_authenticated = True
                    is_client_initializing = False;

            else:
                connection = self.factory.app.connection
                rslt = client_reply(recvMsg=data)
                is_authenticated = True
                self.factory.app.print_message(str(datetime.utcnow()) + " -- Server Sent Nounce")
                self.factory.app.print_message(str(datetime.utcnow()) + " -- Authentication is done")
                connection.write(rslt)
                

    def connectionLost(self, reason):
        global scheduled_loss
        global received
        global connected

        connected = False
        if mode == 'Server':
            Clock.unschedule(timer_callback)
            received = False
            connected = False
            self.factory.app.print_message("connection lost... regen time!")
            if not scheduled_loss:
                App.get_running_app().stop()
        scheduled_loss = False
        ###
        #Time to renegotiate
        ###


class EchoFactory(protocol.ClientFactory):
    protocol = EchoClient

    def __init__(self, app):
        self.app = app

    def clientConnectionLost(self, conn, reason):
        global connected
        connected = False
        self.app.print_message("connection lost")
        ### HUGO WEAVING
        ### REGENERATION     

        ### REGENERATION BABY
        ### HYDRA
        #App.get_running_app().stop()

    def clientConnectionFailed(self, conn, reason):
        self.app.print_message("connection failed")
        App.get_running_app().stop()

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout


Builder.load_string('''
<ScrollableLabel>:
    Label:
        multiline: True
        size_hint_y: None
        height: self.texture_size[1]
        text_size: 700, None
        text: root.text
''')

class ScrollableLabel(ScrollView):
    text = StringProperty('')


def toggle_pressed(instance):
    global mode
    if instance.state == "normal":
        mode = "Server"
        instance.text = "Server"
    else:
        mode = "Client"
        instance.text = "Client"

#TODO:
def set_ip(instance, *args):
    global address
    address = instance.text

def set_port(instance, *args):
    global port
    port = instance.text

def set_secret(instance, *args):
    global k_ab
    global inputVal
    m = hashlib.md5()
    m.update( instance.text )
    inputVal = instance.text
    k_ab = m.hexdigest()


class InfoPage(Screen):

    def connect(self,*args):
        address = self.ip.text
        port = self.port.text
        secret = self.secret.text
        self.manager.current = "ChatPage"

    def __init__(self, **kwargs):
        super (InfoPage, self).__init__(**kwargs)
        root = FloatLayout()
        self.toggle = ToggleButton(text='Server', font_size=14, pos_hint={'center_x': .5, 'center_y': .90},size_hint=(None, None))
        self.toggle.bind(on_press=toggle_pressed)

        ip_label = Label(text='IP Address', pos_hint={'center_x': .5, 'center_y': .80}, size_hint=(None, None),
                         width=500, height=40)
        self.ip = TextInput(text=address, multiline=False, pos_hint={'center_x': .5, 'center_y': .75}, size_hint=(None, None),width=500, height=40)
        self.ip.bind(text=set_ip)

        port_label = Label(text='Port', pos_hint={'center_x': .5, 'center_y': .7}, size_hint=(None, None), width=500,
                           height=40)
        self.port = TextInput(text=port, multiline=False, pos_hint={'center_x': .5, 'center_y': .65}, size_hint=(None, None), width=500, height=40)
        self.port.bind(text=set_port)

        secret_label = Label(text='Secret', pos_hint={'center_x': .5, 'center_y': .6}, size_hint=(None, None),
                             width=500, height=40)
        self.secret = TextInput(multiline=False, pos_hint={'center_x': .5, 'center_y': .55}, size_hint=(None, None),
                           width=500, height=40)

        self.secret.bind(text=set_secret)

        connect_button = Button(text="Connect", pos_hint={'center_x': .5, 'center_y': .45}, size_hint=(None, None),
                                width=250, height=40)
        connect_button.bind(on_press=self.connect)
        root.add_widget(self.toggle)
        root.add_widget(self.ip)
        root.add_widget(ip_label)
        root.add_widget(self.port)
        root.add_widget(port_label)
        root.add_widget(secret_label)
        root.add_widget(self.secret)
        root.add_widget(connect_button)
        self.add_widget(root)

class ChatPage(Screen):
    def on_enter(self):
        if mode == "Server":
            self.print_message("I am the SERVER")
            try:
                connector = reactor.listenTCP(int(port), EchoFactory(self), interface=address)
            except CannotListenError:
                print str(datetime.utcnow()) + " -- Server Already Created"
                print ""
                App.get_running_app().stop()
        else:
            self.print_message("I am the CLIENT")
            connector = reactor.connectTCP(address, int(port), EchoFactory(self))

    def quit(self,*args):
        reactor.stop()
        #self.manager.current = "InfoPage"
        App.get_running_app().stop()

    def next(self,*args):
        global next_button
        next_button = True

    def send_with_auth(self,*args):
        # Ensure Mutual Authentication Here!
        if is_authenticated:
            self.send_message()

    def on_connection(self, connection):
        global connected
        global next_button
        if mode == "Server":
            self.print_message(str(datetime.utcnow()) + " -- I see client is connecting")   
        else: 
            self.print_message(str(datetime.utcnow()) + " -- I am connecting to the server")
            self.print_message(str(datetime.utcnow()) + " -- Sending \"ClientInit\",ClientNounce")
            client_initiate(conn=connection)

        if connected:
            App.get_running_app().stop()
        connected = True

        self.connection = connection
        
         # Server demands after a certain amount of time that things be renegotiated
        global timer_connection
        timer_connection = self.connection
        if mode == "Server":
            Clock.schedule_interval(timer_callback, 10)

    def send_message(self):
        msg = self.message.text
        if True:
        #try:
            self.connection
            self.print_message("Me: " + msg)
            if msg and self.connection:
                text = aes.encrypt(msg, str(k_s))
                print "Encrypthing messsagesss"
                print str(k_s)
                print text
                self.connection.write(text)
                self.message.text = ""
        #except:
        #    self.print_message("Please wait for a connection.")

    def print_message(self, msg):
        self.console.text += msg + "\n"

    def __init__(self, **kwargs):
        super (ChatPage,self).__init__(**kwargs)
        self.quit_button = Button(text="Quit", pos_hint={'center_x': .05, 'center_y': .95}, size_hint=(None, None), width=40, height=40)
        self.quit_button.bind(on_press=self.quit)
        self.next_button = Button(text="Next", pos_hint={'center_x': .95, 'center_y': .95}, size_hint=(None, None), width=40, height=40)
        self.next_button.bind(on_press=self.next)
        self.console = ScrollableLabel(text="",pos_hint={'center_x': .52, 'center_y': .4}, width=10)
        self.message = TextInput(multiline=True, pos_hint={'center_x': .45, 'center_y': .10}, size_hint=(None, None),
                           width=600, height=40)
        self.send_button = Button(text="Send", pos_hint={'center_x': .90, 'center_y': .10}, size_hint=(None, None), width=120, height=40)
        self.send_button.bind(on_press=self.send_with_auth)
        self.add_widget(self.next_button)
        self.add_widget(self.console)
        self.add_widget(self.quit_button)
        self.add_widget(self.message)
        self.add_widget(self.send_button)

# A simple kivy App, with a textbox to enter messages, and
# a large label to display all the messages received from
# the server
class TwistedChatApp(App):
    connection = None

    def build(self):
        sm = ScreenManager()
        sm.add_widget(InfoPage(name='InfoPage'))
        sm.add_widget(ChatPage(name='ChatPage'))
        apptools = App
        #self.connect_to_server()
        return sm

    def setup_gui(self):
        self.textbox = TextInput(size_hint_y=.1, multiline=False)
        self.textbox.bind(on_text_validate=self.send_message)
        self.label = Label(text='connecting...\n')
        self.layout = BoxLayout(orientation='vertical')
        self.layout.add_widget(self.label)
        self.layout.add_widget(self.textbox)
        return self.layout


if __name__ == '__main__':
    TwistedChatApp().run()
