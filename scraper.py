import os
import requests
from geopy.distance import geodesic

MDOT_URL = "MDOT_URL = "https://mdotridedata.state.mi.us/api/v1/organization/michigan_department_of_transportation/dataset/incidents/query?_format=json"
MDOT_API_KEY = os.getenv("MDOT_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

MONROE_COORDS = (41.9164, -83.3977)
DISTANCE_LIMIT_MILES = 40

def fetch_incidents():
    headers = {"apikey": MDOT_API_KEY}
    print("[INFO] Fetching incident data from MDOT...")
    response = requests.get(MDOT_URL, headers=headers, timeout=5)
    print(f"[DEBUG] Status code: {response.status_code}")
    response.raise_for_status()
    return response.json()

def within_distance(incident):
    lat = incident.get("latitude")
    lon = incident.get("longitude")
    if lat is None or lon is None:
        return False
    incident_coords = (float(lat), float(lon))
    distance = geodesic(MONROE_COORDS, incident_coords).miles
    return distance <= DISTANCE_LIMIT_MILES

def main():
    try:
        incidents = fetch_incidents()
        nearby = [i for i in incidents if within_distance(i)]
        print(f"[INFO] Found {len(nearby)} incidents within {DISTANCE_LIMIT_MILES} miles.")

        if WEBHOOK_URL:
            payload = {"incidents": nearby}
            try:
                response = requests.post(WEBHOOK_URL, json=payload, timeout=5)
                print(f"[INFO] Webhook post status: {response.status_code}")
            except requests.RequestException as e:
                print(f"[ERROR] Webhook post failed: {e}")
        else:
            print("[ERROR] WEBHOOK_URL is not set")

    except Exception as e:
        print(f"[ERROR] Unexpected failure: {e}")

if __name__ == "__main__":
    main()
