# Тестирование миграций

## Вариант 1: С Docker (рекомендуется)

### Шаг 1: Запустите Docker Desktop

### Шаг 2: Запустите только БД
```bash
docker-compose up -d db
```

### Шаг 3: Дождитесь готовности БД
```bash
# Проверка статуса
docker-compose ps db

# Просмотр логов
docker-compose logs db
```

### Шаг 4: Проверьте подключение
```bash
cd backend
python check_db.py
```

### Шаг 5: Примените миграции
```bash
# Вариант A: Через скрипт
python apply_migrations.py

# Вариант B: Через Alembic напрямую
alembic upgrade head
```

### Шаг 6: Проверьте результат
```bash
# Проверка текущей версии
alembic current

# Подключение к БД и проверка таблиц
docker-compose exec db psql -U trusted_user -d trusted_db -c "\dt"
```

---

## Вариант 2: Локальная PostgreSQL

### Шаг 1: Убедитесь, что PostgreSQL запущен
```bash
# Windows (если установлен как сервис)
# Проверьте в Services (services.msc)

# Или через командную строку
pg_isready -h localhost -p 5432
```

### Шаг 2: Создайте базу данных (если не создана)
```bash
# Подключитесь к PostgreSQL
psql -U postgres

# Выполните SQL
CREATE DATABASE trusted_db;
CREATE USER trusted_user WITH PASSWORD 'trusted_password';
GRANT ALL PRIVILEGES ON DATABASE trusted_db TO trusted_user;
\q
```

### Шаг 3: Создайте .env файл в backend/
```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=trusted_user
POSTGRES_PASSWORD=trusted_password
POSTGRES_DB=trusted_db
```

### Шаг 4: Проверьте подключение
```bash
cd backend
python check_db.py
```

### Шаг 5: Примените миграции
```bash
python apply_migrations.py
```

---

## Проверка результата

### Список таблиц
```sql
-- В psql или через docker-compose
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public';
```

Ожидаемые таблицы:
- users
- communities
- posts
- post_publications
- analytics_snapshots
- scheduled_tasks

### Проверка структуры таблицы
```sql
\d users
\d communities
```

---

## Если что-то пошло не так

### Откат миграций
```bash
cd backend
alembic downgrade -1  # Откатить последнюю миграцию
alembic downgrade base  # Откатить все миграции
```

### Пересоздание БД (ОСТОРОЖНО - удалит все данные!)
```bash
# В psql
DROP DATABASE trusted_db;
CREATE DATABASE trusted_db;
GRANT ALL PRIVILEGES ON DATABASE trusted_db TO trusted_user;

# Затем примените миграции заново
cd backend
alembic upgrade head
```

---

## Следующие шаги

После успешного применения миграций:
1. ✅ БД готова к использованию
2. ✅ Можно запускать backend API
3. ✅ Можно тестировать endpoints
4. ✅ Можно продолжать разработку роутеров
