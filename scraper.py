import requests
import math

MDOT_URL = "https://mdotridedata.state.mi.us/api/v1/organization/michigan_department_of_transportation/dataset/incidents/query?format=json"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "api_key": "PPVtEiLKbiAGswsa5JAvwdmY"
}
FORT_MONROE_COORDS = (41.9182, -83.3857)  # lat, lon
MAX_DISTANCE_MILES = 40

def haversine(lat1, lon1, lat2, lon2):
    R = 3958.8  # Radius of Earth in miles
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))

def fetch_events():
    print("[INFO] Fetching incident data...")
    response = requests.get(MDOT_URL, headers=HEADERS)
    response.raise_for_status()
    data = response.json()
    print(f"[INFO] Raw incident count: {len(data)}")
    return data

def filter_events(events):
    filtered = []
    for event in events:
        try:
            lat = float(event.get("Latitude", 0))
            lon = float(event.get("Longitude", 0))
            dist = haversine(lat, lon, *FORT_MONROE_COORDS)
            if dist <= MAX_DISTANCE_MILES:
                filtered.append({**event, "DistanceMiles": round(dist, 2)})
        except Exception as e:
            print(f"[WARN] Skipping event due to error: {e}")
    print(f"[INFO] Filtered incident count: {len(filtered)}")
    return filtered

def send_to_webhook(filtered_events):
    if not filtered_events:
        print("[INFO] No events to send.")
        return
    payload = {"alerts": filtered_events}
    response = requests.post(WEBHOOK_URL, json=payload)
    print(f"[INFO] Sent {len(filtered_events)} events. Webhook status: {response.status_code}")
    if response.status_code != 200:
        print(f"[ERROR] Webhook response: {response.text}")

def main():
    events = fetch_events()
    filtered = filter_events(events)
    send_to_webhook(filtered)

if __name__ == "__main__":
    import os
    WEBHOOK_URL = os.getenv("WEBHOOK_URL")
    if not WEBHOOK_URL:
        raise ValueError("Missing WEBHOOK_URL env variable.")
    main()