import requests
import getpass

API_URL = "http://localhost:8080/api/v1"

def assign_assistant():
    print("\n=== Assign Assistant to Course ===")
    
    # 1. Login
    print("Login as Professor/Admin:")
    username = input("Username (email): ").strip()
    password = getpass.getpass("Password: ").strip()
    
    try:
        auth_resp = requests.post(f"{API_URL}/auth/login", data={"username": username, "password": password})
        if auth_resp.status_code != 200:
            print("Login failed. Check credentials.")
            return
        token = auth_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
    except Exception as e:
        print(f"Connection error: {e}")
        return

    # 2. List Courses
    print("\nAvailable Courses:")
    try:
        courses_resp = requests.get(f"{API_URL}/courses/", headers=headers)
        courses = courses_resp.json()
        for c in courses:
            print(f" - ID: {c['id']} | Name: {c['name']}")
    except Exception as e:
        print(f"Failed to fetch courses: {e}")
        return

    # 3. Get Details
    course_id = input("\nEnter Course ID: ").strip()
    assistant_email = input("Assistant Email: ").strip()
    
    # 4. Enroll
    try:
        payload = {"email": assistant_email}
        response = requests.post(f"{API_URL}/courses/{course_id}/enroll", json=payload, headers=headers)
        
        if response.status_code == 200:
            print(f"\nSUCCESS: {assistant_email} assigned to course ID {course_id}.")
            print(response.json())
        else:
            print(f"\nERROR: Failed to assign assistant. Status: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    assign_assistant()
