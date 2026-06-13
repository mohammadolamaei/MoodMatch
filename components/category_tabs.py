from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.togglebutton import ToggleButton


class SoftTabButton(ToggleButton):
    def __init__(self, bg_normal=(0.19, 0.23, 0.29, 1), bg_active=(0.26, 0.62, 0.57, 1), **kwargs):
        super().__init__(background_normal="", background_down="", background_color=(0, 0, 0, 0), **kwargs)
        self.bg_normal = bg_normal
        self.bg_active = bg_active

        with self.canvas.before:
            self._c = Color(*self.bg_normal)
            self._r = RoundedRectangle(pos=self.pos, size=self.size, radius=[14, 14, 14, 14])

        self.bind(pos=self._sync, size=self._sync, state=self._update)
        self._update()

    def _sync(self, *_):
        self._r.pos = self.pos
        self._r.size = self.size

    def _update(self, *_):
        self._c.rgba = self.bg_active if self.state == "down" else self.bg_normal


class CategoryTabs(BoxLayout):
    def __init__(self, on_select, **kwargs):
        super().__init__(size_hint_y=None, height=dp(50), spacing=dp(8), **kwargs)
        self.on_select = on_select
        self.buttons = {}
        self.base_label = {
            "movies": "Movies",
            "books": "Books",
            "games": "Games"
        }

        for key in ["movies", "books", "games"]:
            btn = SoftTabButton(
                text=self.base_label[key],
                color=(0.95, 0.98, 0.97, 1),
                font_size=sp(13)
            )
            btn.bind(on_release=lambda b, k=key: self._select(k))
            self.buttons[key] = btn
            self.add_widget(btn)

    def _select(self, key):
        btn = self.buttons[key]
        if btn.state == "down":
            for other_key, other_btn in self.buttons.items():
                if other_key != key:
                    other_btn.state = "normal"
            self.on_select(key)
        else:
            self.on_select(None)

    def clear(self):
        for key, btn in self.buttons.items():
            btn.text = self.base_label[key]
            btn.state = "normal"

    def set_disabled(self, value):
        for btn in self.buttons.values():
            btn.disabled = value
            btn.opacity = 0.55 if value else 1

    def set_counts(self, counts):
        for key, btn in self.buttons.items():
            btn.text = f"{self.base_label[key]} ({counts.get(key, 0)})"
