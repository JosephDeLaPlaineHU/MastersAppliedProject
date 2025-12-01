import requests
import getpass

API_URL = "http://localhost:8080/api/v1"

def create_course():
    print("\nCreate New Course")
    
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

    # 2. Course Details
    print("\nCourse Details:")
    name = input("Course Name: ").strip()
    description = input("Description: ").strip()
    template_id = input("Proxmox Template ID (e.g., 100): ").strip()
    
    if not template_id.isdigit():
        print("Template ID must be a number.")
        return

    payload = {
        "name": name,
        "description": description,
        "template_id": int(template_id)
    }
    
    # 3. Create
    try:
        response = requests.post(f"{API_URL}/courses/", json=payload, headers=headers)
        if response.status_code == 200:
            course = response.json()
            print(f"\nSUCCESS: Course '{course['name']}' created (ID: {course['id']})")
        else:
            print(f"\nERROR: Failed to create course. Status: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_course()
