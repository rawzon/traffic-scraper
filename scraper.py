import requests
import json
import os

WEBHOOK_URL = os.getenv("WEBHOOK_URL")
MDOT_URL = "https://opendata.arcgis.com/datasets/f1e2c9438c274f8cb0b2e85b1ba6cfb9_0.geojson"

def fetch_data():
    r = requests.get(MDOT_URL)
    r.raise_for_status()
    return r.json()

def filter_i75(data):
    filtered = []
    for feature in data.get("features", []):
        props = feature.get("properties", {})
        route = props.get("Route", "")
        county = props.get("County", "")
        if "I-75" in route and county in ["Wayne", "Monroe", "Oakland", "Macomb"]:
            filtered.append({
                "route": route,
                "county": county,
                "description": props.get("RestrictionLocation", "No description"),
                "start": props.get("StartDate"),
                "end": props.get("EndDate")
            })
    return filtered

def send_to_make(updates):
    if not updates:
        print("✅ No new updates to post.")
        return

    for update in updates:
        message = {
            "route": update["route"],
            "county": update["county"],
            "description": update["description"],
            "start": update["start"],
            "end": update["end"]
        }
        r = requests.post(WEBHOOK_URL, json=message)
        if r.ok:
            print(f"🚀 Sent update for {update['route']} in {update['county']}")
        else:
            print(f"❌ Failed to send update: {r.text}")

if __name__ == "__main__":
    try:
        data = fetch_data()
        updates = filter_i75(data)
        send_to_make(updates)
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching MDOT data: {e}")