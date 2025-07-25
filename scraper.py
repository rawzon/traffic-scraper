import requests
import os
import json
from math import radians, cos, sin, asin, sqrt

# Webhook to send filtered incident data
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# MDOT RIDE incidents endpoint
RIDE_URL = (
    "https://mdotridedata.state.mi.us/api/v1/organization/"
    "michigan_department_of_transportation/dataset/incidents/query?limit=200&_format=json"
)

# Monroe County center point
MONROE_LAT = 41.883866
MONROE_LON = -83.395468
RADIUS_MILES = 40

def haversine(lat1, lon1, lat2, lon2):
    # Calculate great-circle distance (in miles)
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))
    return 3956 * c  # Earth radius in miles

def fetch_incidents():
    print("Fetching incidents from MDOT RIDE...")
    r = requests.get(RIDE_URL)
    r.raise_for_status()
    return r.json()

def filter_by_distance(data):
    print("Filtering incidents within 40 miles of Monroe County...")
    nearby = []
    for incident in data.get("records", []):
        props = incident.get("record", {})
        lat = props.get("latitude")
        lon = props.get("longitude")

        if lat is None or lon is None:
            continue

        distance = haversine(MONROE_LAT, MONROE_LON, lat, lon)
        if distance <= RADIUS_MILES:
            nearby.append({
                "source": "MDOT RIDE",
                "location": props.get("location", "Unknown"),
                "description": props.get("event_type", "No description provided."),
                "start": props.get("start_date"),
                "end": props.get("end_date"),
                "lat": lat,
                "lon": lon,
                "distance_miles": round(distance, 2)
            })
    print(f"Found {len(nearby)} nearby incidents.")
    return nearby

def send_to_webhook(updates):
    if not updates:
        print("No nearby incidents found.")
        return

    for update in updates:
        try:
            r = requests.post(WEBHOOK_URL, json=update)
            if r.ok:
                print(f"Sent: {update['location']} ({update['distance_miles']} miles)")
            else:
                print(f"Failed to send: {r.status_code} - {r.text}")
        except Exception as e:
            print("Error sending to webhook:", e)

if __name__ == "__main__":
    try:
        data = fetch_incidents()
        filtered = filter_by_distance(data)
        send_to_webhook(filtered)
    except requests.RequestException as e:
        print("Error fetching data:", e)