"""Simple test."""
import asyncio
import httpx

async def test():
    async with httpx.AsyncClient() as client:
        # Login
        r = await client.post(
            'http://localhost:8000/api/v1/auth/login',
            json={'email': 'test@example.com', 'password': 'TestPassword123!'}
        )
        print(f'Login: {r.status_code}')
        print(f'Response: {r.json()}')
        if r.status_code == 200:
            data = r.json()
            token = data.get('data', {}).get('token') or data.get('token')
            if token:
                print(f'Token: {token[:50]}...')
            
            # Get me
            r2 = await client.get(
                'http://localhost:8000/api/v1/users/me',
                headers={'Authorization': f'Bearer {token}'}
            )
            print(f'Get me: {r2.status_code}')
            print(f'Response: {r2.json()}')

asyncio.run(test())
