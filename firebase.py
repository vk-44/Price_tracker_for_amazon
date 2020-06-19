import requests
import json
from kivymd.app import MDApp
from kivymd.toast import toast
import threading


class FireBase():
    wak = "Your Firebase web API key"  # web API key

    def dual_thread_sign_up(self, email, password):
        self.email = email
        self.password = password
        threading.Thread(target=self.sign_up).start()
        toast("Signing in...")

    def sign_up(self):
        app = MDApp.get_running_app()
        try:
            signup_url = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/signupNewUser?key=" + self.wak
            signup_payload = {"email": self.email, "password": self.password, "returnSecureToken": True}
            sign_up_request = requests.post(signup_url, data=signup_payload)
            signup_data = json.loads(sign_up_request.content.decode())

            if sign_up_request.ok is True:
                refresh_token = signup_data["refreshToken"]
                localId = signup_data["localId"]
                idToken = signup_data["idToken"]

                with open("refresh_token.txt", "w") as f:
                    f.write(refresh_token)

                app.local_id = localId
                app.id_token = idToken

                my_data = '{"tracking_items": "", "dummy": ""}'

                requests.patch("https://test-4efa7.firebaseio.com/" + localId + ".json?auth=" + idToken, data=my_data)
                app.root.ids["screen_manager"].current = "home_screen"

            if sign_up_request.ok is False:
                error_data = json.loads(sign_up_request.content.decode())
                error_msg = error_data["error"]["message"]
                toast(error_msg)

        except requests.exceptions.ConnectionError:
            app.no_con()

    def exchange_refresh_token(self, refresh_token):
        refresh_url = "https://securetoken.googleapis.com/v1/token?key=" + self.wak
        refresh_payload = '{"grant_type": "refresh_token", "refresh_token": "%s"}' % refresh_token
        refresh_req = requests.post(refresh_url, data=refresh_payload)

        local_id = refresh_req.json()['user_id']
        id_token = refresh_req.json()['id_token']

        return id_token, local_id

    def dual_thread_sign_in(self, email,password):
        self.email_1 = email
        self.password_1 = password
        threading.Thread(target=self.sign_in).start()
        toast("Signing in...")

    def sign_in(self):
        app = MDApp.get_running_app()
        try:
            sign_in_url = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key=" + self.wak
            sign_in_payload = {"email": self.email_1, "password": self.password_1, "returnSecureToken": True}
            sign_in_request = requests.post(sign_in_url, data=sign_in_payload)
            sign_in_data = json.loads(sign_in_request.content.decode())

            if sign_in_request.ok == True:
                refresh_token = sign_in_data["refreshToken"]
                localId = sign_in_data["localId"]
                idToken = sign_in_data["idToken"]

                with open("refresh_token.txt", "w") as f:
                    f.write(refresh_token)

                app.local_id = localId
                app.id_token = idToken

                app.root.ids["screen_manager"].current = "home_screen"
                app.root.ids["login_screen"].ids["login_email"].text = ""
                app.root.ids["login_screen"].ids["login_passw"].text = ""

            if sign_in_request.ok == False:
                error_data = json.loads(sign_in_request.content.decode())
                error_msg = error_data["error"]["message"]
                toast(error_msg)
        except requests.exceptions.ConnectionError:
            app.no_con()

    def reset_password(self, email):
        app = MDApp.get_running_app()
        if email == "":
            toast("Email should not be empty!")
            return
        else:
            try:
                reset_pw_url = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/getOobConfirmationCode?key=" + self.wak
                reset_pw_data = {"email": email, "requestType": "PASSWORD_RESET"}
                requests.post(reset_pw_url, data=reset_pw_data)
                toast("An email has been sent to your inbox!")
            except requests.exceptions.ConnectionError:
                app.no_con()



