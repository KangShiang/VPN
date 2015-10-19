import kivy
from kivy.uix.button import Button
kivy.require('1.0.6') # replace with your current kivy version !

from kivy.app import App
from kivy.uix.label import Label


class MyApp(App):

    def build(self):
    	button = Button(text='Hello world', font_size=14)
        return button


if __name__ == '__main__':
    MyApp().run()