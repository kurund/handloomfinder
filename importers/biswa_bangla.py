from bs4 import BeautifulSoup

from .common import clean, get, guess_state, phones, record, slug

ORG = "biswa-bangla"
NAME = "Biswa Bangla"
HOME_STATE = "West Bengal"
SOURCE_URL = "https://www.artisans.org.in/locations-contact-nos/"


def field(texts, label):
    return next((t.split(":", 1)[1] for t in texts if t.lower().startswith(label)), "")


def fetch(s):
    soup = BeautifulSoup(get(s, SOURCE_URL).text, "html.parser")
    out = []
    for heading in soup.select("h3.elementor-heading-title"):
        column = heading.find_parent(class_="elementor-widget-wrap")
        if not column:
            continue
        texts = [p.get_text(" ", strip=True) for p in column.select(".elementor-widget-text-editor p")]
        address = field(texts, "address")
        if not address:
            continue
        name = clean(heading.get_text(" ", strip=True))
        link = column.select_one('a[href*="goo.gl"], a[href*="google.com/maps"]')
        out.append(record(
            ORG, slug(name), name, address, guess_state(name + " " + address, HOME_STATE), SOURCE_URL, "html",
            phones=phones(field(texts, "contact")), map_url=link["href"] if link else None,
        ))
    return out
