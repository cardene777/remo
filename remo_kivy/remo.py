from kivy.app import App
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
# from kivy.core.image import Image
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
import japanize_kivy
import kivy.utils

import requests
import json


class ImageButton(ButtonBehavior, Image):
    pass


class HomeScreen(Screen):
    pass


class SearchScreen(Screen):
    def text_display(self):
        self.search_word.text = ""


class NoteScreen(Screen):
    pass


class SettingsScreen(Screen):
    pass


GUI = Builder.load_file("remo.kv")


class Remo(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.firebase_url = "https://remo-app-7-default-rtdb.firebaseio.com/.json"

    def build(self):
        return GUI

    def on_start(self):
        pass

    def change_screen(self, screen_name):
        screen_manager = self.root.ids["screen_manager"]
        screen_manager.current = screen_name

    def add_data(self, text):
        json_data: str = '{"name": "cardene", "text": "%s", "review": 0}' % text
        res = requests.post(url=self.firebase_url, json=json.loads(json_data))
        self.root.ids["search_screen"].ids["search_word"].text = ""
        self.change_screen("home_screen")

    def get_data(self):
        res = requests.get(url=self.firebase_url)
        self.root.ids["search_screen"].ids["search_word"].text = ""
        print(res.json())


if __name__ == '__main__':
    Remo().run()
