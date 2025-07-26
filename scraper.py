import requests
import os
import math

# — Constants & Environment Setup —
RIDE_URL = (
    "https://mdotridedata.state.mi.us/api/v1/organization/"
    "michigan_department_of_transportation/dataset/incidents/query"
    "?limit=200&_format=json"
)
MIDRIVE_URL = "https://mdotjboss.state.mi.us/MiDrive/rest/trafficEvents"

WEBHOOK_URL = os.getenv("WEBHOOK_URL")
MDOT_API_KEY = os.getenv("MDOT_API_KEY")

MONROE_LAT = 41.883866
MONROE_LON = -83.395468
MAX_DISTANCE = 40  # miles

# — Utility: Haversine distance in miles —
def haversine(lat1, lon1, lat2, lon2):
    R = 3958.8
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dl / 2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

# — Fetch from RIDE API —
def fetch_ride():
    headers = {"api_key": MDOT_API_KEY} if MDOT_API_KEY else {}
    print("Fetching from RIDE...")
    r = requests.get(RIDE_URL, headers=headers)
    r.raise_for_status()
    return r.json()

def filter_ride(records):
    nearby = []
    for rec in records:
        geom = rec.get("geometry", {})
        coords = geom.get("coordinates", [])
        if len(coords) != 2:
            continue
        lon, lat = coords
        dist = haversine(lat, lon, MONROE_LAT, MONROE_LON)
        if dist <= MAX_DISTANCE:
            props = rec.get("attributes", {})
            props["distance"] = round(dist, 1)
            nearby.append({
                "src": "RIDE",
                "desc": props.get("description") or props.get("event_type", ""),
                "status": props.get("status", ""),
                "loc": props.get("location", ""),
                "distance": props["distance"]
            })
    print(f"RIDE: {len(nearby)} incidents within range")
    return nearby

# — Fetch from MiDrive endpoint —
def fetch_midrive():
    print("Fetching from MiDrive...")
    r = requests.get(MIDRIVE_URL)
    r.raise_for_status()
    return r.json()

def filter_midrive(events):
    nearby = []
    for ev in events:
        county = ev.get("county", "")
        lat = ev.get("latitude")
        lon = ev.get("longitude")
        if county != "Monroe" or lat is None or lon is None:
            continue
        dist = haversine(lat, lon, MONROE_LAT, MONROE_LON)
        if dist <= MAX_DISTANCE:
            nearby.append({
                "src": "MiDrive",
                "desc": ev.get("description", ""),
                "status": ev.get("eventCategory") or ev.get("eventType", ""),
                "loc": ev.get("road") or ev.get("location", ""),
                "distance": round(dist, 1)
            })
    print(f"MiDrive: {len(nearby)} incidents within range")
    return nearby

# — Post formatted messages to webhook —
def post_updates(updates):
    if not updates or not WEBHOOK_URL:
        print("Nothing to post or no webhook.")
        return

    seen = set()
    lines = []
    for ev in updates:
        key = (ev["src"], ev["desc"], ev["loc"], ev["status"])
        if key in seen:
            continue
        seen.add(key)
        lines.append(f"**{ev['src']}**: {ev['desc']} @ {ev['loc']} | {ev['status']} | {ev['distance']} mi")

    content = "\n".join(lines)
    payload = {"content": content}
    resp = requests.post(WEBHOOK_URL, json=payload)
    if resp.ok:
        print(f"Posted {len(lines)} items successfully.")
    else:
        print(f"Webhook failed: {resp.status_code}. {resp.text}")

# — Main workflow —
def main():
    try:
        ride_data = fetch_ride().get("records", [])
        ride_incidents = filter_ride(ride_data)

        midrive_data = fetch_midrive()
        midrive_inc = filter_midrive(midrive_data)

        all_updates = ride_incidents + midrive_inc
        post_updates(all_updates)

    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    import math
    main()
