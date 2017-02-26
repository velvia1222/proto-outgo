#!/usr/bin/python3

from kivy.app import App
from kivy.core.text import LabelBase, DEFAULT_FONT
from kivy.core.window import Window
from kivy.resources import resource_add_path
from kivy.uix.carousel import Carousel
from kivy.uix.widget import Widget

resource_add_path('/usr/share/fonts/truetype')
LabelBase.register(DEFAULT_FONT, 'fonts-japanese-gothic.ttf')
Window.size = (300, 450)


class InputWidget(Widget):

    def build_category(self):
        category_list = self.get_category_list()
        if len(category_list) > 0:
            self.category_spinner.text = category_list[0]
        self.category_spinner.values = self.get_category_list()

    def get_category_list(self):
        return ['外食費', '食費', '日用品', '娯楽', '光熱費', '家賃']

    def select_y(self):
        if self.target_y.state == 'normal':
            self.target_y.state = 'down'

    def select_n(self):
        if self.target_n.state == 'normal':
            self.target_n.state = 'down'

    def input_number(self, number_btn):
        self.number_display.text += number_btn.text

    def backspace(self):
        self.number_display.text = self.number_display.text[:-1]


class ListWidget(Widget):
    pass


class OutgoApp(App):
    def build(self):
        outgoWidget = Carousel()
        outgoWidget.loop = True
        inputWidget = InputWidget()
        inputWidget.build_category()
        listWidget = ListWidget()
        outgoWidget.add_widget(inputWidget)
        outgoWidget.add_widget(listWidget)
        return outgoWidget


if __name__ == '__main__':
    OutgoApp().run()
