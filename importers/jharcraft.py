import re

from bs4 import BeautifulSoup

from .common import get, guess_state, phones, record

ORG = "jharcraft"
NAME = "Jharcraft"
HOME_STATE = "Jharkhand"
SOURCE_URL = "https://www.jharcraft.in/emporium/"


def fetch(s):
    soup = BeautifulSoup(get(s, SOURCE_URL).text, "html.parser")
    out = []
    for item in soup.select(".blog-post-item"):
        title = item.select_one("h3 a")
        body = item.select_one("p.content")
        if not title or not body:
            continue
        lines = [t.strip() for t in body.stripped_strings]
        contact = " ".join(l for l in lines if l.lower().startswith("contact"))
        address = " ".join(l for l in lines if not l.lower().startswith("contact"))
        name = title.get_text(" ", strip=True).title()
        out.append(record(
            ORG, re.sub(r"\W+", "-", name.lower()).strip("-"), name, address,
            guess_state(address, HOME_STATE), SOURCE_URL, "html",
            phones=phones(contact.split(":", 1)[-1]), map_url=title.get("href"),
        ))
    return out
