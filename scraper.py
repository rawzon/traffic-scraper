import requests
import math
import os

# Coordinates for Fort Monroe
TARGET_LAT = 37.0301
TARGET_LON = -76.3452
MAX_RADIUS_MILES = 40

MDOT_FEED_URL = "https://mdottraffic.michigan.gov/devices/services/WebServiceMDOT.asmx/GetIncidents"
WEBHOOK_URL = os.getenv("WEBHOOK_URL")


def haversine(lat1, lon1, lat2, lon2):
    R = 3958.8  # Radius of Earth in miles
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def fetch_incidents():
    try:
        response = requests.get(MDOT_FEED_URL)
        response.raise_for_status()
        return response.json().get("Incidents", [])
    except Exception as e:
        print(f"Fetch error: {e}")
        return []


def filter_incidents(incidents):
    filtered = []
    for incident in incidents:
        lat = incident.get("Latitude")
        lon = incident.get("Longitude")
        if lat is None or lon is None:
            continue
        distance = haversine(TARGET_LAT, TARGET_LON, float(lat), float(lon))
        if distance <= MAX_RADIUS_MILES:
            filtered.append(incident)
    return filtered


def send_to_webhook(data):
    if not WEBHOOK_URL:
        print("Error: WEBHOOK_URL not set")
        return
    try:
        payload = {"content": f"{len(data)} incidents within {MAX_RADIUS_MILES} miles of Fort Monroe"}
        response = requests.post(WEBHOOK_URL, json=payload)
        response.raise_for_status()
        print("Webhook sent successfully")
    except Exception as e:
        print(f"Webhook error: {e}")


if __name__ == "__main__":
    print("Starting scraper...")
    all_incidents = fetch_incidents()
    print(f"Fetched {len(all_incidents)} incidents")
    nearby = filter_incidents(all_incidents)
    print(f"{len(nearby)} incidents within radius")
    send_to_webhook(nearby)
