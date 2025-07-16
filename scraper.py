import requests
import os
import json

WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# ✅ Test payload — will always send this once when script runs
test_update = {
    "source": "Test",
    "route": "I-75",
    "county": "Monroe",
    "location": "Test area near Ford Packaging Center",
    "description": "🚨 This is a test traffic alert to verify Make.com integration.",
    "start": "2025-07-16",
    "end": "2025-07-17"
}

def send_to_make(updates):
    if not updates:
        print("✅ No updates to send.")
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
            print(f"❌ Request error: {e}")

if __name__ == "__main__":
    # 🧪 Send the test alert
    print("📡 Sending test update to Make.com")
    send_to_make([test_update])