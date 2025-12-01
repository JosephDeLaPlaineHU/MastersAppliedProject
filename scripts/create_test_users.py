import requests

API_URL = "http://localhost:8080/api/v1"
PASSWORD = "password123"

ROLES = [
    "student",
    "assistant",
    "professor",
    "business_admin",
    "sys_admin"
]

def create_users():
    print("Creating test users")
    
    for role in ROLES:
        email = f"{role}@example.com"
        username = f"test_{role}"
        
        payload = {
            "email": email,
            "username": username,
            "password": PASSWORD,
            "role": role
        }
        
        print(f"Registering {role} ({email})")
        try:
            response = requests.post(f"{API_URL}/auth/register", json=payload)
            if response.status_code == 200:
                print(f"SUCCESS: Created {username}")
            elif response.status_code == 400 and "already exists" in response.text:
                print(f"SKIPPED: {username} already exists")
            else:
                print(f"FAILED: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"ERROR: {e}")

if __name__ == "__main__":
    create_users()
