import os
import requests

MDOT_API_URL = "https://mdotridedata.state.mi.us/api/v1/organization/michigan_department_of_transportation/dataset/incidents/query?_format=json"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "api_key": os.environ.get("MDOT_API_KEY")
}

def fetch_incidents():
    print("[INFO] Fetching incident data...")
    print(f"[DEBUG] API key loaded: {bool(os.environ.get('MDOT_API_KEY'))}")
    print(f"[DEBUG] Headers: {HEADERS}")

    response = requests.get(MDOT_API_URL, headers=HEADERS)
    print(f"[DEBUG] Status code: {response.status_code}")
    response.raise_for_status()
    return response.json()

def main():
    try:
        data = fetch_incidents()
        print(f"[INFO] Successfully retrieved {len(data)} incidents.")
    except requests.exceptions.HTTPError as e:
        print(f"Unexpected failure: {e}")

if __name__ == "__main__":
    main()
