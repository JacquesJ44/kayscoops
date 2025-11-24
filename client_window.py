from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from kivy.app import App
from kivy.lang import Builder
from db_ops import DBOps

DB = DBOps()

# Load KV file
Builder.load_file("client_screen.kv")

class ClientScreen(Screen):
    name_input = ObjectProperty(None)
    contact_input = ObjectProperty(None)
    email_input = ObjectProperty(None)
    search_input = ObjectProperty(None)
    client_list = ObjectProperty(None)

    selected_client_id = None
    clients = []

    def on_pre_enter(self):
        """Refresh clients whenever screen is opened."""
        self.refresh_clients()

    def refresh_clients(self, search_term=None):
        """Fetch clients from DB and update table/list."""
        self.clients = DB.fetch_clients(search_term)
        self.client_list.clear_widgets()

        # Add headings
        headings = ["ID", "Name", "Contact", "Email", "Total Spent (R)"]
        self.client_list.add_widget(ClientRow(*headings, is_heading=True))

        # Add rows
        for idx, client in enumerate(self.clients):
            client_id, name, contact, email, total_spent = client
            row = ClientRow(
                str(client_id),
                name,
                contact,
                email,
                f"{total_spent:.2f}" if total_spent else "0.00",
                index=idx,
                on_select=lambda i=idx: self.select_client(i)
            )
            self.client_list.add_widget(row)

        # Clear input fields and reset selection
        self.name_input.text = ""
        self.contact_input.text = ""
        self.email_input.text = ""
        self.selected_client_id = None

    def on_search(self, text):
        self.refresh_clients(text.strip())

    def select_client(self, idx):
        """Populate input fields when a client is selected."""
        client = self.clients[idx]
        self.selected_client_id = client[0]
        self.name_input.text = client[1]
        self.contact_input.text = client[2]
        self.email_input.text = client[3]

    def add_client(self):
        name = self.name_input.text.strip()
        contact = self.contact_input.text.strip()
        email = self.email_input.text.strip()

        if not name:
            App.get_running_app().popup("Error", "Please enter a name!")
            return

        if email and DB.email_exists(email):
            App.get_running_app().popup("Error", f"Email '{email}' is already registered!")
            return

        DB.add_client(name, contact, email)
        App.get_running_app().popup("Success", f"Client '{name}' added successfully!")
        self.refresh_clients()

    def update_client(self):
        if not self.selected_client_id:
            App.get_running_app().popup("Error", "Please select a client to update!")
            return

        name = self.name_input.text.strip()
        contact = self.contact_input.text.strip()
        email = self.email_input.text.strip()

        if not name:
            App.get_running_app().popup("Error", "Please enter a name!")
            return

        DB.update_client(self.selected_client_id, name, contact, email)
        App.get_running_app().popup("Success", f"Client '{name}' updated successfully!")
        self.refresh_clients()

    def delete_client(self):
        if not self.selected_client_id:
            App.get_running_app().popup("Error", "Please select a client to delete!")
            return

        def on_confirm(instance):
            DB.delete_client(self.selected_client_id)
            self.selected_client_id = None
            self.refresh_clients()
            App.get_running_app().popup("Deleted", "Client deleted successfully!")
            popup.dismiss()

        def on_cancel(instance):
            popup.dismiss()

        # Build non-blocking confirm popup
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        from kivy.uix.label import Label

        content = BoxLayout(orientation='vertical', spacing=10)
        content.add_widget(Label(text="Are you sure you want to delete this client?"))

        buttons = BoxLayout(size_hint_y=None, height=40, spacing=10)
        yes_btn = Button(text="Yes")
        no_btn = Button(text="No")
        buttons.add_widget(yes_btn)
        buttons.add_widget(no_btn)
        content.add_widget(buttons)

        popup = Popup(title="Confirm Delete", content=content, size_hint=(0.6, 0.4))
        yes_btn.bind(on_release=on_confirm)
        no_btn.bind(on_release=on_cancel)
        popup.open()



# ---------- ClientRow for table ----------
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

class ClientRow(BoxLayout):
    def __init__(self, id_, name, contact, email, spent, index=0, on_select=None, is_heading=False, **kwargs):
        super().__init__(orientation="horizontal", size_hint_y=None, height=40, spacing=5, **kwargs)
        self.index = index
        bg_color = (0.9, 0.9, 0.95, 1) if index % 2 == 0 else (0.85, 0.85, 0.9, 1)
        if is_heading:
            bg_color = (0.65, 0.5, 0.9, 1)
        with self.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(*bg_color)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

        # Columns
        self.add_widget(Label(text=id_, size_hint_x=0.1, bold=is_heading, color=(1,1,1,1) if is_heading else (0,0,0,1)))
        self.add_widget(Label(text=name, size_hint_x=0.25, bold=is_heading, color=(1,1,1,1) if is_heading else (0,0,0,1)))
        self.add_widget(Label(text=contact, size_hint_x=0.25, bold=is_heading, color=(1,1,1,1) if is_heading else (0,0,0,1)))
        self.add_widget(Label(text=email, size_hint_x=0.25, bold=is_heading, color=(1,1,1,1) if is_heading else (0,0,0,1)))
        self.add_widget(Label(text=spent, size_hint_x=0.15, bold=is_heading, color=(1,1,1,1) if is_heading else (0,0,0,1)))

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
