import requests
import os
from geopy.distance import geodesic

WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
API_URL = "https://mdotridedata.state.mi.us/api/v1/organization/michigan_department_of_transportation/dataset/incidents/query?_format=json"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "api_key": os.environ.get("MDOT_API_KEY")
}

CENTER_LAT = 41.9164
CENTER_LON = -83.3977
MAX_RADIUS_MILES = 400

def fetch_incidents():
    print("[INFO] Fetching incident data...")
    response = requests.get(API_URL, headers=HEADERS)
    print(f"[DEBUG] Status code: {response.status_code}")
    response.raise_for_status()
    return response.json()

def filter_incidents(incidents):
    filtered = []
    for item in incidents:
        geom = item.get("geometry", {})
        coords = geom.get("coordinates", [None, None])
        props = item.get("properties", {})

        if coords is None or len(coords) != 2:
            continue

        lon, lat = coords
        dist = geodesic((CENTER_LAT, CENTER_LON), (lat, lon)).miles
        print(f"[DEBUG] Incident: {props.get('description', 'No description')} at ({lat}, {lon}) is {dist:.1f} mi away")

        if dist <= MAX_RADIUS_MILES:
            props["distance_miles"] = round(dist, 2)
            props["latitude"] = lat
            props["longitude"] = lon
            filtered.append(props)
    return filtered

def send_to_webhook(payload):
    if not WEBHOOK_URL:
        print("[ERROR] WEBHOOK_URL not set.")
        return
    try:
        response = requests.post(WEBHOOK_URL, json=payload)
        print(f"[INFO] Webhook response: {response.status_code}")
        response.raise_for_status()
    except Exception as e:
        print(f"[ERROR] Failed to post to webhook: {e}")

def main():
    try:
        data = fetch_incidents()
        print(f"[INFO] Total incidents fetched: {len(data)}")

        filtered = filter_incidents(data)
        print(f"[INFO] Filtered incidents: {len(filtered)}")

        if filtered:
            send_to_webhook({"incidents": filtered})
        else:
            send_to_webhook({"message": "No active incidents within 400 miles of Monroe."})
            print("[INFO] Sent fallback message to webhook.")
    except Exception as e:
        print(f"[ERROR] Unexpected failure: {e}")
        raise

if __name__ == "__main__":
    main()
