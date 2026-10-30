from .common import get, record

ORG = "cooptex"
NAME = "Co-optex"
HOME_STATE = "Tamil Nadu"
SOURCE_URL = "https://admin.cooptex.com/api/Store/DistrictWiseShops"


def fetch(s):
    data = get(s, SOURCE_URL, headers={"Origin": "https://cooptex.com", "Referer": "https://cooptex.com/"}).json()
    out = []
    for state in data["Value"]:
        for district in state["Districts"]:
            for shop in district["Shops"]:
                closed = not (shop.get("ClosedDate") or "0001").startswith("0001")
                out.append(record(
                    ORG, shop["ShopCode"], shop["ShopName"], shop["Address"], state["State"],
                    SOURCE_URL, "api",
                    district=district["District"],
                    lat=shop.get("Lat") or None,
                    lng=shop.get("Long") or None,
                    phones=[p for p in [shop.get("MobileNo"), shop.get("LandLine")] if p],
                    status="closed" if closed else "open",
                ))
    return out
