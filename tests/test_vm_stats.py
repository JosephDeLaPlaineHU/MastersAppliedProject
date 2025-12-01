import requests
import json

# Config
API_URL = "http://localhost:8080/api/v1"
EMAIL = "student3@example.com"
PASSWORD = "password123"

def test_vm_stats():
    # 1. Login
    print(f"Logging in as {EMAIL}")
    response = requests.post(f"{API_URL}/auth/login", data={"username": EMAIL, "password": PASSWORD})
    if response.status_code != 200:
        print("Login failed.")
        return

    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. List VMs to find one
    print("Listing VMs")
    list_response = requests.get(f"{API_URL}/vms/", headers=headers)
    try:
        vms = list_response.json()
    except:
        print("Failed to list VMs")
        return
    
    if not vms:
        print("No VMs found.")
        return

    target_vm = vms[0]
    vm_id = target_vm.get("vm_id") or target_vm.get("vmid")
    
    print(f"Fetching stats for VM ID: {vm_id}...")

    # 3. Get Stats
    stats_response = requests.get(f"{API_URL}/vms/{vm_id}/stats", headers=headers)
    
    if stats_response.status_code == 200:
        stats = stats_response.json()
        print("\nVM STATISTICS")
        print(json.dumps(stats, indent=2))
        print("\n---------------------")
    else:
        print(f"Failed to get stats: {stats_response.text}")

if __name__ == "__main__":
    test_vm_stats()
