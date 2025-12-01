import requests
import getpass

API_URL = "http://127.0.0.1:8081/api/v1"

def search_vm():
    print("Search VM")
    
    username = input("SysAdmin Email: ").strip() or "sys_admin@example.com"
    password = getpass.getpass("Password: ").strip() or "password123"

    res = requests.post(f"{API_URL}/auth/login", data={"username": username, "password": password})
    if res.status_code != 200:
        print(f"Login failed: {res.text}")
        return
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    query = input("Enter VM Name to search: ").strip().lower()
    
    res = requests.get(f"{API_URL}/vms/", headers=headers)
    if res.status_code != 200:
        print(f"Failed to fetch VMs: {res.text}")
        return
        
    vms = res.json()
    found = [v for v in vms if query in v['name'].lower()]
    
    if not found:
        print("No VMs found matching query.")
    else:
        print(f"\nFound {len(found)} VMs:")
        print("-" * 100)
        print(f"{'ID':<5} | {'Name':<30} | {'Status':<10} | {'IP':<15} | {'Owner':<25} | {'Course'}")
        print("-" * 100)
        for v in found:
            ip = v.get('ip_address') or "N/A"
            owner = v.get('owner_email') or "N/A"
            course = v.get('course_name') or "N/A"
            print(f"{v['id']:<5} | {v['name']:<30} | {v['status']:<10} | {ip:<15} | {owner:<25} | {course}")
        print("-" * 100)

if __name__ == "__main__":
    search_vm()
