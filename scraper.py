import requests
import csv
import json
import os
from io import StringIO
from datetime import datetime, timedelta

WEBHOOK_URL = os.getenv("WEBHOOK_URL")
MDOT_URL = "https://mdotridedata.state.mi.us/api/v1/organization/michigan_department_of_transportation/dataset/incidents/query?_format=json"

def fetch_incidents():
    print("[INFO] Fetching incident data...")
    response = requests.get(MDOT_URL)
    print(f"[DEBUG] Status code: {response.status_code}")
    try:
        data = response.json()
        print(f"[DEBUG] Parsed JSON: {json.dumps(data)[:300]}...")  # trim for readability
        return data.get("features", [])
    except Exception as e:
        print(" Response was not valid JSON.")
        print(f"[DEBUG] Raw response:\n{response.text}")
        return []

def filter_incidents(events):
    filtered = []
    for event in events:
        props = event.get("properties", {})
        if not props:
            continue
        # Apply your filtering logic here (location, time, etc.)
        filtered.append(props)
    print(f"[INFO] Filtered incident count: {len(filtered)}")
    return filtered

def send_to_webhook(filtered_events):
    if not filtered_events:
        print("[INFO] No events to send.")
        return
    payload = {"text": json.dumps(filtered_events, indent=2)}
    response = requests.post(WEBHOOK_URL, json=payload)
    print(f"[INFO] Webhook response: {response.status_code} {response.text}")

def main():
    incidents = fetch_incidents()
    filtered = filter_incidents(incidents)
    send_to_webhook(filtered)

if __name__ == "__main__":
    main()
