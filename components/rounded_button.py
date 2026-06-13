from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.button import Button


class RoundedButton(Button):
    def __init__(self, bg_color=(0.20, 0.52, 0.50, 1), radius=14, disabled_color=(0.18, 0.21, 0.25, 1), **kwargs):
        super().__init__(background_normal="", background_down="", background_color=(0, 0, 0, 0), **kwargs)
        self.bg_color = bg_color
        self.disabled_bg_color = disabled_color
        self.radius_value = radius
        self.padding = [dp(12), dp(8), dp(12), dp(8)]
        self.color = (0.94, 0.97, 0.97, 1)

        with self.canvas.before:
            self._bg_color_instruction = Color(*self.bg_color)
            self._bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius_value] * 4)

        self.bind(pos=self._sync, size=self._sync, state=self._update_color, disabled=self._update_color)

    def _sync(self, *_):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size

    def _update_color(self, *_):
        if self.disabled:
            color = self.disabled_bg_color
        elif self.state == "down":
            color = (
                max(0, self.bg_color[0] - 0.06),
                max(0, self.bg_color[1] - 0.06),
                max(0, self.bg_color[2] - 0.06),
                self.bg_color[3]
            )
        else:
            color = self.bg_color
        self._bg_color_instruction.rgba = color

    def set_bg(self, color):
        self.bg_color = color
        self._update_color()
