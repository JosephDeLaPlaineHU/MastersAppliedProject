import requests
import getpass

API_URL = "http://127.0.0.1:8081/api/v1"

def list_course_assistants():
    print("List Course Assistants")
    
    username = input("Professor Email [professor@example.com]: ").strip() or "professor@example.com"
    password = getpass.getpass("Password [password123]: ").strip() or "password123"

    print(f"Logging in as {username}")
    res = requests.post(f"{API_URL}/auth/login", data={"username": username, "password": password})
    
    if res.status_code != 200:
        print(f"Login failed: {res.text}")
        return
        
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. List Courses First
    print("Fetching your courses")
    res = requests.get(f"{API_URL}/courses/", headers=headers)
    if res.status_code != 200:
        print(f"Failed to list courses: {res.text}")
        return
        
    courses = res.json()
    if not courses:
        print("No courses found.")
        return
        
    print(f"\nYour Courses:")
    for c in courses:
        print(f"  [{c['id']}] {c['name']}")
        
    # 2. Select Course
    try:
        course_id = int(input("\nEnter Course ID to view assistants: ").strip())
    except ValueError:
        print("Invalid ID")
        return

    # 3. Get Assistants
    print(f"Fetching assistants for Course {course_id}")
    res = requests.get(f"{API_URL}/courses/{course_id}/assistants", headers=headers)
    
    if res.status_code != 200:
        print(f"Failed to get assistants: {res.text}")
        return
        
    assistants = res.json()
    
    if not assistants:
        print("No assistants found for this course.")
        return
        
    print(f"\nFound {len(assistants)} assistants:")
    print("-" * 60)
    print(f"{'ID':<5} | {'Username':<20} | {'Email'}")
    print("-" * 60)
    for a in assistants:
        print(f"{a['id']:<5} | {a['username']:<20} | {a['email']}")
    print("-" * 60)

if __name__ == "__main__":
    list_course_assistants()
