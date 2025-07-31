import requests
import json
import math

# Constants
FORD_MONROE_LAT = 41.916
FORD_MONROE_LON = -83.385
SEARCH_RADIUS_MILES = 40

# Headers and endpoint
url = "https://mdotridedata.state.mi.us/api/v1/organization/michigan_department_of_transportation/dataset/incidents/query?_format=json"
headers = {
    "Accept": "application/json",
    "x-api-key": "YOUR_MDOT_API_KEY"  # Replace with your actual key in secrets
}

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 3958.8  # Radius in miles
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def fetch_data():
    print("[INFO] Fetching incident data...")
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    print(f"[INFO] Response status: {response.status_code}")
    return response.json()

def filter_incidents(data):
    print("[INFO] Filtering incidents within 40 miles of Ford Monroe...")
    filtered = []
    for item in data.get('features', []):
        props = item.get('properties', {})
        coords = item.get('geometry', {}).get('coordinates', [None, None])
        lon, lat = coords
        if lat is None or lon is None:
            continue
        distance = haversine_distance(FORD_MONROE_LAT, FORD_MONROE_LON, lat, lon)
        if distance <= SEARCH_RADIUS_MILES:
            props['distance_miles'] = round(distance, 2)
            filtered.append(props)
    print(f"[INFO] Found {len(filtered)} matching incidents.")
    return filtered

def send_alerts(filtered_data):
    webhook_url = "YOUR_WEBHOOK_URL"  # Replace with your actual webhook URL in secrets
    if not filtered_data:
        print("[INFO] No alerts to send.")
        return

    payload = {
        "text": f"{len(filtered_data)} MDOT incidents near Ford Monroe:\n\n"
    }
    for incident in filtered_data:
        payload["text"] += f"- {incident.get('description', 'No description')} ({incident['distance_miles']} mi)\n"

    response = requests.post(webhook_url, json=payload)
    print(f"[INFO] Alert sent. Status code: {response.status_code}")

def main():
    try:
        data = fetch_data()
        filtered = filter_incidents(data)
        send_alerts(filtered)
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    main()
