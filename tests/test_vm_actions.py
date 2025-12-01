import requests
import time


API_URL = "http://localhost:8080/api/v1"
EMAIL = "test@example.com"
PASSWORD = "password123"

def test_vm_actions():
    # 1. Login
    print(f"Logging in as {EMAIL}")
    response = requests.post(f"{API_URL}/auth/login", data={"username": EMAIL, "password": PASSWORD})
    if response.status_code != 200:
        print("Login failed. Please run test_vm_creation.py first to register.")
        return

    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("Listing VMs")
    list_response = requests.get(f"{API_URL}/vms/", headers=headers)
    try:
        vms = list_response.json()
    except:
        print(f"Failed to list VMs. Status: {list_response.status_code}")
        print(f"Response: {list_response.text}")
        return
    
    if not vms:
        print("No VMs found. Please run test_vm_creation.py first.")
        return


    
    target_vm = vms[0]
    vm_id = target_vm.get("vm_id") or target_vm.get("vmid")
    
    print(f"Testing actions on VM ID: {vm_id} (Name: {target_vm.get('name')})")

    # 3. Start VM
    print("Starting VM...")
    start_response = requests.post(f"{API_URL}/vms/{vm_id}/start", headers=headers)
    if start_response.status_code == 200:
        print("Start command sent successfully!")
    else:
        print(f"Start failed: {start_response.text}")

    print("Waiting 10 seconds")
    time.sleep(10)

    # 4. Stop VM
    print("Stopping VM")
    stop_response = requests.post(f"{API_URL}/vms/{vm_id}/stop", headers=headers)
    if stop_response.status_code == 200:
        print("Stop command sent successfully!")
    else:
        print(f"Stop failed: {stop_response.text}")

if __name__ == "__main__":
    test_vm_actions()
