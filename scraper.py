import requests
import os
import json

# Get the Make.com webhook URL from GitHub secrets
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# ✅ Correct MDOT feed URL
MDOT_URL = "https://opendata.arcgis.com/datasets/f1e2c9438c274f8cb0b2e85b1ba6cfb9_0.geojson"

# Relevant routes and counties for Monroe-area travel
ROUTES = ["I-75", "US-24", "M-125", "Telegraph", "Dix", "Sylvania"]
COUNTIES = ["Monroe", "Wayne"]

def fetch_mdot_data():
    print("🌐 Fetching MDOT traffic data...")
    r = requests.get(MDOT_URL)
    r.raise_for_status()  # raises an error for bad status codes
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
        print("📡 Sending to Make