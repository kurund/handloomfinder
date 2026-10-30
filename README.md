# Handloom Finder

Find government and cooperative handloom stores across India. A static site (`site/`) over a dataset built from each organisation's own website.

## Layout

- `site/` - the website: `index.html` plus generated `stores.json`. Deployed to Netlify as-is (see `netlify.toml`).
- `importers/` - one module per organisation, plus `build.py`, which runs them all, geocodes and writes the data.
- `data/stores/<org>.json` - the dataset, one file per organisation, with `first_seen`/`last_seen` and `status` per store.
- `data/overrides.json` - manual corrections applied on every run: `exclude` ids, `patch` fields by id (setting `lat`/`lng` marks the location as manual), `district_aliases`.
- `data/manual/` - store lists saved by hand from sites that refuse automated requests (currently APCO). Re-save the file to refresh it.
- `data/geocache.json` - cached OpenStreetMap geocoder responses, so each address is only looked up once.
- `data/sources.md` - research on which organisations publish store lists and in what format.

## Refresh the data

```sh
pip install -r requirements.txt
python -m importers.build
```

The report printed at the end lists new stores, stores missing from their source and stores without a location. A store missing from its source for 14 days becomes `unverified` and the site asks people to call first. If an organisation's site is down, its stores from the last run are kept.

`.github/workflows/refresh-stores.yml` runs this daily and opens a pull request with the changes and the report.

## Run the site locally

```sh
cd site && python3 -m http.server 8766
```

"Near me" needs `localhost` or HTTPS, so open http://localhost:8766 rather than the file directly.

## Adding an organisation

Add `importers/<org>.py` with `ORG`, `NAME`, `HOME_STATE` and a `fetch(session)` that returns `record(...)` dicts, then add it to `SOURCES` in `importers/build.py`.
