from kivy.animation import Animation
from kivy.metrics import dp, sp
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView

from components.recommendation_card import RecommendationCard


class RecommendationList(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(do_scroll_x=False, bar_width=dp(6), size_hint_y=1, **kwargs)
        self.container = GridLayout(cols=1, spacing=dp(10), size_hint_y=None, padding=[0, dp(4), 0, dp(12)])
        self.container.bind(minimum_height=self.container.setter("height"))
        self.add_widget(self.container)

    def _state_label(self, text, color):
        lb = Label(text=text, color=color, size_hint_y=None, height=dp(64), halign="left", valign="middle", font_size=sp(13))
        lb.bind(size=lambda i, v: setattr(i, "text_size", v))
        return lb

    def set_items(self, items, category, picked_ids, on_pick, on_consume, state_text=None):
        self.container.clear_widgets()

        if not category:
            self.container.add_widget(self._state_label(state_text or "Choose a category.", (0.72, 0.85, 0.84, 1)))
            return

        if not items:
            self.container.add_widget(self._state_label(f"No {category} available right now.", (0.95, 0.5, 0.5, 1)))
            return

        for item in items:
            card = RecommendationCard(
                item=item,
                category=category,
                is_picked=item.get("id") in picked_ids,
                on_pick=on_pick,
                on_consume=on_consume
            )
            card.opacity = 0
            self.container.add_widget(card)
            Animation(opacity=1, d=0.14).start(card)
