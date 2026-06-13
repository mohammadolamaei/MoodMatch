import json
import uuid


def parse_json_text(text):
    text = (text or "").strip()
    if not text:
        return None
    if text.startswith("```"):
        text = text.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(text)
    except Exception:
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            chunk = text[start:end + 1]
            try:
                return json.loads(chunk)
            except Exception:
                return None
    return None


def normalize_response(data, consumed_items):
    consumed_titles = {str(i.get("title", "")).strip().lower() for i in consumed_items}
    out = {"movies": [], "books": [], "games": []}

    for cat in ("movies", "books", "games"):
        seen = set()
        rows = data.get(cat, [])
        if not isinstance(rows, list):
            rows = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            title = str(row.get("title", "")).strip()
            if not title:
                continue
            low = title.lower()
            if low in consumed_titles or low in seen:
                continue
            seen.add(low)
            out[cat].append({
                "id": uuid.uuid4().hex,
                "title": title,
                "description": str(row.get("description", "")).strip() or "No description provided.",
                "reason": str(row.get("reason", "")).strip() or "Matches your current mood.",
                "age_suitability": str(row.get("age_suitability", "")).strip() or "General"
            })
    return out


def fill_missing_recommendations(data, payload):
    mood = payload.get("mood", "your mood")
    age = payload.get("age", "your age")
    for cat in ("movies", "books", "games"):
        while len(data[cat]) < 10:
            idx = len(data[cat]) + 1
            data[cat].append({
                "id": uuid.uuid4().hex,
                "title": f"{cat[:-1].title()} Suggestion {idx}",
                "description": f"A fallback {cat[:-1]} recommendation with similar tone and pacing.",
                "reason": f"Chosen to fit {mood}.",
                "age_suitability": f"{age}+"
            })
        data[cat] = data[cat][:10]
    return data
