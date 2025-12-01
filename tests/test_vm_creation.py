import requests


API_URL = "http://localhost:8080/api/v1"
PROFESSOR_EMAIL = "professor@example.com"
PASSWORD = "password123"
TEMPLATE_ID = 100

def test_create_vm_in_course():
    # 1. Login as Professor
    print(f"Logging in as {PROFESSOR_EMAIL}")
    response = requests.post(f"{API_URL}/auth/login", data={"username": PROFESSOR_EMAIL, "password": PASSWORD})
    if response.status_code != 200:
        print("Login failed. Make sure users are seeded.")
        return

    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Login successful!")

    # 2. Get Courses to find "Intro to CS"
    print("Fetching courses")
    courses_resp = requests.get(f"{API_URL}/courses/", headers=headers)
    courses = courses_resp.json()
    
    target_course = next((c for c in courses if c["name"] == "Intro to CS"), None)
    if not target_course:
        print("Course 'Intro to CS' not found. Run seed_courses.py first.")
        return
        
    course_id = target_course["id"]
    print(f"Found Course: {target_course['name']} (ID: {course_id})")

    # 3. Create VM
    print(f"Creating VM from Template {TEMPLATE_ID} in Course {course_id}")
    vm_data = {
        "name": "test-vm-course-1",
        "template_id": TEMPLATE_ID,
        "course_id": course_id,
        "cpu": 1,
        "memory": 512
    }
    create_response = requests.post(f"{API_URL}/vms/", json=vm_data, headers=headers)
    
    if create_response.status_code == 200:
        print("VM Creation SUCCESS!")
        print(f"Response: {create_response.json()}")
    else:
        print(f"VM Creation FAILED: {create_response.text}")

if __name__ == "__main__":
    test_create_vm_in_course()
