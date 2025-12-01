import requests
import getpass

API_URL = "http://127.0.0.1:8081/api/v1"

def list_professor_courses():
    print("List Professor Courses")
    
    # Get Credentials
    username = input("Professor Email [professor@example.com]: ").strip() or "professor@example.com"
    password = getpass.getpass("Password [password123]: ").strip() or "password123"

    # Login
    print(f"Logging in as {username}...")
    res = requests.post(f"{API_URL}/auth/login", data={"username": username, "password": password})
    
    if res.status_code != 200:
        print(f"Login failed: {res.text}")
        return
        
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get Courses
    print("Fetching courses...")
    res = requests.get(f"{API_URL}/courses/", headers=headers)
    
    if res.status_code != 200:
        print(f"Failed to list courses: {res.text}")
        return
        
    courses = res.json()
    
    if not courses:
        print("No courses found for this professor.")
        return
        
    print(f"\nFound {len(courses)} courses:")
    print("-" * 60)
    print(f"{'ID':<5} | {'Name':<20} | {'Description'}")
    print("-" * 60)
    for c in courses:
        desc = c.get('description') or ""
        print(f"{c['id']:<5} | {c['name']:<20} | {desc}")
    print("-" * 60)

if __name__ == "__main__":
    list_professor_courses()
