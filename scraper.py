# Force refresh — debug mode July 16
import requests
import os
import json

WEBHOOK_URL = os.getenv("WEBHOOK_URL")
MDOT_URL = "https://opendata.arcgis.com/datasets/f1e2c9438c274f8cb0b2e85b1ba6cfb9_0.geojson"

ROUTES = ["I-75", "US-24", "M-125", "Telegraph", "Dix", "Sylvania"]
COUNTIES = ["Monroe", "Wayne"]

def fetch_mdot_data():
    print("🌐 Fetching MDOT traffic data...")
    print("🔎 MDOT_URL being used:", MDOT_URL)  # 👈 debug line
    r = requests.get(MDOT_URL)
    r.raise_for_status()
    return r.json()

def filter_michigan_updates(data):
    print("🔍 Filtering updates for Monroe/Wayne County routes...")
    filtered = []
    for feature in data.get("features", []):
        props = feature.get("properties", {})
        route = props.get("Route", "") or ""
        county = props.get("County", "") or ""

        if any(r in route for r in ROUTES) and county in COUNTIES:
            filtered.append({
                "source": "MDOT",
                "route": route,
                "county": county,
                "location": props.get("RestrictionLocation", "Unknown"),
                "description": props.get("Description", "No description provided."),
                "start": props.get("StartDate"),
                "end": props.get("EndDate")
            })
    print(f"📦 Found {len(filtered)} relevant updates.")
    return filtered

def send_to_make(updates):
    if not updates:
        print("✅ No new traffic impacts found.")
        return

    for update in updates:
        print("📡 Sending to Make.com:", json.dumps(update, indent=2))
        try:
            r = requests.post(WEBHOOK_URL, json=update)
            print("🔁 Response status:", r.status_code)
            print("🔍 Response body:", r.text)
            if r.ok:
                print(f"🚀 Sent: {update['route']} - {update['county']}")
            else:
                print(f"❌ Failed to send: {r.text}")
        except Exception as e:
            print(f"❌ Request error: {e}")  # 👈 This was missing indentation

if __name__ == "__main__":
    try:
        data = fetch_mdot_data()
        updates = filter_michigan_updates(data)
        send_to_make(updates)
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching MDOT data: {e}")