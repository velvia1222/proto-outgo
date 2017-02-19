#!/usr/bin/python3

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.core.window import Window

Window.size = (300, 450)


class PrototypeWidget(Widget):

    def select_y(self):
        if self.target_y.state == 'normal':
            self.target_y.state = 'down'

    def select_n(self):
        if self.target_n.state == 'normal':
            self.target_n.state = 'down'

    def input_number(self, numberButton):
        self.number_display.text += numberButton.text

    def backspace(self):
        self.number_display.text = self.number_display.text[:-1]


class PrototypeApp(App):
    def build(self):
        return PrototypeWidget()


if __name__ == '__main__':
    PrototypeApp().run()
