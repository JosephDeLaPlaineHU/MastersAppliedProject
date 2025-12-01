import requests
import json

API_URL = "http://127.0.0.1:8081/api/v1"
ADMIN_EMAIL = "sys_admin@example.com"
ADMIN_PASSWORD = "password123"

def login():
    response = requests.post(f"{API_URL}/auth/login", data={
        "username": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        return None
    return response.json()["access_token"]

def test_console():
    print("Testing Ping")
    try:
        res = requests.get(f"http://127.0.0.1:8081/ping")
        print(f"Ping Status: {res.status_code}")
        print(f"Ping Response: {res.text}")
    except Exception as e:
        print(f"Ping Failed: {e}")

    token = login()
    if not token:
        return

    headers = {"Authorization": f"Bearer {token}"}

    # 1. List VMs to find one
    print("Listing VMs")
    res = requests.get(f"{API_URL}/vms/", headers=headers)
    
    if res.status_code != 200:
        print(f"Failed to list VMs: {res.status_code} - {res.text}")
        print(f"Headers: {res.headers}")
        return

    vms = res.json()
    
    if not vms:
        print("No VMs found to test console.")
        return

    target_vm = vms[0]
    print(f"Testing console for VM: {target_vm['name']} (ID: {target_vm['id']})")

    # 2. Get Console Ticket
    res = requests.post(f"{API_URL}/vms/{target_vm['id']}/console", headers=headers)
    
    if res.status_code == 200:
        data = res.json()
        print("\nSUCCESS! Console Access Granted.")
        print("-" * 50)
        print(f"Direct Proxmox URL: {data['direct_url']}")
        print("-" * 50)
        print("Open this URL in your browser to view the VM screen.")
    else:
        print(f"Failed to get console: {res.status_code} - {res.text}")

if __name__ == "__main__":
    test_console()
