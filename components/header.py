from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label


class Header(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", size_hint_y=None, padding=[dp(12), dp(10), dp(12), dp(10)], spacing=dp(2), **kwargs)
        self.bind(width=self._resize, minimum_height=self.setter("height"))

        with self.canvas.before:
            Color(0.11, 0.13, 0.17, 1)
            self.bg = RoundedRectangle(radius=[16, 16, 16, 16], pos=self.pos, size=self.size)
        self.bind(pos=self._sync, size=self._sync)

        self.title = Label(
            text="MoodMatch",
            bold=True,
            color=(0.95, 0.98, 0.97, 1),
            size_hint_y=None,
            height=dp(40),
            halign="left",
            valign="middle"
        )
        self.subtitle = Label(
            text="movies, books, and games For your current YOU",
            color=(0.72, 0.83, 0.82, 1),
            size_hint_y=None,
            height=dp(24),
            halign="left",
            valign="middle"
        )
        self.title.bind(size=lambda i, v: setattr(i, "text_size", v))
        self.subtitle.bind(size=lambda i, v: setattr(i, "text_size", v))

        self.add_widget(self.title)
        self.add_widget(self.subtitle)
        self._resize()

    def _resize(self, *_):
        if self.width < dp(430):
            self.title.font_size = sp(24)
            self.subtitle.font_size = sp(12)
        else:
            self.title.font_size = sp(28)
            self.subtitle.font_size = sp(13)
        self.height = dp(88)

    def _sync(self, *_):
        self.bg.pos = self.pos
        self.bg.size = self.size
