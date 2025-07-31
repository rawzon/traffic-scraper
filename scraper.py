import requests
import datetime

MDOT_ENDPOINT = (
    "https://mdotridedata.state.mi.us/api/v1/organization/"
    "michigan_department_of_transportation/dataset/incidents/query"
    "?limit=200&_format=json"
)

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "api_key": "PPVtEiLKbiAGswsa5JAvwdmY"  # Replace with your actual key if needed
}

def fetch_incidents():
    print(f"[{datetime.datetime.now()}] Requesting traffic events from MDOT...")
    try:
        response = requests.get(MDOT_ENDPOINT, headers=HEADERS)
        print(f"[DEBUG] Status Code: {response.status_code}")
        response.raise_for_status()
        data = response.json()
        if data:
            print(f"[INFO] Retrieved {len(data)} incidents.")
        else:
            print("[INFO] No events returned.")
        return data
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"[ERROR] An unexpected error occurred: {err}")
    return []

if __name__ == "__main__":
    incidents = fetch_incidents()
    # Optional: Print out first event for inspection
    if incidents:
        print("[DEBUG] Sample Event:")
        print(incidents[0])