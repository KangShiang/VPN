import kivy
import vpn as VPN
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.properties import StringProperty
from kivy.lang import Builder
from kivy.app import App
from kivy.support import install_twisted_reactor
install_twisted_reactor()

kivy.require('1.0.6')  # replace with your current kivy version !
from twisted.internet.error import CannotListenError
from twisted.conch.stdio import runWithProtocol
from twisted.internet import reactor
from kivy.app import App
from kivy.uix.label import Label
from twisted.internet import reactor
import vpn

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
    if instance.state == "normal":
        instance.text = "Client"
    else:
        instance.text = "Server"

#TODO:
def on_enter(instance):
    print instance.text


class InfoPage(Screen):

	def connect(self,*args):
		self.manager.current = "ChatPage"
		vpn.start_server_client(kivyobj=self,reactor=reactor)

	def __init__(self, **kwargs):
		super (InfoPage, self).__init__(**kwargs)
		root = FloatLayout()
		self.toggle = ToggleButton(text='Client', font_size=14, pos_hint={'center_x': .5, 'center_y': .90},size_hint=(None, None))
		self.toggle.bind(on_press=toggle_pressed)

		ip_label = Label(text='IP Address', pos_hint={'center_x': .5, 'center_y': .80}, size_hint=(None, None),
                         width=500, height=40)
		ip = TextInput(text='', multiline=False, pos_hint={'center_x': .5, 'center_y': .75}, size_hint=(None, None),width=500, height=40)
		ip.bind(on_text_validate=on_enter)

		port_label = Label(text='Port', pos_hint={'center_x': .5, 'center_y': .7}, size_hint=(None, None), width=500,
                           height=40)
		port = TextInput(text='', multiline=False, pos_hint={'center_x': .5, 'center_y': .65}, size_hint=(None, None), width=500, height=40)
		port.bind(on_text_validate=on_enter)

		secret_label = Label(text='Secret', pos_hint={'center_x': .5, 'center_y': .6}, size_hint=(None, None),
		                     width=500, height=40)
		secret = TextInput(multiline=False, pos_hint={'center_x': .5, 'center_y': .55}, size_hint=(None, None),
		                   width=500, height=40)

		secret.bind(on_text_validate=on_enter)

		connect_button = Button(text="Connect", pos_hint={'center_x': .5, 'center_y': .45}, size_hint=(None, None),
		                        width=250, height=40)
		connect_button.bind(on_press=self.connect)
		root.add_widget(self.toggle)
		root.add_widget(ip)
		root.add_widget(ip_label)
		root.add_widget(port)
		root.add_widget(port_label)
		root.add_widget(secret_label)
		root.add_widget(secret)
		root.add_widget(connect_button)
		self.add_widget(root)


class ChatPage(Screen):
    
	def back(self,*args):
		self.manager.current = "InfoPage"

	def send(self,*args):
		self.console.text = self.console.text + "\nMe: " + self.message.text

	def __init__(self, **kwargs):
		super (ChatPage,self).__init__(**kwargs)
		back_button = Button(text="Back", pos_hint={'center_x': .05, 'center_y': .95}, size_hint=(None, None), width=40, height=40)
		back_button.bind(on_press=self.back)
		self.console = ScrollableLabel(text="",pos_hint={'center_x': .52, 'center_y': .4})
		self.message = TextInput(multiline=True, pos_hint={'center_x': .45, 'center_y': .10}, size_hint=(None, None),
		                   width=600, height=40)
		send_button = Button(text="Send", pos_hint={'center_x': .90, 'center_y': .10}, size_hint=(None, None), width=120, height=40)
		send_button.bind(on_press=self.send)
		self.add_widget(self.console)
		self.add_widget(back_button)
		self.add_widget(self.message)
		self.add_widget(send_button)



class MyApp(App):
    def build(self):
    	sm = ScreenManager()
        sm.add_widget(InfoPage(name='InfoPage'))
        sm.add_widget(ChatPage(name='ChatPage'))
        apptools = App
        return sm


if __name__ == '__main__':
    MyApp().run()
