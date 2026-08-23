import ssl
import json
import datetime
import urllib.request
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.core.window import Window

# Fix SSL verification error on Android APK
try:
    ssl._create_default_https_context = ssl._create_unverified_context
except Exception:
    pass

FIREBASE_URL = "https://sgod-vip-license-default-rtdb.firebaseio.com/keys/"

class SGodAuthApp(App):
    def build(self):
        Window.clearcolor = (0.04, 0.05, 0.08, 1)

        root = BoxLayout(orientation='vertical', padding=20, spacing=15)

        # Header Title
        lbl_title = Label(
            text="[b][color=#FF1744]⚡ S_GOD SECURITY AUTH ⚡[/color][/b]",
            markup=True,
            font_size="18sp",
            size_hint=(1, 0.15)
        )
        root.add_widget(lbl_title)

        # Key Input Box
        self.key_input = TextInput(
            hint_text="Enter VIP Key here...",
            multiline=False,
            font_size="15sp",
            size_hint=(1, 0.25),
            halign="center",
            background_color=(0.10, 0.12, 0.16, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(0, 0.9, 1, 1)
        )
        root.add_widget(self.key_input)

        # Status / Error Label
        self.lbl_status = Label(
            text="",
            markup=True,
            font_size="13sp",
            size_hint=(1, 0.35)
        )
        root.add_widget(self.lbl_status)

        # Unlock Button
        btn_unlock = Button(
            text="[b]🔓 UNLOCK MOD[/b]",
            markup=True,
            size_hint=(1, 0.25),
            background_normal="",
            background_color=(0.0, 0.7, 0.35, 1)
        )
        btn_unlock.bind(on_release=self.verify_key)
        root.add_widget(btn_unlock)

        return root

    def verify_key(self, instance):
        entered_key = self.key_input.text.strip()

        if not entered_key:
            self.lbl_status.text = "[color=#FF3333]Please enter a VIP Key[/color]"
            return

        self.lbl_status.text = "[color=#00E5FF]Checking key with server...[/color]"

        try:
            url = f"{FIREBASE_URL}{entered_key}.json"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=8) as res:
                response_data = res.read().decode()

                if response_data == "null" or not response_data:
                    self.lbl_status.text = "[color=#FF3333]Invalid Key / Not Found[/color]"
                    return

                key_data = json.loads(response_data)

                if isinstance(key_data, dict):
                    status = key_data.get("status", "")
                    expires_at_str = key_data.get("expires_at", "")

                    if status != "active":
                        self.lbl_status.text = "[color=#FF3333]Key has been revoked or expired[/color]"
                        return

                    # Expiry Check
                    if expires_at_str:
                        exp_time = datetime.datetime.strptime(expires_at_str, '%Y-%m-%d %H:%M:%S')
                        current_time = datetime.datetime.utcnow()

                        if current_time > exp_time:
                            self.lbl_status.text = "[color=#FF3333]Key Expired![/color]"
                            return

                    self.lbl_status.text = f"[color=#00E676]Access Granted! Expires: {expires_at_str}[/color]"
                    # Yahan mod launch karne ka code trigger kar sakte hain
                else:
                    self.lbl_status.text = "[color=#FF3333]Invalid Key Data[/color]"

        except Exception as e:
            self.lbl_status.text = f"[color=#FF3333]Network / Verification Error:\n{str(e)}[/color]"

if __name__ == '__main__':
    SGodAuthApp().run()
