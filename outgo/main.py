#!/usr/bin/python3

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.core.window import Window

Window.size = (300, 400)


class PrototypeWidget(Widget):

    def input_number(self, numberButton):
        self.number_display.text += numberButton.text

    def backspace(self):
        self.number_display.text = self.number_display.text[:-1]

    def clear(self):
        self.number_display.text = ''


class PrototypeApp(App):
    def build(self):
        return PrototypeWidget()


if __name__ == '__main__':
    PrototypeApp().run()
