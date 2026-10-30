import re
from collections import Counter

from bs4 import BeautifulSoup

from .common import clean, get, guess_state, record, slug

ORG = "boyanika"
NAME = "Boyanika"
HOME_STATE = "Odisha"
SOURCE_URL = "https://boyanika.com/store-location/"


SPELLING = {"Cuttak": "Cuttack"}
PREFIX = re.compile(r"^((dist|at|po|post)\b[\s.:/-]*)+", re.I)


def town_and_locality(body):
    parts = [p.strip() for p in re.sub(r"-?\s*\d{5,6}\s*$", "", body).split(",") if p.strip()]
    i = len(parts) - 1
    if i > 0 and re.match(r"dist\b", parts[i], re.I):
        i -= 1
    town = PREFIX.sub("", parts[i]).strip(" -").title() if parts else body
    town = SPELLING.get(town, town)
    locality = next((PREFIX.sub("", p) for p in reversed(parts[:i]) if not re.search(r"\d", p)), None)
    return town, locality


def fetch(s):
    soup = BeautifulSoup(get(s, SOURCE_URL).text, "html.parser")
    rows = []
    for p in soup.select(".elementor-widget-text-editor p"):
        text = clean(p.get_text(" ", strip=True))
        if not re.match(r"boyanika\b", text, re.I) or re.search(r"certified|W\.?C\.?S\.? Ltd", text, re.I):
            continue
        body = re.sub(r"^boyanika\s*,?\s*", "", text, flags=re.I)
        body = re.sub(r"\s*State:\s*\w+|,?\s*India$", "", body)
        rows.append((*town_and_locality(body), body))
    towns = Counter(t for t, _, _ in rows)
    out = []
    for town, locality, body in rows:
        name = f"{town} ({locality})" if towns[town] > 1 and locality and locality.lower() != town.lower() else town
        out.append(record(ORG, slug(name), name, body, guess_state(body, HOME_STATE), SOURCE_URL, "html"))
    return out
