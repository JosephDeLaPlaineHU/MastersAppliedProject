import requests

API_URL = "http://127.0.0.1:8081/api/v1"
ADMIN_EMAIL = "sys_admin@example.com"
ADMIN_PASSWORD = "password123"

def login(email, password):
    try:
        res = requests.post(f"{API_URL}/auth/login", data={"username": email, "password": password})
        if res.status_code == 200:
            return res.json()["access_token"]
    except:
        pass
    return None

def test_assign_professor():
    print("Testing Assign Professor")
    
    # 1. Login as SysAdmin
    token = login(ADMIN_EMAIL, ADMIN_PASSWORD)
    if not token:
        print("FATAL: Could not login as SysAdmin")
        return
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Get a Course
    res = requests.get(f"{API_URL}/courses/", headers=headers)
    courses = res.json()
    if not courses:
        print("No courses found. Creating one")
        return
        
    target_course = courses[0]
    print(f"Target Course: {target_course['name']} (ID: {target_course['id']})")
    print(f"Current Professor ID: {target_course['professor_id']}")
    
    # 3. Find a Professor to Assign
    prof_email = "new_prof@example.com"
    prof_pass = "password123"
    
    requests.post(f"{API_URL}/auth/register", json={
        "email": prof_email,
        "username": "new_prof",
        "password": prof_pass,
        "role": "professor"
    })
    
    print(f"Assigning {prof_email} to course")
    
    # 4. Call Assign Endpoint
    res = requests.put(
        f"{API_URL}/courses/{target_course['id']}/professor", 
        headers=headers,
        json={"email": prof_email}
    )
    
    if res.status_code == 200:
        print("SUCCESS: Professor assigned.")
        print(res.json())
    else:
        print(f"FAILED: {res.status_code} - {res.text}")

if __name__ == "__main__":
    test_assign_professor()
