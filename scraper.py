import requests
import math

API_URL = (
    "https://mdotridedata.state.mi.us/api/v1/organization/"
    "michigan_department_of_transportation/dataset/incidents/query?_format=json"
)
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "api_key": "PPVtEiLKbiAGswsa5JAvwdmY"
}
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

MONROE_LAT = 41.916
MONROE_LON = -83.385
RADIUS_MILES = 40

def haversine(lat1, lon1, lat2, lon2):
    R = 3958.8
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = (
        math.sin(dLat / 2) ** 2 +
        math.cos(math.radians(lat1)) *
        math.cos(math.radians(lat2)) *
        math.sin(dLon / 2) ** 2
    )
    return R * 2 * math.asin(math.sqrt(a))

def fetch_incidents():
    print("[INFO] Fetching incident data...")
    try:
        response = requests.get(API_URL, headers=HEADERS)
        print(f"[DEBUG] Status code: {response.status_code}")
        if response.status_code != 200:
            print("[ERROR] Failed to fetch data:", response.text)
            return []
        return response.json()
    except requests.exceptions.JSONDecodeError:
        print("[ERROR] Invalid JSON response.")
        return []

def filter_by_distance(data):
    filtered = []
    for item in data:
        lat = item.get("latitude")
        lon = item.get("longitude")
        if lat is None or lon is None:
            continue
        distance = haversine(MONROE_LAT, MONROE_LON, float(lat), float(lon))
        print(f"[DEBUG] Incident at ({lat}, {lon}) is {distance:.2f} miles from Monroe.")
        if distance <= RADIUS_MILES:
            item["distance"] = round(distance, 2)
            filtered.append(item)
    return filtered

def send_to_webhook(data):
    if not data:
        print("[INFO] No incidents within radius to send.")
        return
    try:
        response = requests.post(WEBHOOK_URL, json=data)
        print(f"[INFO] Webhook status: {response.status_code}")
    except Exception as e:
        print("[ERROR] Webhook failed:", str(e))

def main():
    raw_data = fetch_incidents()
    nearby_data = filter_by_distance(raw_data)
    send_to_webhook(nearby_data)

if __name__ == "__main__":
    main()
