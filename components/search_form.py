from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput

from components.rounded_button import RoundedButton
from utils.validators import validate_age, validate_custom_mood


class SearchForm(BoxLayout):
    genders = [
        "Boy",
        "Girl",
        "Boy, But Thinks He's a Girl",
        "Girl, But Thinks She's a Dragon",
        "Hippopotamus",
        "Attack Helicopter"
    ]
    moods = ["Happy", "Sad", "Excited", "Relaxed", "Bored", "Motivated", "Stressed", "Curious", "Custom"]

    def __init__(self, on_find, on_clear, on_input_change, **kwargs):
        super().__init__(orientation="vertical", size_hint_y=None, padding=dp(12), spacing=dp(8), **kwargs)
        self.on_find_cb = on_find
        self.on_clear_cb = on_clear
        self.on_input_change_cb = on_input_change

        with self.canvas.before:
            Color(0.11, 0.13, 0.17, 1)
            self.bg = RoundedRectangle(radius=[16, 16, 16, 16], pos=self.pos, size=self.size)
        self.bind(pos=self._sync, size=self._sync, width=self._resize)

        self.grid = GridLayout(cols=1, spacing=dp(6), size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter("height"))

        self.error = Label(text="", color=(0.95, 0.5, 0.5, 1), size_hint_y=None, height=dp(22), halign="left", valign="middle")
        self.error.bind(size=lambda i, v: setattr(i, "text_size", v))

        title_color = (0.82, 0.91, 0.9, 1)
        input_fg = (0.93, 0.97, 0.96, 1)
        hint_fg = (0.58, 0.72, 0.71, 1)
        field_bg = (0.15, 0.17, 0.21, 1)

        self.age_title = Label(text="Age", size_hint_y=None, height=dp(20), halign="left", valign="middle", color=title_color)
        self.age_title.bind(size=lambda i, v: setattr(i, "text_size", v))
        self.age_input = TextInput(
            hint_text="Enter age (5-100)",
            multiline=False,
            input_filter="int",
            size_hint_y=None,
            height=dp(44),
            foreground_color=input_fg,
            cursor_color=input_fg,
            hint_text_color=hint_fg,
            background_normal="",
            background_active="",
            background_color=field_bg,
            padding=[dp(12), dp(10), dp(12), dp(10)]
        )

        self.gender_title = Label(text="Gender (Optional)", size_hint_y=None, height=dp(20), halign="left", valign="middle", color=title_color)
        self.gender_title.bind(size=lambda i, v: setattr(i, "text_size", v))
        self.gender_spinner = Spinner(
            text="Prefer not to say",
            values=self.genders,
            size_hint_y=None,
            height=dp(44),
            color=input_fg,
            background_normal="",
            background_down="",
            background_color=field_bg
        )

        self.mood_title = Label(text="Mood", size_hint_y=None, height=dp(20), halign="left", valign="middle", color=title_color)
        self.mood_title.bind(size=lambda i, v: setattr(i, "text_size", v))
        self.mood_spinner = Spinner(
            text="Select mood",
            values=self.moods,
            size_hint_y=None,
            height=dp(44),
            color=input_fg,
            background_normal="",
            background_down="",
            background_color=field_bg
        )

        self.custom_mood = TextInput(
            hint_text="Custom mood (max 10 words)",
            multiline=False,
            size_hint_y=None,
            height=dp(44),
            opacity=0,
            disabled=True,
            foreground_color=input_fg,
            cursor_color=input_fg,
            hint_text_color=hint_fg,
            background_normal="",
            background_active="",
            background_color=field_bg,
            padding=[dp(12), dp(10), dp(12), dp(10)]
        )
        self.feeling_input = TextInput(
            hint_text="Optional: describe how you feel",
            multiline=True,
            size_hint_y=None,
            height=dp(84),
            foreground_color=input_fg,
            cursor_color=input_fg,
            hint_text_color=hint_fg,
            background_normal="",
            background_active="",
            background_color=field_bg,
            padding=[dp(12), dp(10), dp(12), dp(10)]
        )

        self.age_input.bind(text=lambda *_: self.on_input_change_cb())
        self.gender_spinner.bind(text=lambda *_: self.on_input_change_cb())
        self.mood_spinner.bind(text=self.on_mood_changed)
        self.custom_mood.bind(text=lambda *_: self.on_input_change_cb())
        self.feeling_input.bind(text=lambda *_: self.on_input_change_cb())

        self.grid.add_widget(self.age_title)
        self.grid.add_widget(self.age_input)
        self.grid.add_widget(self.gender_title)
        self.grid.add_widget(self.gender_spinner)
        self.grid.add_widget(self.mood_title)
        self.grid.add_widget(self.mood_spinner)
        self.grid.add_widget(self.custom_mood)
        self.grid.add_widget(self.feeling_input)
        self.grid.add_widget(self.error)

        btn_row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        self.find_btn = RoundedButton(text="Find Recommendations", bg_color=(0.26, 0.62, 0.57, 1), disabled_color=(0.23, 0.26, 0.31, 1), color=(1, 1, 1, 1), radius=15)
        self.clear_btn = RoundedButton(text="Clear", bg_color=(0.22, 0.28, 0.34, 1), disabled_color=(0.22, 0.25, 0.3, 1), color=(0.95, 0.98, 0.97, 1), radius=15)
        self.find_btn.bind(on_release=lambda *_: self.submit())
        self.clear_btn.bind(on_release=lambda *_: self.clear())

        btn_row.add_widget(self.find_btn)
        btn_row.add_widget(self.clear_btn)

        self.add_widget(self.grid)
        self.add_widget(btn_row)
        self.bind(minimum_height=self.setter("height"))
        self._resize()

    def _sync(self, *_):
        self.bg.pos = self.pos
        self.bg.size = self.size

    def _resize(self, *_):
        text_size = sp(14) if self.width < dp(430) else sp(15)
        label_size = sp(12) if self.width < dp(430) else sp(13)

        self.age_input.font_size = text_size
        self.gender_spinner.font_size = text_size
        self.mood_spinner.font_size = text_size
        self.custom_mood.font_size = text_size
        self.feeling_input.font_size = text_size
        self.find_btn.font_size = text_size
        self.clear_btn.font_size = text_size

        self.age_title.font_size = label_size
        self.gender_title.font_size = label_size
        self.mood_title.font_size = label_size
        self.error.font_size = label_size

        self.height = self.grid.height + dp(46) + dp(8) + dp(24)

    def on_mood_changed(self, *_):
        if self.mood_spinner.text == "Custom":
            self.custom_mood.disabled = False
            self.custom_mood.opacity = 1
        else:
            self.custom_mood.disabled = True
            self.custom_mood.opacity = 0
            self.custom_mood.text = ""
        self.on_input_change_cb()

    def set_loading(self, loading):
        self.find_btn.disabled = loading
        self.find_btn.text = "Loading..." if loading else "Find Recommendations"

    def submit(self):
        age_ok, age_msg, age = validate_age(self.age_input.text)
        if not age_ok:
            self.error.text = age_msg
            return

        mood = self.mood_spinner.text
        if mood not in self.moods:
            self.error.text = "Please select a mood."
            return

        if mood == "Custom":
            custom_ok, custom_msg, clean_custom = validate_custom_mood(self.custom_mood.text)
            if not custom_ok:
                self.error.text = custom_msg
                return
            custom_mood = clean_custom
        else:
            custom_mood = ""

        self.error.text = ""
        payload = {
            "age": age,
            "gender": "" if self.gender_spinner.text == "Prefer not to say" else self.gender_spinner.text,
            "mood": mood,
            "custom_mood": custom_mood,
            "feeling": self.feeling_input.text.strip()
        }
        self.on_find_cb(payload)

    def clear(self):
        self.reset()
        self.on_clear_cb()

    def reset(self):
        self.age_input.text = ""
        self.gender_spinner.text = "Prefer not to say"
        self.mood_spinner.text = "Select mood"
        self.custom_mood.text = ""
        self.custom_mood.disabled = True
        self.custom_mood.opacity = 0
        self.feeling_input.text = ""
        self.error.text = ""
        self.set_loading(False)

    def get_values(self):
        return {
            "age": self.age_input.text.strip(),
            "gender": "" if self.gender_spinner.text == "Prefer not to say" else self.gender_spinner.text,
            "mood": self.mood_spinner.text if self.mood_spinner.text in self.moods else "",
            "custom_mood": self.custom_mood.text.strip(),
            "feeling": self.feeling_input.text.strip()
        }

    def set_values(self, values):
        if not values:
            return
        self.age_input.text = str(values.get("age", ""))
        g = values.get("gender") or "Prefer not to say"
        m = values.get("mood") or "Select mood"
        self.gender_spinner.text = g if g in self.genders else "Prefer not to say"
        self.mood_spinner.text = m if m in self.moods else "Select mood"

        if self.mood_spinner.text == "Custom":
            self.custom_mood.disabled = False
            self.custom_mood.opacity = 1
            self.custom_mood.text = values.get("custom_mood", "")
        else:
            self.custom_mood.disabled = True
            self.custom_mood.opacity = 0

        self.feeling_input.text = values.get("feeling", "")
        self.set_loading(False)
