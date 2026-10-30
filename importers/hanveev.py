import re

from bs4 import BeautifulSoup

from .common import get, guess_state, phones, record

ORG = "hanveev"
NAME = "Hanveev"
HOME_STATE = "Kerala"
SOURCE_URL = "https://hanveevs.com/about/shops"


def fetch(s):
    soup = BeautifulSoup(get(s, SOURCE_URL).text, "html.parser")
    out = []
    for card in soup.select(".shop-card"):
        name = card.h4.get_text(strip=True)
        address = card.select_one(".fa-map-marker + p").get_text(" ", strip=True)
        tel = [a["href"] for a in card.select('a[href^="tel:"]')]
        hours_li = card.select_one(".fa-clock-o")
        hours = None
        if hours_li:
            hours = re.sub(r"\s+", " ", hours_li.parent.get_text(" ", strip=True))
            hours = re.sub(r"\b0(\d:)", r"\1", hours.replace("Opens ", "").replace(" Closes ", " - "))
            if card.find(string=re.compile("Sunday Holiday")):
                hours += ", closed Sunday"
        out.append(record(
            ORG, re.sub(r"\W+", "-", name.lower()).strip("-"), name, address,
            guess_state(address, HOME_STATE), SOURCE_URL, "html",
            phones=phones(*tel), hours=hours,
        ))
    return out
