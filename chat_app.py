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

# Variables for connection establishment
address = "127.0.0.1"
port = "8080"
secret = ""
mode = "Server"
connector = None
connected = False
received = False

def encrypt(data):
    # called on send
    return data

def decrypt(data):
    # called on receive
    return data

class EchoClient(protocol.Protocol):
    def handle_first_out(self):
        # Called on connection made
        # can send message with self.transport.write("str") 
        pass
    
    def handle_first_in(self,data):
        # called on first received data
        return data

    def connectionMade(self):
        self.factory.app.on_connection(self.transport)
        self.handle_first_out()

    def dataReceived(self, data):
        global received
        if not received:
            data = self.handle_first_in(data)
        else:
            data = decrypt(data)
            received = True
        self.factory.app.print_message("Other: " + data)
    
    def connectionLost(self, reason):
        App.get_running_app().stop()


class EchoFactory(protocol.ClientFactory):
    protocol = EchoClient

    def __init__(self, app):
        self.app = app

    def clientConnectionLost(self, conn, reason):
        self.app.print_message("connection lost")
        App.get_running_app().stop()
        

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
        size_hint_y: None
        height: self.texture_size[1]
        text_size: self.width, None
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
    global secret
    secret = instance.text

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
        print port
        if mode == "Server":
            self.print_message("I am the SERVER")
            try:
                connector = reactor.listenTCP(int(port), EchoFactory(self), interface=address)
            except CannotListenError:
                print "Server Already Created"
                App.get_running_app().stop()
        else:
            self.print_message("I am the CLIENT")
            connector = reactor.connectTCP(address, int(port), EchoFactory(self))

    def quit(self,*args):
        try:
            self.connection
            print "DISCONNECTOR"
            self.connection.loseConnection()
            if connector:
                connector.disconnect()
        except:
            pass
        reactor.stop()
        #self.manager.current = "InfoPage"
        App.get_running_app().stop()

    def send(self,*args):
        self.console.text = self.console.text + "\nMe: " + self.message.text

    def on_connection(self, connection):
        global connected
        if connected:
            App.get_running_app().stop()
        connected = True
        self.print_message("connected succesfully!")
        self.connection = connection

    def send_message(self, *args):
        msg = self.message.text
        try:
            self.connection
            self.print_message("Me: " + msg)
            if msg and self.connection:
                self.message.text = encrypt(self.message.text)
                self.connection.write(str(self.message.text))
                self.message.text = ""
        except:
            self.print_message("Please wait for a connection.")

    def print_message(self, msg):
        self.console.text += msg + "\n"

    def __init__(self, **kwargs):
        super (ChatPage,self).__init__(**kwargs)
        self.quit_button = Button(text="Quit", pos_hint={'center_x': .05, 'center_y': .95}, size_hint=(None, None), width=40, height=40)
        self.quit_button.bind(on_press=self.quit)
        self.console = ScrollableLabel(text="",pos_hint={'center_x': .52, 'center_y': .4})
        self.message = TextInput(multiline=True, pos_hint={'center_x': .45, 'center_y': .10}, size_hint=(None, None),
                           width=600, height=40)
        self.send_button = Button(text="Send", pos_hint={'center_x': .90, 'center_y': .10}, size_hint=(None, None), width=120, height=40)
        self.send_button.bind(on_press=self.send_message)
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
