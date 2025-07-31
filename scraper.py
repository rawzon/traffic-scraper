import requests, os, json

def fetch_data():
    url = "https://mdot-api-url.example.com/incidents"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "api_key": os.environ.get("MDOT_API_KEY")
    }

    response = requests.get(url, headers=headers)

    print(f"[DEBUG] Headers: {headers}")
    print(f"[DEBUG] Status code: {response.status_code}")

    if response.status_code != 200:
        raise Exception(f"[ERROR] Unexpected failure: {response.status_code} - {response.text}")

    return response.json()

def main():
    print("[INFO] Fetching incident data...")
    data = fetch_data()

    # Optional: print a small preview to confirm format
    print("[INFO] Sample incident:", json.dumps(data[0], indent=2) if data else "[INFO] No incidents found")

if __name__ == "__main__":
    main()
