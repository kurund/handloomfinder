import re
import sys
import unicodedata

from bs4 import BeautifulSoup

from .common import get, guess_state, record, slug

ORG = "upica"
NAME = "UPICA"
HOME_STATE = "Uttar Pradesh"
SOURCE_URL = "https://upica.co.in/upica-center.html"

# The source lists centres in Hindi only; new entries missing here are imported untranslated and reported.
ENGLISH = {
    "सर्वोदय नगर, कानपुर": "Sarvodaya Nagar, Kanpur",
    "हैंडलूम हवेली, चुन्नी गंज कानपुर": "Handloom Haveli, Chunniganj, Kanpur",
    "संजय प्लेस आगरा": "Sanjay Place, Agra",
    "इम्पोरियम संजय प्लेस आगरा": "Emporium, Sanjay Place, Agra",
    "86, हजरतगंज लखनऊ": "86, Hazratganj, Lucknow",
    "लेखराज मार्केट इन्दिरा नगर, लखनऊ": "Lekhraj Market, Indira Nagar, Lucknow",
    "डायमंड डेरी काम्प्लेक्स, उदय गंज, लखनऊ": "Diamond Dairy Complex, Udaiganj, Lucknow",
    "सिनेमा रोड गोलघर, गोरखपुर": "Cinema Road, Golghar, Gorakhpur",
    "तिलक रोड नगर पालिका, देवरिया": "Tilak Road, Nagar Palika, Deoria",
    "अल्का होटल कोर्ट रोड, आज़मगढ़": "Alka Hotel, Court Road, Azamgarh",
    "नदेसर वाराणसी": "Nadesar, Varanasi",
    "गोदौलिया वाराणसी": "Godaulia, Varanasi",
    "घंटाघर इलाहाबाद": "Ghantaghar, Prayagraj",
    "सिविल लाइन्स, इलाहाबाद": "Civil Lines, Prayagraj",
    "एन0 टी0 पी0 सी0 शॉपिंग काम्प्लेक्स शक्ति नगर, सोनभद्र": "NTPC Shopping Complex, Shakti Nagar, Sonbhadra",
    "कोर्ट परिसर गाजियाबाद": "Court Premises, Ghaziabad",
    "गाँधी वाटिका, रुढ़की": "Gandhi Vatika, Roorkee, Uttarakhand",
    "हेंडलूम हवेली मानिक तल्ला, कोलकाता": "Handloom Haveli, Maniktala, Kolkata",
    "इंद्रा बाजार, जयपुर": "Indra Bazar, Jaipur",
    "हेंडलूम हवेली, जयपुर": "Handloom Haveli, Jaipur",
    "नाना चौक, मुंबई": "Nana Chowk, Mumbai",
    "यू पी भवन नवी मुंबई": "UP Bhawan, Navi Mumbai",
    "अहमदाबाद": "Ahmedabad",
}


def normalise(text):
    return unicodedata.normalize("NFC", re.sub(r"\s+", " ", text)).strip()


ENGLISH = {normalise(k): v for k, v in ENGLISH.items()}


def fetch(s):
    soup = BeautifulSoup(get(s, SOURCE_URL).text, "html.parser")
    lines = soup.get_text("\n", strip=True).split("\n")
    start, end = lines.index("बिक्री केंद्र का नाम") + 1, lines.index("क्षेत्रफल वर्ग फुट")
    out = []
    for hindi in map(normalise, lines[start:end]):
        if "वेयर हाउस" in hindi:
            continue
        address = ENGLISH.get(hindi)
        if not address:
            print(f"warning: {NAME} centre has no English name yet: {hindi}", file=sys.stderr)
            address = hindi
        name = address.removesuffix(", Uttarakhand")
        out.append(record(ORG, slug(name) or slug(hindi), name, address, guess_state(address, HOME_STATE), SOURCE_URL, "html"))
    return out
