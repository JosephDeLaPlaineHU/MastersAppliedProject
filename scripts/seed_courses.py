import requests

API_URL = "http://localhost:8080/api/v1"
PASSWORD = "password123"

def seed_courses():
    # 1. Create Student 2
    print("Creating Student 2")
    requests.post(f"{API_URL}/auth/register", json={
        "email": "student2@example.com",
        "username": "student2",
        "password": PASSWORD,
        "role": "student"
    })

    # 2. Login as Professor
    print("Logging in as Professor")
    resp = requests.post(f"{API_URL}/auth/login", data={"username": "professor@example.com", "password": PASSWORD})
    if resp.status_code != 200:
        print("Failed to login as professor. Make sure create_test_users.py was run.")
        return
    
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Create Courses
    print("Creating Course 1: Intro to CS")
    c1_resp = requests.post(f"{API_URL}/courses/", json={
        "name": "Intro to CS", 
        "description": "Basic Programming",
        "template_id": 100
    }, headers=headers)
    if c1_resp.status_code == 200:
        course1_id = c1_resp.json()["id"]
        print(f"Created Course 1 (ID: {course1_id})")
    else:
        print(f"Failed to create Course 1: {c1_resp.text}")
        return

    print("Creating Course 2: Advanced AI")
    c2_resp = requests.post(f"{API_URL}/courses/", json={
        "name": "Advanced AI", 
        "description": "Machine Learning",
        "template_id": 100
    }, headers=headers)
    if c2_resp.status_code == 200:
        course2_id = c2_resp.json()["id"]
        print(f"Created Course 2 (ID: {course2_id})")
    else:
        print(f"Failed to create Course 2: {c2_resp.text}")
        return

    # 4. Enroll Users
    # Course 1: student, student2, assistant
    users_c1 = ["student@example.com", "student2@example.com", "assistant@example.com"]
    print(f"Enrolling users to Course 1: {users_c1}")
    for email in users_c1:
        r = requests.post(f"{API_URL}/courses/{course1_id}/enroll", json={"email": email}, headers=headers)
        print(f"  {email}: {r.status_code} - {r.text}")

    # Course 2: student
    users_c2 = ["student@example.com"]
    print(f"Enrolling users to Course 2: {users_c2}")
    for email in users_c2:
        r = requests.post(f"{API_URL}/courses/{course2_id}/enroll", json={"email": email}, headers=headers)
        print(f"  {email}: {r.status_code} - {r.text}")

    print("Seeding Complete!")

if __name__ == "__main__":
    seed_courses()
