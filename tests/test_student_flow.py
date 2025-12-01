import requests
import time

API_URL = "http://127.0.0.1:8081/api/v1"

# Potential student credentials based on previous logs and common defaults
STUDENTS = [
    ("student@example.com", "password123"),
    ("student2@example.com", "password123"),
    ("intro-to-cs-student2@example.com", "password123"),
    ("test_student@example.com", "password123")
]

def login(email, password):
    try:
        res = requests.post(f"{API_URL}/auth/login", data={"username": email, "password": password})
        if res.status_code == 200:
            return res.json()["access_token"]
    except Exception as e:
        print(f"Connection error: {e}")
        pass
    return None

def test_student_flow():
    print("Starting Student Flow Test")
    
    token = None
    email = None
    
    for e, p in STUDENTS:
        print(f"Attempting login as {e}")
        token = login(e, p)
        if token:
            email = e
            print(f"Login Success as {e}")
            break
            
    if not token:
        print("Could not login as any student. Trying to register one")
        reg_email = "auto_student@example.com"
        reg_pass = "password123"
        res = requests.post(f"{API_URL}/auth/register", json={
            "email": reg_email,
            "username": "auto_student",
            "password": reg_pass,
            "role": "student"
        })
        if res.status_code == 200:
            print("Registered auto_student. Logging in")
            token = login(reg_email, reg_pass)
        else:
            print(f"Registration failed: {res.text}")
            token = login(reg_email, reg_pass)

    if not token:
        print("FATAL: Could not authenticate as a student.")
        return

    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. List VMs
    print("\n1. Listing My VMs")
    res = requests.get(f"{API_URL}/vms/", headers=headers)
    if res.status_code != 200:
        print(f"Failed to list VMs: {res.text}")
        return
        
    vms = res.json()
    if not vms:
        print("No VMs found for this student.")
        print("NOTE: Students cannot create VMs. An admin/professor must enroll them in a course.")
        return
        
    target_vm = vms[0]
    print(f"Found VM: {target_vm['name']} (ID: {target_vm['id']})")
    
    # 2. Start VM
    print(f"\n2. Starting VM {target_vm['name']}")
    
    res = requests.post(f"{API_URL}/vms/{target_vm['vm_id']}/start", headers=headers)
    if res.status_code == 200:
        print("VM Start Signal Sent.")
    else:
        print(f"Failed to start VM: {res.text}")
        
    # 3. Get Console
    print(f"\n3. Getting Console Link")
    
    res = requests.post(f"{API_URL}/vms/{target_vm['id']}/console", headers=headers)
    
    if res.status_code == 200:
        data = res.json()
        print("\n" + "="*60)
        print("STUDENT CONSOLE ACCESS GRANTED")
        print("="*60)
        print(f"Link: {data['direct_url']}")
        print("="*60)
    else:
        print(f"Failed to get console: {res.text}")

if __name__ == "__main__":
    test_student_flow()
