#!/usr/bin/python3

from kivy.adapters.listadapter import ListAdapter
from kivy.app import App
from kivy.core.text import LabelBase, DEFAULT_FONT
from kivy.core.window import Window
from kivy.properties import ListProperty
from kivy.resources import resource_add_path
from kivy.uix.carousel import Carousel
from kivy.uix.listview import CompositeListItem, ListItemButton
from kivy.uix.widget import Widget

resource_add_path('/usr/share/fonts/truetype')
LabelBase.register(DEFAULT_FONT, 'fonts-japanese-gothic.ttf')
Window.size = (300, 450)

testdata = [('y', 3000, '外食費'), ('y', 2000, '娯楽'), ('y', 1000, '食費'), ('y', 1000, '食費'), ('y', 1000, '食費'), ('y', 1000, '食費'), ('y', 1000, '食費'), ('y', 1000, '食費'), ('y', 1000, '食費'), ('y', 1000, '食費')]


class OutgoRoot(Widget):
    pass


class InputWidget(Widget):
    def build_category(self):
        category_list = self.get_category_list()
        if len(category_list) > 0:
            self.category_spinner.text = category_list[0]
        return category_list

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

    def enter(self, outgoRoot):
        outgoRoot.carousel.load_slide(outgoRoot.list_widget)

    def cancel(self, outgoRoot):
        outgoRoot.carousel.load_slide(outgoRoot.list_widget)


class ListWidget(Widget):
    pass


class ListLabelWidget(Widget):
    def build_adapter(self):
        return ListAdapter(
                data=testdata,
                args_converter=lambda index, data: \
                        {'cls_dicts': [
                                {'cls': ListItemLabelWidget,
                                    'kwargs': {'text': '', 'items': data}},
                                {'cls': ListItemEditBtnWidget,
                                    'kwargs': {'text': ''}},
                                {'cls': ListItemDelBtnWidget,
                                    'kwargs': {'text': ''}}],
                            'height': Window.height / 6},
                cls=ListItemWidget,
                selection_mode='multiple')


class ListItemWidget(CompositeListItem):
    pass


class ListItemLabelWidget(ListItemButton):
    items = ListProperty()

    def print_item(self):
        return self.items[0] + ' ' + str(self.items[1]) + ' ' + self.items[2]


class ListItemEditBtnWidget(ListItemButton):
    pass


class ListItemDelBtnWidget(ListItemButton):
    pass


def move_to_input(outgoRoot):
    outgoRoot.carousel.load_slide(outgoRoot.input_widget)


class OutgoApp(App):
    def build(self):
        return OutgoRoot()


if __name__ == '__main__':
    OutgoApp().run()
