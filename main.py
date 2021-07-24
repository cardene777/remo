from kivy.app import App
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.image import Image
import japanize_kivy

import requests
import json
import datetime
import random


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


class CheckMemoScreen(Screen):
    pass


class MemoUpdateScreen(Screen):
    pass


class MemoDeleteScreen(Screen):
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
        self.root = Builder.load_file("main.kv")

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

    def insert_data(self, now_screen, title, text, review, review_day, next_screen):
        self.root.ids[now_screen].ids['title_label'].text = title
        self.root.ids[now_screen].ids['text_label'].text = text
        self.root.ids[now_screen].ids['review_label'].text = review
        self.root.ids[now_screen].ids['review_day_label'].text = review_day

        self.change_screen(next_screen)

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
                    self.insert_data("memo_detail_screen", review_res_data[rr]["title"], review_res_data[rr]["text"],
                                     str(review_res_data[rr]["review"]), review_res_data[rr]["review_day"],
                                     "memo_detail_screen"
                                     )

        res = requests.get(url=self.firebase_url)
        res_data = res.json()
        remo_display = self.root.ids['memo_list_screen'].ids['remo_data']
        remo_datas: list = []
        remo_display.clear_widgets()
        for r in res_data:
            print(self.user_localId, res_data)
            if res_data[r]["name"] == self.user_localId:
                remo_datas.append(res_data[r])
                title: str = str(res_data[r]["title"])
                data = Button(text=f"{title}", font_size=60, on_release=review_detail,
                              background_normal='', background_color="#669999")
                remo_display.add_widget(data)

        self.change_screen("memo_list_screen")

    def check_memo(self):
        res = requests.get(url=self.firebase_url)
        res_data = res.json()
        todays = datetime.date.today()
        memos: list = []
        for r in res_data:
            memo_year, memo_month, memo_day = str(res_data[r]["review_day"]).split("-")
            memo_review_day = datetime.date(int(memo_year), int(memo_month), int(memo_day))
            if res_data[r]["name"] == self.user_localId and memo_review_day <= todays:
                memos.append(res_data[r])
        if not memos:
            self.root.ids['check_memo_screen'].ids['finish_button'].text = ""
            self.root.ids['check_memo_screen'].ids['finish_button'].disabled = True
            self.root.ids['check_memo_screen'].ids['next_memo'].text = ""
            self.root.ids['check_memo_screen'].ids['next_memo'].disabled = True
            self.root.ids['check_memo_screen'].ids['error_label'].text = "復習するメモはありません。"

            self.insert_data("check_memo_screen", "", "", "", "", "check_memo_screen")

        else:
            memo = random.choice(memos)
            self.root.ids['check_memo_screen'].ids['finish_button'].text = "完了"
            self.root.ids['check_memo_screen'].ids['finish_button'].disabled = False
            self.root.ids['check_memo_screen'].ids['next_memo'].text = "次のメモを復習する"
            self.root.ids['check_memo_screen'].ids['next_memo'].disabled = False
            self.root.ids['check_memo_screen'].ids['error_label'].text = ""

            self.insert_data("check_memo_screen", memo["title"], memo["text"], str(memo["review"]),
                             memo["review_day"], "check_memo_screen")

    def check_finish(self, title, text, review, review_day):
        review: int = int(review)
        res = requests.get(url=self.firebase_url)
        res_data = res.json()
        today = datetime.date.today()
        for r in res_data:
            if res_data[r]["name"] == self.user_localId and res_data[r]["title"] == title:
                if review == 0:
                    new_review_day = str(today + datetime.timedelta(days=1))
                    review += 1
                elif review == 1:
                    new_review_day = str(today + datetime.timedelta(days=3))
                    review += 1
                elif review == 2:
                    new_review_day = str(today + datetime.timedelta(days=7))
                    review += 1
                elif review == 3:
                    new_review_day = str(today + datetime.timedelta(days=25))
                    review += 1
                elif review == 4:
                    new_review_day = str(today + datetime.timedelta(days=32))
                    review += 1
                elif review == 5:
                    new_review_day = str(today + datetime.timedelta(days=50))
                    review += 1
                elif review == 6:
                    new_review_day = str(today + datetime.timedelta(days=100))
                    review += 1
                elif review == 7:
                    new_review_day = str(today + datetime.timedelta(days=150))
                    review += 1
                elif review == 8:
                    new_review_day = str(today + datetime.timedelta(days=300))
                    review += 1
                else:
                    new_review_day = str(today + datetime.timedelta(days=365))
                    review += 1
                json_data: str = '{"name": "%s", "title": "%s",  "text": "%s", "review": %s, "review_day": "%s"}' \
                                 % (self.user_localId, title, text, review, new_review_day)
                res = requests.patch(url=f"https://remo-app-7-default-rtdb.firebaseio.com/{r}/.json",
                                     json=json.loads(json_data))

                self.root.ids['check_memo_screen'].ids['finish_button'].text = "完了"
                self.root.ids['check_memo_screen'].ids['finish_button'].disabled = True
                self.root.ids['check_memo_screen'].ids['next_memo'].text = "次のメモを復習する"
                self.root.ids['check_memo_screen'].ids['next_memo'].disabled = False
                self.root.ids['check_memo_screen'].ids['error_label'].text = ""

                self.insert_data("check_memo_screen", title, text, str(review), new_review_day, "check_memo_screen")

    def memo_update_display(self, title, text, review, review_day):
        self.insert_data("memo_update_screen", title, text, str(review), review_day, "memo_update_screen")

    def memo_delete_display(self, title, text, review, review_day):
        self.insert_data("memo_delete_screen", title, text, str(review), review_day, "memo_delete_screen")

    def memo_update(self, title, text, review, review_day):
        res = requests.get(url=self.firebase_url)
        res_data = res.json()
        for r in res_data:
            if res_data[r]["name"] == self.user_localId and res_data[r]["title"] == title:
                json_data: str = '{"name": "%s", "title": "%s",  "text": "%s", "review": %s, "review_day": "%s"}' \
                                 % (self.user_localId, title, text, review, review_day)
                res = requests.patch(url=f"https://remo-app-7-default-rtdb.firebaseio.com/{r}/.json",
                                     json=json.loads(json_data))

                self.insert_data("memo_detail_screen", title, text, str(review), review_day, "memo_detail_screen")

    def memo_delete(self, title):
        res = requests.get(url=self.firebase_url)
        res_data = res.json()
        for r in res_data:
            if res_data[r]["name"] == self.user_localId and res_data[r]["title"] == title:
                res = requests.delete(url=f"https://remo-app-7-default-rtdb.firebaseio.com/{r}/.json")

                self.get_data()


if __name__ == '__main__':
    MainApp().run()
