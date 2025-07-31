import os
import requests

MDOT_URL = "https://mdotridedata.state.mi.us/api/v1/organization/michigan_department_of_transportation/dataset/incidents/query?_format=json"
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

def fetch_data():
    api_key = os.environ.get("MDOT_API_KEY")
    if not api_key:
        raise ValueError("[ERROR] Missing MDOT_API_KEY in environment")

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Authorization": f"Bearer {api_key}"
    }

    print("[INFO] Fetching incident data...")
    print(f"[DEBUG] Headers: {headers}")

    response = requests.get(MDOT_URL, headers=headers)
    print(f"[DEBUG] Status code: {response.status_code}")

    if response.status_code != 200:
        raise Exception(f"[ERROR] Unexpected failure: {response.status_code} - {response.text}")

    return response.json()

def send_to_webhook(payload):
    if not WEBHOOK_URL:
        raise ValueError("[ERROR] Missing WEBHOOK_URL in environment")

    print("[INFO] Sending data to webhook...")
    response = requests.post(WEBHOOK_URL, json=payload)
    print(f"[DEBUG] Webhook status: {response.status_code}")

    if response.status_code != 200:
        raise Exception(f"[ERROR] Webhook failed: {response.status_code} - {response.text}")

def main():
    data = fetch_data()
    # You can add filtering logic here if needed
    send_to_webhook(data)

if __name__ == "__main__":
    main()
