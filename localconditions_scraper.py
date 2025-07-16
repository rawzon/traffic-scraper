import requests
from bs4 import BeautifulSoup

def fetch_monroe_traffic():
    url = "https://www.localconditions.com/weather-monroe-michigan/48161/traffic.php"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    alerts = []

    for item in soup.select(".traffic-alerts li"):
        alerts.append(item.get_text(strip=True))

    return alerts

def send_to_make(alerts):
    import json
    import os

    webhook_url = os.environ.get("WEBHOOK_URL")
    if not webhook_url:
        print("Webhook URL not set")
        return

    payload = {
        "source": "LocalConditions",
        "alerts": alerts
    }

    requests.post(webhook_url, json=payload)

if __name__ == "__main__":
    alerts = fetch_monroe_traffic()
    if alerts:
        print("Found Monroe traffic alerts:")
        for alert in alerts:
            print(f"- {alert}")
        send_to_make(alerts)
    else:
        print("No traffic alerts found.")
