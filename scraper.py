import requests
from bs4 import BeautifulSoup
import hashlib
import os
import subprocess
import tempfile

WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Injected via GitHub Secrets
POSTED_FILE = "posted.txt"

def load_posted_hashes():
    if not os.path.exists(POSTED_FILE):
        return set()
    with open(POSTED_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f)

def save_posted_hashes(hashes):
    with tempfile.NamedTemporaryFile("w", delete=False, dir=".", encoding="utf-8") as tf:
        for h in hashes:
            tf.write(h + "\n")
    os.replace(tf.name, POSTED_FILE)

def hash_text(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def scrape_truckers_report():
    url = "https://www.truckersreport.com/roadreports/michigan"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        return [
            post.get_text(separator=' ', strip=True)
            for post in soup.select('div.RoadReportCard')
            if "I-75" in post.get_text() or "I75" in post.get_text()
        ]
    except Exception as e:
        print(f"❌ Error fetching TruckersReport: {e}")
        return []

def scrape_mdot_restrictions():
    url = "https://mdotjboss.state.mi.us/traffic/Restrictions/"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        updates = []
        for row in soup.select('table tbody tr'):
            cols = row.find_all('td')
            if len(cols) >= 3:
                location = cols[0].get_text(strip=True)
                description = cols[1].get_text(strip=True)
                dates = cols[2].get_text(strip=True)
                combined = f"{location} - {description} ({dates})"
                if "I-75" in combined or "I75" in combined:
                    updates.append(combined)
        return updates
    except Exception as e:
        print(f"❌ Error fetching MDOT Restrictions: {e}")
        return []

def send_update(message):
    try:
        data = {"Message": message}
        print("📤
