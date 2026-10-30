import html
import json
import re

from .common import DATA, clean, guess_state, record

ORG = "apco"
NAME = "APCO"
HOME_STATE = "Andhra Pradesh"
# APCO's site refuses automated requests, so this is a copy saved by hand from
# https://apcohandlooms.com/wp-json/wp/v2/store?per_page=100
SOURCE_FILE = DATA / "manual" / "apco.json"
SPELLING = {"Cuttak": "Cuttack", "Gunturu": "Guntur", "Chitoor": "Chittoor", "Collectrate": "Collectorate", "Vmrda": "VMRDA"}


def display_name(raw):
    name = clean(html.unescape(raw))
    if name.isupper():
        name = name.title()
    name = re.sub(r"^Apco\s+", "", name, flags=re.I)
    name = re.sub(r"\bhlh\b", "Handloom House", name, flags=re.I)
    name = re.sub(r"\bPondyBazar\b", "Pondy Bazaar, Chennai", name)
    words = [SPELLING.get(w.title(), w) for w in name.split()]
    return " ".join(w[0].upper() + w[1:] for w in words)


def fetch(s):
    if not SOURCE_FILE.exists():
        raise FileNotFoundError(f"save the APCO store list to {SOURCE_FILE.relative_to(DATA.parent)}")
    out = []
    for store in json.loads(SOURCE_FILE.read_text()):
        name = display_name(store["title"]["rendered"])
        out.append(record(ORG, store["slug"][:40], name, "", guess_state(name, HOME_STATE), store["link"], "manual"))
    return out
