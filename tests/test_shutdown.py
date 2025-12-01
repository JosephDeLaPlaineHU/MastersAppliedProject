import requests
import time

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

def test_shutdown():
    print("--- Testing VM Shutdown ---")
    token = login()
    if not token:
        return

    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. List VMs
    res = requests.get(f"{API_URL}/vms/", headers=headers)
    if res.status_code != 200:
        print(f"Failed to list VMs: {res.text}")
        return
        
    vms = res.json()
    if not vms:
        print("No VMs found.")
        return
        
    target_vm = vms[0]
    print(f"Target VM: {target_vm['name']} (ID: {target_vm['id']}, VMID: {target_vm['vm_id']})")
    
    # 2. Stop VM 
    print(f"Sending STOP Signal to VM {target_vm['vm_id']}...")
    
    res = requests.post(f"{API_URL}/vms/{target_vm['vm_id']}/stop", headers=headers)
    
    if res.status_code == 200:
        print("SUCCESS: Stop signal sent.")
        print(res.json())
    else:
        print(f"FAILED: {res.status_code} - {res.text}")

if __name__ == "__main__":
    test_shutdown()
