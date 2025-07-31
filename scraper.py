import requests
import os
from geopy.distance import distance

WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
API_URL = "https://mdotridedata.state.mi.us/api/v1/organization/michigan_department_of_transportation/dataset/incidents/query?_format=json"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "api_key": "PPVtEiLKbiAGswsa5JAvwdmY"
}

CENTER_LAT = 42.3240
CENTER_LON = -83.3780
MAX_MILES = 40

def fetch_incident_data():
    print("[INFO] Fetching incident data...")
    response = requests.get(API_URL, headers=HEADERS)
    print(f"[DEBUG] Status code: {response.status_code}")
    response.raise_for_status()
    return response.json()

def filter_incidents_by_distance(incidents, center_lat, center_lon, max_miles):
    filtered = []
    for item in incidents:
        coords = item.get("geometry", {}).get("coordinates")
        if not coords or len(coords) != 2:
            continue
        lon, lat = coords
        dist = distance((center_lat, center_lon), (lat, lon)).miles
        print(f"[DEBUG] Incident at ({lat}, {lon}) is {dist:.2f} mi away")
        if dist <= max_miles:
            props = item.get("properties", {})
            props["distance_miles"] = round(dist, 2)
            filtered.append(props)
    return filtered

def send_to_webhook(filtered_incidents):
    if not filtered_incidents:
        print("[INFO] No relevant incidents to send.")
        return
    payload = {"incidents": filtered_incidents}
    response = requests.post(WEBHOOK_URL, json=payload)
    response.raise_for_status()
    print(f"[INFO] Sent {len(filtered_incidents)} incidents to webhook.")

if __name__ == "__main__":
    print("Starting scraper...")
    try:
        incidents = fetch_incident_data()
        print(f"[INFO] Total incidents fetched: {len(incidents)}")
        filtered = filter_incidents_by_distance(incidents, CENTER_LAT, CENTER_LON, MAX_MILES)
        print(f"[INFO] Filtered incidents: {len(filtered)}")
        send_to_webhook(filtered)
    except Exception as e:
        print(f"[ERROR] {e}")
        raise
