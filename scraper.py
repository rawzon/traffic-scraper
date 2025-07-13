import requests
from bs4 import BeautifulSoup
import hashlib
import os
import subprocess

WEBHOOK_URL = "https://hook.us2.make.com/16at3ymjvi0s1fc8s7k8x8ie3n2c226p"  # Replace with your Make.com webhook URL
POSTED_FILE = "posted.txt"

def load_posted_hashes():
    if not os.path.exists(POSTED_FILE):
        return set()
    with open(POSTED_FILE, "r") as f:
        return set(line.strip() for line in f.readlines())

def save_posted_hashes(hashes):
    with open(POSTED_FILE, "w") as f:
        for h in hashes:
            f.write(h + "\n")

def hash_text(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def scrape_truckers_report():
    url = "https://www.truckersreport.com/roadreports/michigan"
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')

    updates = []

    posts = soup.select('div.RoadReportCard')  # updated selector
    for post in posts:
        text = post.get_text(separator=' ', strip=True)
        if "I-75" in text or "I75" in text:
            updates.append(text)

    return updates

def scrape_mdot_restrictions():
    url = "https://mdotjboss.state.mi.us/traffic/Restrictions/"
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')

    updates = []

    rows = soup.select('table tbody tr')
    for row in rows:
        cols = row.find_all('td')
        if len(cols) >= 3:

