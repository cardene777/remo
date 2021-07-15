from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

import japanize_kivy


GUI = Builder.load_file("remo.kv")


class Remo(App):
    def build(self):
        return GUI


if __name__ == '__main__':
    Remo().run()