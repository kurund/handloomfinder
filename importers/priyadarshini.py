import re
from collections import Counter

from bs4 import BeautifulSoup

from .common import clean, get, guess_state, record, slug

ORG = "priyadarshini"
NAME = "Priyadarshini Handlooms"
HOME_STATE = "Karnataka"
SOURCE_URL = "https://priyadarshinihandlooms.in/pages/priyadarshini-showrooms"


def fetch(s):
    page = get(s, SOURCE_URL + ".json").json()["page"]
    rows = []
    for tr in BeautifulSoup(page["body_html"], "html.parser").find_all("tr"):
        cells = [td.get_text(" ", strip=True) for td in tr.find_all("td")]
        if len(cells) < 2 or not cells[0].isdigit():
            continue
        address = clean(cells[1])
        parts = [p.strip() for p in address.split(",")]
        town = re.sub(r"[-\s]*\d+$", "", parts[-1]).strip()
        rows.append((town, parts[0], address))
    towns = Counter(t for t, _, _ in rows)
    return [
        record(ORG, slug(name), name, address, guess_state(address, HOME_STATE), SOURCE_URL, "html")
        for town, first, address in rows
        for name in [f"{town} ({first})" if towns[town] > 1 else town]
    ]
