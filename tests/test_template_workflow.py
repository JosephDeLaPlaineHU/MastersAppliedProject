import requests
import time

API_URL = "http://127.0.0.1:8081/api/v1"
ADMIN_EMAIL = "sys_admin@example.com"
ADMIN_PASSWORD = "password123"

def login():
    res = requests.post(f"{API_URL}/auth/login", data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    if res.status_code == 200:
        return res.json()["access_token"]
    return None

def test_template_workflow():
    print("Testing Template Creation Workflow")
    token = login()
    if not token:
        print("FATAL: Login failed")
        return
    headers = {"Authorization": f"Bearer {token}"}

    # 1. List ISOs
    print("\n1. Listing ISOs...")
    res = requests.get(f"{API_URL}/resources/isos", headers=headers)
    if res.status_code != 200:
        print(f"Failed to list ISOs: {res.text}")
        return
    isos = res.json()
    if not isos:
        print("No ISOs found. Cannot proceed.")
        return
    
    target_iso = isos[0]
    iso_volid = target_iso.get('volid')
    print(f"Selected ISO: {iso_volid}")

    # 2. Build Draft VM
    print(f"\n2. Building Draft VM from {iso_volid}...")
    draft_name = "test-template-draft"
    res = requests.post(f"{API_URL}/vms/templates/build", headers=headers, json={
        "name": draft_name,
        "iso_file": iso_volid,
        "cpu": 2,
        "memory": 2048,
        "disk_size": "10G"
    })
    
    if res.status_code != 200:
        print(f"Failed to build draft: {res.text}")
        return
        
    draft_data = res.json()
    print(f"Draft VM Created: VMID {draft_data.get('vmid')}")
    
    res = requests.get(f"{API_URL}/vms/", headers=headers)
    vms = res.json()
    target_vmid = int(draft_data.get('vmid'))
    draft_vm_db = next((v for v in vms if v['vm_id'] == target_vmid), None)
    
    if not draft_vm_db:
        print("Could not find draft VM in DB list.")
        return
        
    print(f"Draft VM DB ID: {draft_vm_db['id']}")
    
    print("Waiting 15s for Proxmox to finish creation task...")
    time.sleep(15)

    # 3. Finalize 
    print("\n3. Finalizing Template (Converting)...")
    res = requests.post(f"{API_URL}/vms/templates/{draft_vm_db['id']}/finalize", headers=headers)
    
    if res.status_code == 200:
        print("SUCCESS: Template Finalized.")
        print(res.json())
    else:
        print(f"Failed to finalize: {res.text}")

if __name__ == "__main__":
    test_template_workflow()
