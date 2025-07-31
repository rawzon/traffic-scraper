import requests
from datetime import datetime

MDOT_ENDPOINT = "https://mdotjboss.state.mi.us/MiDrive/rest/trafficEvents"
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def fetch_traffic_events():
    print(f"[{datetime.now()}] Requesting traffic events from MDOT...")
    try:
        response = requests.get(MDOT_ENDPOINT, headers=HEADERS, timeout=15)
        print(f"[DEBUG] Status Code: {response.status_code}")
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        print(f"[ERROR] HTTP error occurred: {http_err}")
        return []
    except requests.exceptions.RequestException as req_err:
        print(f"[ERROR] Request failed: {req_err}")
        return []

    try:
        data = response.json()
        print(f"[DEBUG] Received {len(data)} events")
    except ValueError as val_err:
        print(f"[ERROR] Failed to decode JSON: {val_err}")
        return []

    return data

def filter_relevant_events(events):
    filtered = []
    for event in events:
        if event.get("county") == "Monroe":
            filtered.append({
                "type": event.get("eventType", "Unknown"),
                "description": event.get("description", "No description provided."),
                "road": event.get("road", "Unknown"),
                "location": event.get("location", {}),
                "last_updated": event.get("lastUpdatedDate", "N/A")
            })
    print(f"[DEBUG] Filtered down to {len(filtered)} Monroe events")
    return filtered

def main():
    events = fetch_traffic_events()
    if not events:
        print("[INFO] No events returned or request failed.")
        return

    relevant = filter_relevant_events(events)
    if not relevant:
        print("[INFO] No relevant Monroe County events found.")
        return

    print(f"\nTraffic Alerts ({len(relevant)} total):")
    for i, event in enumerate(relevant, start=1):
        print(f"\n[{i}] {event['type']}")
        print(f"    Description: {event['description']}")
        print(f"    Road: {event['road']}")
        print(f"    Last updated: {event['last_updated']}")
        if event["location"]:
            lat = event["location"].get("latitude")
            lon = event["location"].get("longitude")
            print(f"    Location: {lat}, {lon}")

if __name__ == "__main__":
    main()
