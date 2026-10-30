import json
import math
import re
from urllib.parse import unquote

from .common import DATA, get

CACHE_PATH = DATA / "geocache.json"
NOMINATIM = "https://nominatim.openstreetmap.org"
COORDS = [
    re.compile(r"@(-?\d+\.\d+),(-?\d+\.\d+)"),
    re.compile(r"!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)"),
    re.compile(r"[?&](?:q|ll|query)=(-?\d+\.\d+),\+?(-?\d+\.\d+)"),
]


class Geocoder:
    def __init__(self, s):
        self.s = s
        self.cache = json.loads(CACHE_PATH.read_text()) if CACHE_PATH.exists() else {}

    def save(self):
        CACHE_PATH.write_text(json.dumps(self.cache, indent=1, sort_keys=True, ensure_ascii=False) + "\n")

    def _nominatim(self, path, params):
        key = path + "?" + "&".join(f"{k}={v}" for k, v in sorted(params.items()))
        if key not in self.cache:
            r = get(self.s, NOMINATIM + path, params={**params, "format": "jsonv2", "addressdetails": 1})
            self.cache[key] = r.json()
        return self.cache[key]

    def search(self, **params):
        return self._nominatim("/search", {**params, "countrycodes": "in", "limit": 1})

    def reverse(self, lat, lng):
        return self._nominatim("/reverse", {"lat": round(lat, 5), "lon": round(lng, 5), "zoom": 10})

    def map_link(self, url):
        """Follow a Google Maps short link and read coordinates out of the redirect chain."""
        key = "maplink:" + url
        if key not in self.cache:
            found = None
            for _ in range(5):
                r = self.s.get(url, allow_redirects=False, timeout=30)
                url = r.headers.get("Location")
                if not url:
                    break
                for pattern in COORDS:
                    m = pattern.search(unquote(url))
                    if m:
                        found = [float(m.group(1)), float(m.group(2))]
                        break
                if found:
                    break
            self.cache[key] = found
        return self.cache[key]


def district_of(address):
    d = address.get("state_district") or address.get("county") or address.get("city") or address.get("town")
    return re.sub(r"\s+(District|Taluk|Tahsil)$", "", re.sub(r"\s+", " ", d).strip()) if d else None


PLACE_TYPES = {"city", "town", "village", "hamlet", "suburb", "neighbourhood", "quarter", "municipality",
               "county", "state_district", "district", "city_district", "postcode"}
GENERIC = re.compile(
    r"\b(opp|opposite|near|nr|road|rd|street|st|main|highway|junction|jn|building|bldg|complex|bank|co-op|"
    r"municipal|shop|market|office|premises|regional|floor|emporium|megastore|showroom|agency|ccic|op|cdb|"
    r"handloom|house|mega|silk|celebrations|collectorate|bazaar|bazar)\b\.?",
    re.I,
)


def towns(rec):
    name = re.sub(r"\s*[-(].*$", "", rec["name"].split(",")[-1])
    parts = [name] + list(reversed(re.split(r",|\.\s", rec["address"])))
    if not rec["address"]:
        words = GENERIC.sub(" ", name).split()
        parts += [w for w in [words[-1], words[0]] if len(w) > 4] if words else []
    out = []
    for part in parts:
        part = re.sub(r"\S*\d\S*", " ", part)
        town = re.sub(r"\s+", " ", GENERIC.sub(" ", part)).strip(" -,.")
        if len(town) > 3 and town.lower() not in (t.lower() for t in out):
            out.append(town)
    return out


def km(a, b):
    r = math.pi / 180
    h = math.sin((b[0] - a[0]) * r / 2) ** 2 + math.cos(a[0] * r) * math.cos(b[0] * r) * math.sin((b[1] - a[1]) * r / 2) ** 2
    return 12742 * math.asin(math.sqrt(h))


def first_hit(geo, rec, params, places_only=False):
    hits = geo.search(**params)
    if not hits or hits[0].get("address", {}).get("state", "").lower() != rec["state"].lower():
        return None
    kind = hits[0].get("addresstype")
    if kind in ("state", "country", "region") or (places_only and kind not in PLACE_TYPES):
        return None
    return hits[0]


def in_state(geo, rec):
    state = geo.reverse(rec["lat"], rec["lng"]).get("address", {}).get("state")
    return not state or state.lower() == rec["state"].lower()


def locate(geo, rec):
    if rec["lat"] and rec["geo_source"] != "manual" and not in_state(geo, rec):
        rec["lat"] = rec["lng"] = rec["geo_source"] = None
    if rec["lat"]:
        rec["geo_source"] = rec["geo_source"] or "official"
    elif rec.get("map_url") and (coords := geo.map_link(rec["map_url"])) and in_state(geo, {**rec, "lat": coords[0], "lng": coords[1]}):
        rec["lat"], rec["lng"] = coords
        rec["geo_source"] = "maplink"
    else:
        town = next((h for t in towns(rec) if (h := first_hit(geo, rec, {"q": f"{t}, {rec['state']}"}, places_only=True))), None)
        anchor = (float(town["lat"]), float(town["lon"])) if town else None
        candidates = [("address", {"q": f"{rec['address']}, {rec['state']}"}, 15)] if rec["address"] else []
        if rec["pincode"]:
            candidates.append(("pincode", {"postalcode": rec["pincode"], "country": "India"}, 25))
        best = None
        for precision, params, radius in candidates:
            hit = first_hit(geo, rec, params)
            if hit and (not anchor or km(anchor, (float(hit["lat"]), float(hit["lon"]))) <= radius):
                best = (precision, hit)
                break
        if not best and town:
            best = ("town", town)
        if best:
            precision, hit = best
            if precision == "address" and hit.get("addresstype") in PLACE_TYPES:
                precision = "town"
            rec["lat"], rec["lng"] = float(hit["lat"]), float(hit["lon"])
            rec["geo_source"] = f"geocoded-{precision}"
            rec["district"] = rec["district"] or district_of(hit["address"])
    if rec["lat"] and not rec["district"]:
        rec["district"] = district_of(geo.reverse(rec["lat"], rec["lng"]).get("address", {}))
