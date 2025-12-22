from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, ListProperty
from kivy.app import App
from kivy.lang import Builder
from db_ops import DBOps
import sqlite3

DB = DBOps()

# Load KV file
Builder.load_file("new_scoop_screen.kv")


# ---------- Scoop Item Row ----------
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

class ScoopItemRow(BoxLayout):
    def __init__(self, name, quantity, index=0, **kwargs):
        super().__init__(orientation="horizontal", size_hint_y=None, height=40, spacing=5, **kwargs)
        bg_color = (0.9, 0.9, 0.95, 1) if index % 2 == 0 else (0.85, 0.85, 0.9, 1)
        with self.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(*bg_color)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

        self.add_widget(Label(text=name, size_hint_x=0.7, color=(0,0,0,1)))
        self.add_widget(Label(text=str(quantity), size_hint_x=0.3, color=(0,0,0,1)))

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


# ---------- New Scoop Screen ----------
class NewScoopScreen(Screen):
    client_search = ObjectProperty(None)
    client_dropdown = ObjectProperty(None)
    item_search = ObjectProperty(None)
    item_dropdown = ObjectProperty(None)
    quantity_input = ObjectProperty(None)
    scoop_price_input = ObjectProperty(None)
    scoop_items_container = ObjectProperty(None)

    clients = ListProperty([])
    items = ListProperty([])
    current_scoop_items = ListProperty([])
    selected_client_id = None

    def on_pre_enter(self):
        """Bind search inputs and refresh data."""
        self.client_search.bind(text=self.client_search_changed)
        self.item_search.bind(text=self.item_search_changed)
        self.refresh_clients()
        self.refresh_items()
        self.refresh_table()

    # ---------- Client ----------
    def refresh_clients(self, search_term=""):
        try:
            self.clients = DB.fetch_clients(search_term)
        except sqlite3.OperationalError as e:
            if "no such table" in str(e):
                from db import init_db
                init_db()  # create tables
                self.clients = DB.fetch_clients(search_term)
            else:
                raise
        self.client_dropdown.values = [f"{c[1]} (ID:{c[0]})" for c in self.clients]

    def client_search_changed(self, instance, value):
        self.refresh_clients(value.strip())

    # ---------- Items ----------
    def refresh_items(self, search_term=""):
        try:
            self.items = DB.fetch_items(search_term)
        except sqlite3.OperationalError as e:
            if "no such table" in str(e):
                from db import init_db
                init_db()  # create tables
                self.items = DB.fetch_items(search_term)
            else:
                raise
        self.item_dropdown.values = [f"{i[1]} (Stock:{i[2]})" for i in self.items]

    def item_search_changed(self, instance, value):
        self.refresh_items(value.strip())

    # ---------- Table ----------
    def refresh_table(self):
        if not self.scoop_items_container:
            return
        self.scoop_items_container.clear_widgets()
        for idx, item in enumerate(self.current_scoop_items):
            row = ScoopItemRow(item["name"], item["quantity"], index=idx)
            self.scoop_items_container.add_widget(row)

    def add_item_to_scoop(self):
        item_name = self.item_dropdown.text
        qty_text = self.quantity_input.text.strip()
        if not item_name or not qty_text.isdigit() or int(qty_text) < 1:
            App.get_running_app().popup("Error", "Select an item and enter a valid quantity!")
            return

        qty = int(qty_text)
        item_data = next((i for i in self.items if f"{i[1]} (Stock:{i[2]})" == item_name), None)
        if not item_data:
            App.get_running_app().popup("Error", "Selected item not found!")
            return
        if qty > item_data[2]:
            App.get_running_app().popup("Error", f"Not enough stock for {item_data[1]}! Only {item_data[2]} available.")
            return

        self.current_scoop_items.append({
            "item_id": item_data[0],
            "name": item_data[1],
            "quantity": qty
        })
        self.refresh_table()

    def remove_item_from_scoop(self, index):
        if 0 <= index < len(self.current_scoop_items):
            self.current_scoop_items.pop(index)
            self.refresh_table()

    def remove_last_item(self):
        if self.scoop_items_container.children:
            self.remove_item_from_scoop(len(self.scoop_items_container.children)-1)


    # ---------- Finalize Scoop ----------
    def finalize_scoop(self):
        client_text = self.client_dropdown.text
        if not client_text:
            App.get_running_app().popup("Error", "Select a client!")
            return
        if not self.current_scoop_items:
            App.get_running_app().popup("Error", "Add at least one item to the scoop!")
            return
        try:
            price = float(self.scoop_price_input.text.strip())
        except ValueError:
            App.get_running_app().popup("Error", "Enter a valid price!")
            return

        client_id = int(client_text.split("ID:")[1].strip(")"))
        DB.save_scoop(client_id, price, self.current_scoop_items)
        App.get_running_app().popup("Success", f"Scoop for {client_text.split(' (')[0]} saved!")

        # Reset
        self.current_scoop_items.clear()
        self.refresh_table()
        self.client_search.text = ""
        self.client_dropdown.text = ""
        self.item_search.text = ""
        self.item_dropdown.text = ""
        self.quantity_input.text = "1"
        self.refresh_clients()
        self.refresh_items()
