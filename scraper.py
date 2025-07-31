import os
import requests
import math

# Your location (Monroe, MI area)
MY_LAT = 41.9164
MY_LON = -83.3977
RADIUS_MILES = 40

# MDOT API URL
MDOT_URL = "https://mdotridedata.state.mi.us/api/v1/organization/michigan_department_of_transportation/dataset/incidents/query?_format=json"

# Environment variables
MDOT_API_KEY = os.getenv("MDOT_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if not MDOT_API_KEY:
    print("❌ ERROR: MDOT_API_KEY environment variable not set.")
    exit(1)
if not WEBHOOK_URL:
    print("❌ ERROR: WEBHOOK_URL environment variable not set.")
    exit(1)

# Haversine formula for distance in miles
def haversine(lat1, lon1, lat2, lon2):
    R = 3958.8  # Earth radius in miles
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
    print("[INFO] Fetching incident data from MDOT...")
    response = requests.get(MDOT_URL, headers=headers, timeout=10)
    print(f"[DEBUG] Status code: {response.status_code}")
    response.raise_for_status()
    return response.json()

def is_within_radius(incident):
    lat = incident.get("latitude")
    lon = incident.get("longitude")
    if lat is None or lon is None:
        return False
    try:
        return haversine(MY_LAT, MY_LON, float(lat), float(lon)) <= RADIUS_MILES
    except Exception as e:
        print(f"[WARN] Invalid coordinates: {e}")
        return False

def format_incidents(incidents):
    direction_map = {1: "EB", 2: "WB", 3: "SB", 4: "NB"}
    formatted_list = []

    for i in incidents:
        road = i.get("roadway", "Unknown road")
        location = i.get("location-desc", "Unknown location")
        incident = i.get("incident", {})
        description = i.get("description", "").strip()

        # Treat empty or literal "No description available" as missing description
        if not description or description.lower() == "no description available":
            lanes = ", ".join(incident.get("lanes-blocked", [])) if incident.get("lanes-blocked") else "N/A"
            direction = direction_map.get(i.get("dir-of-travel", 0), "Unknown")
            start_time = i.get("startdatetime", "Unknown time")
            description = f"Lanes blocked: {lanes}, Direction: {direction}, Reported: {start_time}"

        lat = i.get("latitude")
        lon = i.get("longitude")
        if lat and lon:
            map_link = f"https://www.google.com/maps?q={lat},{lon}"
        else:
            map_link = "Location link unavailable"

        formatted_list.append(f"{road} - {location}: {description}\nMap: {map_link}")

    return "\n\n".join(formatted_list) if formatted_list else "No incidents near Monroe, MI at this time."

def main():
    try:
        data = fetch_incidents()
        print(f"[DEBUG] Fetched {len(data)} total incidents.")

        filtered = [inc for inc in data if is_within_radius(inc)]
        print(f"[INFO] Found {len(filtered)} incidents within {RADIUS_MILES} miles.")

        message = format_incidents(filtered)

        # Debug print of final message before sending
        print("=== Final message ===")
        print(message)

        # Optional test payload - uncomment to send a simple test message instead
        # payload = { "text": "Test post from scraper - description logic check" }

        # Normal payload sending formatted incidents
        payload = { "text": message }

        print("[INFO] Sending data to webhook...")
        resp = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        print(f"[INFO] Webhook response status: {resp.status_code}")
        if resp.status_code != 200:
            print(f"[ERROR] Webhook error: {resp.text}")

    except Exception as e:
        print(f"[ERROR] Exception occurred: {e}")

if __name__ == "__main__":
    main()
