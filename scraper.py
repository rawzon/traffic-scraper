import requests
from bs4 import BeautifulSoup
import hashlib
import os
import subprocess

WEBHOOK_URL = "https://hook.us2.make.com/16at3ymjvi0s1fc8s7k8x8ie3n2c226p"  # Replace this
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

    posts = soup.select('div.roadreport-list > div.roadreport-item')
    updates = []

    for post in posts:
        text = post.get_text(separator=' ', strip=True)
        if "I-75" in text or "I75" in text:
            updates.append(text)

    return updates

def send_update(message):
    data = {"Message": message}
    response = requests.post(WEBHOOK_URL, json=data)
    print(f"Sent update: {message[:60]}... Status: {response.status_code}")
    return response.status_code == 200

def git_commit_posted_file():
    subprocess.run(["git", "config", "--global", "user.email", "actions@github.com"], check=True)
    subprocess.run(["git", "config", "--global", "user.name", "GitHub Actions"], check=True)
    subprocess.run(["git", "add", POSTED_FILE], check=True)
    subprocess.run(["git", "commit", "-m", "Update posted messages list"], check=True)
    subprocess.run(["git", "push"], check=True)

if __name__ == "__main__":
    posted_hashes = load_posted_hashes()
    updates = scrape_truckers_report()

    new_posts = []
    for u in updates:
        h = hash_text(u)
        if h not in posted_hashes:
            if send_update(u):
                posted_hashes.add(h)
                new_posts.append(u)

    if new_posts:
        save_posted_hashes(posted_hashes)
        git_commit_posted_file()
        print(f"Posted {len(new_posts)} new updates.")
    else:
        print("No new updates to post.")
