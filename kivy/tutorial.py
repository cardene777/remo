import kivy.uix.label
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, NoTransition, CardTransition
from kivy.uix.button import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.label import Label

import requests
import json
from os import walk
from functools import partial

from workout_banner import WorkoutBanner
from my_firebase import MyFirebase


class HomeScreen(Screen):
    pass


class LabelButton(ButtonBehavior, Label):
    pass


class ImageButton(ButtonBehavior, Image):
    pass


class LoginScreen(Screen):
    pass


class SettingsScreen(Screen):
    pass


class ChangeAvatarScreen(Screen):
    pass


GUI = Builder.load_file("tutorial.kv")


class Tutorial(App):
    my_friend_id = 1

    def __init__(self, **kwargs):
        super().__init__()
        self.my_firebase = MyFirebase()

    def build(self):
        return GUI

    def on_start(self):
        # Populate avatar grid
        avatar_grid = self.root.ids["change_avatar_screen"].ids["avatar_grid"]
        for root_dir, folders, files in walk("icons/avatars"):
            for f in files:
                img = ImageButton(source=f"icons/avatars/{f}", on_release=partial(self.change_avatar, f))
                avatar_grid.add_widget(img)

        try:
            # Try to read the persistem signin credentials (refresh token)
            with open("refresh_token.txt", "r") as f:
                refresh_token = f.read()

            # Use refresh token to get a new idToken
            id_token, local_id = self.my_firebase.exchange_refresh_token(refresh_token)

            # Get database data
            result = requests.get(f"https://tutorial-78ce1-default-rtdb.firebaseio.com/{local_id}.json?auth={id_token}")
            # print("Was it okay?", result.ok)
            # print(result)
            data = json.loads(result.content.decode())
            # print(f"data = {data}")

            # Get and updates avatar image
            avatar_image = self.root.ids["avatar_image"]
            avatar_image.source = "icons/avatars/" + data["avatar"]

            # Get and updates streak label
            streak_label = self.root.ids["home_screen"].ids["streak_label"]
            streak_label.text = str(data["streak"]) + "Day Streak!"

            # Get and update friend id label
            friend_id_label = self.root.ids["settings_screen"].ids["friend_id_label"]
            friend_id_label.text = f"Friend ID: {str(self.my_friend_id)}"

            banner_grid = self.root.ids["home_screen"].ids["banner_grid"]
            workouts = data["workouts"][1:]
            for workout in workouts:
                for _ in range(5):
                    # Populate workout grid in home screen
                    W = WorkoutBanner(workout_image=workout["workout_image"], description=workout["description"],
                                      type_image=workout["type_image"], number=workout["number"], units=workout["units"],
                                      likes=workout["likes"])
                    # print(workout["workout_image"])
                    # print(workout["units"])
                    banner_grid.add_widget(W)

            self.root.ids["screen_manager"].transition = NoTransition()
            self.change_screen("home_screen")
            self.root.ids["screen_manager"].transition = CardTransition()

        except Exception as e:
            print(e)

    def change_avatar(self, image, widget_id):
        # Change avatar in the app
        avatar_image = self.root.ids["avatar_image"]
        avatar_image.source = f"icons/avatars/{image}"

        # Change avatar in firebase database
        my_data = '{"avatar": "%s"}' % image
        # print(data)
        requests.patch(f"https://tutorial-78ce1-default-rtdb.firebaseio.com/{str(self.my_friend_id)}.json",
                       data=my_data)

        self.change_screen("settings_screen")

    def change_screen(self, screen_name):
        print(self.root.ids)
        screen_manager = self.root.ids["screen_manager"]
        screen_manager.current = screen_name


if __name__ == '__main__':
    Tutorial().run()
