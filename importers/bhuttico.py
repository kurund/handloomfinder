import re

from bs4 import BeautifulSoup

from .common import clean, get, guess_state, record, slug

ORG = "bhuttico"
NAME = "Bhuttico"
HOME_STATE = "Himachal Pradesh"
SOURCE_URL = "https://bhuttico.com/pages/visit-a-bhuttico-store-near-you"


def fetch(s):
    soup = BeautifulSoup(get(s, SOURCE_URL).text, "html.parser")
    out = []
    for store in soup.select(".store"):
        heading = store.select_one("h3")
        if not heading:
            continue
        name = re.sub(r"\b(bhuttico|shawls|showroom|store)\b", " ", heading.get_text(" ", strip=True), flags=re.I)
        name = clean(re.sub(r"\s*\|\s*", " - ", name)).strip(" -")
        address = next((p.get_text(" ", strip=True).split(":", 1)[1] for p in store.select("p")
                        if p.get_text(strip=True).lower().startswith("address")), name)
        out.append(record(ORG, slug(name), name, address, guess_state(address, HOME_STATE), SOURCE_URL, "html"))
    return out
