# Быстрый гайд по деплою

## Правильный подход: Git + Docker (рекомендуется)

### Шаг 1: Подготовка сервера
```bash
# Подключиться по SSH
ssh user@your-server-ip

# Установить Docker и Docker Compose (если еще не установлены)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker

# Установить Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Шаг 2: Клонирование проекта
```bash
# Создать директорию (замените на название вашего проекта)
mkdir -p /opt/public-boost
cd /opt/public-boost

# Клонировать репозиторий (РЕКОМЕНДУЕТСЯ)
git clone <your-repo-url> .

# Или загрузить файлы через scp (если нет git)
# scp -r /local/path/to/project/* user@server:/opt/public-boost/
```

### Шаг 3: Настройка .env
```bash
# Скопировать пример
cp .env.example .env

# Отредактировать .env
nano .env

# Обязательно изменить:
# - SECRET_KEY (сгенерировать: openssl rand -hex 32)
# - ENCRYPTION_KEY (сгенерировать: python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
# - POSTGRES_PASSWORD (сильный пароль)
# - REDIS_PASSWORD (сильный пароль)
# - DEBUG=false
# - CORS_ORIGINS (ваш домен)
```

### Шаг 4: Запуск (Docker установит ВСЕ зависимости автоматически!)
```bash
# Docker автоматически:
# 1. Скачает базовые образы (Python, Node, PostgreSQL, Redis, Nginx)
# 2. Установит все зависимости Python в контейнер
# 3. Установит все зависимости Node.js в контейнер
# 4. Соберет образы

# Сборка и запуск
docker-compose -f docker-compose.prod.yml up -d --build

# Проверка статуса
docker-compose -f docker-compose.prod.yml ps

# Просмотр логов
docker-compose -f docker-compose.prod.yml logs -f
```

### Шаг 5: Применение миграций БД
```bash
# Вход в контейнер backend
docker-compose -f docker-compose.prod.yml exec backend bash

# Применение миграций
alembic upgrade head

# Выход
exit
```

---

## ❌ НЕ РЕКОМЕНДУЕТСЯ: Перенос зависимостей по SSH

### Почему НЕ стоит:
1. **Конфликты версий** - локальные версии могут не подойти для сервера
2. **Зависимости системы** - могут быть разные версии Python, Node.js
3. **Загрязнение системы** - установка пакетов напрямую в систему
4. **Сложность обновления** - нужно вручную обновлять каждую зависимость
5. **Проблемы с правами** - могут быть конфликты прав доступа

### Если все же нужно (не рекомендуется):
```bash
# НЕ ДЕЛАЙТЕ ТАК:
# scp -r backend/venv user@server:/opt/trusted-recommender/backend/
# scp -r frontend/node_modules user@server:/opt/trusted-recommender/frontend/
```

---

## Обновление приложения

```bash
# Остановить контейнеры
docker-compose -f docker-compose.prod.yml down

# Обновить код
git pull
# или загрузить новые файлы через scp

# Пересобрать образы (Docker установит зависимости заново)
docker-compose -f docker-compose.prod.yml build

# Применить миграции (если есть)
docker-compose -f docker-compose.prod.yml run --rm backend alembic upgrade head

# Запустить
docker-compose -f docker-compose.prod.yml up -d
```

---

## Что Docker делает автоматически:

### Backend:
- ✅ Скачивает Python 3.11 образ
- ✅ Устанавливает все зависимости из `requirements.txt`
- ✅ Копирует код приложения
- ✅ Создает необходимые директории

### Frontend:
- ✅ Скачивает Node.js образ
- ✅ Устанавливает зависимости из `package.json`
- ✅ Собирает приложение (`npm run build`)
- ✅ Настраивает Nginx для раздачи статики

### База данных:
- ✅ Скачивает PostgreSQL 16 образ
- ✅ Создает базу данных
- ✅ Настраивает пользователя и пароль

### Redis:
- ✅ Скачивает Redis 7 образ
- ✅ Настраивает пароль
- ✅ Создает volumes для данных

---

## Преимущества Docker подхода:

1. **Изоляция** - все зависимости в контейнерах, система чистая
2. **Воспроизводимость** - одинаково работает везде
3. **Безопасность** - нет конфликтов с системными пакетами
4. **Простота** - одна команда `docker-compose up` запускает все
5. **Масштабируемость** - легко добавить больше инстансов
6. **Откат** - легко вернуться к предыдущей версии

---

## Итого:

✅ **ПРАВИЛЬНО**: Git clone → Docker build → Docker up
❌ **НЕПРАВИЛЬНО**: Перенос зависимостей по SSH

**Docker установит ВСЕ зависимости автоматически при сборке образов!**
