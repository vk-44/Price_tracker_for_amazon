from kivymd.app import MDApp
from kivymd.uix.list import ThreeLineAvatarListItem, ILeftBody, OneLineAvatarListItem
from kivy.uix.image import AsyncImage
from kivymd.toast import toast
import requests
import json
from fake_usrag_bor import FakeUserAgentBOR
from bs4 import BeautifulSoup
from functools import partial
import concurrent.futures
import threading


class Image(ILeftBody, AsyncImage):
    pass


class ViewList():
    def dual_thread(self):
        app = MDApp.get_running_app()
        threading.Thread(target=self.view_list).start()
        fiil = OneLineAvatarListItem(text="        ITEMS YOU TAGGED!", font_style="H6")  # First item in list
        fiil.add_widget(Image(source="icons/amazon-icon.jpg"))
        app.root.ids["tracking_item_screen"].ids["md_list"].add_widget(fiil)
        toast("loading...", duration=5)

    def view_list(self):
        app = MDApp.get_running_app()
        try:
            db_url = requests.get("https://test-4efa7.firebaseio.com/" + app.local_id + ".json?auth=" + app.id_token)
            data = json.loads(db_url.content.decode())
            try:
                self.database = data["tracking_items"]
                database_keys = self.database.keys()
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    executor.map(self.adding_to_list, database_keys)
            except:
                toast("Empty list!")
        except requests.exceptions.ConnectionError:
            app.no_con()

    def adding_to_list(self, db_key):
        app = MDApp.get_running_app()
        items = self.database[db_key]
        url = items["url"]
        ua = FakeUserAgentBOR()
        headers = {"User-Agent": ua.random_chrome_user_agent()}
        try:
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.text, 'lxml')
            title = items["title"]
            if title == "":
                title = soup.find(id="productTitle").text
                title = title.strip()
                requests.patch("https://test-4efa7.firebaseio.com/%s/tracking_items/%s.json?auth=%s"
                               % (app.local_id, db_key, app.id_token),
                               data=json.dumps({"title": title}))
            try:
                price = soup.find(id="priceblock_ourprice").text
            except:
                price = "Error fetching price!"

            item = ThreeLineAvatarListItem(theme_text_color="Custom",
                                           text=title,
                                           secondary_theme_text_color="Custom",
                                           secondary_text="Current Price: " + str(price),
                                           secondary_text_color=[0, 0, 1, 1],
                                           tertiary_theme_text_color="Custom",
                                           tertiary_text="Your Price:  ₹ " + str(
                                               items["user_price"]),
                                           tertiary_text_color=[0, 1, 0, 1],
                                           on_release=partial(MDApp.get_running_app().popup, db_key,
                                                              title,
                                                              price, url))
            if price == "Error fetching price!":
                item.secondary_text_color = [1, 0, 0, 1]

            img_link = items["img_link"]
            if img_link == "":
                img = soup.find(id="imgTagWrapperId")
                img_str = img.img.get('data-a-dynamic-image')
                img_dict = json.loads(img_str)
                img_link = list(img_dict.keys())[3]
                requests.patch("https://test-4efa7.firebaseio.com/%s/tracking_items/%s.json?auth=%s"
                               % (app.local_id, db_key, app.id_token),
                               data=json.dumps({"img_link": img_link}))

            item.add_widget(Image(source=img_link))

            app.root.ids["tracking_item_screen"].ids["md_list"].add_widget(item)
        except:
            pass



