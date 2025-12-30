# План работы на следующий день

## Текущий статус

✅ **Завершено:**
- Проектирование (Stage 1-5): MVP boundaries, архитектура, схема БД, API design, frontend design
- Backend структура: модели, миграции, конфигурация
- Auth endpoints: register, login, logout (работают)
- Users endpoints: GET /me, PATCH /me (работают)
- Docker setup: dev и prod конфигурации
- Документация по деплою

## С чего начать завтра

### 1. Продолжить реализацию API роутеров

**Приоритет 1: Communities endpoints**
- `GET /api/v1/communities` - список сообществ пользователя
- `GET /api/v1/communities/{id}` - детали сообщества
- `POST /api/v1/communities` - подключение нового сообщества
- `PATCH /api/v1/communities/{id}` - обновление (имя)
- `POST /api/v1/communities/{id}/disconnect` - отключение
- `POST /api/v1/communities/{id}/refresh-token` - обновление токена

**Приоритет 2: Posts endpoints**
- `GET /api/v1/posts` - список постов
- `GET /api/v1/posts/{id}` - детали поста
- `POST /api/v1/posts` - создание поста
- `PATCH /api/v1/posts/{id}` - обновление поста
- `DELETE /api/v1/posts/{id}` - удаление поста
- `POST /api/v1/posts/{id}/publish-now` - публикация сейчас
- `POST /api/v1/posts/{id}/retry` - повторная попытка

**Приоритет 3: Analytics endpoints**
- `GET /api/v1/analytics/dashboard` - дашборд
- `GET /api/v1/analytics/communities/{id}` - аналитика сообщества
- `POST /api/v1/analytics/communities/{id}/refresh` - обновление аналитики
- `GET /api/v1/analytics/recommendations` - рекомендации

**Приоритет 4: Calendar и Upload**
- `GET /api/v1/calendar` - календарь постов
- `POST /api/v1/upload/image` - загрузка изображений

### 2. Реализовать бизнес-логику

- Валидация подписки (feature gating)
- Валидация времени публикации (не в прошлом, не более 30 дней)
- Валидация контента (макс. 10000 символов)
- Обработка ошибок и валидация

### 3. Настроить Celery для фоновых задач

- Настройка Celery app
- Задачи для публикации постов
- Задачи для получения аналитики
- Задачи для обновления токенов

### 4. Интеграции с внешними API (позже)

- VK API клиент
- Telegram Bot API клиент
- Обработка rate limits
- Обработка ошибок API

## Порядок работы

1. **Начать с Communities endpoints** - это базовая функциональность, нужна для всего остального
2. **Затем Posts endpoints** - основная функциональность приложения
3. **Потом Analytics** - для дашборда
4. **В конце Calendar и Upload** - вспомогательные функции

## Важные моменты

- Все endpoints должны проверять subscription tier (Basic/Extended)
- Все endpoints должны проверять ownership (пользователь может работать только со своими данными)
- Валидация на уровне Pydantic схем
- Обработка ошибок должна быть понятной для фронтенда
- Тестировать каждый endpoint после создания

## Файлы для создания/изменения

**Новые файлы:**
- `backend/app/api/communities.py`
- `backend/app/api/posts.py`
- `backend/app/api/analytics.py`
- `backend/app/api/calendar.py`
- `backend/app/api/upload.py`
- `backend/app/services/vk_client.py` (позже)
- `backend/app/services/telegram_client.py` (позже)
- `backend/app/celery_app.py` (позже)

**Изменения в существующих:**
- `backend/app/main.py` - добавить новые роутеры
- `backend/app/schemas/` - дополнить схемы если нужно
- `backend/app/core/config.py` - добавить настройки для внешних API (позже)

## Тестирование

После каждого роутера:
- Протестировать endpoints через curl/PowerShell
- Проверить валидацию
- Проверить feature gating
- Проверить обработку ошибок

## Заметки

- Backend запущен на http://localhost:8000
- БД доступна через docker-compose
- Миграции применены
- Auth работает, можно использовать токены для тестирования
