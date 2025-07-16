import json

def send_to_make(updates):
    if not updates:
        print("✅ No new traffic impacts found.")
        return

    for update in updates:
        print("📡 Sending to Make.com:", json.dumps(update, indent=2))  # show payload
        
        r = requests.post(WEBHOOK_URL, json=update)
        
        print("🔁 Response status:", r.status_code)
        print("🔍 Response body:", r.text)
        
        if r.ok:
            print(f"🚀 Success: {update['route']} - {update['county']}")
        else:
            print(f"❌ Failed to post: {r.text}")