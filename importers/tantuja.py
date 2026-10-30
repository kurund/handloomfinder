import re

from bs4 import BeautifulSoup

from .common import clean, get, guess_state, phones, record, slug

ORG = "tantuja"
NAME = "Tantuja"
HOME_STATE = "West Bengal"
SOURCE_URL = "https://tantuja.in/stores"
EMBED_COORDS = re.compile(r"!2d(-?\d+\.\d+)!3d(-?\d+\.\d+)")


def fetch(s):
    soup = BeautifulSoup(get(s, SOURCE_URL).text, "html.parser")
    out, seen = [], set()
    for card in soup.select(".card"):
        title, body = card.select_one(".card-title"), card.select_one(".card-text, .txt")
        if not title or not body:
            continue
        name = clean(re.sub(r"[\s,-]*showroom[\s.:]*$", "", clean(title.get_text(" ", strip=True)), flags=re.I))
        address = clean(body.get_text(" ", strip=True))
        if (name.lower(), address.lower()) in seen:
            continue
        seen.add((name.lower(), address.lower()))
        state = guess_state(name + " " + address, HOME_STATE)
        contact = card.select_one(".txt2")
        contact = contact.get_text(" ", strip=True).split("Email")[0] if contact else ""
        if state == HOME_STATE and re.search(r"\bkol", address, re.I):
            # Kolkata landlines are listed as 8 digits without the 033 STD code.
            contact = re.sub(r"(?<!\d)(\d{8})(?!\d)", r"033\1", contact)
        frame = card.find("iframe")
        m = EMBED_COORDS.search(frame.get("src", "")) if frame else None
        out.append(record(
            ORG, slug(name), name, address, state, SOURCE_URL, "html",
            phones=phones(contact),
            lat=float(m.group(2)) if m else None,
            lng=float(m.group(1)) if m else None,
            geo_source="maplink" if m else None,
        ))
    return out
