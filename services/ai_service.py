import json
import os
import uuid

from openai import OpenAI

from utils.helpers import parse_json_text, normalize_response, fill_missing_recommendations

API_KEY = os.getenv("MOODMATCH_API_KEY", "sk-wmezTZy8Ad2Fhet02Jbh3jylad58Y1q7Io618BjYIxTsCv9O")

client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.gapgpt.app/v1"
)


class AIService:
    def __init__(self):
        self.model = "deepseek-v4-flash"

    def get_recommendations(self, payload):
        if not API_KEY:
            return False, "Missing API key. Set MOODMATCH_API_KEY or API_KEY in services/ai_service.py"

        prompt = self._build_prompt(payload)

        text = self._call_responses_api(prompt)
        if not text:
            text = self._call_chat_completions_api(prompt)

        if not text:
            return False, "AI returned an empty response."

        parsed = parse_json_text(text)
        if not parsed:
            return False, f"AI returned invalid JSON. Raw output: {text[:220]}"

        normalized = normalize_response(parsed, payload.get("consumedItems", []))
        final_data = fill_missing_recommendations(normalized, payload)
        return True, final_data

    def _call_responses_api(self, prompt):
        try:
            response = client.responses.create(
                model=self.model,
                input=prompt,
                temperature=0.7
            )
        except Exception:
            return ""

        text = getattr(response, "output_text", "") or ""
        if text.strip():
            return text.strip()

        output = getattr(response, "output", None)
        if not output:
            return ""

        chunks = []
        for part in output:
            content = getattr(part, "content", None)
            if not content:
                continue
            for entry in content:
                t = getattr(entry, "text", "")
                if t:
                    chunks.append(t)
        return "\n".join(chunks).strip()

    def _call_chat_completions_api(self, prompt):
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You only return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            if not response.choices:
                return ""
            msg = response.choices[0].message
            return (msg.content or "").strip()
        except Exception:
            return ""

    def _build_prompt(self, payload):
        body = {
            "age": payload.get("age"),
            "gender": payload.get("gender", ""),
            "mood": payload.get("mood", ""),
            "feeling": payload.get("feeling", ""),
            "consumedItems": payload.get("consumedItems", [])
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