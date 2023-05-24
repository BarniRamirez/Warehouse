import kivy
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty

from kivy.properties import StringProperty
from kivymd.icon_definitions import md_icons
from kivymd.uix.list import OneLineIconListItem
from kivy.lang import Builder
from kivymd.app import MDApp


class MyMainApp(MDApp):
    def build(self):

        self.theme_cls.material_style = "M3"
        self.theme_cls.theme_style = "Light"
        return Builder.load_file("GUI.kv")

    def btn(self):
        if self.theme_cls.theme_style == "Light":
            self.theme_cls.theme_style = "Dark"
        else:
            self.theme_cls.theme_style = "Light"
        print("ciao")


if __name__ == "__main__":
    MyMainApp().run()