import json
import os


class LocalStore:
    def __init__(self, app):
        self.app = app
        base = app.user_data_dir
        os.makedirs(base, exist_ok=True)
        self.path = os.path.join(base, "moodmatch_store.json")

    def load(self):
        if not os.path.exists(self.path):
            return {}
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def save(self, payload):
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def set_latest_search(self, search):
        data = self.load()
        data["latest_search"] = search
        self.save(data)
