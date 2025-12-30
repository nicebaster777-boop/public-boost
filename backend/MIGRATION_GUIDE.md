# Руководство по применению миграций

## Локальная разработка

### Вариант 1: С Docker Compose

1. **Запустите Docker Desktop** (если не запущен)

2. **Запустите контейнеры:**
```bash
docker-compose up -d db
```

3. **Дождитесь готовности БД** (проверка healthcheck)

4. **Примените миграции:**
```bash
# В контейнере backend
docker-compose run --rm backend alembic upgrade head

# Или локально (если установлены зависимости)
cd backend
alembic upgrade head
```

### Вариант 2: Локальная PostgreSQL

1. **Установите PostgreSQL** (если не установлен)

2. **Создайте базу данных:**
```sql
CREATE DATABASE trusted_db;
CREATE USER trusted_user WITH PASSWORD 'trusted_password';
GRANT ALL PRIVILEGES ON DATABASE trusted_db TO trusted_user;
```

3. **Создайте .env файл** в папке backend:
```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=trusted_user
POSTGRES_PASSWORD=trusted_password
POSTGRES_DB=trusted_db
```

4. **Примените миграции:**
```bash
cd backend
alembic upgrade head
```

## Проверка миграций

### Просмотр текущей версии
```bash
alembic current
```

### Просмотр истории миграций
```bash
alembic history
```

### Откат миграции (если нужно)
```bash
alembic downgrade -1  # Откатить на одну версию
alembic downgrade base  # Откатить все миграции
```

## Создание новой миграции

```bash
cd backend
alembic revision --autogenerate -m "Описание изменений"
```

## Production (на VPS)

```bash
# В контейнере backend
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

## Troubleshooting

### Ошибка подключения к БД
- Проверьте, что PostgreSQL запущен
- Проверьте переменные окружения в .env
- Проверьте, что порт 5432 доступен

### Ошибка "Target database is not up to date"
- Примените все миграции: `alembic upgrade head`

### Ошибка "Can't locate revision identified by"
- Проверьте, что файл миграции существует в `migrations/versions/`
- Проверьте, что revision ID в файле миграции корректен
