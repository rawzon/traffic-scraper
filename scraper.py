import os
import requests
from geopy.distance import geodesic

# MDOT endpoint and credentials
MDOT_URL = "https://mdotridedata.state.mi.us/api/v1/organization/michigan_department_of_transportation/dataset/incidents/query?_format=json"
MDOT_API_KEY = os.getenv("MDOT_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Monroe reference point and radius
MONROE_COORDS = (41.9164, -83.3977)
DISTANCE_LIMIT_MILES = 40

def fetch_incidents():
    if not MDOT_API_KEY:
        raise ValueError("MDOT_API_KEY is not set")
    headers = {
        "Accept": "application/json",
        "api_key": MDOT_API_KEY
    }
    print("[INFO] Fetching incident data from MDOT...")
    response = requests.get(MDOT_URL, headers=headers, timeout=10)
    print(f"[DEBUG] Status code: {response.status_code}")
    response.raise_for_status()
    return response.json()

def within_distance(incident):
    lat = incident.get("latitude")
    lon = incident.get("longitude")
    if lat is None or lon is None:
        return False
    try:
        incident_coords = (float(lat), float(lon))
        distance = geodesic(MONROE_COORDS, incident_coords).miles
        return distance <= DISTANCE_LIMIT_MILES
    except Exception as e:
        print(f"[WARN] Skipping invalid coordinates: {e}")
        return False

def format_incidents(incidents):
    if not incidents:
        return "No traffic incidents reported near Monroe, MI at this time."

    lines = []
    for i in incidents:
        road = i.get("roadway", "Unknown road")
        location = i.get("location-desc", "Unknown location")
        desc = i.get("description") or "No description available"
        lines.append(f"{road} - {location}: {desc}")
    return "\n".join(lines)

def main():
    try:
        data = fetch_incidents()
        print(f"[DEBUG] Raw type: {type(data)}")
        print(f"[DEBUG] Sample item: {data[0] if isinstance(data, list) and data else 'No data'}")

        filtered = [i for i in data if within_distance(i)]
        print(f"[INFO] Found {len(filtered)} incidents within {DISTANCE_LIMIT_MILES} miles.")

        message = format_incidents(filtered)
        payload = {"text": message}

        if WEBHOOK_URL:
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
