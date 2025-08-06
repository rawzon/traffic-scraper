import os
import requests
import math
import json

# Your location (Monroe, MI area)
MY_LAT = 41.9164
MY_LON = -83.3977
RADIUS_MILES = 40

MDOT_URL = "https://mdotridedata.state.mi.us/api/v1/organization/michigan_department_of_transportation/dataset/incidents/query?_format=json"

MDOT_API_KEY = os.getenv("MDOT_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if not MDOT_API_KEY or not WEBHOOK_URL:
    print("❌ ERROR: Missing environment variables.")
    exit(1)

def haversine(lat1, lon1, lat2, lon2):
    R = 3958.8
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) *
         math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def fetch_incidents():
    headers = {
        "Accept": "application/json",
        "api_key": MDOT_API_KEY
    }
    response = requests.get(MDOT_URL, headers=headers, timeout=10)
    response.raise_for_status()
    return response.json()

def is_within_radius(incident):
    lat = incident.get("latitude")
    lon = incident.get("longitude")
    if lat is None or lon is None:
        return False
    try:
        return haversine(MY_LAT, MY_LON, float(lat), float(lon)) <= RADIUS_MILES
    except:
        return False

def format_incident(i):
    direction_map = {1: "EB", 2: "WB", 3: "SB", 4: "NB"}

    road = i.get("roadway", "Unknown road")
    location = i.get("location-desc", "Unknown location")
    incident = i.get("incident", {})
    description = i.get("description", "").strip()

    if not description or description.lower() == "no description available":
        lanes = ", ".join(incident.get("lanes-blocked", [])) if incident.get("lanes-blocked") else "N/A"
        direction = direction_map.get(i.get("dir-of-travel", 0), "Unknown")
        start_time = i.get("startdatetime", "Unknown time")
        description = f"Lanes blocked: {lanes}, Direction: {direction}, Reported: {start_time}"

    lat = i.get("latitude")
    lon = i.get("longitude")
    map_link = f"https://www.google.com/maps?q={lat},{lon}" if lat and lon else "Location link unavailable"

    return {
        "road": road,
        "location": location,
        "description": description,
        "map": map_link
    }

def main():
    try:
        data = fetch_incidents()
        filtered = [i for i in data if is_within_radius(i)]
        incidents = [format_incident(i) for i in filtered]

        if incidents:
            # Use the first incident (or loop if you want to send multiple later)
            first = incidents[0]
            message = (
                f"🚨 Traffic Alert 🚨\n"
                f"Road: {first['road']}\n"
                f"Location: {first['location']}\n"
                f"{first['description']}\n"
                f"Map: {first['map']}"
            )
        else:
            message = "✅ No traffic incidents reported near Monroe, MI at this time."

        payload = { "message": message }

        print("[DEBUG] Payload being sent to Make:")
        print(json.dumps(payload, indent=2))

        resp = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        print(f"[INFO] Webhook response: {resp.status_code}")
        if resp.status_code != 200:
            print(f"[ERROR] Webhook error: {resp.text}")

    except Exception as e:
        print(f"[ERROR] Exception occurred: {e}")

if __name__ == "__main__":
    main()