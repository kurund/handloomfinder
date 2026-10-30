import re

from bs4 import BeautifulSoup

from .common import clean, get, guess_state, phones, record, slug

ORG = "mrignayani"
NAME = "Mrignayani"
HOME_STATE = "Madhya Pradesh"
SOURCE_URL = "https://mrignayani.org/branches/"


def fetch(s):
    soup = BeautifulSoup(get(s, SOURCE_URL).text, "html.parser")
    out = []
    for row in soup.select("table tr"):
        cells = row.find_all("td")
        if len(cells) < 4:
            continue
        name = re.sub(r"^Mrignayani Emporium,?\s*", "", clean(cells[0].get_text(" ", strip=True)))
        address = clean(cells[1].get_text(" ", strip=True))
        out.append(record(
            ORG, slug(name), name, address, guess_state(name + " " + address, HOME_STATE), SOURCE_URL, "html",
            phones=phones(cells[3].get_text(" ", strip=True)),
        ))
    return out
