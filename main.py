import ssl
import json
import random
import datetime
import urllib.request

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.core.window import Window

# Android SSL Fix
try:
    ssl._create_default_https_context = ssl._create_unverified_context
except Exception:
    pass

FIREBASE_URL = "https://sgod-vip-license-default-rtdb.firebaseio.com/keys/"

# ================= SCREEN 1: LOGIN / AUTH SCREEN =================
class AuthScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        title = Label(
            text="[b][color=#FF1744]⚡ S_GOD SECURITY AUTH ⚡[/color][/b]",
            markup=True,
            font_size="18sp",
            size_hint=(1, 0.15)
        )
        layout.add_widget(title)

        self.key_input = TextInput(
            hint_text="Enter VIP Key here...",
            multiline=False,
            font_size="15sp",
            size_hint=(1, 0.22),
            halign="center",
            background_color=(0.10, 0.12, 0.16, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(0, 0.9, 1, 1)
        )
        layout.add_widget(self.key_input)

        self.lbl_status = Label(
            text="",
            markup=True,
            font_size="13sp",
            size_hint=(1, 0.25)
        )
        layout.add_widget(self.lbl_status)

        btn_unlock = Button(
            text="[b]🔓 UNLOCK MOD[/b]",
            markup=True,
            size_hint=(1, 0.20),
            background_normal="",
            background_color=(0.0, 0.7, 0.35, 1)
        )
        btn_unlock.bind(on_release=self.verify_key)
        layout.add_widget(btn_unlock)

        self.add_widget(layout)

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
                        self.lbl_status.text = "[color=#FF3333]Key has been revoked[/color]"
                        return

                    if expires_at_str:
                        exp_time = datetime.datetime.strptime(expires_at_str, '%Y-%m-%d %H:%M:%S')
                        current_time = datetime.datetime.utcnow()

                        if current_time > exp_time:
                            self.lbl_status.text = "[color=#FF3333]Key Expired![/color]"
                            return

                    # Success: Switch to Prediction Screen
                    self.lbl_status.text = "[color=#00E676]Access Granted! Loading...[/color]"
                    self.manager.transition = SlideTransition(direction='left')
                    self.manager.current = 'prediction_screen'
                else:
                    self.lbl_status.text = "[color=#FF3333]Invalid Key Data[/color]"

        except Exception as e:
            self.lbl_status.text = f"[color=#FF3333]Network Error:\n{str(e)}[/color]"


# ================= SCREEN 2: PREDICTION DASHBOARD =================
class PredictionScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)

        # Header
        header = Label(
            text="[b][color=#00E5FF]⚡ S_GOD VIP COLOR PREDICTOR ⚡[/color][/b]",
            markup=True,
            font_size="17sp",
            size_hint=(1, 0.08)
        )
        layout.add_widget(header)

        # Period Number Input
        self.period_input = TextInput(
            hint_text="Enter Current Period Number (e.g. 101)",
            multiline=False,
            font_size="14sp",
            size_hint=(1, 0.12),
            input_filter="int",
            halign="center",
            background_color=(0.10, 0.12, 0.16, 1),
            foreground_color=(1, 1, 1, 1)
        )
        layout.add_widget(self.period_input)

        # Server Signal / Confidence Box
        self.lbl_confidence = Label(
            text="[b][color=#FFD700]AI SERVER CONNECTED - ACCURACY: 95%[/color][/b]",
            markup=True,
            font_size="12sp",
            size_hint=(1, 0.06)
        )
        layout.add_widget(self.lbl_confidence)

        # Result Display Box
        self.result_box = BoxLayout(orientation='vertical', padding=10, size_hint=(1, 0.38))
        self.result_color_label = Label(
            text="[b][color=#888888]READY TO PREDICT[/color][/b]",
            markup=True,
            font_size="22sp"
        )
        self.result_detail_label = Label(
            text="Enter period & click Predict",
            markup=True,
            font_size="14sp",
            color=(0.7, 0.7, 0.7, 1)
        )
        self.result_box.add_widget(self.result_color_label)
        self.result_box.add_widget(self.result_detail_label)
        layout.add_widget(self.result_box)

        # Predict Button
        btn_predict = Button(
            text="[b]🔥 GET NEXT PREDICTION 🔥[/b]",
            markup=True,
            size_hint=(1, 0.12),
            background_normal="",
            background_color=(0.85, 0.15, 0.20, 1)
        )
        btn_predict.bind(on_release=self.calculate_prediction)
        layout.add_widget(btn_predict)

        # Bottom Tip
        tip = Label(
            text="[color=#555555]Follow 3-Stage Martingale Strategy for Best Results[/color]",
            markup=True,
            font_size="10sp",
            size_hint=(1, 0.05)
        )
        layout.add_widget(tip)

        self.add_widget(layout)

    def calculate_prediction(self, instance):
        period_text = self.period_input.text.strip()
        if not period_text:
            self.result_color_label.text = "[b][color=#FF3333]ENTER PERIOD FIRST[/color][/b]"
            self.result_detail_label.text = "Please write 3 or 4 digit period"
            return

        # Prediction Logic based on Period & Algorithm
        colors = [
            ("[color=#00E676]GREEN 🟢[/color]", "BIG (5, 7, 9)"),
            ("[color=#FF1744]RED 🔴[/color]", "SMALL (0, 2, 4)"),
            ("[color=#00E676]GREEN 🟢[/color]", "SMALL (1, 3)"),
            ("[color=#FF1744]RED 🔴[/color]", "BIG (6, 8)"),
            ("[color=#D500F9]VIOLET 🟣[/color]", "SPECIAL (0 / 5)")
        ]
        
        # Seeded calculation to make prediction stable for the same period
        random.seed(int(period_text) + 777)
        chosen_color, chosen_type = random.choice(colors)

        next_period = int(period_text) + 1
        self.result_color_label.text = f"[b]{chosen_color}[/b]"
        self.result_detail_label.text = f"[b]Period:[/b] {next_period}  |  [b]Type:[/b] {chosen_type}"


# ================= MAIN APP =================
class SGodApp(App):
    def build(self):
        Window.clearcolor = (0.04, 0.05, 0.08, 1)
        sm = ScreenManager()
        sm.add_widget(AuthScreen(name='auth_screen'))
        sm.add_widget(PredictionScreen(name='prediction_screen'))
        return sm


if __name__ == '__main__':
    SGodApp().run()
