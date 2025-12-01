import requests
import time

API_URL = "http://localhost:8080/api/v1"
PROFESSOR_EMAIL = "professor@example.com"
PASSWORD = "password123"

def test_provisioning():
    # 1. Login as Professor
    print(f"Logging in as {PROFESSOR_EMAIL}")
    response = requests.post(f"{API_URL}/auth/login", data={"username": PROFESSOR_EMAIL, "password": PASSWORD})
    if response.status_code != 200:
        print("Login failed.")
        return

    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get Course ID
    print("Fetching courses")
    courses_resp = requests.get(f"{API_URL}/courses/", headers=headers)
    courses = courses_resp.json()
    target_course = next((c for c in courses if c["name"] == "Intro to CS"), None)
    
    if not target_course:
        print("Course 'Intro to CS' not found.")
        return
    
    course_id = target_course["id"]
    print(f"Found Course: {target_course['name']} (ID: {course_id}, Template: {target_course.get('template_id')})")

    # 3. Trigger Provisioning
    print("Triggering Provisioning for ALL students")
    prov_resp = requests.post(f"{API_URL}/courses/{course_id}/provision", json={}, headers=headers)
    
    if prov_resp.status_code == 200:
        print("Provisioning Triggered Successfully!")
        print(prov_resp.json())
    else:
        print(f"Provisioning Failed: {prov_resp.text}")
        return

    # 4. Verify VMs Created
    print("Waiting for creation")
    time.sleep(5)
    
    print("Listing VMs")
    vms_resp = requests.get(f"{API_URL}/vms/", headers=headers)
    vms = vms_resp.json()
    
    course_vms = [vm for vm in vms if vm.get("name", "").startswith("intro-to-cs")]
    print(f"Found {len(course_vms)} VMs for this course:")
    for vm in course_vms:
        print(f" - {vm['name']} (ID: {vm['vm_id']}, Status: {vm['status']})")

if __name__ == "__main__":
    test_provisioning()
