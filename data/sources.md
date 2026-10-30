# Store data sources

Researched 2026-10-30. Several Indian government sites refused connections from outside India, so "couldn't check" rows should be retried from an Indian IP.

Easy = can be imported automatically; Imported = has an importer in `importers/`. Manual = has to be compiled by hand. None of the non-Co-optex sources give coordinates, so all need geocoding.

| Org | State | List URL | Format | Stores | Fields | Verdict |
|---|---|---|---|---|---|---|
| Co-optex | Tamil Nadu (+14 states) | https://admin.cooptex.com/api/Store/DistrictWiseShops | JSON API | 141 | Name, address, district, coordinates, phones, email | Imported (`cooptex`) |
| Hanveev | Kerala | https://hanveevs.com/about/shops | HTML cards | 39 | Name, address, phone, hours | Imported (`hanveev`) |
| Hantex | Kerala | hantex.kerala.gov.in/index.php/store/{kollam,ernakulam,palakkad,kozhikode}-region | HTML per region | ~60-100 | Name, address, phone, hours (from search snippets) | Probably easy, couldn't check |
| APCO | Andhra Pradesh | https://apcohandlooms.com/wp-json/wp/v2/store?per_page=100 | WP JSON, names only | 54 | Name + photo (address may be in photo) | Manual |
| KHDC / Priyadarshini | Karnataka | https://priyadarshinihandlooms.in/pages/priyadarshini-showrooms | HTML table | 8 | Address only | Manual |
| TSCO | Telangana | https://tgsco.co.in/pages/details-of-the-showrooms | HTML | 1 listed (~46 reported in 2018) | Name, phone | Not available |
| PONTEX | Puducherry | none | - | unknown | - | Not available |
| Boyanika | Odisha | https://boyanika.com/store-location/ | HTML lines | ~40 | Address with PIN | Imported (`boyanika`) |
| Tantuja | West Bengal | https://tantuja.in/stores | HTML | 27 listed (84 claimed) | Name, address, mostly HQ phone | Imported (`tantuja`), 29 of 84 claimed |
| Biswa Bangla | West Bengal | https://www.artisans.org.in/locations-contact-nos/ | HTML | 7 | Name, address, phone, maps link | Imported (`biswa_bangla`), mixed crafts |
| Jharcraft | Jharkhand | https://www.jharcraft.in/emporium/ | HTML cards | 14 | Name, address, phone, maps link | Imported (`jharcraft`) |
| AGMC (Pragjyotika) | Assam | agmcltd.assam.gov.in | - | 7 | Town names | Manual, couldn't check |
| ARTFED (Jagaran) | Assam | artfed.assam.gov.in | - | 32-55 | unknown | Couldn't check |
| Bihar, Manipur | | none found | - | - | - | Not available |
| Garvi Gurjari | Gujarat | https://garvigurjari.gujarat.gov.in/emporia-rajkot (dropdown lists all outlet pages) | HTML page per outlet | 16-22 | Name, address, manager, phones, email | Imported (`garvi_gurjari`), Kolkata-2 and Lucknow pages 404 |
| Mrignayani | Madhya Pradesh | https://mrignayani.org/branches/ | HTML table | 8 | Name, address, phone, email | Imported (`mrignayani`) |
| UPICA | Uttar Pradesh (+ other states) | https://upica.co.in/upica-center.html | HTML table, Hindi | ~24 | Locality only | Manual |
| Maharashtra Handloom Corp | Maharashtra | https://www.mahahandloom.com/elm-about-us/ | Prose | 3-4 | HQ address | Manual |
| Bhuttico (private coop) | Himachal Pradesh | https://bhuttico.com/pages/visit-a-bhuttico-store-near-you | HTML cards | 20 | Town only | Imported (`bhuttico`), town-level only |
| Rajasthali, MP Handloom, UP Handloom Corp, Himbunkar, J&K, Khadi India | | none found or site unreachable | - | - | - | Not available |

## Notes

- Don't use westbengalhandloom.com: it redirects to what looks like a phishing page. Tantuja's real site is tantuja.in.
- APCO's map locator at /storelocator/ only contains the plugin's demo stores (South Africa/US), not APCO outlets.
- "Golconda" is Telangana's handicrafts brand, not the handloom cooperative.
- Private shops also trade as "Rajasthali", so third-party addresses for it are unreliable.
- Many orgs have outlets outside their home state (Delhi's Baba Kharak Singh Marg, Kolkata's Dakshinapan), so `state` must be where the store is, and shared complexes may produce near-duplicates.
- Raw research files are in the session scratchpad and are not kept in the repo.
