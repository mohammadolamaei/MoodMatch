import threading
from copy import deepcopy

from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout

from components.header import Header
from components.search_form import SearchForm
from components.status_box import StatusBox
from components.category_tabs import CategoryTabs
from components.recommendation_list import RecommendationList
from utils.validators import normalize_mood


class MainScreen(BoxLayout):
    def __init__(self, store, ai_service, **kwargs):
        super().__init__(orientation="vertical", spacing=dp(10), padding=[dp(10), dp(10), dp(10), dp(10)], **kwargs)
        self.store = store
        self.ai_service = ai_service

        with self.canvas.before:
            Color(0.06, 0.08, 0.1, 1)
            self.bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._sync_bg, size=self._sync_bg)

        self.state = {
            "request_status": "idle",
            "active_category": None,
            "search_state": {},
            "available": {"movies": [], "books": [], "games": []},
            "picked_ids": {"movies": set(), "books": set(), "games": set()},
            "consumed": [],
            "history": [],
            "cache": {}
        }

        self.header = Header()
        self.search_form = SearchForm(
            on_find=self.on_find,
            on_clear=self.on_clear,
            on_input_change=self.on_input_change
        )
        self.status_box = StatusBox()
        self.tabs = CategoryTabs(on_select=self.on_category_select)
        self.results = RecommendationList()

        self.add_widget(self.header)
        self.add_widget(self.search_form)
        self.add_widget(self.status_box)
        self.add_widget(self.tabs)
        self.add_widget(self.results)

        self.tabs.set_disabled(True)
        self.results.set_items([], None, set(), None, None, "Enter details, then tap Find Recommendations.")
        self.status_box.set_idle("Enter details, then tap Find Recommendations.")

        self.restore_state()

    def _sync_bg(self, *_):
        self.bg.pos = self.pos
        self.bg.size = self.size

    def restore_state(self):
        data = self.store.load()
        if not data:
            return
        self.state["consumed"] = data.get("consumed", [])
        self.state["history"] = data.get("history", [])
        self.state["cache"] = data.get("cache", {})
        latest = data.get("latest_search", {})
        self.search_form.set_values(latest)
        if latest:
            self.state["search_state"] = latest

    def persist(self):
        payload = {
            "consumed": self.state["consumed"],
            "history": self.state["history"][-300:],
            "cache": self.state["cache"],
            "latest_search": self.search_form.get_values()
        }
        self.store.save(payload)

    def on_input_change(self):
        has_data = any(self.state["available"][k] for k in ("movies", "books", "games"))
        if has_data:
            self.reset_results_only()
            self.status_box.set_idle("Inputs changed. Tap Find Recommendations.")
            self.results.set_items([], None, set(), None, None, "Inputs changed. Tap Find Recommendations.")

    def on_clear(self):
        self.search_form.reset()
        self.reset_all()

    def reset_results_only(self):
        self.state["request_status"] = "idle"
        self.state["active_category"] = None
        self.state["available"] = {"movies": [], "books": [], "games": []}
        self.state["picked_ids"] = {"movies": set(), "books": set(), "games": set()}
        self.tabs.clear()
        self.tabs.set_disabled(True)
        self.results.set_items([], None, set(), None, None, "Enter details, then tap Find Recommendations.")
        self.status_box.set_idle("Enter details, then tap Find Recommendations.")
        self.search_form.set_loading(False)
        self.persist()

    def reset_all(self):
        self.reset_results_only()
        self.state["search_state"] = {}
        self.persist()

    def on_find(self, payload):
        self.state["search_state"] = payload
        self.store.set_latest_search(payload)
        self.state["request_status"] = "loading"
        self.search_form.set_loading(True)
        self.status_box.set_loading("Finding recommendations...")
        self.tabs.set_disabled(True)
        self.results.set_items([], None, set(), None, None, "Loading recommendations...")

        t = threading.Thread(target=self._fetch_recommendations, args=(payload,), daemon=True)
        t.start()

    def _fetch_recommendations(self, payload):
        mood = normalize_mood(payload.get("mood"), payload.get("custom_mood"))
        body = {
            "age": payload.get("age"),
            "gender": payload.get("gender", ""),
            "mood": mood,
            "feeling": payload.get("feeling", ""),
            "consumedItems": deepcopy(self.state["consumed"])
        }

        cache_key = f'{body["age"]}|{body["gender"]}|{body["mood"]}|{body["feeling"]}'.strip()
        if cache_key in self.state["cache"]:
            data = self.state["cache"][cache_key]
            Clock.schedule_once(lambda dt: self._apply_response(data, from_cache=True))
            return

        ok, data_or_error = self.ai_service.get_recommendations(body)
        if not ok:
            Clock.schedule_once(lambda dt: self._show_error(data_or_error))
            return

        self.state["cache"][cache_key] = data_or_error
        Clock.schedule_once(lambda dt: self._apply_response(data_or_error, from_cache=False))

    def _show_error(self, text):
        self.state["request_status"] = "error"
        self.search_form.set_loading(False)
        error_text = text if text else "Unknown request error"
        self.status_box.set_error(error_text)
        self.results.set_items([], None, set(), None, None, f"Request failed: {error_text[:160]}")

    def _apply_response(self, data, from_cache=False):
        self.state["request_status"] = "success"
        self.search_form.set_loading(False)
        self.state["available"] = {
            "movies": data.get("movies", []),
            "books": data.get("books", []),
            "games": data.get("games", [])
        }
        self.state["picked_ids"] = {"movies": set(), "books": set(), "games": set()}
        self.state["active_category"] = None
        self.tabs.set_disabled(False)
        self.tabs.clear()

        source = "cache" if from_cache else "AI"
        counts = self.category_counts()
        self.status_box.set_success(
            f"Ready from {source}: {counts['movies']} movies, {counts['books']} books, {counts['games']} games."
        )
        self.tabs.set_counts(counts)
        self.results.set_items([], None, set(), None, None, "Recommendations are ready. Choose a category.")
        self.persist()

    def category_counts(self):
        return {
            "movies": len(self.state["available"].get("movies", [])),
            "books": len(self.state["available"].get("books", [])),
            "games": len(self.state["available"].get("games", []))
        }

    def on_category_select(self, category):
        self.state["active_category"] = category

        if not category:
            self.results.set_items([], None, set(), None, None, "Category closed. Choose a tab to show results.")
            return

        items = self.state["available"].get(category, [])
        self.results.set_items(
            items,
            category,
            self.state["picked_ids"][category],
            self.on_pick,
            self.on_consume,
            None
        )

    def on_pick(self, category, item_id):
        items = self.state["available"][category]
        if not items:
            return

        current_picked = self.state["picked_ids"][category]

        if item_id in current_picked:
            idx = next((i for i, row in enumerate(items) if row.get("id") == item_id), None)
            if idx is None or len(items) < 2:
                return
            item = items.pop(idx)
            items.append(item)
            next_item = items[0]
            self.state["picked_ids"][category] = {next_item.get("id")}
        else:
            self.state["picked_ids"][category] = {item_id}

        self.on_category_select(category)
        self.persist()

    def on_consume(self, category, item):
        item_id = item.get("id")
        title = item.get("title", "")

        self.state["consumed"].append({
            "id": item_id,
            "title": title,
            "category": category
        })
        self.state["history"].append({
            "id": item_id,
            "title": title,
            "category": category,
            "age": self.state["search_state"].get("age"),
            "mood": self.state["search_state"].get("mood")
        })

        current = self.state["available"][category]
        self.state["available"][category] = [x for x in current if x.get("id") != item_id]
        if item_id in self.state["picked_ids"][category]:
            self.state["picked_ids"][category].remove(item_id)

        if not self.state["available"][category]:
            self.search_form.set_loading(True)
            self.status_box.set_loading(f"{category.title()} exhausted. Fetching more...")
            self.results.set_items([], None, set(), None, None, f"Refreshing {category} recommendations...")
            payload = deepcopy(self.state["search_state"])
            t = threading.Thread(target=self._fetch_recommendations, args=(payload,), daemon=True)
            t.start()
        else:
            counts = self.category_counts()
            self.tabs.set_counts(counts)
            self.on_category_select(category)
            self.status_box.set_success(f"{title} marked as done. Showing next recommendation.")

        self.persist()
