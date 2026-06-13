from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.textinput import TextInput


class RoundedInput(TextInput):
    def __init__(self, bg=(0.15, 0.17, 0.21, 1), border=(0.26, 0.31, 0.36, 1), radius=14, **kwargs):
        super().__init__(
            background_color=(0, 0, 0, 0),
            background_normal="",
            background_active="",
            padding=[dp(12), dp(12), dp(12), dp(12)],
            **kwargs
        )
        self.bg_color = bg
        self.border_color = border
        self.radius_value = radius

        with self.canvas.before:
            self._border_c = Color(*self.border_color)
            self._border_r = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius_value] * 4)
            self._bg_c = Color(*self.bg_color)
            self._bg_r = RoundedRectangle(pos=(self.x + 1, self.y + 1), size=(self.width - 2, self.height - 2), radius=[max(2, self.radius_value - 1)] * 4)

        self.bind(pos=self._sync, size=self._sync, focus=self._on_focus)

    def _sync(self, *_):
        self._border_r.pos = self.pos
        self._border_r.size = self.size
        self._bg_r.pos = (self.x + 1, self.y + 1)
        self._bg_r.size = (max(1, self.width - 2), max(1, self.height - 2))

    def _on_focus(self, *_):
        if self.focus:
            self._border_c.rgba = (0.29, 0.67, 0.62, 1)
        else:
            self._border_c.rgba = self.border_color
