import re

from bs4 import BeautifulSoup

from .common import clean, get, guess_state, record, slug

ORG = "mahahandloom"
NAME = "MahaHandloom"
HOME_STATE = "Maharashtra"
SOURCE_URL = "https://www.mahahandloom.com/elm-about-us/"
API_URL = "https://www.mahahandloom.com/wp-json/wp/v2/pages/3741"


def fetch(s):
    text = BeautifulSoup(get(s, API_URL).json()["content"]["rendered"], "html.parser").get_text("\n", strip=True)
    lines = text.split("\n")
    outlets = lines[lines.index("Our Major Outlets") + 1:]
    outlets = outlets[:next(i for i, l in enumerate(outlets) if l.endswith("?"))]
    visit = re.search(r"Visit us at (.+?), and explore", text)
    out = []
    for line in outlets:
        line = clean(line)
        is_main = line.lower().startswith("main show")
        address = visit.group(1) if is_main and visit else re.sub(r"^Main Show ?room at\s*", "", line, flags=re.I)
        name = "Nagpur (Main Showroom)" if is_main else re.sub(r"\s+(Kasturba|near).*$", "", line)
        out.append(record(ORG, slug(name), name, address, guess_state(address, HOME_STATE), SOURCE_URL, "html"))
    return out
