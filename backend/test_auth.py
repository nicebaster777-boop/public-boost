"""Test script for auth endpoints."""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_register():
    """Test user registration."""
    print("\n=== Testing Registration ===")
    
    url = f"{BASE_URL}/auth/register"
    data = {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "timezone": "Europe/Moscow"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 201:
            print("[OK] Registration successful!")
            return response.json()["data"]["token"]
        else:
            print(f"[ERROR] Registration failed: {response.json()}")
            return None
    except Exception as e:
        print(f"[ERROR] Exception: {e}")
        return None


def test_login():
    """Test user login."""
    print("\n=== Testing Login ===")
    
    url = f"{BASE_URL}/auth/login"
    data = {
        "email": "test@example.com",
        "password": "TestPassword123!"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("[OK] Login successful!")
            return response.json()["data"]["token"]
        else:
            print(f"[ERROR] Login failed: {response.json()}")
            return None
    except Exception as e:
        print(f"[ERROR] Exception: {e}")
        return None


def test_get_me(token):
    """Test getting current user."""
    print("\n=== Testing GET /users/me ===")
    
    url = f"{BASE_URL}/users/me"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("[OK] Get user info successful!")
        else:
            print(f"[ERROR] Get user info failed: {response.json()}")
    except Exception as e:
        print(f"[ERROR] Exception: {e}")


def test_invalid_login():
    """Test login with invalid credentials."""
    print("\n=== Testing Invalid Login ===")
    
    url = f"{BASE_URL}/auth/login"
    data = {
        "email": "test@example.com",
        "password": "WrongPassword"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 401:
            print("[OK] Invalid login correctly rejected!")
        else:
            print(f"[WARNING] Expected 401, got {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Exception: {e}")


if __name__ == "__main__":
    print("Starting Auth Endpoints Tests...")
    print("=" * 50)
    
    # Test registration
    token = test_register()
    
    # Test login
    login_token = test_login()
    
    # Test get current user
    if login_token:
        test_get_me(login_token)
    
    # Test invalid login
    test_invalid_login()
    
    print("\n" + "=" * 50)
    print("Tests completed!")
