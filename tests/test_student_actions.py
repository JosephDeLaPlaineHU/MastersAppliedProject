import requests
import time

API_URL = "http://localhost:8080/api/v1"
TEST_USER = "student_test_actions"
TEST_EMAIL = "student_test_actions@example.com"
PASSWORD = "password123"
ADMIN_EMAIL = "sys_admin@example.com"

def test_student_actions():
    # 0. Setup: Create User & Enroll
    print("Setup: Creating & Enrolling Test User")
    requests.post(f"{API_URL}/auth/register", json={
        "email": TEST_EMAIL,
        "username": TEST_USER,
        "password": PASSWORD,
        "role": "student"
    })
    
    admin_resp = requests.post(f"{API_URL}/auth/login", data={"username": ADMIN_EMAIL, "password": PASSWORD})
    if admin_resp.status_code != 200:
        print("Admin login failed.")
        return
    admin_token = admin_resp.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    courses = requests.get(f"{API_URL}/courses/", headers=admin_headers).json()
    target_course = next((c for c in courses if c["name"] == "Intro to CS"), None)
    if not target_course:
        print("Course 'Intro to CS' not found.")
        return
    
    print(f"Enrolling {TEST_EMAIL}")
    requests.post(f"{API_URL}/courses/{target_course['id']}/enroll", json={"email": TEST_EMAIL}, headers=admin_headers)
    
    print("Waiting for provisioning")
    time.sleep(5)

    # 1. Get Other Student's VM ID (as Admin) for Negative Test
    vms = requests.get(f"{API_URL}/vms/", headers=admin_headers).json()
    other_vm = next((vm for vm in vms if TEST_USER not in vm["name"] and "student" in vm["name"]), None)
    if other_vm:
        print(f"Found other student's VM: {other_vm['name']} (ID: {other_vm['vm_id']})")

    # 2. Login as Test Student
    print(f"\nTesting as {TEST_EMAIL}")
    resp = requests.post(f"{API_URL}/auth/login", data={"username": TEST_EMAIL, "password": PASSWORD})
    if resp.status_code != 200:
        print("Student login failed.")
        return
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. List Courses
    print("\n[Test] List Courses (Should only see enrolled):")
    courses = requests.get(f"{API_URL}/courses/", headers=headers).json()
    print(f"Visible Courses: {[c['name'] for c in courses]}")
    if len(courses) == 1 and courses[0]['name'] == "Intro to CS":
        print("PASS: Only enrolled course visible.")
    else:
        print("FAIL: Unexpected course list.")

    # 4. List VMs
    print("\n[Test] List VMs (Should only see own):")
    my_vms = requests.get(f"{API_URL}/vms/", headers=headers).json()
    print(f"Visible VMs: {[vm['name'] for vm in my_vms]}")
    if all(TEST_USER in vm['name'] for vm in my_vms):
        print("PASS: Only own VMs visible.")
    else:
        print("FAIL: Saw other users' VMs.")

    if not my_vms:
        print("No VMs found for student. Skipping start/stop tests.")
        return

    target_vm_id = my_vms[0]['vm_id']
    
    # 5. Start Own VM
    print(f"\n[Test] Start Own VM ({target_vm_id}):")
    start_resp = requests.post(f"{API_URL}/vms/{target_vm_id}/start", headers=headers)
    print(f"Status: {start_resp.status_code} - {start_resp.text}")
    
    # 6. Stop Own VM
    print(f"\n[Test] Stop Own VM ({target_vm_id}):")
    stop_resp = requests.post(f"{API_URL}/vms/{target_vm_id}/stop", headers=headers)
    print(f"Status: {stop_resp.status_code} - {stop_resp.text}")

    # 7. Negative Test: Start Other VM
    if other_vm:
        other_id = other_vm['vm_id']
        print(f"\n[Test] Start Other VM ({other_id}) - Should Fail:")
        neg_resp = requests.post(f"{API_URL}/vms/{other_id}/start", headers=headers)
        print(f"Status: {neg_resp.status_code} - {neg_resp.text}")
        if neg_resp.status_code == 403:
            print("PASS: Access Denied.")
        else:
            print("FAIL: Access Granted or other error.")

if __name__ == "__main__":
    test_student_actions()
