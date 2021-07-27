from kivy.app import App
from kivy.lang import Builder
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
import japanize_kivy

import requests
import json
import datetime
import random
from functools import partial


class ImageButton(ButtonBehavior, Image):
    pass


class HomeScreen(Screen):
    pass


class AddScreen(Screen):
    pass


class AddMemoScreen(Screen):
    def text_display(self):
        self.memo.text = ""


class AddQuestionScreen(Screen):
    def text_display(self):
        self.question.text = ""
        self.answer.text = ""


class MemoScreen(Screen):
    pass


class SettingsScreen(Screen):
    pass


class MemoListScreen(Screen):
    pass


class MemoDetailScreen(Screen):
    pass


class QuestionDetailScreen(Screen):
    pass


class CheckMemoScreen(Screen):
    pass


class MemoUpdateScreen(Screen):
    pass


class MemoDeleteScreen(Screen):
    pass


class QuestionUpdateScreen(Screen):
    pass


class QuestionDeleteScreen(Screen):
    pass


class MainApp(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.firebase_url = "https://remo-app-7-default-rtdb.firebaseio.com/.json"

    def build(self):
        self.root = Builder.load_file("main.kv")

    def on_start(self):
        pass

    def change_screen(self, screen_name, *args):
        screen_manager = self.root.ids["screen_manager"]
        screen_manager.current = screen_name

    def insert_data(self, next_screen, review, review_day, memo="", question="", answer=""):
        """
        データ挿入して画面を変更
        :param review:
        :param review_day:
        :param next_screen:
        :param memo:
        :param question:
        :param answer:
        :return:
        """
        if memo != "":
            self.root.ids[next_screen].ids['memo_label'].text = memo
        else:
            self.root.ids[next_screen].ids['question_label'].text = question
            self.root.ids[next_screen].ids['answer_label'].text = answer
        self.root.ids[next_screen].ids['review_label'].text = review
        self.root.ids[next_screen].ids['review_day_label'].text = review_day

        self.change_screen(next_screen)

    def add_data(self, kind, review_day, text=None, question=None, answer=None):
        """
        データ追加
        :param answer:
        :param question:
        :param kind: data kind
        :param title:
        :param review_day: review day
        :param text: add keyword
        :return:
        """
        if kind == "memo":
            json_data: str = '{"memo": "%s", "review": 0, "review_day": "%s"}' \
                             % (text, review_day)
            self.root.ids["add_memo_screen"].ids["memo"].text = ""
        else:
            json_data: str = '{"question": "%s", "answer": "%s", "review": 0, "review_day": "%s"}' \
                             % (question, answer, review_day)
            self.root.ids["add_memo_screen"].ids["memo"].text = ""
        res = requests.post(url=self.firebase_url, json=json.loads(json_data))
        self.change_screen("home_screen")

    def answer_display(self, review, review_day, question, answer):
        """
        ボタンを押して回答を表示
        :param review: 復習回数
        :param review_day: 次回の復習日
        :param question: 質問
        :param answer: 回答
        :return:
        """
        self.root.ids["question_detail_screen"].ids['answer_label'].color = 1, 0, 0, 1
        self.insert_data("question_detail_screen", review, review_day, question=question, answer=answer)

    def review_detail(self, *args):
        """
        詳細表示関数
        :param args: 必要なデータが格納
        :return:
        """
        review_res = requests.get(url=f"https://remo-app-7-default-rtdb.firebaseio.com/{str(args[0])}.json")
        review_res_data = review_res.json()
        try:
            self.root.ids["memo_detail_screen"].ids['path_id'].text = str(args[0])
            self.insert_data("memo_detail_screen", str(review_res_data["review"]), review_res_data["review_day"],
                             memo=review_res_data["memo"])

        except KeyError:
            self.root.ids["question_detail_screen"].ids['path_id'].text = str(args[0])
            self.insert_data("question_detail_screen", str(review_res_data["review"]), review_res_data["review_day"],
                             question=review_res_data["question"], answer=review_res_data["answer"])

    def get_data(self):
        """
        データ取得
        :return:
        """

        res = requests.get(url=self.firebase_url)
        res_data = res.json()
        remo_display = self.root.ids['memo_list_screen'].ids['remo_data']
        remo_display.clear_widgets()
        for r in res_data:
            try:
                memo: str = str(res_data[r]["memo"])[:10] + " ..."
                data = Button(text=memo, font_size=40, on_release=partial(self.review_detail, str(r)),
                              background_normal='', background_color="#669999")

            except KeyError:
                question: str = str(res_data[r]["question"])[:10] + " ..."
                data = Button(text=question, font_size=40, on_release=partial(self.review_detail, str(r)),
                              background_normal='', background_color="#2F4F4F")

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
            if memo_review_day <= todays:
                memos.append(res_data[r])
        if not memos:
            self.root.ids['check_memo_screen'].ids['finish_button'].text = ""
            self.root.ids['check_memo_screen'].ids['finish_button'].disabled = True
            self.root.ids['check_memo_screen'].ids['next_memo'].text = ""
            self.root.ids['check_memo_screen'].ids['next_memo'].disabled = True
            self.root.ids['check_memo_screen'].ids['error_label'].text = "復習するメモはありません。"

            self.insert_data("check_memo_screen", "", "", "", "")

        else:
            memo = random.choice(memos)
            self.root.ids['check_memo_screen'].ids['finish_button'].text = "完了"
            self.root.ids['check_memo_screen'].ids['finish_button'].disabled = False
            self.root.ids['check_memo_screen'].ids['next_memo'].text = "次のメモを復習する"
            self.root.ids['check_memo_screen'].ids['next_memo'].disabled = False
            self.root.ids['check_memo_screen'].ids['error_label'].text = ""

            self.insert_data("check_memo_screen", memo["title"], memo["text"], str(memo["review"]),
                             memo["review_day"])

    def check_finish(self, title, text, review, review_day):
        review: int = int(review)
        res = requests.get(url=self.firebase_url)
        res_data = res.json()
        today = datetime.date.today()
        for r in res_data:
            if res_data[r]["title"] == title:
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
                json_data: str = '{"title": "%s",  "text": "%s", "review": %s, "review_day": "%s"}' \
                                 % (title, text, review, new_review_day)
                res = requests.patch(url=f"https://remo-app-7-default-rtdb.firebaseio.com/{r}/.json",
                                     json=json.loads(json_data))

                self.root.ids['check_memo_screen'].ids['finish_button'].text = "完了"
                self.root.ids['check_memo_screen'].ids['finish_button'].disabled = True
                self.root.ids['check_memo_screen'].ids['next_memo'].text = "次のメモを復習する"
                self.root.ids['check_memo_screen'].ids['next_memo'].disabled = False
                self.root.ids['check_memo_screen'].ids['error_label'].text = ""

                self.insert_data("check_memo_screen", title, text, str(review), new_review_day)

    def memo_update_display(self, path_id, memo, review, review_day):
        self.root.ids["memo_update_screen"].ids['path_id'].text = path_id
        self.insert_data("memo_update_screen", str(review), review_day, memo)

    def question_update_display(self, path_id, question, answer, review, review_day):
        self.root.ids["question_update_screen"].ids['path_id'].text = path_id
        self.insert_data("question_update_screen", str(review), review_day, question=question, answer=answer)

    def memo_delete_display(self, path_id, memo, review, review_day):
        self.root.ids["memo_delete_screen"].ids['path_id'].text = path_id
        self.insert_data("memo_delete_screen", str(review), review_day, memo=memo)

    def question_delete_display(self, path_id, question, answer, review, review_day):
        self.root.ids["question_delete_screen"].ids['path_id'].text = path_id
        self.insert_data("question_delete_screen", str(review), review_day, question=question, answer=answer)

    def memo_update(self, path_id, memo, review, review_day):
        json_data: str = '{"memo": "%s", "review": "%s", "review_day": "%s"}' \
                         % (memo, review, review_day)
        res = requests.patch(url=f"https://remo-app-7-default-rtdb.firebaseio.com/{str(path_id)}/.json",
                             json=json.loads(json_data))

        self.insert_data("memo_detail_screen", str(review), review_day, memo=memo)

    def question_update(self, path_id, question, answer, review, review_day):
        json_data: str = '{"question": "%s", "answer": "%s", "review": "%s", "review_day": "%s"}' \
                         % (question, answer, review, review_day)
        res = requests.patch(url=f"https://remo-app-7-default-rtdb.firebaseio.com/{str(path_id)}/.json",
                             json=json.loads(json_data))

        self.insert_data("question_detail_screen", str(review), review_day, question=question, answer=answer)

    def memo_delete(self, path_id):
        res = requests.delete(url=f"https://remo-app-7-default-rtdb.firebaseio.com/{str(path_id)}/.json")

        self.get_data()

    def question_delete(self, path_id):
        res = requests.delete(url=f"https://remo-app-7-default-rtdb.firebaseio.com/{str(path_id)}/.json")

        self.get_data()


if __name__ == '__main__':
    MainApp().run()
