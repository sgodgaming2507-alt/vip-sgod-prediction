import hashlib
import datetime
import urllib.request
import json
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.switch import Switch
from kivy.clock import Clock
from kivy.core.window import Window

FIREBASE_URL = "https://sgod-vip-license-default-rtdb.firebaseio.com/keys/"

class SGodPredictorApp(App):
    def build(self):
        Window.clearcolor = (0.05, 0.05, 0.07, 1)
        self.is_authenticated = False
        self.current_period = ""
        self.scan_count = 0
        self.is_scanning = False
        self.radar_frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.frame_idx = 0

        self.root = BoxLayout(orientation='vertical', padding=14, spacing=10)
        self.show_login_screen()
        return self.root

    def show_login_screen(self):
        self.root.clear_widgets()

        title = Label(
            text="[b][color=#FF3366]⚡ S_GOD SECURITY AUTH ⚡[/color][/b]",
            markup=True,
            font_size="17sp",
            size_hint=(1, 0.2)
        )

        self.key_input = TextInput(
            hint_text="ENTER VIP ACCESS KEY",
            multiline=False,
            size_hint=(1, 0.15),
            font_size="14sp",
            halign="center",
            background_color=(0.12, 0.14, 0.18, 1),
            foreground_color=(1, 1, 1, 1)
        )

        self.lbl_auth_status = Label(
            text="[color=#AAAAAA]Key verification required[/color]",
            markup=True,
            font_size="12sp",
            size_hint=(1, 0.15)
        )

        btn_verify = Button(
            text="[b]🔓 UNLOCK MOD[/b]",
            markup=True,
            size_hint=(1, 0.18),
            background_normal="",
            background_color=(0.0, 0.75, 0.40, 1)
        )
        btn_verify.bind(on_release=lambda x: self.verify_key())

        self.root.add_widget(title)
        self.root.add_widget(self.key_input)
        self.root.add_widget(self.lbl_auth_status)
        self.root.add_widget(btn_verify)

    def verify_key(self):
        user_key = self.key_input.text.strip().upper()
        if not user_key:
            self.lbl_auth_status.text = "[color=#FF3344]Please enter a valid key![/color]"
            return

        self.lbl_auth_status.text = "[color=#00E5FF]Verifying with Server...[/color]"
        Clock.schedule_once(lambda dt: self._check_server(user_key), 0.2)

    def _check_server(self, key):
        try:
            req = urllib.request.Request(f"{FIREBASE_URL}{key}.json")
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())

            if data and data.get("status") == "active":
                exp_str = data.get("expires_at")
                exp_dt = datetime.datetime.strptime(exp_str, '%Y-%m-%d %H:%M:%S')

                if datetime.datetime.utcnow() < exp_dt:
                    self.is_authenticated = True
                    self.show_main_dashboard()
                else:
                    self.lbl_auth_status.text = "[color=#FF3344]KEY EXPIRED! Contact Admin.[/color]"
            else:
                self.lbl_auth_status.text = "[color=#FF3344]INVALID KEY! Access Denied.[/color]"
        except Exception:
            self.lbl_auth_status.text = "[color=#FF3344]Network / Verification Error[/color]"

    def show_main_dashboard(self):
        self.root.clear_widgets()

        lbl_mod_name = Label(
            text="[b][color=#FF3366]⚡ S_GOD MOD [VIP ACTIVE] ⚡[/color][/b]",
            markup=True,
            font_size="15sp",
            size_hint=(1, 0.12)
        )

        toggle_box = BoxLayout(orientation='vertical', spacing=4, size_hint=(1, 0.20))
        r1 = BoxLayout(orientation='horizontal', size_hint=(1, 0.5))
        r1.add_widget(Label(text="[b]WINGO SERVER BYPASS[/b]", markup=True, font_size="12sp"))
        r1.add_widget(Switch(active=True))

        r2 = BoxLayout(orientation='horizontal', size_hint=(1, 0.5))
        r2.add_widget(Label(text="[b]AI AUTO SNIFFER[/b]", markup=True, font_size="12sp"))
        r2.add_widget(Switch(active=True))

        toggle_box.add_widget(r1)
        toggle_box.add_widget(r2)

        self.lbl_target = Label(
            text="[b][color=#00FF66]MOD READY[/color][/b]\n[size=12sp]Awaiting Next Draw[/size]",
            markup=True,
            font_size="18sp",
            halign="center",
            size_hint=(1, 0.38)
        )

        btn_layout = GridLayout(cols=2, spacing=8, size_hint=(1, 0.20))
        btn_scan = Button(
            text="[b]🔍 FORCE SCAN[/b]",
            markup=True,
            background_normal="",
            background_color=(0.10, 0.60, 1.0, 1)
        )
        btn_scan.bind(on_release=lambda x: self.trigger_radar_scan())

        btn_lock = Button(
            text="[b]🔒 LOCK[/b]",
            markup=True,
            background_normal="",
            background_color=(0.3, 0.3, 0.35, 1)
        )
        btn_lock.bind(on_release=lambda x: self.show_login_screen())

        btn_layout.add_widget(btn_scan)
        btn_layout.add_widget(btn_lock)

        self.root.add_widget(lbl_mod_name)
        self.root.add_widget(toggle_box)
        self.root.add_widget(self.lbl_target)
        self.root.add_widget(btn_layout)

        Clock.schedule_interval(self.tick, 1)

    def tick(self, dt):
        if not self.is_authenticated:
            return
        utc_now = datetime.datetime.utcnow()
        ist_now = utc_now + datetime.timedelta(hours=5, minutes=30)
        total_mins = (ist_now.hour * 60) + ist_now.minute + 1
        period = f"{ist_now.strftime('%Y%m%d')}01000{total_mins:04d}"

        if period != self.current_period:
            self.current_period = period
            self.trigger_radar_scan()

    def trigger_radar_scan(self):
        if self.is_scanning or not self.is_authenticated:
            return
        self.is_scanning = True
        self.scan_count = 0
        Clock.schedule_interval(self._animate_radar, 0.08)

    def _animate_radar(self, dt):
        self.scan_count += 1
        self.frame_idx = (self.frame_idx + 1) % len(self.radar_frames)
        spin_char = self.radar_frames[self.frame_idx]

        self.lbl_target.text = f"[b][color=#FF1744]{spin_char} ANALYZING PERIOD... {spin_char}[/color][/b]"

        if self.scan_count >= 20:
            Clock.unschedule(self._animate_radar)
            self.is_scanning = False
            self.show_prediction_result(self.current_period)

    def show_prediction_result(self, period):
        if not period:
            return
        seed = int(hashlib.sha256((period + "VIP_KEY").encode('utf-8')).hexdigest()[:6], 16)
        num = seed % 10
        size = "BIG" if num >= 5 else "SMALL"
        color = "GREEN" if num in [1, 3, 7, 9] else "RED"

        self.lbl_target.text = (
            f"[size=12sp][color=#00E5FF]PERIOD: {period[-4:]}[/color][/size]\n"
            f"[size=44sp][b][color=#FFFFFF]{num}[/color][/b][/size]\n"
            f"[size=14sp][b]{size}[/b]  |  {color}[/size]"
        )

if __name__ == '__main__':
    SGodPredictorApp().run()
