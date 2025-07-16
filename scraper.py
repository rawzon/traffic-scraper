import requests
import os

WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# MDOT GeoJSON feed
MDOT_URL = "https://opendata.arcgis.com/datasets/f1e2c9438c274f8cb0b2e85b1ba6cfb9_0.geojson"

# Routes and counties relevant to Ford Monroe Packaging Center
ROUTES = ["I-75", "US-24", "M-125", "Telegraph", "Dix", "Sylvania"]
COUNTIES = ["Monroe", "Wayne"]

def fetch_mdot_data():
    r = requests.get(MDOT_URL)
    r.raise_for_status()
    return r.json()

def filter_michigan_updates(data):
    filtered = []
    for feature in data.get("features", []):
        props = feature.get("properties", {})
        route = props.get("Route", "")
        county = props.get("County", "")
        if any(r in route for r in ROUTES) and county in COUNTIES:
            filtered.append({
                "source": "MDOT",
                "route": route,
                "county": county,
                "location": props.get("RestrictionLocation"),
                "description": props.get("Description"),
                "start": props.get("StartDate"),
                "end": props.get("EndDate")
            })
    return filtered

def send_to_make(updates):
    if not updates:
        print("✅ No new traffic impacts found.")
        return

    for update in updates:
        r = requests.post(WEBHOOK_URL, json=update)
        if r.ok:
            print(f"🚀 Sent: {update['route']} - {update['county']}")
        else:
            print(f"❌ Failed: {r.text}")

if __name__ == "__main__":
    try:
        data = fetch_mdot_data()
        updates = filter_michigan_updates(data)
        send_to_make(updates)
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching MDOT data: {e}")