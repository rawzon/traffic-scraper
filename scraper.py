import os
import requests
from datetime import datetime
from geopy.distance import geodesic

# Environment variables
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
MDOT_API_KEY = os.getenv("MDOT_API_KEY")
CENTER_COORDS = (41.9160, -83.3852)  # Monroe, MI
RADIUS_MILES = 40

def is_within_radius(lat, lon, center, radius):
    try:
        return geodesic(center, (lat, lon)).miles <= radius
    except:
        return False

def fetch_alerts():
    headers = {
        "Accept": "application/json",
        "api_key": MDOT_API_KEY
    }
    url = "https://mdot-api.com/TrafficAlert"  # Replace with actual endpoint
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"[ERROR] API status: {response.status_code}")
            return []
    except Exception as e:
        print(f"[ERROR] Fetch failed: {e}")
        return []

def filter_alerts(data):
    filtered = []
    for alert in data:
        lat, lon = alert.get("latitude"), alert.get("longitude")
        if lat and lon and is_within_radius(float(lat), float(lon), CENTER_COORDS, RADIUS_MILES):
            filtered.append(alert)
    return filtered

def format_message(alerts):
    if not alerts:
        return {"text": "✅ No traffic alerts near Monroe within 40 miles."}
    lines = [f"🚨 {len(alerts)} alert(s) near Monroe:\n"]
    for alert in alerts:
        desc = alert.get("description", "No description")
        time = alert.get("actdatetime", "Unknown time")
        loc = f"{alert.get('latitude')}, {alert.get('longitude')}"
        lines.append(f"- {desc} at {loc} (since {time})")
    return {"text": "\n".join(lines)}

def send_to_webhook(payload):
    try:
        response = requests.post(WEBHOOK_URL, json=payload, timeout=5)
        print(f"[INFO] Webhook response: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Webhook failed: {e}")

def main():
    print("[INFO] Starting scraper...")
    alerts = fetch_alerts()
    filtered = filter_alerts(alerts)
    payload = format_message(filtered)
    send_to_webhook(payload)

if __name__ == "__main__":
    main()
