import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_root():
    print("Testing Root Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Failed: {e}")

def test_create_user():
    print("\nTesting User Creation...")
    user_data = {"username": "test_user_1", "password": "securepassword"}
    try:
        response = requests.post(f"{BASE_URL}/users/", json=user_data)
        if response.status_code == 200:
            print("User created successfully!")
            return response.json()['id']
        elif response.status_code == 400:
            print("User already exists (expected if re-running).")
            # Hack to get ID if exists
            # In real test we would query DB or generic 'get user'
            return 1 
        else:
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"Failed: {e}")
        return None

def test_create_subject(user_id):
    if not user_id: return
    print("\nTesting Subject Creation...")
    subject_data = {
        "name": "Physics",
        "difficulty": 8,
        "exam_date": "2026-06-01",
        "topics": [
            {"name": "Thermodynamics", "weightage": 1.5},
            {"name": "Kinematics", "weightage": 1.0}
        ]
    }
    try:
        response = requests.post(f"{BASE_URL}/users/{user_id}/subjects/", json=subject_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    test_root()
    uid = test_create_user()
    test_create_subject(uid)
