import requests
import json

WEBHOOK_URL = "https://hook.us2.make.com/16at3ymjvi0s1fc8s7k8x8ie3n2c226p"

def send_test_update():
    data = {
        "title": "Test Crash on I-75",
        "description": "This is a test traffic alert sent from GitHub Actions."
    }

    print("Sending this data to Make.com:")
    print(json.dumps(data, indent=2))

    response = requests.post(WEBHOOK_URL, json=data)
    print(f"Posted: {data['title']} - Status: {response.status_code}")

if __name__ == "__main__":
    send_test_update()
