import requests
from geopy.distance import geodesic

MDOT_API_KEY = "PPVtEiLKbiAGswsa5JAvwdmY"
MDOT_API_URL = "https://mdotridedata.state.mi.us/api/v1/organization/michigan_department_of_transportation/dataset/incidents/query?_format=json"
WEBHOOK_URL = "YOUR_WEBHOOK_URL"  # Replace with actual webhook if needed

CENTER_COORDS = (41.9160, -83.3852)  # Monroe, MI
RADIUS_MILES = 40

def fetch_incidents():
    headers = {
        "Accept": "application/json",
        "api_key": MDOT_API_KEY
    }

    print("[INFO] Fetching incident data from MDOT...")
    response = requests.get(MDOT_API_URL, headers=headers, timeout=10)
    print(f"[DEBUG] Status code: {response.status_code}")
    response.raise_for_status()
    return response.json()

def is_within_radius(lat, lon):
    try:
        dist = geodesic(CENTER_COORDS, (lat, lon)).miles
        return dist <= RADIUS_MILES, round(dist, 2)
    except Exception as e:
        print(f"[WARN] Distance calculation error: {e}")
        return False, None

def filter_incidents(data):
    filtered = []
    for item in data:
        try:
            lat = item.get("latitude")
            lon = item.get("longitude")
            if lat is None or lon is None:
                continue
            within, dist = is_within_radius(float(lat), float(lon))
            if within:
                incident = {
                    "description": item.get("description", "No description"),
                    "road": item.get("roadname", "Unknown road"),
                    "timestamp": item.get("actdatetime", "Unknown time"),
                    "distance": dist
                }
                filtered.append(incident)
        except Exception as e:
            print(f"[WARN] Skipping invalid item: {e}")
    print(f"[INFO] Found {len(filtered)} incidents within 40 miles.")
    return filtered

def format_payload(incidents):
    if not incidents:
        return {"text": "No active traffic incidents within 40 miles of Monroe."}
    
    lines = [f"{len(incidents)} incident(s) near Monroe:"]
    for inc in incidents:
        lines.append(f"- {inc['description']} on {inc['road']} ({inc['distance']} mi) reported at {inc['timestamp']}")
    return {"text": "\n".join(lines)}

def send_to_webhook(payload):
    if not WEBHOOK_URL or WEBHOOK_URL == "YOUR_WEBHOOK_URL":
        print("[INFO] Skipping webhook post (no URL set)")
        return
    try:
        response = requests.post(WEBHOOK_URL, json=payload, timeout=5)
        print(f"[INFO] Webhook post status: {response.status_code}")
        if response.status_code != 200:
            print(f"[ERROR] Webhook rejected: {response.text[:120]}")
    except Exception as e:
        print(f"[ERROR] Webhook failed: {e}")

def main():
    try:
        data = fetch_incidents()
        filtered = filter_incidents(data)
        payload = format_payload(filtered)
        send_to_webhook(payload)
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    main()
