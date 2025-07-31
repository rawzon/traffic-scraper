import requests
import os

URL = "https://mdotridedata.state.mi.us/api/v1/organization/michigan_department_of_transportation/dataset/incidents/query?_format=json"
API_KEY = os.environ.get("MDOT_API_KEY")

headers_options = {
    "x-api-key": {"Accept": "application/json", "x-api-key": API_KEY},
    "api_key": {"Accept": "application/json", "api_key": API_KEY},
    "Authorization": {"Accept": "application/json", "Authorization": f"Bearer {API_KEY}"},
    "none": {"Accept": "application/json"}
}

def try_headers(label, headers):
    print(f"\n[TEST] Trying headers: {label}")
    try:
        response = requests.get(URL, headers=headers)
        print(f"  → Status Code: {response.status_code}")
        if response.status_code == 200:
            print(f"  Success with header style: {label}")
            print(f"  Response Preview:\n  {response.text[:250]}")
            return True
        else:
            print(f"  Failed with header style: {label}")
    except Exception as e:
        print(f"  Exception during request with {label}: {e}")
    return False

print("[INFO] Starting header strategy test...")

for label, headers in headers_options.items():
    if try_headers(label, headers):
        break
else:
    print("\n[ERROR] All header variations failed. Please verify your API key or contact MDOT support.")
