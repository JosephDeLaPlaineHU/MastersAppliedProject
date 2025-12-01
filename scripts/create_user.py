import requests
import getpass

API_URL = "http://localhost:8080/api/v1"

def create_user():
    print("\nCreate New User")
    email = input("Email: ").strip()
    username = input("Username: ").strip()
    password = getpass.getpass("Password: ").strip()
    
    print("\nSelect Role:")
    print("1. Student")
    print("2. Assistant")
    print("3. Professor")
    print("4. Business Admin")
    print("5. Sys Admin")
    
    role_choice = input("Choice (1-5): ").strip()
    role_map = {
        "1": "student",
        "2": "assistant",
        "3": "professor",
        "4": "business_admin",
        "5": "sys_admin"
    }
    role = role_map.get(role_choice, "student")
    
    payload = {
        "email": email,
        "username": username,
        "password": password,
        "role": role
    }
    
    try:
        response = requests.post(f"{API_URL}/auth/register", json=payload)
        if response.status_code == 200:
            print(f"\nSUCCESS: User {username} ({role}) created!")
        else:
            print(f"\nERROR: Failed to create user. Status: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"\nERROR: Could not connect to API. Is the backend running? ({e})")

if __name__ == "__main__":
    create_user()
