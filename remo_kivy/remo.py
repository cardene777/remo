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


class AddMemoScreen(Screen):
    def text_display(self):
        self.memo_title.text = ""
        self.memo_text.text = ""


class MemoScreen(Screen):
    pass


class SettingsScreen(Screen):
    pass


class MemoListScreen(Screen):
    pass


class MemoDetailScreen(Screen):
    pass


class ErrorScreen(Screen):
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

    def change_screen(self, screen_name, *args):
        screen_manager = self.root.ids["screen_manager"]
        if screen_name == "error_screen":
            self.root.ids["error_screen"].ids["error_message"].text = str(args[0])
        screen_manager.current = screen_name

    def sign_out(self):
        self.root.ids.firebase_login_screen.log_out()
        self.change_screen('firebase_login_screen')

    def add_data(self, title, text, review_day):
        """
        データ追加
        :param title:
        :param review_day: review day
        :param text: add keyword
        :return:
        """
        json_data: str = '{"name": "%s", "title": "%s",  "text": "%s", "review": 0, "review_day": "%s"}' \
                         % (self.user_localId, title, text, review_day)
        res = requests.post(url=self.firebase_url, json=json.loads(json_data))
        self.root.ids["add_memo_screen"].ids["memo_title"].text = ""
        self.root.ids["add_memo_screen"].ids["memo_text"].text = ""
        self.change_screen("home_screen")

    def get_data(self):
        """
        データ取得
        :return:
        """

        def review_detail(instance):
            review_res = requests.get(url=self.firebase_url)
            review_res_data = review_res.json()
            for rr in review_res_data:
                if review_res_data[rr]["name"] == self.user_localId and review_res_data[rr]["title"] == instance.text:
                    print("ok")
                    self.root.ids['memo_detail_screen'].ids['title_label'].text = review_res_data[rr]["title"]
                    self.root.ids['memo_detail_screen'].ids['text_label'].text = review_res_data[rr]["text"]
                    self.root.ids['memo_detail_screen'].ids['review_label'].text = str(review_res_data[rr]["review"])
                    self.root.ids['memo_detail_screen'].ids['review_day_label'].text = review_res_data[rr][
                        "review_day"]
                    review_screen_manager = self.root.ids["screen_manager"]
                    review_screen_manager.current = "memo_detail_screen"

        res = requests.get(url=self.firebase_url)
        res_data = res.json()
        remo_display = self.root.ids['memo_list_screen'].ids['remo_data']
        remo_datas: list = []
        remo_display.clear_widgets()
        for r in res_data:
            if res_data[r]["name"] == self.user_localId:
                remo_datas.append(res_data[r])
                title: str = str(res_data[r]["title"])
                data = Button(text=f"{title}", font_size=50, on_release=review_detail)
                remo_display.add_widget(data)

        screen_manager = self.root.ids["screen_manager"]
        screen_manager.current = "memo_list_screen"


if __name__ == '__main__':
    MainApp().run()
