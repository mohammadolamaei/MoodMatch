from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from components.rounded_button import RoundedButton


class RecommendationCard(BoxLayout):
    def __init__(self, item, category, is_picked, on_pick, on_consume, **kwargs):
        super().__init__(orientation="vertical", size_hint_y=None, padding=[dp(10), dp(10), dp(10), dp(10)], spacing=dp(6), **kwargs)

        with self.canvas.before:
            Color(0.12, 0.15, 0.19, 1)
            self.bg = RoundedRectangle(radius=[14, 14, 14, 14], pos=self.pos, size=self.size)
        self.bind(pos=self._sync, size=self._sync)

        self.title = Label(text=item.get("title", "Untitled"), bold=True, font_size=sp(17), color=(0.95, 0.98, 0.97, 1), size_hint_y=None, halign="left", valign="middle")
        self.desc = Label(text=item.get("description", ""), font_size=sp(13), color=(0.84, 0.9, 0.89, 1), size_hint_y=None, halign="left", valign="top")
        self.reason = Label(text=f'Reason: {item.get("reason", "")}', font_size=sp(12), color=(0.64, 0.87, 0.82, 1), size_hint_y=None, halign="left", valign="middle")
        self.age = Label(text=f'Age suitability: {item.get("age_suitability", "N/A")}', font_size=sp(12), color=(0.75, 0.87, 0.86, 1), size_hint_y=None, halign="left", valign="middle")

        for lab in (self.title, self.desc, self.reason, self.age):
            lab.bind(width=self._reflow)

        action_text = {"movies": "Watched", "books": "Read", "games": "Played"}[category]
        pick_text = "Pick Again" if is_picked else "Pick"

        self.row = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(8))
        pick_btn = RoundedButton(text=pick_text, bg_color=(0.22, 0.35, 0.50, 1), disabled_color=(0.18, 0.22, 0.28, 1), color=(0.95, 0.98, 0.97, 1), font_size=sp(13), radius=13)
        done_btn = RoundedButton(text=action_text, bg_color=(0.20, 0.25, 0.32, 1), disabled_color=(0.18, 0.21, 0.26, 1), color=(0.95, 0.98, 0.97, 1), font_size=sp(13), radius=13)

        pick_btn.bind(on_release=lambda *_: on_pick(category, item.get("id")))
        done_btn.bind(on_release=lambda *_: on_consume(category, item))

        self.row.add_widget(pick_btn)
        self.row.add_widget(done_btn)

        self.add_widget(self.title)
        self.add_widget(self.desc)
        self.add_widget(self.reason)
        self.add_widget(self.age)
        self.add_widget(self.row)

        self._reflow()

    def _reflow(self, *_):
        width = max(dp(50), self.width - self.padding[0] - self.padding[2])

        self.title.text_size = (width, None)
        self.desc.text_size = (width, None)
        self.reason.text_size = (width, None)
        self.age.text_size = (width, None)

        self.title.texture_update()
        self.desc.texture_update()
        self.reason.texture_update()
        self.age.texture_update()

        self.title.height = max(dp(26), self.title.texture_size[1] + dp(2))
        self.desc.height = max(dp(40), self.desc.texture_size[1] + dp(2))
        self.reason.height = max(dp(22), self.reason.texture_size[1] + dp(2))
        self.age.height = max(dp(20), self.age.texture_size[1] + dp(2))

        self.height = (
            self.padding[1] + self.padding[3] +
            self.title.height + self.desc.height + self.reason.height + self.age.height +
            self.row.height + self.spacing * 4
        )

    def _sync(self, *_):
        self.bg.pos = self.pos
        self.bg.size = self.size
