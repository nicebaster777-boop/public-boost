"""Simple API test script."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import requests

BASE_URL = "http://localhost:8000/api/v1"

# Test login
print("1. Testing login...")
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"email": "test@example.com", "password": "TestPassword123!"}
)
print(f"   Status: {login_response.status_code}")
if login_response.status_code == 200:
    token = login_response.json()["data"]["token"]
    print(f"   Token received: {token[:50]}...")
    
    # Test get me
    print("\n2. Testing GET /users/me...")
    headers = {"Authorization": f"Bearer {token}"}
    me_response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    print(f"   Status: {me_response.status_code}")
    print(f"   Response: {json.dumps(me_response.json(), indent=2)}")
else:
    print(f"   Error: {login_response.json()}")
