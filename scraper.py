import requests
import math
import os

FORD_MONROE_LAT = 41.916
FORD_MONROE_LON = -83.415
RADIUS_MILES = 200

def haversine(lat1, lon1, lat2, lon2):
    R = 3958.8  # Radius of Earth in miles
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) *
         math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    return R * 2 * math.asin(math.sqrt(a))

def fetch_incidents():
    headers = {
        "User-Agent": "Mozilla/5.0",
        "api_key": "PPVtEiLKbiAGswsa5JAvwdmY"
    }
    url = "https://mdotjboss.state.mi.us/MiDrive/rest/incidentevents"
    print("[INFO] Fetching incident data...")
    print(f"[DEBUG] Headers being sent: {headers}")
    response = requests.get(url, headers=headers)
    print(f"[DEBUG] Status code: {response.status_code}")
    return response.json()

def filter_incidents(incidents):
    filtered = []
    for inc in incidents:
        coords = inc.get("location", {})
        lat = coords.get("latitude")
        lon = coords.get("longitude")
        if lat is None or lon is None:
            continue
        distance = haversine(FORD_MONROE_LAT, FORD_MONROE_LON, lat, lon)
        print(f"[DEBUG] {inc.get('roadName', 'Unknown Road')} - {distance:.2f} mi away")
        if distance <= RADIUS_MILES:
            filtered.append(inc)
    return filtered

def send_to_webhook(filtered):
    if not filtered:
        print("[INFO] No events to send.")
        return
    payload = {"incidents": filtered}
    webhook_url = os.getenv("WEBHOOK_URL")
    try:
        requests.post(webhook_url, json=payload)
        print(f"[INFO] Sent {len(filtered)} event(s) to webhook.")
    except Exception as e:
        print(f"[ERROR] Failed to send to webhook: {e}")

def main():
    data = fetch_incidents()
    print(f"[INFO] Raw incident count: {len(data)}")
    filtered = filter_incidents(data)
    print(f"[INFO] Filtered incident count: {len(filtered)}")
    send_to_webhook(filtered)

if __name__ == "__main__":
    main()
