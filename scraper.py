import os
import requests
from geopy.distance import geodesic

# Config
CENTER_COORDS = (41.9160, -83.3852)  # Monroe, MI
RADIUS_MILES = 40

MDOT_API_KEY = os.getenv("MDOT_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

MDOT_URL = "https://mdotridedata.state.mi.us/api/v1/organization/michigan_department_of_transportation/dataset/incidents/query?_format=json"

def fetch_incidents():
    if not MDOT_API_KEY:
        raise ValueError("Missing MDOT_API_KEY in environment")
    
    headers = {
        "Accept": "application/json",
        "api_key": MDOT_API_KEY
    }

    print("[INFO] Fetching incident data from MDOT...")
    response = requests.get(MDOT_URL, headers=headers, timeout=10)
    print(f"[DEBUG] Status code: {response.status_code}")

    if response.status_code != 200:
        raise Exception(f"MDOT API error: {response.status_code} — {response.text[:120]}")
    
    return response.json()

def is_near_monroe(lat, lon):
    try:
        dist = geodesic(CENTER_COORDS, (lat, lon)).miles
        return dist <= RADIUS_MILES, round(dist, 2)
    except:
        return False, None

def filter_and_format(raw):
    incidents = []
    for item in raw.get("features", []):
        props = item.get("properties", {})
        geom = item.get("geometry", {})
        coords = geom.get("coordinates", [None, None])
        if len(coords) != 2:
            continue
        lon, lat = coords
        is_near, dist = is_near_monroe(lat, lon)
        print(f"[DEBUG] Incident '{props.get('description', 'Unknown')}' → {dist} mi from Monroe")
        if is_near:
            incidents.append({
                "description": props.get("description", "No description"),
                "road": props.get("roadname", "Unknown road"),
                "distance": dist,
                "timestamp": props.get("actdatetime", "Unknown time"),
                "lat": lat,
                "lon": lon
            })
    return incidents

def build_payload(incidents):
    if not incidents:
        return {"text": "No active traffic incidents within 40 miles of Monroe."}
    
    lines = [f"{len(incidents)} traffic alert(s) near Monroe:\n"]
    for inc in incidents:
        lines.append(f"- {inc['description']} on {inc['road']} ({inc['distance']} mi), reported at {inc['timestamp']}")
    return {"text": "\n".join(lines)}

def post_to_webhook(payload):
    if not WEBHOOK_URL:
        raise ValueError("Missing WEBHOOK_URL in environment")

    print("[INFO] Sending payload to webhook...")
    response = requests.post(WEBHOOK_URL, json=payload, timeout=5)
    print(f"[INFO] Webhook response status: {response.status_code}")
    if response.status_code != 200:
        print(f"[ERROR] Webhook failed: {response.text[:120]}")

def main():
    try:
        raw = fetch_incidents()
        filtered = filter_and_format(raw)
        payload = build_payload(filtered)
        post_to_webhook(payload)
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    main()
