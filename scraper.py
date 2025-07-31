import requests
import os
import math
import time

# Constants
RIDE_URL = "https://mdotridedata.state.mi.us/api/v1/organization/michigan_department_of_transportation/dataset/incidents/query?limit=200&_format=json"
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
MDOT_API_KEY = os.getenv("MDOT_API_KEY")

# Monroe coordinates and distance threshold
MONROE_LAT = 41.9403
MONROE_LON = -83.3960
DISTANCE_THRESHOLD_MILES = 40

# Haversine formula to calculate distance between two lat/lon points
def haversine(lat1, lon1, lat2, lon2):
    R = 3958.8  # Radius of Earth in miles
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c

# Fetch incidents from MDOT
def fetch_incidents(retries=3, delay=5):
    if not MDOT_API_KEY:
        raise Exception("❌ Missing MDOT_API_KEY environment variable.")

    print("📡 Fetching incidents from MDOT RIDE...")

    headers = {
        "api_key": MDOT_API_KEY
    }

    for attempt in range(retries):
        try:
            response = requests.get(RIDE_URL, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"⚠️ Attempt {attempt + 1} failed: {e}")
            time.sleep(delay)

    raise Exception("❌ MDOT API failed after all retries.")

# Filter incidents within distance threshold
def filter_nearby_incidents(incidents):
    print("🧭 Filtering incidents within 40 miles of Monroe County...")
    nearby = []

    for item in incidents:
        geometry = item.get("geometry", {})
        coords = geometry.get("coordinates", [])

        if len(coords) != 2:
            continue

        lon, lat = coords
        distance = haversine(lat, lon, MONROE_LAT, MONROE_LON)

        if distance <= DISTANCE_THRESHOLD_MILES:
            item["distance_miles"] = round(distance, 1)
            nearby.append(item)

    print(f"✅ Found {len(nearby)} nearby incidents.")
    return nearby

# Format message for Discord/webhook
def format_incident_message(incident):
    props = incident.get("attributes", {})
    desc = props.get("description", "No description")
    type_ = props.get("incident_type", "Unknown type")
    status = props.get("status", "Unknown status")
    dist = incident.get("distance_miles", "?")

    return f"🚨 **{type_}** - {desc}\n📍 Status: {status} | Distance: {dist} mi\n"

# Send messages to webhook
def post_to_webhook(messages):
    if not WEBHOOK_URL:
        print("❌ No WEBHOOK_URL provided.")
        return

    payload = {
        "content": "\n".join(messages)
    }

    response = requests.post(WEBHOOK_URL, json=payload)
    if response.status_code == 204 or response.ok:
        print("✅ Posted to webhook successfully.")
    else:
        print(f"❌ Failed to post to webhook: {response.status_code}")
        print(response.text)

# Main entry point
def main():
    try:
        data = fetch_incidents()
        nearby = filter_nearby_incidents(data)

        if not nearby:
            print("📭 No nearby incidents found.")
            return

        messages = [format_incident_message(inc) for inc in nearby]
        post_to_webhook(messages)

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()