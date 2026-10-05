"""Find B2B microgreens leads (restaurants, health food stores, juice bars)
with the Google Places API (New).

Google Maps Platform terms let you store a place ID indefinitely, but not
the name, address, rating or phone the API returns. So the lead file keeps
only place IDs plus your own sales notes, and `show` fetches current contact
details live whenever you sit down to do outreach.

Usage:
    export GOOGLE_PLACES_API_KEY=...
    python find_leads.py search          # add new leads to leads.csv
    python find_leads.py show            # print live details for every lead
    python find_leads.py show --status new
"""
import argparse
import csv
import os
import sys
import time

import requests

# Kingston, Jamaica. Change these for another city.
CENTER = {"latitude": 18.0179, "longitude": -76.8099}
RADIUS_M = 15000  # Places API (New) allows up to 50,000

QUERIES = [
    "fine dining restaurants",
    "sushi restaurants",
    "health food store",
    "juice bar",
]

LEADS_FILE = "leads.csv"
# place_id is the only Google-sourced field stored; the rest are yours.
FIELDS = ["place_id", "category", "status", "contacted_on", "notes"]

SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"
DETAILS_URL = "https://places.googleapis.com/v1/places/{}"
# Text Search returns at most 3 pages of 20.
MAX_PAGES = 3


def api_key():
    key = os.environ.get("GOOGLE_PLACES_API_KEY")
    if not key:
        sys.exit("Set the GOOGLE_PLACES_API_KEY environment variable first.")
    return key


def search(key, query):
    """Yield (place_id, display_name) for every result of one text query."""
    headers = {
        "X-Goog-Api-Key": key,
        "X-Goog-FieldMask": "places.id,places.displayName,nextPageToken",
    }
    body = {
        "textQuery": query,
        "pageSize": 20,
        "locationBias": {"circle": {"center": CENTER, "radius": RADIUS_M}},
    }
    for _ in range(MAX_PAGES):
        resp = requests.post(SEARCH_URL, json=body, headers=headers, timeout=30)
        if not resp.ok:
            sys.exit(f"Search for {query!r} failed ({resp.status_code}): {resp.text}")
        data = resp.json()
        for place in data.get("places", []):
            yield place["id"], place.get("displayName", {}).get("text", "")
        token = data.get("nextPageToken")
        if not token:
            break
        body["pageToken"] = token
        time.sleep(2)  # give the next page token time to become valid


def details(key, place_id):
    headers = {
        "X-Goog-Api-Key": key,
        "X-Goog-FieldMask": "displayName,formattedAddress,nationalPhoneNumber,"
        "websiteUri,rating,businessStatus",
    }
    resp = requests.get(DETAILS_URL.format(place_id), headers=headers, timeout=30)
    if not resp.ok:
        return None
    return resp.json()


def load_leads():
    if not os.path.exists(LEADS_FILE):
        return {}
    with open(LEADS_FILE, newline="", encoding="utf-8") as f:
        return {row["place_id"]: row for row in csv.DictReader(f)}


def save_leads(leads):
    with open(LEADS_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, FIELDS)
        writer.writeheader()
        writer.writerows(leads.values())


def cmd_search(args):
    key = api_key()
    leads = load_leads()
    added = 0
    for query in QUERIES:
        for place_id, name in search(key, query):
            lead = leads.get(place_id)
            if lead is None:
                leads[place_id] = {
                    "place_id": place_id,
                    "category": query,
                    "status": "new",
                    "contacted_on": "",
                    "notes": "",
                }
                added += 1
                print(f"+ {name}  [{query}]")
            elif query not in lead["category"].split("; "):
                lead["category"] += f"; {query}"
    save_leads(leads)
    print(f"\n{added} new leads, {len(leads)} total in {LEADS_FILE}")


def cmd_show(args):
    key = api_key()
    leads = load_leads()
    if not leads:
        sys.exit(f"No leads yet. Run: python {sys.argv[0]} search")
    for lead in leads.values():
        if args.status and lead["status"] != args.status:
            continue
        info = details(key, lead["place_id"])
        if info is None:
            print(f"? {lead['place_id']}: lookup failed (place may have closed)\n")
            continue
        if info.get("businessStatus") == "CLOSED_PERMANENTLY":
            continue
        print(info.get("displayName", {}).get("text", ""))
        print(f"  {info.get('formattedAddress', '')}")
        print(f"  phone:   {info.get('nationalPhoneNumber', '-')}")
        print(f"  website: {info.get('websiteUri', '-')}")
        print(f"  rating:  {info.get('rating', '-')}")
        print(f"  [{lead['category']}] status={lead['status']} {lead['notes']}\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("search", help="find new leads").set_defaults(func=cmd_search)
    show = sub.add_parser("show", help="print live details for saved leads")
    show.add_argument("--status", help="only leads with this status, e.g. new")
    show.set_defaults(func=cmd_show)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
