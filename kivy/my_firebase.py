import requests
import json

from kivy.app import App


class MyFirebase:
    # Web API key
    wak = "AIzaSyDtDBKDRmjoYmHaTqosiadbsRc91cuX9kk"

    def sign_up(self, email, password):
        app = App.get_running_app()
        # Send email and password to firebase
        # Firebase will return localID, authToken(idToken), refreshToken
        signup_url = f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/signupNewUser?key={self.wak}"
        signup_payload = {"email": email, "password": password, "returnSecureToken": True}
        sign_up_request = requests.post(signup_url, data=signup_payload)
        # print(sign_up_request.ok)
        # print(sign_up_request.content.decode())
        sign_up_data = json.loads(sign_up_request.content.decode())

        if sign_up_request.ok:
            refresh_token = sign_up_data["refreshToken"]
            localId = sign_up_data["localId"]
            idToken = sign_up_data["idToken"]
            # Save refresh Token to a file
            with open("refresh_token.txt", "w") as f:
                f.write(refresh_token)
            # Save localId to a variable in main app class
            # Save idToken to a variable in main app class
            app.localId = localId
            app.id_token = idToken

            # Create new key in database from localId
            # Get friend ID
            # Get request on firebase to get the next friend id
            # Update firebase's next friend id field
            friend_get_req = requests.get(
                f"https://tutorial-78ce1-default-rtdb.firebaseio.com/next_friend_id.json?auth={idToken}"
            )
            my_friend_id = friend_get_req.json()

            print(friend_get_req.json())
            # Default streak
            # Default Avatar
            # Friends list
            # Empty workouts area
            my_data = '{"avatar": "man.png", "friends": "", "workouts": "", "streak ": "0", "my_friend_id": %s}' % \
                      my_friend_id
            post_request = requests.patch(
                f"https://tutorial-78ce1-default-rtdb.firebaseio.com/{localId}.json?auth={idToken}",
                data=my_data)
            # print(post_request.ok)
            # print(json.loads(post_request.content.decode()))
            app.change_screen("home_screen")

        if not sign_up_request.ok:
            error_data = json.loads(sign_up_request.content.decode())
            error_message = error_data["error"]["message"]
            app.root.ids["login_screen"].ids["login_message"].text = error_message

    def exchange_refresh_token(self, refresh_token):
        refresh_url = "https://securetoken.googleapis.com/v1/token?key=" + self.wak
        refresh_payload = '{"grant_type": "refresh_token", "refresh_token": "%s"}' % refresh_token
        refresh_req = requests.post(refresh_url, data=refresh_payload)
        id_token = refresh_req.json()['id_token']
        local_id = refresh_req.json()['user_id']
        return id_token, local_id

    def sign_in(self):
        pass
