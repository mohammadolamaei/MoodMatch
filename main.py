from kivy.app import App
from kivy.core.window import Window

from screens.main_screen import MainScreen
from services.ai_service import AIService
from storage.local_store import LocalStore


class MoodMatchApp(App):
    def build(self):
        if Window.width < 400:
            Window.size = (400, 760)
        self.store = LocalStore(self)
        self.ai_service = AIService()
        return MainScreen(store=self.store, ai_service=self.ai_service)


if __name__ == "__main__":
    MoodMatchApp().run()
