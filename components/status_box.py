from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label


class StatusBox(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(size_hint_y=None, height=dp(56), padding=[dp(10), dp(8), dp(10), dp(8)], **kwargs)
        with self.canvas.before:
            Color(0.12, 0.15, 0.18, 1)
            self.bg = RoundedRectangle(radius=[12, 12, 12, 12], pos=self.pos, size=self.size)
        self.bind(pos=self._sync, size=self._sync, width=self._resize)

        self.label = Label(text="Ready", color=(0.79, 0.9, 0.88, 1), halign="left", valign="middle")
        self.label.bind(size=lambda i, v: setattr(i, "text_size", v))
        self.add_widget(self.label)
        self._resize()

    def _resize(self, *_):
        self.label.font_size = sp(12) if self.width < dp(430) else sp(13)

    def _sync(self, *_):
        self.bg.pos = self.pos
        self.bg.size = self.size

    def set_idle(self, text="Ready"):
        self.label.text = text
        self.label.color = (0.79, 0.9, 0.88, 1)

    def set_loading(self, text):
        self.label.text = text
        self.label.color = (0.93, 0.83, 0.45, 1)

    def set_error(self, text):
        self.label.text = text
        self.label.color = (0.95, 0.5, 0.5, 1)

    def set_success(self, text):
        self.label.text = text
        self.label.color = (0.42, 0.86, 0.69, 1)
