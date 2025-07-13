import requests
from bs4 import BeautifulSoup
import hashlib
import os
import subprocess
import tempfile

WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Uses GitHub secret if automated
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
        print(f"Error fetching TruckersReport: {e}")
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
        print(f"Error fetching MDOT Restrictions: {e}")
        return []

def send_update(message):
    try:
        data = {"Message": message}
        print("Sending payload:", data)
        response = requests.post(WEBHOOK_URL, json=data, timeout=10)
        if response.status_code == 200:
            print(f"✅ Sent: {message[:60]}...")
            return True
        else:
            print(f"❌ Webhook failed! Status: {response.status_code}, Reason: {response.reason}")
            return False
    except Exception as e:
        print(f"Exception during webhook call: {e}")
        return False

def git_commit_posted_file():
    try:
        subprocess.run(["git", "config", "--global", "user.email", "actions@github.com"], check=True)
        subprocess.run(["git", "config", "--global", "user.name", "GitHub Actions"], check=True)
        subprocess.run(["git", "add", POSTED_FILE], check=True)

        result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if not result.stdout.strip():
            print("📝 No changes to commit. Skipping push.")
            return

        subprocess.run(["git", "commit", "-m", "Update posted messages list"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ Changes committed and pushed.")
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {e}")
    except Exception as e:
        print(f"Unexpected Git error: {e}")

def main():
    posted_hashes = load_posted_hashes()
    updates = scrape_truckers_report() + scrape_mdot_restrictions()

    print(f"🔍 Found {len(updates)} total updates.")
    new_posts = []
    for update in updates:
        h = hash_text(update)
        if h not in posted_hashes:
            if send_update(update):
                posted_hashes.add(h)
                new_posts.append(update)

    if new_posts:
        save_posted_hashes(posted_hashes)
        git_commit
