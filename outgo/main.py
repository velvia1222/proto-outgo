from datetime import datetime
from math import floor
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
                outgo.number = row[1]
                outgo.status = row[2]
                outgo.buyer = row[3]
                outgo.amount = row[4]
                outgo.category = row[5]
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
                updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cur.execute('''
                        update outgo
                        set updated_at = ?, status = ?, buyer = ?, amount = ?, category = ?
                        where number = ?''',
                        (updated_at, self.status, self.buyer, 0 if not self.amount else self.amount, self.category, self.number))

            con.commit()
        finally:
            con.close()

    def delete(self):
        con = sqlite3.connect(SQLITE_FILE)
        try:
            cur = con.cursor()
            cur.execute('''
                    delete from outgo
                        where number = ?''',
                    (self.number,))

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

    def pay_off(self, list_widget):
        selected_outgoes, confirm_text = self.calc_payment()
        content = ConfirmContent()
        confirm_label = ConfirmLabel(text=confirm_text)
        content.add_widget(confirm_label)
        popup = ConfirmPopup(title='Pay off confirm', content=content)
        do_button = PopupButton(
                text='Pay',
                right=Window.width - 51,
                on_press=(lambda self: self.pay_off(selected_outgoes, list_widget, popup)))
        cancel_button = PopupButton(
                text='Cancel',
                right=Window.width / 2 - 41,
                on_press=popup.dismiss)
        content.add_widget(do_button)
        content.add_widget(cancel_button)
        popup.open()

    def calc_payment(self):
        adapter = self.listview_widget.adapter
        views_len = len(adapter.data)
        selected_outgoes = []
        selected_labels = []
        selected_labels.append('')
        selected_labels.append('')
        y_amount = 0
        n_amount = 0

        index = 0
        while index < views_len:
            label = adapter.get_view(index).list_item_label
            if label.is_selected:
                outgo = label.outgo
                if outgo.buyer == 'y':
                    y_amount += outgo.amount
                else:
                    n_amount += outgo.amount
                selected_outgoes.append(outgo)
                selected_labels.append(label.text)
            index += 1

        if n_amount < y_amount:
            payer = 'n'
            payment = floor((y_amount - n_amount) / 2)
        else:
            payer = 'y'
            payment = floor((n_amount - y_amount) / 2)

        selected_labels[0] = '{}が{}円支払ってください'.format(
                payer, str(payment))

        return selected_outgoes, '\n'.join(selected_labels)


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
    def pay_off(self, selected_outgoes, list_widget, popup):
        for outgo in selected_outgoes:
            outgo.status = '1'
            outgo.save()
        list_widget.update_outgo_data()
        popup.dismiss()

    def delete(self, outgo, list_widget, popup):
        outgo.delete()
        list_widget.update_outgo_data()
        popup.dismiss()


class ConfirmContent(Widget):
    pass


class ConfirmLabel(Label):
    pass


class ListItemLabelWidget(ListItemButton):
    outgo = ObjectProperty()

    def print_item(self, outgo):
        return ' {} {} {}'.format(outgo.buyer, str(outgo.amount), outgo.category)


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

    def delete(self, list_widget):
        content = ConfirmContent()
        confirm_label = ConfirmLabel(text=self.make_delete_text())
        content.add_widget(confirm_label)
        popup = ConfirmPopup(title='Delete confirm', content=content)
        outgo = self.outgo
        do_button = PopupButton(
                text='Delete',
                right=Window.width - 51,
                on_press=(lambda self: self.delete(outgo, list_widget, popup)))
        cancel_button = PopupButton(
                text='Cancel',
                right=Window.width / 2 - 41,
                on_press=popup.dismiss)
        content.add_widget(do_button)
        content.add_widget(cancel_button)
        popup.open()

    def make_delete_text(self):
        return ' {} {} {}'.format(self.outgo.buyer, str(self.outgo.amount), self.outgo.category)


class OutgoApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


if __name__ == '__main__':
    OutgoApp().run()
