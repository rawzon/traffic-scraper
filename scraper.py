import requests
import math
import time

# Constants
API_URL = "https://mdotridedata.state.mi.us/api/v1/organization/michigan_department_of_transportation/dataset/incidents/query?limit=200&_format=json"
API_KEY = "PPVtEiLKbiAGswsa5JAvwdmY"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "api_key": API_KEY
}
CENTER_LAT = 41.91685
CENTER_LON = -83.38579
RADIUS_MI = 40

# Haversine formula
def is_within_radius(lat, lon, radius_mi):
    R = 3958.8  # Earth radius in miles
    dlat = math.radians(lat - CENTER_LAT)
    dlon = math.radians(lon - CENTER_LON)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(CENTER_LAT)) * math.cos(math.radians(lat)) * math.sin(dlon/2)**2
    distance = R * 2 * math.asin(math.sqrt(a))
    return distance <= radius_mi

def fetch_events():
    try:
        print("[INFO] Fetching incident data...")
        response = requests.get(API_URL, headers=HEADERS, timeout=30)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"[ERROR] Failed to fetch events: {e}")
        return []

    filtered = []
    for item in data.get("records", []):
        coords = item.get("location", {})
        lat, lon = coords.get("latitude"), coords.get("longitude")
        if lat and lon and is_within_radius(float(lat), float(lon), RADIUS_MI):
            filtered.append({
                "type": item.get("incidentType"),
                "desc": item.get("description"),
                "road": item.get("roadName"),
                "lat": lat,
                "lon": lon,
                "start": item.get("startDateTime")
            })

    print(f"[INFO] {len(filtered)} events within {RADIUS_MI} miles.")
    return filtered

def main():
    events = fetch_events()
    if not events:
        print("[INFO] No events retrieved.")
        return

    for e in events:
        print(f"- {e['type']}: {e['desc']} on {e['road']} ({e['lat']}, {e['lon']}) @ {e['start']}")

if __name__ == "__main__":
    main()