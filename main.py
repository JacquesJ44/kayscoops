from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from dashboard_window import DashboardScreen
from client_window import ClientScreen
from items_window import ItemsScreen
from new_scoop_window import NewScoopScreen
from orders_window import OrdersScreen

from db import create_tables

class KayScoopsApp(App):
    def build(self):
        create_tables()
        
        sm = ScreenManager()

        # Add screens with consistent names
        sm.add_widget(DashboardScreen(name="dashboard"))
        sm.add_widget(ClientScreen(name="clients"))  # <-- use 'clients'
        sm.add_widget(ItemsScreen(name="items"))
        sm.add_widget(NewScoopScreen(name="newscoop"))
        sm.add_widget(OrdersScreen(name="orders"))

        return sm

    # Optional helper for popups
    def popup(self, title, message):
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button

        content = BoxLayout(orientation='vertical', spacing=10)
        content.add_widget(Label(text=message))
        btn = Button(text="OK", size_hint_y=None, height=40)
        content.add_widget(btn)
        p = Popup(title=title, content=content, size_hint=(0.6, 0.4))
        btn.bind(on_release=p.dismiss)
        p.open()

    def confirm(self, title, message):
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        result = {'confirmed': False}
        content = BoxLayout(orientation='vertical', spacing=10)
        content.add_widget(Label(text=message))
        btn_layout = BoxLayout(size_hint_y=None, height=40, spacing=10)
        yes_btn = Button(text="Yes")
        no_btn = Button(text="No")
        btn_layout.add_widget(yes_btn)
        btn_layout.add_widget(no_btn)
        content.add_widget(btn_layout)

        popup_obj = Popup(title=title, content=content, size_hint=(0.6, 0.4))
        yes_btn.bind(on_release=lambda x: (popup_obj.dismiss(), result.update({'confirmed': True})))
        no_btn.bind(on_release=lambda x: popup_obj.dismiss())
        popup_obj.open()

        from kivy.clock import Clock
        import time
        while popup_obj._window:
            time.sleep(0.05)
        return result['confirmed']


if __name__ == "__main__":
    KayScoopsApp().run()
