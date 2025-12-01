import requests
import getpass

API_URL = "http://127.0.0.1:8081/api/v1"

def sysadmin_report():
    print("SysAdmin System Report")
    
    username = input("SysAdmin Email: ").strip() or "sys_admin@example.com"
    password = getpass.getpass("Password: ").strip() or "password123"

    print(f"Logging in as {username}")
    res = requests.post(f"{API_URL}/auth/login", data={"username": username, "password": password})
    
    if res.status_code != 200:
        print(f"Login failed: {res.text}")
        return
        
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Users Report
    print("\n[1] Users Report")
    res = requests.get(f"{API_URL}/users/", headers=headers)
    if res.status_code == 200:
        users = res.json()
        print(f"Total Users: {len(users)}")
        by_role = {}
        for u in users:
            role = u['role']
            if role not in by_role: by_role[role] = []
            by_role[role].append(u)
            
        for role, u_list in by_role.items():
            print(f"  {role.upper()}: {len(u_list)}")
            for u in u_list:
                print(f"    - {u['username']} ({u['email']})")
    else:
        print(f"Failed to fetch users: {res.text}")

    # 2. Courses Report
    print("\n[2] Courses Report")
    res = requests.get(f"{API_URL}/courses/", headers=headers)
    if res.status_code == 200:
        courses = res.json()
        print(f"Total Courses: {len(courses)}")
        for c in courses:
            print(f"  [{c['id']}] {c['name']} (Prof ID: {c['professor_id']})")
    else:
        print(f"Failed to fetch courses: {res.text}")

    # 3. VMs Report
    print("\n[3] VMs Report")
    res = requests.get(f"{API_URL}/vms/", headers=headers)
    if res.status_code == 200:
        vms = res.json()
        print(f"Total VMs: {len(vms)}")
        by_status = {}
        for vm in vms:
            status = vm.get('status', 'unknown')
            if status not in by_status: by_status[status] = []
            by_status[status].append(vm)
            
        for status, vm_list in by_status.items():
            print(f"  {status.upper()}: {len(vm_list)}")
            for vm in vm_list:
                ip = vm.get('ip_address') or "N/A"
                print(f"    - {vm['name']} (ID: {vm['id']}) [IP: {ip}]")
    else:
        print(f"Failed to fetch VMs: {res.text}")

if __name__ == "__main__":
    sysadmin_report()
