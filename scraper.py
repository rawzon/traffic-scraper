import requests
import math
import os

# --- CONFIG ---
MDOT_URL = "https://mdotridedata.state.mi.us/api/v1/organization/michigan_department_of_transportation/dataset/incidents/query?_format=json"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "api_key": "PPVtEiLKbiAGswsa5JAvwdmY"
}
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
RADIUS_MILES = 200
CENTER_LAT = 41.916664
CENTER_LON = -83.395699

# --- HELPERS ---
def miles_between(lat1, lon1, lat2, lon2):
    R = 3959  # Earth radius in miles
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (math.sin(d_lat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(d_lon / 2) ** 2)
    return R * 2 * math.asin(math.sqrt(a))

# --- MAIN ---
print("Starting scraper...")

try:
    res = requests.get(MDOT_URL, headers=HEADERS, timeout=15)
    res.raise_for_status()
    data = res.json()
except Exception as e:
    print(f"Fetch error: {e}")
    data = {}

incidents = data.get("features", [])
print(f"Fetched {len(incidents)} incidents")

filtered = []
for item in incidents:
    props = item.get("properties", {})
    geom = item.get("geometry", {})
    coords = geom.get("coordinates", [None, None])

    if not coords or len(coords) != 2:
        continue

    lon, lat = coords
    distance = miles_between(lat, lon, CENTER_LAT, CENTER_LON)
    print(f"[{props.get('name', 'Unnamed')}] → {distance:.1f} miles")

    if distance <= RADIUS_MILES:
        props["distance_miles"] = distance
        filtered.append(props)

print(f"{len(filtered)} incidents within radius")

payload = {
    "total": len(filtered),
    "incidents": filtered
}

try:
    r = requests.post(WEBHOOK_URL, json=payload, timeout=10)
    r.raise_for_status()
    print("Webhook sent successfully")
except Exception as e:
    print(f"Webhook error: {e}")
