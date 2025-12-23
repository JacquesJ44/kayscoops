from kivy.uix.screenmanager import Screen
from kivy.properties import ListProperty, StringProperty, ObjectProperty
from kivy.clock import mainthread
from kivy.lang import Builder
import os
import sqlite3

from db_ops import DBOps
from invoice_generator import generate_invoice

# Custom Button for list items
from kivy.uix.button import Button

class OrderLabel(Button):
    parent_screen = ObjectProperty()

# Load KV file
Builder.load_file("orders_screen.kv")


class OrdersScreen(Screen):
    search_term = StringProperty("")
    orders_display = ListProperty([])   # Display strings
    orders_raw = []                     # Raw tuples from DB
    selected_order = None               # Selected order string

    def on_pre_enter(self):
        """Refresh clients whenever screen is opened."""
        if not hasattr(self, 'db'):
            self.db = DBOps()  # safe lazy init
        self.refresh_orders()

    # ---------- Refresh Orders ----------
    def refresh_orders(self, search=""):
        try:
            self.orders_raw = self.db.fetch_orders(search)
        except sqlite3.OperationalError as e:
            if "no such table" in str(e):
                from db import init_db
                init_db()  # create tables
                self.orders_raw = self.db.fetch_orders(search)
            else:
                raise

        self.orders_display = [
            f"ID: {o[0]} | Client: {o[1]} | Date: {o[2]} | Total: R{o[3]:.2f}"
            for o in self.orders_raw
        ]

    # Called from KV when typing in search box
    def on_search_changed(self, instance, value):
        self.refresh_orders(value.strip())

    # ---------- Select Order ----------
    def select_order(self, text):
        self.selected_order = text
        self.ids.status_label.text = f"Selected: {text}"

    # ---------- Generate Invoice ----------
    @mainthread
    def generate_invoice_action(self):
        if not self.selected_order:
            self.ids.status_label.text = "Please select an order first."
            return

        try:
            scoop_id = int(self.selected_order.split("ID: ")[1].split(" ")[0])
            generate_invoice(scoop_id)
            filename = f"invoice_{scoop_id}.pdf"

            if os.path.exists(filename):
                if os.name == "nt":
                    os.startfile(filename)
                else:
                    os.system(f"open '{filename}'")
                self.ids.status_label.text = f"Invoice generated: {filename}"
            else:
                self.ids.status_label.text = "Failed to generate invoice."

        except Exception as e:
            self.ids.status_label.text = f"Error: {e}"
