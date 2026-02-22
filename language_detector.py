import re

def detect_language(text: str) -> str:
    t = (text or "").lower()

    # Turkish characters
    if re.search(r"[çğıöşü]", t):
        return "tr"

    # Common TR lab words
    tr_words = ["negatif", "pozitif", "yüksek", "düşük", "idrar", "kan", "referans"]
    if any(w in t for w in tr_words):
        return "tr"

    return "en"