from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivymd.uix.toolbar import MDTopAppBar
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivymd.uix.datatables import MDDataTable
from kivy.uix.anchorlayout import AnchorLayout
from kivy.metrics import dp

import pandas as pd


dataframe = pd.read_csv('test.csv')
print(dataframe)

column_data_test = list(dataframe.columns)
print("COL DATA: \n",column_data_test)

row_data = dataframe.to_records(index=False)
print("ROW DATA: \n",row_data)

class MenuItem(Button):
    pass


class MainApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "KivyMD Examples - Bottom Navigation"
        self.menu_items = [
            {"text": "Item 1"},
            {"text": "Item 2"},
            {"text": "Item 3"}
        ]

    def build(self):
        self.root = Builder.load_file("my.kv")

    def open_menu(self, *args):
        menu = BoxLayout(orientation='vertical', spacing='2dp', size_hint_y=None)
        menu.bind(minimum_height=menu.setter('height'))

        for item in self.menu_items:
            menu.add_widget(MenuItem(text=item['text']))

        self.menu = Popup( title='Menu', content=menu, size_hint=(None, None), size=('200dp', '200dp'))
        self.menu.open()

    def open_table_button_pressed(self):
        column_data = []

        for column_name in column_data_test:
            column_width = dp(40)
            column_data.append((column_name, column_width))

        layout = BoxLayout(orientation='vertical', spacing='2dp')
        self.data_tables = MDDataTable(
            use_pagination=True,
            check=True,
            column_data=column_data,
            row_data=row_data
        )
        scroll_view = ScrollView(size_hint=(1, None), height=Window.height * 0.6)
        scroll_view.add_widget(self.data_tables)
        layout.add_widget(scroll_view)
        self.layout = Popup(title='Table', content=layout, size_hint=(None, None), size=('800dp', '600dp'))
        self.layout.open()

    def menu_item_selected(self, text):
        print("Menu item selected:", text)
        self.menu.dismiss()

    def custom_button_pressed(self):
        # Perform actions when the custom button is pressed
        button = self.root.ids.custom_button
        button.md_bg_color = [1, 0, 0, 1]  # Set button background color to red


    def text_entered(self, text):
        # Perform actions when text is entered in the text field
        button = self.root.ids.custom_button
        if text:
            button.md_bg_color = [0, 1, 0, 1]  # Set button background color to green
        else:
            button.md_bg_color = [0, 0, 1, 1]  # Set button background color to blue


if __name__ == "__main__":
    MainApp().run()
