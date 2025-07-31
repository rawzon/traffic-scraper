import os
import requests
from datetime import datetime, timezone

# === Load env variables ===
MDOT_API_KEY = os.getenv("MDOT_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# === Debug print ===
print("🔍 Checking environment variables...")
print(f"✅ MDOT_API_KEY is set: {bool(MDOT_API_KEY)}")
print(f"✅ WEBHOOK_URL is set: {bool(WEBHOOK_URL)}")

# === Validation ===
if not MDOT_API_KEY:
    print("❌ ERROR: MDOT_API_KEY is not set.")
    exit(1)

if not WEBHOOK_URL:
    print("❌ ERROR: WEBHOOK_URL is not set.")
    exit(1)

# === Build and send the request ===
headers = {"Accept": "application/json", "x-api-key": MDOT_API_KEY}
url = "https://mdotjboss.state.mi.us/MiDrive/rest/trafficEvents"
response = requests.get(url, headers=headers)

# === Check for request success ===
if response.status_code != 200:
    print(f"❌ Failed to fetch data: {response.status_code}")
    exit(1)

events = response.json()

# === Filter and format relevant data ===
filtered = [
    e for e in events
    if "I-75" in e.get("roadName", "")
    and e.get("county") in ["Monroe", "Wayne"]
    and e.get("eventType") in ["CONSTRUCTION", "LANE_CLOSURE"]
]

if not filtered:
    print("ℹ️ No relevant I-75 events found.")
    exit(0)

now = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S")

message = f"🛣️ **I-75 Traffic Events - {now}**\n\n"
for e in filtered:
    message += f"- 📍 *{e.get('location')}*\n"
    message += f"  🏗️ {e.get('eventType')} – {e.get('description')}\n"
    message += f"  🕒 {e.get('startDate')} → {e.get('endDate')}\n\n"

# === Post to webhook ===
discord_payload = {"content": message.strip()}
r = requests.post(WEBHOOK_URL, json=discord_payload)

if r.status_code in [200, 204]:
    print("✅ Posted to Discord successfully.")
else:
    print(f"❌ Failed to post to Discord: {r.status_code} - {r.text}")