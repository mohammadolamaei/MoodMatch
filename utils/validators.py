def validate_age(value):
    raw = str(value).strip()
    if not raw:
        return False, "Age is required.", None
    try:
        age = int(raw)
    except Exception:
        return False, "Age must be a number.", None
    if age < 5 or age > 100:
        return False, "Age must be between 5 and 100.", None
    return True, "", age


def validate_custom_mood(value):
    text = " ".join((value or "").strip().split())
    if not text:
        return False, "Custom mood cannot be empty.", ""
    words = text.split(" ")
    if len(words) > 10:
        return False, "Custom mood must be at most 10 words.", ""
    if len(text) > 80:
        return False, "Custom mood is too long.", ""
    return True, "", text


def normalize_mood(mood, custom_mood=""):
    if mood == "Custom":
        return " ".join((custom_mood or "").strip().split()).lower()
    return (mood or "").strip().lower()
