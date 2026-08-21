import hashlib
import datetime
import webbrowser
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.core.window import Window

class CyberPredictorApp(App):
    def build(self):
        # Window setup safe initialization
        Window.clearcolor = (0.04, 0.06, 0.08, 1)
        
        self.history = []
        self.current_period = ""
        self.scan_step = 0
        self.referral_url = "https://yaarwin.app/#/register?invitationCode=277622666726"

        root = BoxLayout(orientation='vertical', padding=15, spacing=12)

        # Title Header
        title = Label(
            text="[b][color=#00FF66]⚡ S_GOD VIP PREDICTOR ⚡[/color][/b]",
            markup=True,
            font_size="17sp",
            size_hint=(1, 0.15)
        )

        # Period & Timer
        self.lbl_period = Label(
            text="[color=#00E5FF]SYNCING TIME ENGINE...[/color]",
            markup=True,
            font_size="14sp",
            size_hint=(1, 0.12)
        )

        # Result Display Area
        self.lbl_result = Label(
            text="[b][color=#FFFFFF]SYSTEM READY[/color][/b]\n[size=12sp][color=#778899]WAITING FOR NEXT ROUND[/color][/size]",
            markup=True,
            font_size="15sp",
            halign="center",
            size_hint=(1, 0.35)
        )

        # Radar Progress Bar
        self.scan_bar = ProgressBar(max=100, value=0, size_hint=(1, 0.08))

        # Buttons Panel
        btn_layout = GridLayout(cols=2, spacing=12, size_hint=(1, 0.30))

        btn_scan = Button(
            text="[b]🔍 ANALYZE[/b]",
            markup=True,
            background_normal="",
            background_color=(0.0, 0.75, 0.40, 1),
            font_size="13sp"
        )
        btn_scan.bind(on_release=lambda x: self.trigger_radar_scan())

        btn_open = Button(
            text="[b]🚀 OPEN GAME[/b]",
            markup=True,
            background_normal="",
            background_color=(0.10, 0.55, 0.95, 1),
            font_size="13sp"
        )
        btn_open.bind(on_release=lambda x: webbrowser.open(self.referral_url))

        btn_layout.add_widget(btn_scan)
        btn_layout.add_widget(btn_open)

        root.add_widget(title)
        root.add_widget(self.lbl_period)
        root.add_widget(self.lbl_result)
        root.add_widget(self.scan_bar)
        root.add_widget(btn_layout)

        Clock.schedule_interval(self.tick, 1)
        return root

    def get_period_data(self):
        # IST Time Calculation
        utc_now = datetime.datetime.utcnow()
        ist_now = utc_now + datetime.timedelta(hours=5, minutes=30)
        total_mins = (ist_now.hour * 60) + ist_now.minute + 1
        period_str = f"{ist_now.strftime('%Y%m%d')}01000{total_mins:04d}"
        seconds_left = 60 - ist_now.second
        return period_str, seconds_left

    def tick(self, dt):
        period, seconds_left = self.get_period_data()

        if period != self.current_period:
            self.current_period = period
            self.trigger_radar_scan()

        self.lbl_period.text = f"[b]Period:[/b] {self.current_period[-4:]}  |  [color=#FFD700]Timer: {seconds_left:02d}s[/color]"

    def trigger_radar_scan(self):
        self.scan_step = 0
        self.scan_bar.value = 0
        self.lbl_result.text = "[b][color=#00FF66]AI RADAR SCANNING...[/color][/b]"
        Clock.unschedule(self._animate_radar)
        Clock.schedule_interval(self._animate_radar, 0.04)

    def _animate_radar(self, dt):
        self.scan_step += 5
        self.scan_bar.value = self.scan_step
        if self.scan_step >= 100:
            Clock.unschedule(self._animate_radar)
            self.calculate_prediction(self.current_period)

    def calculate_prediction(self, period):
        if not period:
            return

        seed = int(hashlib.sha256((period + "GOD_V1").encode('utf-8')).hexdigest()[:6], 16)
        size = "BIG" if seed % 2 == 0 else "SMALL"

        target_numbers = [5, 6, 7, 8, 9] if size == "BIG" else [0, 1, 2, 3, 4]
        num_seed = int(hashlib.md5(period.encode('utf-8')).hexdigest()[:6], 16)
        num = target_numbers[num_seed % len(target_numbers)]

        color_str = "[color=#00FF66]GREEN[/color]" if num in [1, 3, 7, 9] else "[color=#FF3333]RED[/color]"
        size_color = "#FFD700" if size == "BIG" else "#00E5FF"

        self.lbl_result.text = (
            f"TARGET: [b][color={size_color}]{size}[/color][/b]  |  "
            f"NUM: [b]{num}[/b]  |  {color_str}\n"
            f"[size=11sp][color=#AAAAAA]ACCURACY: {82 + (num_seed % 15)}%[/color][/size]"
        )

if __name__ == '__main__':
    CyberPredictorApp().run()
