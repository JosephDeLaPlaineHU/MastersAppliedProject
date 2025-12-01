import requests
import time

API_URL = "http://127.0.0.1:8081/api/v1"
ADMIN_EMAIL = "sys_admin@example.com"
ADMIN_PASSWORD = "password123"
# Alpine Linux ISO (Small, fast download)
ISO_URL = "https://dl-cdn.alpinelinux.org/alpine/v3.19/releases/x86_64/alpine-virt-3.19.1-x86_64.iso"
ISO_NAME = "alpine-test-download.iso"

def login():
    res = requests.post(f"{API_URL}/auth/login", data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    if res.status_code == 200:
        return res.json()["access_token"]
    return None

def test_iso_download():
    print("--- Testing ISO Download Workflow ---")
    token = login()
    if not token:
        print("FATAL: Login failed")
        return
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Start Download
    print(f"\n1. Starting Download of {ISO_NAME}...")
    res = requests.post(f"{API_URL}/resources/isos/download", headers=headers, json={
        "url": ISO_URL,
        "file_name": ISO_NAME,
        "storage": "local" # Assuming 'local' exists and supports ISOs
    })
    
    if res.status_code != 200:
        print(f"Failed to start download: {res.status_code}")
        print(res.text)
        return
        
    data = res.json()
    upid = data.get("upid")
    print(f"Download Started. UPID: {upid}")
    
    # 2. Poll Status
    print("\n2. Polling Status (for 30s)...")
    start_time = time.time()
    while time.time() - start_time < 30:
        res = requests.get(f"{API_URL}/resources/tasks/{upid}", headers=headers)
        if res.status_code == 200:
            status_data = res.json()
            status = status_data.get("status", {}).get("status", "unknown")
            progress = status_data.get("progress", 0)
            print(f"Status: {status} | Progress: {progress}%")
            
            if status == "stopped":
                print("Download finished early!")
                break
        else:
            print(f"Failed to get status: {res.text}")
            
        time.sleep(2)
        
    # 3. Cancel Task
    print("\n3. Cancelling Task...")
    res = requests.delete(f"{API_URL}/resources/tasks/{upid}", headers=headers)
    if res.status_code == 200:
        print("Cancellation Requested.")
    else:
        print(f"Failed to cancel: {res.text}")
        
    # Verify Cancellation
    time.sleep(2)
    res = requests.get(f"{API_URL}/resources/tasks/{upid}", headers=headers)
    print("Final Status:", res.json().get("status", {}).get("status"))

if __name__ == "__main__":
    test_iso_download()
