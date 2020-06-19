from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen, NoTransition, SlideTransition
from kivymd.uix.dialog import MDDialog
from kivymd.toast import toast
import requests
import json
import os
import certifi
import threading
import webbrowser
from fake_usrag_bor import FakeUserAgentBOR
from bs4 import BeautifulSoup
from firebase import FireBase
from item_list import ViewList
from indian_currency_format import currency_in_indian_format

os.environ['SSL_CERT_FILE'] = certifi.where()


class LoginScreen(Screen):
    pass


class SignupScreen(Screen):
    pass


class HomeScreen(Screen):
    pass


class TrackingItemScreen(Screen):
    pass


class Main(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "LightGreen"
        self.theme_cls.primary_hue = "A700"
        self.firebase = FireBase()
        self.view_list = ViewList()
        return

    def on_start(self):
        try:
            with open("refresh_token.txt", "r") as f:
                refresh_token = f.read()

            id_token, local_id = self.firebase.exchange_refresh_token(refresh_token)
            self.local_id = local_id
            self.id_token = id_token

            self.root.ids["screen_manager"].transition = NoTransition()
            self.root.ids["screen_manager"].current = "home_screen"
            self.root.ids["screen_manager"].transition = SlideTransition()

        except requests.exceptions.ConnectionError:
            self.no_con()

        except:
            if os.stat("refresh_token.txt").st_size == 0:
                pass

    def no_con(self):
        dialog = MDDialog(
            title='Network Error!', size_hint=(.8, .2),
            text_button_ok='OK', auto_dismiss=False,
            text="Check you connection.")
        dialog.open()

    def add_to_list(self):
        id = self.root.ids["home_screen"].ids
        self.url = id["url"].text
        user_price = id["user_price"].text

        if self.url.startswith("http") is False:
            toast("Invalid URL")
            return

        try:
            user_price = int(user_price)
        except:
            toast("Invalid user price")
            return

        self.user_price = currency_in_indian_format(user_price)
        self.dual_thread()

    def dual_thread(self):
        threading.Thread(target=self.adding_to_db).start()
        toast("Adding to database...")

    def adding_to_db(self):
        ua = FakeUserAgentBOR()
        headers = {"User-Agent": ua.random_chrome_user_agent()}
        try:
            page = requests.get(self.url, headers=headers)
            soup = BeautifulSoup(page.text, 'lxml')
            try:
                title = soup.find(id="productTitle").text
                title = title.strip()
            except:
                title = ""

            try:
                img = soup.find(id="imgTagWrapperId")
                img_str = img.img.get('data-a-dynamic-image')
                img_dict = json.loads(img_str)
                img_link = list(img_dict.keys())[3]
            except:
                img_link = ""

            items_payload = {"url": self.url, "user_price": self.user_price, "title": title, "img_link": img_link}
            requests.post("https://test-4efa7.firebaseio.com/%s/tracking_items.json?auth=%s"
                          % (self.local_id, self.id_token), data=json.dumps(items_payload))
            toast("Item added successfully")

        except requests.exceptions.ConnectionError:
            self.no_con()

        except requests.exceptions.MissingSchema:
            toast("Given URL is not valid!")

    def clear_list(self):
        self.root.ids["tracking_item_screen"].ids["md_list"].clear_widgets()

    def popup(self, db_key, title, price, url, widget):
        self.url = url
        self.db_key = db_key
        title = title[:25] + "..."
        dialog = MDDialog(
            title=title, size_hint=(.8, .2),
            text=price,
            text_button_ok='open URL',
            text_button_cancel="Delete",
            events_callback=self.popup_callback)
        dialog.open()

    def popup_callback(self, *args):
        if args[0] == "Delete":
            try:
                toast("Removing item from list...")
                requests.delete("https://test-4efa7.firebaseio.com/%s/tracking_items/%s.json?auth=%s"
                                % (self.local_id, self.db_key, self.id_token))
                self.clear_list()
                self.view_list.dual_thread()
            except requests.exceptions.ConnectionError:
                self.no_con()
        else:
            webbrowser.open(self.url)

    def sign_out(self):
        dialog = MDDialog(
            title="Log out!", size_hint=(.8, .2),
            text="you will be returned to the login screen",
            text_button_ok='Log out',
            events_callback=self.clear_refresh_token)
        dialog.open()

    def clear_refresh_token(self, *args):
        with open("refresh_token.txt", "w") as f:
            f.write("")
        self.root.ids["screen_manager"].current = "login_screen"


Main().run()
