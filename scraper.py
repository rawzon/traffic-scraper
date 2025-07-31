import requests
import json
import math
import os

# Your coordinates
MY_LAT = 41.8995
MY_LON = -84.0335
RADIUS_MILES = 40

# MDOT API URL
URL = "https://mdotjboss.state.mi.us/MiDrive/rest/incident"

# Get env variables
MDOT_API_KEY = os.getenv("MDOT_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if not MDOT_API_KEY:
    print("❌ ERROR: MDOT_API_KEY environment variable not set.")
    exit(1)
if not WEBHOOK_URL:
    print("❌ ERROR: WEBHOOK_URL environment variable not set.")
    exit(1)

print("[INFO] Fetching incident data from MDOT...")
headers = {"mdotApiKey": MDOT_API_KEY}
response = requests.get(URL, headers=headers)

print("[DEBUG] Status code:", response.status_code)
data = response.json()

print("[DEBUG] Raw type:", type(data))
if isinstance(data, list) and data:
    print("[DEBUG] Sample item:", data[0])

# Distance calculator (Haversine formula)
def haversine(lat1, lon1, lat2, lon2):
    R = 3958.8  # miles
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) *
         math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# Filter nearby incidents
def nearby(incident):
    try:
        dist = haversine(MY_LAT, MY_LON, incident["latitude"], incident["longitude"])
        return dist <= RADIUS_MILES
    except:
        return False

filtered = [i for i in data if nearby(i)]
print(f"[INFO] Found {len(filtered)} incidents within {RADIUS_MILES} miles.")

# Format each incident
def format_incidents(incidents):
    results = []
    direction_map = {1: "EB", 2: "WB", 3: "SB", 4: "NB"}

    for i in incidents:
        road = i.get("roadway", "Unknown road")
        location = i.get("location-desc", "Unknown location")
        incident = i.get("incident", {})
        description = i.get("description", "").strip()

        if not description:
            lanes = ", ".join(incident.get("lanes-blocked", [])) if incident.get("lanes-blocked") else "N/A"
            direction = direction_map.get(i.get("dir-of-travel", 0), "Unknown")
            start_time = i.get("startdatetime", "Unknown time")
            description = f"Lanes blocked: {lanes}, Direction: {direction}, Reported: {start_time}"

        results.append(f"{road} - {location}: {description}")

    return "\n\n".join(results)

message = format_incidents(filtered)

# Post to webhook
print("[INFO] Sending to webhook...")
payload = {
    "title": "I-75 Traffic Alert",
    "description": message if message else "No incidents found nearby."
}
webhook_response = requests.post(WEBHOOK_URL, json=payload)
print("[INFO] Webhook post status:", webhook_response.status_code)
