import requests
from bs4 import BeautifulSoup

WEBHOOK_URL = "https://hook.us2.make.com/16at3ymjvi0s1fc8s7k8x8ie3n2c226p"  # <-- Replace with your Make webhook

def scrape_truckers_report():
    url = "https://www.truckersreport.com/roadreports/michigan"
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')

    # Select all posts on the page
    posts = soup.select('div.roadreport-list > div.roadreport-item')
    for post in posts:
        text = post.get_text(separator=' ', strip=True)
        if "I-75" in text or "I75" in text:
            return text

    return None

def send_update(message):
    data = {
        "Message": message
    }
    response = requests.post(WEBHOOK_URL, json=data)
    print(f"Sent update: {message[:60]}... Status: {response.status_code}")

if __name__ == "__main__":
    update = scrape_truckers_report()
    if update:
        send_update(update)
    else:
        print("No relevant updates found.")
