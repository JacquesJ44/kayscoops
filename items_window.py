from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from kivy.app import App
from kivy.lang import Builder
from db_ops import DBOps
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivy.uix.button import Button
from kivy.uix.popup import Popup
import sqlite3

# Load KV file
Builder.load_file("items_screen.kv")


class ItemRow(BoxLayout):
    def __init__(self, id_, name, quantity, cost, selling, index=0, on_select=None, is_heading=False, **kwargs):
        super().__init__(orientation="horizontal", size_hint_y=None, height=40, spacing=5, **kwargs)
        self.index = index
        bg_color = (0.9, 0.9, 0.95, 1) if index % 2 == 0 else (0.85, 0.85, 0.9, 1)
        if is_heading:
            bg_color = (0.65, 0.5, 0.9, 1)
        with self.canvas.before:
            Color(*bg_color)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

        # Columns
        self.add_widget(Label(text=id_, size_hint_x=0.1, bold=is_heading, color=(1,1,1,1) if is_heading else (0,0,0,1)))
        self.add_widget(Label(text=name, size_hint_x=0.3, bold=is_heading, color=(1,1,1,1) if is_heading else (0,0,0,1)))
        self.add_widget(Label(text=quantity, size_hint_x=0.15, bold=is_heading, color=(1,1,1,1) if is_heading else (0,0,0,1)))
        self.add_widget(Label(text=cost, size_hint_x=0.2, bold=is_heading, color=(1,1,1,1) if is_heading else (0,0,0,1)))
        self.add_widget(Label(text=selling, size_hint_x=0.25, bold=is_heading, color=(1,1,1,1) if is_heading else (0,0,0,1)))

        if not is_heading and on_select:
            self.bind(on_touch_down=lambda widget, touch: self._on_touch(touch, on_select))

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def _on_touch(self, touch, callback):
        if self.collide_point(*touch.pos):
            callback()
            return True
        return False


class ItemsScreen(Screen):
    name_input = ObjectProperty(None)
    quantity_input = ObjectProperty(None)
    cost_input = ObjectProperty(None)
    selling_input = ObjectProperty(None)
    search_input = ObjectProperty(None)
    items_list = ObjectProperty(None)

    selected_item_id = None
    items = []

    def on_pre_enter(self):
        """Refresh clients whenever screen is opened."""
        if not hasattr(self, 'db'):
            self.db = DBOps()  # safe lazy init
        self.refresh_items()

    def refresh_items(self, search_term=None):
        """Fetch clients from DB and update table/list."""
        try:
            self.items = self.db.fetch_items(search_term)
        except sqlite3.OperationalError as e:
            if "no such table" in str(e):
                from db import init_db
                init_db()  # create tables
                self.items = self.db.fetch_items(search_term)
            else:
                raise
        
        self.items_list.clear_widgets()

        # Headings
        headings = ["ID", "Name", "Quantity", "Cost (R)", "Selling (R)"]
        self.items_list.add_widget(ItemRow(*headings, is_heading=True))

        # Rows
        for idx, item in enumerate(self.items):
            item_id, name, quantity, cost_price, selling_price = item
            self.items_list.add_widget(ItemRow(
                str(item_id),
                name,
                str(quantity),
                f"{cost_price:.2f}" if cost_price else "0.00",
                f"{selling_price:.2f}" if selling_price else "0.00",
                index=idx,
                on_select=lambda i=idx: self.load_item(i)
            ))

        # Clear inputs
        self.name_input.text = ""
        self.quantity_input.text = ""
        self.cost_input.text = ""
        self.selling_input.text = ""
        self.selected_item_id = None

    def load_item(self, idx):
        """Populate input fields when an item is selected."""
        item = self.items[idx]
        self.selected_item_id = item[0]
        self.name_input.text = item[1]
        self.quantity_input.text = str(item[2])
        self.cost_input.text = str(item[3]) if item[3] else "0.00"
        self.selling_input.text = str(item[4]) if item[4] else "0.00"

    def on_search(self, text):
        self.refresh_items(text.strip())

    def add_item(self):
        name = self.name_input.text.strip()
        quantity = self.quantity_input.text.strip()
        cost = self.cost_input.text.strip()
        selling = self.selling_input.text.strip()

        if not name or not quantity:
            App.get_running_app().popup("Error", "Please enter name and quantity!")
            return

        self.db.add_item(name, int(quantity), float(cost) if cost else 0, float(selling) if selling else 0)
        App.get_running_app().popup("Success", f"Item '{name}' added successfully!")
        self.refresh_items()

    def update_item(self):
        if not self.selected_item_id:
            App.get_running_app().popup("Error", "Please select an item to update!")
            return

        name = self.name_input.text.strip()
        quantity = self.quantity_input.text.strip()
        cost = self.cost_input.text.strip()
        selling = self.selling_input.text.strip()

        if not name or not quantity:
            App.get_running_app().popup("Error", "Please enter name and quantity!")
            return

        self.db.update_item(self.selected_item_id, name, int(quantity), float(cost) if cost else 0, float(selling) if selling else 0)
        App.get_running_app().popup("Success", f"Item '{name}' updated successfully!")
        self.refresh_items()

    def delete_item(self):
        if not self.selected_item_id:
            App.get_running_app().popup("Error", "Please select an item to delete!")
            return

        content = BoxLayout(orientation='vertical', spacing=10)
        content.add_widget(Label(text="Are you sure you want to delete this item?"))

        buttons = BoxLayout(size_hint_y=None, height=40, spacing=10)
        yes_btn = Button(text="Yes")
        no_btn = Button(text="No")
        buttons.add_widget(yes_btn)
        buttons.add_widget(no_btn)
        content.add_widget(buttons)

        popup = Popup(title="Confirm Delete", content=content, size_hint=(0.6, 0.4))

        def on_confirm(instance):
            try:
                self.db.delete_item(self.selected_item_id)
                App.get_running_app().popup("Deleted", "Item deleted successfully!")
                self.selected_item_id = None
                self.refresh_items()
            except sqlite3.IntegrityError:
                App.get_running_app().popup("Error", "Cannot delete this item because it is referenced in another table.")
            popup.dismiss()

        def on_cancel(instance):
            popup.dismiss()

        yes_btn.bind(on_release=on_confirm)
        no_btn.bind(on_release=on_cancel)
        popup.open()
