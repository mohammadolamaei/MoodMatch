import json
import os
import uuid
from typing import Any

import requests

from utils.helpers import fill_missing_recommendations, normalize_response, parse_json_text

API_KEY = os.getenv("MOODMATCH_API_KEY", "sk-wmezTZy8Ad2Fhet02Jbh3jylad58Y1q7Io618BjYIxTsCv9O")
API_BASE_URL = os.getenv("MOODMATCH_API_BASE_URL", "https://api.gapgpt.app/v1").rstrip("/")
API_MODEL = os.getenv("MOODMATCH_API_MODEL", "deepseek-v4-flash")


class AIService:
    def __init__(self):
        self.model = API_MODEL
        self.base_url = API_BASE_URL
        self.session = requests.Session()
        self.timeout = (10, 60)

    def get_recommendations(self, payload):
        if not API_KEY or API_KEY.startswith("sk-wmezTZy8Ad2Fhet02Jbh3jylad58Y1q7Io618BjYIxTsCv9O"):
            return False, "Missing API key. Set MOODMATCH_API_KEY."

        prompt = self._build_prompt(payload)
        text, chat_error = self._call_chat_completions_api(prompt)

        if not text:
            if not chat_error:
                return False, "AI returned an empty response."
            return False, "AI request failed on Android. " + chat_error

        parsed = parse_json_text(text)
        if not parsed:
            return False, f"AI returned invalid JSON. Raw output: {text[:220]}"

        normalized = normalize_response(parsed, payload.get("consumedItems", []))
        final_data = fill_missing_recommendations(normalized, payload)
        return True, final_data

    def _call_chat_completions_api(self, prompt):
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        }
        body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You only return valid JSON."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.7,
        }

        try:
            response = self.session.post(
                url, headers=headers, json=body, timeout=self.timeout
            )
        except requests.RequestException as exc:
            return "", f"{type(exc).__name__}: {exc}"

        if response.status_code >= 400:
            details = (response.text or "").strip().replace("\n", " ")
            return "", f"HTTP {response.status_code}: {details[:220]}"

        try:
            data = response.json()
        except ValueError:
            return "", f"Non-JSON response: {(response.text or '')[:220]}"

        try:
            choices = data.get("choices") or []
            if not choices:
                return "", "chat completions returned no choices."
            msg = choices[0].get("message") or {}
            content = self._extract_text(msg.get("content", ""))
            if content.strip():
                return content.strip(), ""
            return "", "chat completions message content was empty."
        except Exception as exc:
            return "", f"{type(exc).__name__}: {exc}"

    def _extract_text(self, value: Any) -> str:
        chunks = []

        def walk(node):
            if node is None:
                return
            if isinstance(node, str):
                if node.strip():
                    chunks.append(node)
                return
            if isinstance(node, list):
                for item in node:
                    walk(item)
                return
            if isinstance(node, dict):
                node_type = node.get("type")
                if node_type == "output_text" and isinstance(node.get("text"), str):
                    walk(node.get("text"))
                else:
                    for key in ("output_text", "text", "content"):
                        walk(node.get(key))
                return

            node_type = getattr(node, "type", None)
            if node_type == "output_text":
                walk(getattr(node, "text", None))
                return

            for attr in ("output_text", "text", "content"):
                walk(getattr(node, attr, None))

        walk(value)
        return "\n".join(chunks)

    def _build_prompt(self, payload):
        body = {
            "age": payload.get("age"),
            "gender": payload.get("gender", ""),
            "mood": payload.get("mood", ""),
            "feeling": payload.get("feeling", ""),
            "consumedItems": payload.get("consumedItems", []),
        }
        return (
            "Return only JSON with this exact shape: "
            '{"movies":[],"books":[],"games":[]}. '
            "Generate exactly 10 movies, 10 books, and 10 games. "
            "Each item must include: title, description, reason, age_suitability. "
            "Descriptions should be medium length. "
            "Do not repeat consumed items by title. "
            "No markdown. No explanation. No extra keys.\n\n"
            f"Input:\n{json.dumps(body, ensure_ascii=False)}\n"
            f"Request id: {uuid.uuid4().hex[:10]}"
        )
