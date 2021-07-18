from kivy.app import App
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


class ImageButton(ButtonBehavior, Image):
    pass


class HomeScreen(Screen):
    pass


class SearchScreen(Screen):
    pass


class NoteScreen(Screen):
    pass


class SettingsScreen(Screen):
    pass


GUI = Builder.load_file("remo.kv")


class Remo(App):
    def build(self):
        return GUI

    def on_start(self):
        pass

    def change_screen(self, screen_name):
        screen_manager = self.root.ids["screen_manager"]
        screen_manager.current = screen_name


if __name__ == '__main__':
    Remo().run()