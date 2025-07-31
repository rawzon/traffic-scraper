import requests
import datetime
import os

MDOT_URL = "https://mdotridedata.state.mi.us/api/v1/organization/michigan_department_of_transportation/dataset/incidents/query?format=json"
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

def fetch_events():
    print("[INFO] Fetching incident data...")
    response = requests.get(MDOT_URL)
    response.raise_for_status()

    data = response.json()
    print(f"[DEBUG] Received {len(data)} records")

    events = []
    for item in data:
        # Optionally print keys to inspect structure
        print(f"[DEBUG] Incident keys: {list(item.keys())}")

        # You can filter for geographic location, severity, type, etc. here
        events.append({
            "location": item.get("location"),
            "description": item.get("description"),
            "start_time": item.get("startTime"),
            "end_time": item.get("endTime"),
            "severity": item.get("severity"),
        })

    return events

def format_alert(event):
    return (
        f"🚨 New Incident:\n"
        f"📍 Location: {event['location']}\n"
        f"📝 Description: {event['description']}\n"
        f"⏰ Start: {event['start_time']}\n"
        f"⏳ End: {event['end_time']}\n"
        f"⚠️ Severity: {event['severity']}"
    )

def send_alerts(events):
    for event in events:
        alert = format_alert(event)
        print(f"[INFO] Sending alert: {alert}")
        response = requests.post(WEBHOOK_URL, json={"text": alert})
        response.raise_for_status()

def main():
    events = fetch_events()
    if events:
        send_alerts(events)
    else:
        print("[INFO] No events to report.")

if __name__ == "__main__":
    main()