import requests
import datetime
from geopy.distance import geodesic

# Constants
MONROE_COORDS = (41.9164, -83.3977)
MAX_RADIUS_MILES = 400
MDOT_URL = "https://mdotjboss.state.mi.us/MiDrive/rest/incidentEvents"
WEBHOOK_URL = "YOUR_WEBHOOK_URL"

def fetch_incidents():
    response = requests.get(MDOT_URL)
    print(f"[DEBUG] Status code: {response.status_code}")
    if response.status_code != 200:
        raise Exception(f"Failed to fetch incidents: {response.status_code}")
    return response.json()

def is_within_radius(incident):
    lat = incident.get("latitude")
    lon = incident.get("longitude")
    if lat is None or lon is None:
        return False
    distance = geodesic(MONROE_COORDS, (lat, lon)).miles
    print(f"[DEBUG] Incident: {incident.get('eventName', 'Unnamed')} | Distance: {distance:.1f} mi")
    return distance <= MAX_RADIUS_MILES

def filter_incidents(incidents):
    filtered = [inc for inc in incidents if is_within_radius(inc)]
    print(f"[INFO] Total incidents fetched: {len(incidents)}")
    print(f"[INFO] Filtered incidents: {len(filtered)}")
    return filtered

def format_incident(incident):
    name = incident.get("eventName", "Unnamed Incident")
    road = incident.get("roadName", "Unknown Road")
    lat = incident.get("latitude")
    lon = incident.get("longitude")
    return f"🚧 {name} on {road} at ({lat}, {lon})"

def post_to_webhook(message):
    payload = {"text": message}
    response = requests.post(WEBHOOK_URL, json=payload)
    if response.status_code != 200:
        print(f"[ERROR] Failed to post message: {response.status_code}")
    else:
        print(f"[INFO] Message posted successfully.")

def main():
    print("Starting scraper...")
    try:
        incidents = fetch_incidents()
        relevant = filter_incidents(incidents)
        if not relevant:
            print("[INFO] No relevant incidents to send.")
            return
        messages = [format_incident(inc) for inc in relevant]
        for msg in messages:
            print(f"[INFO] Sending: {msg}")
            post_to_webhook(msg)
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    main()
