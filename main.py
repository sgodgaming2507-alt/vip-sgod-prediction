import hashlib
import datetime
import webbrowser
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.utils import platform

if platform == 'android':
    from jnius import autoclass
    from android.runnable import run_on_ui_thread
    WebView = autoclass('android.webkit.WebView')
    WebViewClient = autoclass('android.webkit.WebViewClient')
    activity = autoclass('org.kivy.android.PythonActivity').mActivity
else:
    def run_on_ui_thread(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper

Window.clearcolor = (0.06, 0.08, 0.12, 1)

class SmartGameAssistApp(App):
    def build(self):
        self.history = []
        self.current_period = ""
        self.cached_predictions = {}
        
        # 🔗 APNA REFERRAL LINK YAHAN REPLACE KAREIN
        self.referral_url = "https://example.com/register?r_code=SGOD_VIP"
        self.game_url = self.referral_url

        self.root = BoxLayout(orientation='vertical', spacing=0)

        # Top Overlay Panel (Screen ka 35%)
        top_panel = BoxLayout(orientation='vertical', padding=8, spacing=4, size_hint=(1, 0.35))

        title = Label(
            text="[b][color=#FFD700]VIP S_GOD PREDICTOR[/color][/b]",
            markup=True,
            font_size="15sp",
            size_hint=(1, 0.18)
        )

        self.p = Label(
            text="Syncing Period...",
            markup=True,
            font_size="13sp",
            size_hint=(1, 0.14),
            color=(0.2, 0.9, 1, 1)
        )

        self.r = Label(
            text="[b]PREDICTION: WAITING...[/b]",
            markup=True,
            font_size="14sp",
            size_hint=(1, 0.34),
            color=(0.95, 0.95, 0.95, 1)
        )

        # Action Buttons
        btn_layout = GridLayout(cols=4, spacing=5, size_hint=(1, 0.34))
        
        btn_big = Button(
            text="+ BIG",
            background_normal="",
            background_color=(0.9, 0.65, 0, 1),
            font_size="12sp",
            bold=True
        )
        btn_big.bind(on_release=lambda x: self.add_real_result(1))

        btn_small = Button(
            text="+ SMALL",
            background_normal="",
            background_color=(0.1, 0.6, 0.9, 1),
            font_size="12sp",
            bold=True
        )
        btn_small.bind(on_release=lambda x: self.add_real_result(0))

        btn_ref = Button(
            text="🎁 REGISTER",
            background_normal="",
            background_color=(0.0, 0.75, 0.3, 1),
            font_size="11sp",
            bold=True
        )
        btn_ref.bind(on_release=lambda x: webbrowser.open(self.referral_url))

        btn_reload = Button(
            text="🔄 RELOAD",
            background_normal="",
            background_color=(0.35, 0.35, 0.35, 1),
            font_size="11sp"
        )
        btn_reload.bind(on_release=lambda x: self.reload_webview())

        btn_layout.add_widget(btn_big)
        btn_layout.add_widget(btn_small)
        btn_layout.add_widget(btn_ref)
        btn_layout.add_widget(btn_reload)

        for w in [title, self.p, self.r, btn_layout]:
            top_panel.add_widget(w)

        # Bottom WebView Area (Screen ka 65%)
        self.web_area = BoxLayout(size_hint=(1, 0.65))

        self.root.add_widget(top_panel)
        self.root.add_widget(self.web_area)

        Clock.schedule_interval(self.tick, 1)
        Clock.schedule_once(self.init_webview, 0.5)

        return self.root

    @run_on_ui_thread
    def init_webview(self, *args):
        if platform == 'android':
            self.webview = WebView(activity)
            settings = self.webview.getSettings()
            settings.setJavaScriptEnabled(True)
            settings.setDomStorageEnabled(True)
            self.webview.setWebViewClient(WebViewClient())
            self.webview.loadUrl(self.game_url)
            activity.setContentView(self.webview)

    @run_on_ui_thread
    def reload_webview(self):
        if platform == 'android' and hasattr(self, 'webview'):
            self.webview.reload()

    def get_ist_time(self):
        utc_now = datetime.datetime.now(datetime.timezone.utc)
        ist_tz = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
        return utc_now.astimezone(ist_tz)

    def get_okwin_period(self):
        ist_now = self.get_ist_time()
        total_minutes = (ist_now.hour * 60) + ist_now.minute + 1
        date_str = ist_now.strftime('%Y%m%d')
        return f"{date_str}01000{total_minutes:04d}"

    def add_real_result(self, val):
        self.history.append(val)
        if len(self.history) > 12:
            self.history.pop(0)
        self.calc_advanced_prediction(self.current_period, force=True)

    def tick(self, dt):
        period = self.get_okwin_period()
        ist_now = self.get_ist_time()
        seconds_left = 60 - ist_now.second

        if period != self.current_period:
            self.current_period = period
            self.calc_advanced_prediction(period)

        self.p.text = f"[b]Period:[/b] {self.current_period[-4:]} | [color=#ffbb00]Timer: {seconds_left:02d}s[/color]"

    def calc_advanced_prediction(self, period, force=False):
        if not period:
            return

        if force or (period not in self.cached_predictions):
            history_len = len(self.history)
            
            if history_len < 2:
                seed = (period + "SALT_V2").encode('utf-8')
                val = int(hashlib.sha256(seed).hexdigest()[:8], 16)
                size = "BIG" if (val % 2 == 0) else "SMALL"
            else:
                transitions = {'00': 0, '01': 0, '10': 0, '11': 0}
                for i in range(history_len - 1):
                    pair = f"{self.history[i]}{self.history[i+1]}"
                    transitions[pair] = transitions.get(pair, 0) + 1
                
                last_state = str(self.history[-1])
                prob_to_big = transitions.get(last_state + '1', 0)
                prob_to_small = transitions.get(last_state + '0', 0)
                size = "BIG" if prob_to_big >= prob_to_small else "SMALL"

            num_list = [5, 6, 7, 8, 9] if size == "BIG" else [0, 1, 2, 3, 4]
            p_seed = int(hashlib.md5(period.encode('utf-8')).hexdigest()[:6], 16)
            num = num_list[p_seed % len(num_list)]
            color_str = "[color=#00ff66]GREEN[/color]" if num in [1, 3, 7, 9] else "[color=#ff3333]RED[/color]"

            self.cached_predictions[period] = {
                "size": size,
                "num": num,
                "color": color_str
            }

        d = self.cached_predictions[period]
        self.r.text = f"Forecast: [color=#ffff00][b]{d['size']}[/b][/color] | Target: [b]{d['num']}[/b] | {d['color']}"

if __name__ == '__main__':
    SmartGameAssistApp().run()
