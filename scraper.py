import requests
from math import radians, cos, sin, asin, sqrt

# Coordinates for Ford Monroe Packaging Center
TARGET_LAT = 41.9046
TARGET_LON = -83.4264

# Haversine formula to compute distance in miles
def haversine(lat1, lon1, lat2, lon2):
    R = 3959  # Earth radius in miles
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return R * c

# Filter incidents within 40 miles
def filter_relevant_events(events):
    filtered = []
    farthest_distance = 0
    for event in events:
        loc = event.get("location", {})
        lat = loc.get("latitude")
        lon = loc.get("longitude")
        if lat is not None and lon is not None:
            distance = haversine(TARGET_LAT, TARGET_LON, lat, lon)
            if distance <= 40:
                filtered.append({
                    "type": event.get("eventType", "Unknown"),
                    "description": event.get("description", "No description provided."),
                    "road": event.get("road", "Unknown"),
                    "location": loc,
                    "last_updated": event.get("lastUpdatedDate", "N/A"),
                    "distance_miles": round(distance, 2)
                })
                farthest_distance = max(farthest_distance, distance)
    print(f"[DEBUG] Filtered {len(filtered)} events within 40 miles")
    print(f"[DEBUG] Farthest event in filtered set: {round(farthest_distance, 2)} miles away")
    return filtered

# Grab MDOT traffic events
def fetch_mdot_events():
    url = "https://mdotjboss.state.mi.us/MiDrive/rest/events"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        all_events = response.json()
        print(f"[DEBUG] Fetched {len(all_events)} total events")
        return all_events
    except Exception as e:
        print(f"[ERROR] Failed to fetch events: {e}")
        return []

# Main logic
if __name__ == "__main__":
    events = fetch_mdot_events()
    if events:
        nearby = filter_relevant_events(events)
        for event in nearby:
            print(f"\n📍 {event['type']} on {event['road']}")
            print(f"→ {event['description']}")
            print(f"⏱️ Last updated: {event['last_updated']}")
            print(f"📌 Location: {event['location']}")
            print(f"📏 Distance: {event['distance_miles']} miles")
    else:
        print("[INFO] No events retrieved.")