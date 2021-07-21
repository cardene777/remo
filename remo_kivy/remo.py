from kivy.app import App
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.button import Button
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


class ReviewScreen(Screen):
    pass


class MainApp(MDApp):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.firebase_url = "https://remo-app-7-default-rtdb.firebaseio.com/.json"
        self.user_idToken = ""
        self.user_localId = ""

    def build(self):
        self.root = Builder.load_file("remo.kv")

    def on_start(self):
        pass

    def change_screen(self, screen_name):
        screen_manager = self.root.ids["screen_manager"]
        screen_manager.current = screen_name

    def sign_out(self):
        self.root.ids.firebase_login_screen.log_out()
        self.change_screen('firebase_login_screen')

    def add_data(self, text):
        """
        データ追加
        :param text: add keyword
        :return:
        """
        json_data: str = '{"name": "%s", "text": "%s", "review": 0}' % (self.user_localId, text)
        res = requests.post(url=self.firebase_url, json=json.loads(json_data))
        self.root.ids["search_screen"].ids["search_word"].text = ""
        self.change_screen("home_screen")

    def get_data(self):
        """
        データ取得
        :return:
        """
        res = requests.get(url=self.firebase_url)
        res_data = res.json()
        remo_display = self.root.ids['review_screen'].ids['remo_data']
        remo_datas: list = []
        for r in res_data:
            if res_data[r]["name"] == self.user_localId:
                remo_datas.append(res_data[r])
                data = Button(text=str(remo_datas))
                remo_display.add_widget(data)

        screen_manager = self.root.ids["screen_manager"]
        screen_manager.current = "review_screen"


if __name__ == '__main__':
    MainApp().run()

