"""Демонстрация функционала API без подключения внешних API."""

import asyncio
import httpx

BASE_URL = "http://localhost:8000/api/v1"

async def demo():
    """Демонстрация работы API."""
    async with httpx.AsyncClient() as client:
        print("=" * 60)
        print("ДЕМОНСТРАЦИЯ ФУНКЦИОНАЛА API")
        print("=" * 60)
        
        # 1. Регистрация пользователя
        print("\n1. Регистрация нового пользователя...")
        r = await client.post(
            f"{BASE_URL}/auth/register",
            json={
                "email": "demo@example.com",
                "password": "DemoPassword123!",
                "timezone": "Europe/Moscow"
            }
        )
        if r.status_code == 201:
            print("   [OK] Пользователь создан")
            user_data = r.json()["data"]
            print(f"   Email: {user_data['email']}")
            print(f"   Subscription: {user_data['subscription_tier']}")
        elif r.status_code == 409:
            print("   [INFO] Пользователь уже существует, используем существующего")
        else:
            print(f"   [ERROR] Ошибка: {r.status_code} - {r.text}")
            return
        
        # 2. Вход
        print("\n2. Вход в систему...")
        r = await client.post(
            f"{BASE_URL}/auth/login",
            json={"email": "demo@example.com", "password": "DemoPassword123!"}
        )
        if r.status_code != 200:
            print(f"   [ERROR] Ошибка входа: {r.status_code}")
            return
        token = r.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("   [OK] Успешный вход, получен токен")
        
        # 3. Получение информации о пользователе
        print("\n3. Получение информации о пользователе...")
        r = await client.get(f"{BASE_URL}/users/me", headers=headers)
        if r.status_code == 200:
            user = r.json()
            print(f"   [OK] Email: {user['email']}")
            print(f"   [OK] Subscription: {user['subscription_tier']}")
            print(f"   [WARN] Для работы с постами нужен 'extended' tier")
        
        # 4. Обновление subscription tier (для демо)
        print("\n4. Обновление subscription tier на 'extended' (для демо)...")
        r = await client.patch(
            f"{BASE_URL}/users/me",
            json={"subscription_tier": "extended"},
            headers=headers
        )
        if r.status_code == 200:
            print("   [OK] Subscription tier обновлен на 'extended'")
        
        # 5. Создание VK сообщества (без реального токена)
        print("\n5. Создание VK сообщества (демо токен)...")
        r = await client.post(
            f"{BASE_URL}/communities",
            json={
                "platform": "vk",
                "external_id": "123456789",
                "name": "Демо VK Группа",
                "access_token": "demo_vk_token_12345",
                "refresh_token": "demo_refresh_token"
            },
            headers=headers
        )
        if r.status_code == 201:
            response_data = r.json()
            vk_community = response_data.get("data", response_data)
            vk_id = vk_community["id"]
            print(f"   [OK] Создано: {vk_community['name']} (ID: {vk_id})")
        else:
            try:
                error_detail = r.json()
            except:
                error_detail = r.text
            print(f"   [ERROR] Ошибка: {r.status_code} - {error_detail}")
            vk_id = None
        
        # 6. Создание Telegram сообщества
        print("\n6. Создание Telegram сообщества (демо токен)...")
        r = await client.post(
            f"{BASE_URL}/communities",
            json={
                "platform": "telegram",
                "external_id": "@demo_channel",
                "name": "Демо Telegram Канал",
                "bot_token": "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
            },
            headers=headers
        )
        if r.status_code == 201:
            response_data = r.json()
            tg_community = response_data.get("data", response_data)
            tg_id = tg_community["id"]
            print(f"   [OK] Создано: {tg_community['name']} (ID: {tg_id})")
        else:
            try:
                error_detail = r.json()
            except:
                error_detail = r.text
            print(f"   [ERROR] Ошибка: {r.status_code} - {error_detail}")
            tg_id = None
        
        # 7. Список сообществ
        print("\n7. Получение списка сообществ...")
        r = await client.get(f"{BASE_URL}/communities", headers=headers)
        if r.status_code == 200:
            data = r.json()
            print(f"   [OK] Найдено сообществ: {data['pagination']['total']}")
            for c in data["data"]:
                print(f"      - {c['name']} ({c['platform']})")
        
        # 8. Создание черновика поста
        print("\n8. Создание черновика поста...")
        r = await client.post(
            f"{BASE_URL}/posts",
            json={
                "content_text": "Это демонстрационный пост для тестирования API",
                "image_url": None,
                "scheduled_at": None,
                "community_ids": None
            },
            headers=headers
        )
        if r.status_code == 201:
            response_data = r.json()
            draft_post = response_data.get("data", response_data)
            draft_id = draft_post["id"]
            print(f"   [OK] Создан черновик (ID: {draft_id})")
            print(f"   Статус: {draft_post['status']}")
        else:
            try:
                error_detail = r.json()
            except:
                error_detail = r.text
            print(f"   [ERROR] Ошибка: {r.status_code} - {error_detail}")
            draft_id = None
        
        # 9. Создание запланированного поста
        if vk_id and tg_id:
            print("\n9. Создание запланированного поста...")
            from datetime import datetime, timedelta, timezone
            scheduled_time = datetime.now(timezone.utc) + timedelta(hours=2)
            r = await client.post(
                f"{BASE_URL}/posts",
                json={
                    "content_text": "Этот пост будет опубликован через 2 часа",
                    "image_url": None,
                    "scheduled_at": scheduled_time.isoformat(),
                    "community_ids": [str(vk_id), str(tg_id)]
                },
                headers=headers
            )
            if r.status_code == 201:
                response_data = r.json()
                scheduled_post = response_data.get("data", response_data)
                print(f"   [OK] Создан запланированный пост (ID: {scheduled_post['id']})")
                print(f"   Статус: {scheduled_post['status']}")
                print(f"   Запланирован на: {scheduled_post['scheduled_at']}")
                print(f"   Целевые сообщества: {len(scheduled_post['publications'])}")
            else:
                try:
                    error_detail = r.json()
                except:
                    error_detail = r.text
                print(f"   [ERROR] Ошибка: {r.status_code} - {error_detail}")
        
        # 10. Список постов
        print("\n10. Получение списка постов...")
        r = await client.get(f"{BASE_URL}/posts", headers=headers)
        if r.status_code == 200:
            data = r.json()
            print(f"   [OK] Найдено постов: {data['pagination']['total']}")
            for p in data["data"]:
                print(f"      - {p['status']}: {p['content_text'][:50]}...")
        
        print("\n" + "=" * 60)
        print("ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
        print("=" * 60)
        print("\nДля интерактивного тестирования откройте:")
        print("   http://localhost:8000/docs")
        print("\nДля просмотра альтернативной документации:")
        print("   http://localhost:8000/redoc")

if __name__ == "__main__":
    asyncio.run(demo())
