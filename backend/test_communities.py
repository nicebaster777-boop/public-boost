"""Test script for communities endpoints."""

import asyncio
import httpx

BASE_URL = "http://localhost:8000/api/v1"

async def test():
    async with httpx.AsyncClient() as client:
        # 1. Login
        print("1. Login...")
        r = await client.post(
            f"{BASE_URL}/auth/login",
            json={"email": "test@example.com", "password": "TestPassword123!"}
        )
        if r.status_code != 200:
            print(f"   ERROR: Login failed: {r.status_code}")
            return
        token = r.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        print(f"   OK: Token received")
        
        # 2. Get communities (empty list)
        print("\n2. GET /communities (empty)...")
        r = await client.get(f"{BASE_URL}/communities", headers=headers)
        print(f"   Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"   Communities: {len(data['data'])}")
            print(f"   Pagination: {data['pagination']}")
        
        # 3. Create VK community
        print("\n3. POST /communities (VK)...")
        r = await client.post(
            f"{BASE_URL}/communities",
            json={
                "platform": "vk",
                "external_id": "123456789",
                "name": "Test VK Group",
                "access_token": "test_vk_token_12345",
                "refresh_token": "test_refresh_token"
            },
            headers=headers
        )
        print(f"   Status: {r.status_code}")
        if r.status_code == 201:
            community = r.json()["data"]
            community_id = community["id"]
            print(f"   Created: {community['name']} (ID: {community_id})")
        else:
            print(f"   ERROR: {r.json()}")
            return
        
        # 4. Get communities (with one)
        print("\n4. GET /communities (with one)...")
        r = await client.get(f"{BASE_URL}/communities", headers=headers)
        if r.status_code == 200:
            data = r.json()
            print(f"   Communities: {len(data['data'])}")
        
        # 5. Get community details
        print(f"\n5. GET /communities/{community_id}...")
        r = await client.get(f"{BASE_URL}/communities/{community_id}", headers=headers)
        print(f"   Status: {r.status_code}")
        if r.status_code == 200:
            community = r.json()["data"]
            print(f"   Name: {community['name']}")
            print(f"   Platform: {community['platform']}")
        
        # 6. Update community
        print(f"\n6. PATCH /communities/{community_id}...")
        r = await client.patch(
            f"{BASE_URL}/communities/{community_id}",
            json={"name": "Updated VK Group Name"},
            headers=headers
        )
        print(f"   Status: {r.status_code}")
        if r.status_code == 200:
            community = r.json()["data"]
            print(f"   Updated name: {community['name']}")
        
        # 7. Create Telegram community
        print("\n7. POST /communities (Telegram)...")
        r = await client.post(
            f"{BASE_URL}/communities",
            json={
                "platform": "telegram",
                "external_id": "@test_channel",
                "name": "Test Telegram Channel",
                "bot_token": "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
            },
            headers=headers
        )
        print(f"   Status: {r.status_code}")
        if r.status_code == 201:
            telegram_community = r.json()["data"]
            telegram_id = telegram_community["id"]
            print(f"   Created: {telegram_community['name']}")
        
        # 8. Get all communities
        print("\n8. GET /communities (all)...")
        r = await client.get(f"{BASE_URL}/communities", headers=headers)
        if r.status_code == 200:
            data = r.json()
            print(f"   Total: {data['pagination']['total']}")
            for c in data["data"]:
                print(f"   - {c['name']} ({c['platform']})")
        
        print("\n✅ All tests completed!")

if __name__ == "__main__":
    asyncio.run(test())
