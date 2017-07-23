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

# const
SQLITE_FILE = 'outgo_db.sqlite'
CATEGORY_LIST = ['外食費', '食費', '日用品', '娯楽', '光熱費', '家賃']

resource_add_path('/usr/share/fonts/truetype')
LabelBase.register(DEFAULT_FONT, 'fonts-japanese-gothic.ttf')
Window.size = (300, 450)


class OutgoModel():

    number = None
    status = ""
    buyer = ""
    amount = 0
    category = ""

    @staticmethod
    def all():
        con = sqlite3.connect(SQLITE_FILE)
        try:
            cur = con.cursor()
            cur.execute('''
                    select * from outgo
                    where outgo.status = '0'
                    order by number;
            ''')
            outgoes = []
            for row in cur:
                outgo = OutgoModel()
                outgo.number = row[0]
                outgo.status = row[1]
                outgo.buyer = row[2]
                outgo.amount = row[3]
                outgo.category = row[4]
                outgoes.append(outgo)
            return outgoes
        finally:
            con.close()

    def save(self):
        con = sqlite3.connect(SQLITE_FILE)
        try:
            cur = con.cursor()
            if self.number is None:
                cur.execute('''
                        insert into outgo
                            (status, buyer, amount, category)
                        values (?, ?, ?, ?)''',
                        (self.status, self.buyer, 0 if not self.amount else self.amount, self.category))
            else:
                cur.execute('''
                        update outgo
                        set status = ?, buyer = ?, amount = ?, category = ?
                        where number = ?''',
                        (self.status, self.buyer, 0 if not self.amount else self.amount, self.category, self.number))

            con.commit()
        finally:
            con.close()


class OutgoRoot(Widget):
    pass


class CarouselWidget(Carousel):
    pass


class InputWidget(BoxLayout):
    number = None

    def get_category(self):
        self.category_spinner.text = CATEGORY_LIST[0]
        return CATEGORY_LIST

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
        self.save_outgo()
        self.clear()
        list_widget.update_outgo_data()
        carousel_widget.load_slide(list_widget)

    def cancel(self, carousel_widget, list_widget):
        self.clear()
        carousel_widget.load_slide(list_widget)

    def save_outgo(self):
        outgo = OutgoModel()
        outgo.number = self.number
        outgo.status = '0'
        outgo.buyer = 'n' if self.target_n.state == 'down' else 'y'
        outgo.amount = self.number_display.text
        outgo.category = self.category_spinner.text
        outgo.save()

    def clear(self):
        self.number = None
        self.enter_button.text = 'Enter'


class ListWidget(BoxLayout):
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
                size_hint_x=0.95,
                size_hint_y=0.95)
        popup = ConfirmPopup(content=content)
        do_button = PopupButton(
                text='Do',
                right=Window.width - 51,
                on_press=popup.dismiss)
        cancel_button = PopupButton(
                text='Cancel',
                right=Window.width / 2 - 41,
                on_press=popup.dismiss)
        content.add_widget(do_button)
        content.add_widget(cancel_button)
        popup.open()


class ListViewWidget(ListView):

    def update_adapter(self):
        self.adapter = self.build_adapter()

    def build_adapter(self):
        return ListAdapter(
                data=OutgoModel.all(),
                args_converter=lambda index, outgo: \
                        {'outgo': outgo},
                template='ListItemWidget',
                selection_mode='multiple')


class ConfirmPopup(Popup):
    pass


class PopupButton(Button):
    pass


class ConfirmContent(Widget):
    pass


class ConfirmLabel(Label):
    def get_text(self, listview_widget):
        adapter = listview_widget.adapter
        views_len = len(adapter.data)
        selected_labels = []

        index = 0
        while index < views_len:
            label = adapter.get_view(index).list_item_label
            if label.is_selected:
                selected_labels.append(label.text)
            index += 1

        return "\n".join(selected_labels)


class ListItemLabelWidget(ListItemButton):
    def print_item(self, outgo):
        return ' ' + outgo.buyer + ' ' + str(outgo.amount) + ' ' + outgo.category


class ListItemBtnWidget(ListItemButton):
    outgo = ObjectProperty()

    def edit(self, carousel_widget, input_widget):
        input_widget.number = self.outgo.number
        input_widget.number_display.text = '' if self.outgo.amount == 0 else str(self.outgo.amount)
        category = self.outgo.category
        input_widget.category_spinner.text = category if category in CATEGORY_LIST else CATEGORY_LIST[0]
        if self.outgo.buyer == 'n':
            input_widget.target_n.state = 'down'
            input_widget.target_y.state = 'normal'
        else:
            input_widget.target_y.state = 'down'
            input_widget.target_n.state = 'normal'
        input_widget.enter_button.text = 'Edit'
        carousel_widget.load_slide(input_widget)


class OutgoApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


if __name__ == '__main__':
    OutgoApp().run()
