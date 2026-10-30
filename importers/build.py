import datetime
import json
import re
import traceback

from . import (
    apco, bhuttico, biswa_bangla, boyanika, cooptex, garvi_gurjari, hanveev, jharcraft, mahahandloom, mrignayani,
    priyadarshini, tantuja, upica,
)
from .common import DATA, SITE, STORES_DIR, session, unique_ids
from .geocode import Geocoder, locate

SOURCES = [
    cooptex, hanveev, jharcraft, garvi_gurjari, boyanika, tantuja, biswa_bangla, mrignayani, bhuttico,
    priyadarshini, upica, mahahandloom, apco,
]
UNVERIFIED_AFTER_DAYS = 14
KEEP_FROM_PREVIOUS = ("lat", "lng", "geo_source", "district")


def load(path, default):
    return json.loads(path.read_text()) if path.exists() else default


def merge(previous, fresh, today):
    before = {r["id"]: r for r in previous}
    for r in fresh:
        prev = before.get(r["id"], {})
        r["first_seen"] = prev.get("first_seen", today)
        r["last_seen"] = today
        if not r["lat"] and prev.get("lat") and prev.get("address") == r["address"]:
            r.update({k: prev[k] for k in KEEP_FROM_PREVIOUS if prev.get(k)})
    fresh_ids = {r["id"] for r in fresh}
    gone = [r for r in previous if r["id"] not in fresh_ids]
    added = [r for r in fresh if r["id"] not in before]
    return fresh + gone, added, gone


def apply_overrides(records, overrides):
    excluded = set(overrides.get("exclude", []))
    aliases = overrides.get("district_aliases", {})
    out = []
    for r in records:
        if r["id"] in excluded:
            continue
        patch = overrides.get("patch", {}).get(r["id"], {})
        r.update(patch)
        if "lat" in patch:
            r["geo_source"] = "manual"
        district = re.sub(r"\s+", " ", r["district"]).strip() if r["district"] else r["district"]
        r["district"] = aliases.get(district, district)
        out.append(r)
    return out


def set_status(r, today):
    if r["status"] == "closed":
        return
    age = (datetime.date.fromisoformat(today) - datetime.date.fromisoformat(r["last_seen"])).days
    r["status"] = "unverified" if age > UNVERIFIED_AFTER_DAYS else "open"


def site_record(r, org_names):
    out = {
        "id": r["id"], "o": org_names[r["org"]], "n": r["name"], "a": r["address"],
        "s": r["state"], "d": r["district"] or "Other", "lat": r["lat"], "lng": r["lng"], "p": r["phones"],
    }
    if r["hours"]:
        out["h"] = r["hours"]
    if r["geo_source"] in ("geocoded-town", "geocoded-pincode"):
        out["x"] = 1
    if r["status"] == "unverified":
        out["u"] = 1
    return out


def main():
    today = datetime.date.today().isoformat()
    s = session()
    geo = Geocoder(s)
    overrides = load(DATA / "overrides.json", {})
    STORES_DIR.mkdir(parents=True, exist_ok=True)
    report = [f"# Store data refresh {today}", ""]
    everything = []

    for src in SOURCES:
        path = STORES_DIR / f"{src.ORG}.json"
        previous = load(path, [])
        try:
            fresh = unique_ids(src.fetch(s))
        except Exception:
            report.append(f"- **{src.NAME}: import failed**, kept {len(previous)} stores from last run")
            report.append(f"  ```\n  {traceback.format_exc(limit=2).strip()}\n  ```")
            everything += previous
            continue
        records, added, gone = merge(previous, fresh, today)
        added = [r for r in added if r["id"] not in overrides.get("exclude", [])]
        records = apply_overrides(records, overrides)
        for r in records:
            locate(geo, r)
            set_status(r, today)
        geo.save()
        records.sort(key=lambda r: (r["state"], r["district"] or "", r["name"]))
        path.write_text(json.dumps(records, indent=1, ensure_ascii=False) + "\n")
        everything += records

        unlocated = [r for r in records if not r["lat"]]
        report.append(f"- **{src.NAME}**: {len(fresh)} in source, {len(added)} new, {len(gone)} missing, {len(unlocated)} without location")
        report += [f"  - new: {r['name']} ({r['state']})" for r in added if previous]
        report += [f"  - missing from source: {r['name']} ({r['id']}, last seen {r['last_seen']})" for r in gone]
        report += [f"  - no location: {r['name']} - {r['address']}" for r in unlocated]

    org_names = {src.ORG: src.NAME for src in SOURCES}
    listed = [r for r in everything if r["status"] != "closed"]
    listed.sort(key=lambda r: (r["state"], r["district"] or "", r["name"]))
    SITE.mkdir(exist_ok=True)
    (SITE / "stores.json").write_text(json.dumps(
        {"updated": today, "stores": [site_record(r, org_names) for r in listed]},
        separators=(",", ":"), ensure_ascii=False,
    ))
    report += ["", f"{len(listed)} stores published to site/stores.json"]
    print("\n".join(report))


if __name__ == "__main__":
    main()
