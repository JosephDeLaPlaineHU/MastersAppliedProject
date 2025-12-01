import requests
import getpass

API_URL = "http://localhost:8080/api/v1"

def list_students():
    print("\nList Course Students & VMs")
    
    # 1. Login
    print("Login (Professor/Assistant/Admin):")
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
        if courses_resp.status_code == 200:
            courses = courses_resp.json()
            for c in courses:
                print(f" - ID: {c['id']} | Name: {c['name']}")
        else:
            print("Could not fetch courses.")
    except Exception as e:
        print(f"Failed to fetch courses: {e}")
        return

    # 3. Get Details
    course_id = input("\nEnter Course ID: ").strip()
    
    # 4. Fetch Students
    try:
        response = requests.get(f"{API_URL}/courses/{course_id}/students", headers=headers)
        
        if response.status_code == 200:
            students = response.json()
            print(f"\nStudents in Course {course_id}")
            print(f"{'Username':<20} | {'Email':<30} | {'VM Name':<25} | {'Status':<10}")
            print("-" * 95)
            
            for s in students:
                vm = s['vm']
                vm_name = vm['name'] if vm else "No VM"
                vm_status = vm['status'] if vm else "-"
                print(f"{s['username']:<20} | {s['email']:<30} | {vm_name:<25} | {vm_status:<10}")
                
            print(f"\nTotal Students: {len(students)}")
        else:
            print(f"\nERROR: Failed to list students. Status: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_students()
