from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.app import App

# Load the KV file for this screen
Builder.load_file("dashboard_screen.kv")


class DashboardScreen(Screen):
    """
    A clean dashboard screen controller.
    All UI layout & styling is in dashboard_screen.kv.
    This class handles logic, navigation, and callbacks.
    """

    def on_enter(self, *args):
        """Called when entering the dashboard screen."""
        print("Dashboard loaded")

    # ---------- Navigation Actions ----------
    def go_to_clients(self):
        """Navigate to the Clients screen."""
        self.manager.current = "clients"

    def go_to_orders(self):
        """Navigate to the Orders screen."""
        self.manager.current = "orders"

    def go_to_newscoop(self):
        """Navigate to the Reports screen."""
        self.manager.current = "newscoop"

    def go_to_items(self):
        """Navigate to Inventory screen (optional)."""
        self.manager.current = "items"

    # ---------- General Actions ----------
    def exit_app(self):
        """Gracefully exit the app."""
        App.get_running_app().stop()
