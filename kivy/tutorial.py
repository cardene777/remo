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


class AddFriendScreen(Screen):
    pass


class AddWorkoutScreen(Screen):
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
    def __init__(self, **kwargs):
        super().__init__()
        self.my_firebase = MyFirebase()
        self.my_friend_id = 1
        self.workout_image = None
        self.option_choice = None

    def build(self):
        return GUI

    def update_workout_image(self, filename, widget_id):
        self.workout_image = filename

    def on_start(self):
        # Populate avatar grid
        avatar_grid = self.root.ids["change_avatar_screen"].ids["avatar_grid"]
        for root_dir, folders, files in walk("icons/avatars"):
            for f in files:
                img = ImageButton(source=f"icons/avatars/{f}", on_release=partial(self.change_avatar, f))
                avatar_grid.add_widget(img)

        # Populate workout image grid
        workout_image_grid = self.root.ids["add_workout_screen"].ids["workout_image_grid"]
        for root_dir, folders, files in walk("icons/workouts"):
            for f in files:
                if ".png" in f:
                    img = ImageButton(source=f"icons/workouts/{f}", on_release=partial(self.update_workout_image, f))
                    workout_image_grid.add_widget(img)

        try:
            # Try to read the persistem signin credentials (refresh token)
            with open("refresh_token.txt", "r") as f:
                refresh_token = f.read()

            # Use refresh token to get a new idToken
            id_token, local_id = self.my_firebase.exchange_refresh_token(refresh_token)
            self.lcoal_id = local_id
            self.id_token = id_token

            # Get database data
            result = requests.get(f"https://tutorial-78ce1-default-rtdb.firebaseio.com/{local_id}.json?auth={id_token}")
            # print("Was it okay?", result.ok)
            # print(result)
            data = json.loads(result.content.decode())
            # print(f"data = {data}")

            # Get and updates avatar image
            avatar_image = self.root.ids["avatar_image"]
            avatar_image.source = "icons/avatars/" + data["avatar"]

            # Get friend list
            self.friends_list = data["friends"]

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
                                      type_image=workout["type_image"], number=workout["number"],
                                      units=workout["units"],
                                      likes=workout["likes"])
                    # print(workout["workout_image"])
                    # print(workout["units"])
                    banner_grid.add_widget(W)

            self.root.ids["screen_manager"].transition = NoTransition()
            self.change_screen("home_screen")
            self.root.ids["screen_manager"].transition = CardTransition()

        except Exception as e:
            print(e)

    def add_friend(self, friend_id):
        # Query database and make sure friend_id exists
        check_req = requests.get(
            f'https://tutorial-78ce1-default-rtdb.firebaseio.com/.json?orderBy="my_friend_id"&equalTo={friend_id}'
        )
        # print("------------------------")
        # print(check_req.ok)
        # print(check_req.json())
        # print("------------------------")
        data = check_req.json()
        if data == {}:
            # if it doesn't display it doesn't in the message on the add friend screen
            self.root.ids["add_friend_screen"].ids["add_friend_label"].text = "Invalid friend ID"
        else:
            key = data.keys()[0]
            new_friend_id = data[key]["my_friend_id"]
            self.root.ids["add_friend_screen"].ids[
                "add_friend_label"].text = f"Friend ID {friend_id} added successfullu"
            # Add friend id to friends list and new friend list
            self.friends_list += f", {friend_id}"
            patch_data = f'{"friends": "{self.friends_list}"}'
            patch_req = requests.patch(
                f"https://tutorial-78ce1-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}",
                data=patch_data)

            print(patch_req.ok)
            print(patch_req.json())

        # if it does, "success" and to friend list

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

    def add_workout(self):
        # Get data from all fields in add workout screen
        workout_ids = self.root.ids["add_workout_screen"].ids
        # Already have workou image in self.workout_image variable
        description_input = workout_ids["description_input"].text
        # Already have option choice in self.option_choice
        quantity_input = workout_ids["quantity_input"].text
        units_input = workout_ids["units_input"].text
        month_input = workout_ids["month_input"].text
        day_input = workout_ids["day_input"].text
        year_input = workout_ids["year_input"].text

        # Make sure fields aren't garbage
        if self.workout_image is None:
            print("come back to this")

        # They are allawed to leave to description
        if self.option_choice is None:
            workout_ids["time_label"].color = (1, 0, 0, 1)
            workout_ids["distance_label"].color = (1, 0, 0, 1)
            workout_ids["sets_label"].color = (1, 0, 0, 1)
            return

        try:
            int_quantity = float(quantity_input)
        except:
            workout_ids["quantity_input"].color = (1, 0, 0, 1)
            return

        if units_input == "":
            workout_ids["units_input"].background_color = (1, 0, 0, 1)
            return

        try:
            int_month = int(month_input)
        except:
            workout_ids["month_input"].background_color = (1, 0, 0, 1)
            return

        try:
            int_day = int(day_input)
        except:
            workout_ids["day_input"].background_color = (1, 0, 0, 1)
            return

        try:
            int_year = int(year_input)
        except:
            workout_ids["year_input"].background_color = (1, 0, 0, 1)
            return


        # If all data is ok, send the data to firebase real-time database

    def change_screen(self, screen_name):
        print(self.root.ids)
        screen_manager = self.root.ids["screen_manager"]
        screen_manager.current = screen_name


if __name__ == '__main__':
    Tutorial().run()
