import re
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STORES_DIR = DATA / "stores"
SITE = ROOT / "site"

USER_AGENT = "Mozilla/5.0 (compatible; HandloomFinder/0.1; handloom store directory)"

CITY_STATE = {
    "new delhi": "Delhi",
    "delhi": "Delhi",
    "mumbai": "Maharashtra",
    "bangalore": "Karnataka",
    "bengaluru": "Karnataka",
    "chennai": "Tamil Nadu",
    "kolkata": "West Bengal",
    "hyderabad": "Telangana",
    "lucknow": "Uttar Pradesh",
}


def session():
    s = requests.Session()
    s.headers["User-Agent"] = USER_AGENT
    return s


def get(s, url, **kwargs):
    r = s.get(url, timeout=30, **kwargs)
    r.raise_for_status()
    time.sleep(1)
    return r


def clean(text):
    text = re.sub(r"\s+", " ", text or "").strip(" ,.\"'")
    text = re.sub(r"\(\s+", "(", re.sub(r"\s+\)", ")", text))
    return re.sub(r"\s*,[\s,]*", ", ", text)


def unique_ids(records):
    seen = {}
    for r in records:
        n = seen[r["id"]] = seen.get(r["id"], 0) + 1
        if n > 1:
            r["id"] = f"{r['id']}-{n}"
    return records


def phones(*texts):
    """Indian numbers normalised to +91 followed by 10 digits; anything else is dropped."""
    out = []
    for text in texts:
        for chunk in re.split(r"[/,;|]|\bor\b", text or ""):
            digits = re.sub(r"\D", "", chunk)
            if len(digits) == 12 and digits.startswith("91"):
                digits = digits[2:]
            elif len(digits) == 11 and digits.startswith("0"):
                digits = digits[1:]
            if len(digits) == 10 and digits[0] != "0" and f"+91{digits}" not in out:
                out.append(f"+91{digits}")
    return out


def pincode(text):
    m = re.search(r"(?<!\d)([1-9]\d{2})\s?(\d{3})(?!\d)", text or "")
    return m.group(1) + m.group(2) if m else None


def guess_state(text, default):
    lowered = (text or "").lower()
    for city, state in CITY_STATE.items():
        if re.search(rf"\b{city}\b", lowered):
            return state
    return default


def record(org, source_id, name, address, state, source_url, source_type, **extra):
    return {
        "id": f"{org}-{source_id}",
        "org": org,
        "name": clean(name),
        "address": clean(address),
        "district": extra.get("district"),
        "state": state,
        "pincode": extra.get("pincode") or pincode(address),
        "lat": extra.get("lat"),
        "lng": extra.get("lng"),
        "geo_source": "official" if extra.get("lat") else None,
        "phones": extra.get("phones", []),
        "hours": extra.get("hours"),
        "map_url": extra.get("map_url"),
        "source_url": source_url,
        "source_type": source_type,
        "status": extra.get("status", "open"),
    }
