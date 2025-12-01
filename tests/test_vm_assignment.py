import requests

API_URL = "http://127.0.0.1:8081/api/v1"
ADMIN_EMAIL = "sys_admin@example.com"
ADMIN_PASSWORD = "password123"

def login():
    res = requests.post(f"{API_URL}/auth/login", data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    if res.status_code == 200:
        return res.json()["access_token"]
    return None

def test_vm_assignment():
    print("Testing VM Assignment")
    token = login()
    if not token:
        print("FATAL: Login failed")
        return
    headers = {"Authorization": f"Bearer {token}"}

    # 1. List VMs to find one to assign
    res = requests.get(f"{API_URL}/vms/", headers=headers)
    vms = res.json()
    if not vms:
        print("No VMs found to assign.")
        return
        
    target_vm = vms[0]
    print(f"Target VM: {target_vm['name']} (ID: {target_vm['id']})")
    
    # 2. Find a course to assign to
    res = requests.get(f"{API_URL}/courses/", headers=headers)
    courses = res.json()
    if not courses:
        print("No courses found. Cannot test course assignment.")
        return
    target_course = courses[0]
    print(f"Target Course: {target_course['name']} (ID: {target_course['id']})")

    # 3. Assign to 'student2@example.com' and the course
    target_email = "student2@example.com"
    print(f"Assigning to {target_email} in course {target_course['name']}")
    
    res = requests.post(f"{API_URL}/vms/{target_vm['id']}/assign", headers=headers, json={
        "email": target_email,
        "course_id": target_course['id']
    })
    
    if res.status_code == 200:
        print("SUCCESS: VM Assigned.")
        print(res.json())
    else:
        print(f"FAILED: {res.status_code} - {res.text}")

if __name__ == "__main__":
    test_vm_assignment()
