#!/usr/bin/python3

from kivy.adapters.listadapter import ListAdapter
from kivy.app import App
from kivy.core.text import LabelBase, DEFAULT_FONT
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.properties import ListProperty, ObjectProperty
from kivy.resources import resource_add_path
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.carousel import Carousel
from kivy.uix.label import Label
from kivy.uix.listview import CompositeListItem, ListItemButton, ListView
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
import sqlite3

SQLITE_FILE = 'outgo_db.sqlite'
resource_add_path('/usr/share/fonts/truetype')
LabelBase.register(DEFAULT_FONT, 'fonts-japanese-gothic.ttf')
Window.size = (300, 450)

testdata = [('y', 3000, '外食費'), ('y', 2000, '娯楽'), ('y', 1000, '食費'), ('y', 1000, '食費'), ('y', 1000, '食費'), ('y', 1000, '食費'), ('y', 1000, '食費'), ('y', 1000, '食費'), ('y', 1000, '食費'), ('y', 1000, '食費'), ('y', 1000, '食費'), ('y', 1000, '食費'), ('y', 1000, '食費'), ('y', 1000, '食費'), ('y', 1000, '食費'), ('y', 1000, '食費'), ('y', 1000, '食費'), ('y', 1000, '食費'), ('y', 1000, '食費'), ('y', 1000, '食費'), ('y', 1000, '食費'), ('y', 1000, '食費'), ('y', 1000, '食費'), ('y', 1000, '食費'), ('y', 1000, '食費'), ('y', 1000, '食費'), ('y', 1000, '食費'), ('y', 1000, '最後！')]

testconfirmdata = '''
y 3000 外食費
y 2000 食費
'''


class OutgoModel():
    def fetch(self):
        con = sqlite3.connect(SQLITE_FILE)
        try:
            curs = con.cursor()
            curs.execute('''select * from outgo order by number;''')
            return curs.fetchall()
        finally:
            con.close()

    def save(self, status, buyer, amount, category):
        con = sqlite3.connect(SQLITE_FILE)
        try:
            curs = con.cursor()
            curs.execute('''
                    insert into outgo
                        (status, buyer, amount, category) values
                        (?, ?, ?, ?)''',
                    (status, buyer, 0 if not amount else amount, category))
            con.commit()
        finally:
            con.close()


class OutgoRoot(Widget):
    pass


class CarouselWidget(Carousel):
    pass


class InputWidget(BoxLayout):
    model = ObjectProperty()

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

    def enter(self, carousel_widget, list_widget):
        self.model.save(
                '0',
                'n' if self.target_n.state == 'down' else 'y',
                self.number_display.text,
                self.category_spinner.text)
        list_widget.update_outgo_data()
        carousel_widget.load_slide(list_widget)

    def cancel(self, outgoRoot):
        outgoRoot.carousel.load_slide(outgoRoot.list_widget)


class ListWidget(Widget):
    def update_outgo_data(self):
        self.listview_widget.update_adapter()

    def select_all(self):
        adapter = self.listview_widget.adapter
        views_len = len(adapter.data)
        all_selected = True

        index = 0
        while index < views_len:
            label = adapter.get_view(index).list_item_label
            if not label.is_selected:
                all_selected = False
                label.trigger_action()
            index += 1

        if all_selected:
            index = 0
            while index < views_len:
                adapter.get_view(index).list_item_label.trigger_action()
                index += 1

    def pay_off(self):
        content = ConfirmContent(
                height=Window.height - 50,
                width=Window.width - 50)
        popup = ConfirmPopup(content=content)
        done_button = PopupButton(
                text='Done',
                right=249,
                on_press=popup.dismiss)
        cancel_button = PopupButton(
                text='Cancel',
                right=109,
                on_press=popup.dismiss)
        content.add_widget(done_button)
        content.add_widget(cancel_button)
        popup.open()


class ListViewWidget(ListView):
    model = ObjectProperty()

    def update_adapter(self):
        self.adapter = self.build_adapter()

    def build_adapter(self):
        return ListAdapter(
                data=self.model.fetch(),
                args_converter=lambda index, data: \
                        {'data': data},
                template='ListItemWidget',
                selection_mode='multiple')


class ConfirmPopup(Popup):
    pass


class PopupButton(Button):
    pass


class ConfirmContent(Widget):
    pass


class ConfirmLabel(Label):
    def get_text(self):
        return testconfirmdata


class ListItemLabelWidget(ListItemButton):
    def print_item(self, items):
        return ' ' + items[2] + ' ' + str(items[3]) + ' ' + items[4]


class ListItemBtnWidget(ListItemButton):
    def move_to_input(self, outgoRoot):
        outgoRoot.carousel.load_slide(outgoRoot.input_widget)


class OutgoApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.outgo_model = OutgoModel()


if __name__ == '__main__':
    OutgoApp().run()
