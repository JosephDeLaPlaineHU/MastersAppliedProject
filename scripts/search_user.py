import requests
import getpass
import sys

API_URL = "http://127.0.0.1:8081/api/v1"

def search_user():
    print("Search User")
    
    username = input("SysAdmin Email: ").strip() or "sys_admin@example.com"
    password = getpass.getpass("Password: ").strip() or "password123"

    res = requests.post(f"{API_URL}/auth/login", data={"username": username, "password": password})
    if res.status_code != 200:
        print(f"Login failed: {res.text}")
        return
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    query = input("Enter Username or Email to search: ").strip().lower()
    
    res = requests.get(f"{API_URL}/users/", headers=headers)
    if res.status_code != 200:
        print(f"Failed to fetch users: {res.text}")
        return
        
    users = res.json()
    found = [u for u in users if query in u['username'].lower() or query in u['email'].lower()]
    
    if not found:
        print("No users found matching query.")
    else:
        print(f"\nFound {len(found)} users:")
        for u in found:
            print("-" * 60)
            print(f"USER: {u['username']} ({u['email']}) | Role: {u['role']} | ID: {u['id']}")
            
            detail_res = requests.get(f"{API_URL}/users/{u['id']}", headers=headers)
            if detail_res.status_code == 200:
                details = detail_res.json()
                
                # Courses
                courses = details.get('courses', [])
                if courses:
                    print(f"  Courses ({len(courses)}):")
                    for c in courses:
                        print(f"    - [{c['id']}] {c['name']}")
                else:
                    print("  Courses: None")
                    
                # VMs
                vms = details.get('vms', [])
                if vms:
                    print(f"  VMs ({len(vms)}):")
                    for v in vms:
                        ip = v.get('ip') or "N/A"
                        print(f"    - [{v['id']}] {v['name']} ({v['status']}) IP: {ip}")
                else:
                    print("  VMs: None")
            else:
                print(f"  [Error fetching details: {detail_res.text}]")
        print("-" * 60)

if __name__ == "__main__":
    search_user()
