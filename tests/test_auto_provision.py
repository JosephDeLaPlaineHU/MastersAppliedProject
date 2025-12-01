import requests
import time

API_URL = "http://localhost:8080/api/v1"
PROFESSOR_EMAIL = "professor@example.com"
PASSWORD = "password123"
STUDENT_EMAIL = "student3@example.com"

def test_auto_provision():
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
    print(f"Found Course: {target_course['name']} (ID: {course_id})")

    # 3. Enroll Student 
    print(f"Enrolling {STUDENT_EMAIL}")
    enroll_resp = requests.post(f"{API_URL}/courses/{course_id}/enroll", json={"email": STUDENT_EMAIL}, headers=headers)
    
    if enroll_resp.status_code == 200:
        print("Enrollment Successful!")
        print(enroll_resp.json())
    else:
        print(f"Enrollment Failed: {enroll_resp.text}")
        return

    # 4. Verify VM Creation
    print("Waiting for auto-provisioning")
    time.sleep(5)
    
    print("Listing VMs")
    vms_resp = requests.get(f"{API_URL}/vms/", headers=headers)
    vms = vms_resp.json()
    
    # Look for VM for student3
    student_vm = next((vm for vm in vms if "student3" in vm["name"]), None)
    
    if student_vm:
        print(f"SUCCESS: Found auto-provisioned VM!")
        print(f" - Name: {student_vm['name']}")
        print(f" - ID: {student_vm['vm_id']}")
        print(f" - Status: {student_vm['status']}")
    else:
        print("FAILURE: Auto-provisioned VM not found.")

if __name__ == "__main__":
    test_auto_provision()
