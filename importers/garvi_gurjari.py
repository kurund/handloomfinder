import re
import sys
from urllib.parse import parse_qs, urlparse

import requests
from bs4 import BeautifulSoup

from .common import get, guess_state, phones, record

ORG = "garvi-gurjari"
NAME = "Garvi Gurjari"
HOME_STATE = "Gujarat"
BASE = "https://garvigurjari.gujarat.gov.in/"
# This page's dropdown lists every outlet; /emporia itself shows a shorter list.
INDEX = BASE + "emporia-rajkot"


def outlet(s, slug, label):
    url = BASE + slug
    try:
        page = get(s, url)
    except requests.HTTPError as e:
        if e.response.status_code != 404:
            raise
        print(f"warning: {NAME} outlet page missing: {url}", file=sys.stderr)
        return None
    soup = BeautifulSoup(page.text, "html.parser")
    frame = soup.find("iframe", id="gmap_canvas")
    address = parse_qs(urlparse(frame["src"]).query)["q"][0] if frame else ""
    address = re.sub(r"^Garvi Gurjari Emporium\s*", "", address)
    text = soup.get_text("\n", strip=True)
    nums = re.findall(r"^\+91[\d\s-]{8,}$", text, flags=re.M)
    return record(
        ORG, slug.removeprefix("emporia-") if slug != "emporia" else "ahmedabad-1",
        label, address, guess_state(label + " " + address, HOME_STATE), url, "html",
        phones=phones(*nums),
    )


def fetch(s):
    soup = BeautifulSoup(get(s, INDEX).text, "html.parser")
    options = [(o["value"], o.get_text(strip=True)) for o in soup.select("#emporia_select option") if o.get("value")]
    records = [r for slug, label in options if (r := outlet(s, slug, label))]
    # The site-wide number in the page chrome appears on every outlet; keep it only where it's the sole contact.
    shared = set.intersection(*(set(r["phones"]) for r in records)) if records else set()
    for r in records:
        own = [p for p in r["phones"] if p not in shared]
        r["phones"] = own or r["phones"]
    return records
