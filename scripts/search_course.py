import requests
import getpass

API_URL = "http://127.0.0.1:8081/api/v1"

def search_course():
    print("Search Course")
    
    username = input("SysAdmin Email: ").strip() or "sys_admin@example.com"
    password = getpass.getpass("Password: ").strip() or "password123"

    res = requests.post(f"{API_URL}/auth/login", data={"username": username, "password": password})
    if res.status_code != 200:
        print(f"Login failed: {res.text}")
        return
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    query = input("Enter Course Name to search: ").strip().lower()
    
    res = requests.get(f"{API_URL}/courses/", headers=headers)
    if res.status_code != 200:
        print(f"Failed to fetch courses: {res.text}")
        return
        
    courses = res.json()
    found = [c for c in courses if query in c['name'].lower()]
    
    if not found:
        print("No courses found matching query.")
    else:
        print(f"\nFound {len(found)} courses:")
        for c in found:
            print("-" * 60)
            print(f"COURSE: {c['name']} (ID: {c['id']})")
            
            detail_res = requests.get(f"{API_URL}/courses/{c['id']}", headers=headers)
            if detail_res.status_code == 200:
                details = detail_res.json()
                
                # Professor
                prof = details.get('professor')
                if prof:
                    print(f"  Professor: {prof['username']} ({prof['email']})")
                else:
                    print("  Professor: N/A")
                    
                # Assistants
                assistants = details.get('assistants', [])
                if assistants:
                    print(f"  Assistants ({len(assistants)}):")
                    for a in assistants:
                        print(f"    - {a['username']} ({a['email']})")
                else:
                    print("  Assistants: None")

                # Students
                students = details.get('students', [])
                if students:
                    print(f"  Students ({len(students)}):")
                    for s in students:
                        print(f"    - {s['username']} ({s['email']})")
                else:
                    print("  Students: None")
            else:
                print(f"  [Error fetching details: {detail_res.text}]")
        print("-" * 60)

if __name__ == "__main__":
    search_course()
