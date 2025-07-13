import requests
from bs4 import BeautifulSoup

# Replace this with your actual Make.com webhook URL
WEBHOOK_URL = "WEBHOOK_URL = "https://hook.us2.make.com/16at3ymjvi0s1fc8s7k8x8ie3n2c226p"
"

def scrape_mdot_i75_incidents():
    url = "https://mdotjboss.state.mi.us/MiDrive/incident"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    incidents = []

    # NOTE: This selector is an example. You'll want to inspect the actual MDOT page HTML to get correct selectors.
    incident_blocks = soup.select(".incident-list-item")  # <-- You may need to adjust this selector

    for block in incident_blocks:
        title_el = block.select_one(".incident-title")
        desc_el = block.select_one(".incident-description")

        title = title_el.get_text(strip=True) if title_el else ""
        description = desc_el.get_text(strip=True) if desc_el else ""

        # Filter for I-75 related incidents
        if "I-75" in title or "I-75" in description:
            incidents.append({
                "title": title,
                "description": description
            })

    return incidents

def send_to_make_webhook(incidents):
    for incident in incidents:
        response = requests.post(WEBHOOK_URL, json=incident)
        print(f"Posted: {incident['title']} - Status: {response.status_code}")

def main():
    incidents = scrape_mdot_i75_incidents()
    if incidents:
        send_to_make_webhook(incidents)
    else:
        print("No I-75 incidents found.")

if __name__ == "__main__":
    main()
