import requests
import os

# Fetch the webhook URL from environment variables
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

def fetch_incident_data():
    url = "https://mdotridedata.state.mi.us/api/v1/organization/michigan_department_of_transportation/dataset/incidents/query?_format=json"
    headers = {
        "Accept": "application/json"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    # Expecting a top-level list, not a dict
    return response.json()

def filter_incidents_by_distance(incidents, center_lat, center_lon, max_miles):
    from geopy.distance import distance

    def is_within_range(feature):
        coords = feature.get("geometry", {}).get("coordinates")
        if not coords:
            return False
        lon, lat = coords
        dist = distance((center_lat, center_lon), (lat, lon)).miles
        return dist <= max_miles

    return [incident for incident in incidents if is_within_range(incident)]

def send_to_webhook(filtered_incidents):
    if not filtered_incidents:
        print("No relevant incidents to send.")
        return

    payload = {"incidents": filtered_incidents}
    response = requests.post(WEBHOOK_URL, json=payload)
    response.raise_for_status()
    print(f"Sent {len(filtered_incidents)} incidents to webhook.")

if __name__ == "__main__":
    print("Starting scraper...")
    try:
        incidents = fetch_incident_data()
        print(f"Total incidents fetched: {len(incidents)}")

        # Debugging the first item’s structure
        if incidents:
            print("First item keys:", list(incidents[0].keys()))

        # Spatial filter: within 40 miles of Fort Monroe
        CENTER_LAT = 42.3240
        CENTER_LON = -83.3780
        MAX_MILES = 40

        filtered = filter_incidents_by_distance(incidents, CENTER_LAT, CENTER_LON, MAX_MILES)
        print(f"Filtered incidents: {len(filtered)}")

        send_to_webhook(filtered)

    except Exception as e:
        print(f"Error occurred: {e}")
        raise
