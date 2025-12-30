# Deployment Guide

## Подготовка к деплою на VPS

### Требования
- VPS с Ubuntu 20.04+ или Debian 11+
- Минимум 2GB RAM, 2 CPU cores
- 20GB+ свободного места
- Docker и Docker Compose установлены
- Доменное имя (опционально, но рекомендуется)

---

## Шаг 1: Подготовка сервера

### Установка Docker и Docker Compose

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Добавление пользователя в группу docker
sudo usermod -aG docker $USER
newgrp docker

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Проверка установки
docker --version
docker-compose --version
```

---

## Шаг 2: Клонирование проекта

```bash
# Создание директории
mkdir -p /opt/trusted-recommender
cd /opt/trusted-recommender

# Клонирование репозитория (или загрузка файлов)
# git clone <your-repo-url> .

# Или загрузка через scp/sftp
```

---

## Шаг 3: Настройка переменных окружения

```bash
# Копирование примера
cp .env.example .env

# Редактирование .env файла
nano .env
```

**Критически важно изменить:**
- `SECRET_KEY` - сгенерировать случайную строку (минимум 32 символа)
- `ENCRYPTION_KEY` - сгенерировать 32-символьную строку для Fernet
- `POSTGRES_PASSWORD` - сильный пароль для БД
- `REDIS_PASSWORD` - сильный пароль для Redis
- `CORS_ORIGINS` - добавить ваш домен
- `DEBUG=false` - обязательно для production

**Генерация ключей:**
```bash
# SECRET_KEY (32+ символов)
openssl rand -hex 32

# ENCRYPTION_KEY (32 символа для Fernet)
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

---

## Шаг 4: Настройка SSL (опционально, но рекомендуется)

### Использование Let's Encrypt (Certbot)

```bash
# Установка Certbot
sudo apt install certbot python3-certbot-nginx -y

# Получение сертификата (замените yourdomain.com)
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Сертификаты будут в:
# /etc/letsencrypt/live/yourdomain.com/fullchain.pem
# /etc/letsencrypt/live/yourdomain.com/privkey.pem

# Копирование в nginx/ssl
sudo mkdir -p nginx/ssl
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/
sudo chown $USER:$USER nginx/ssl/*
```

**Обновление nginx.conf:**
Раскомментируйте секцию HTTPS в `nginx/nginx.conf` и укажите правильные пути к сертификатам.

---

## Шаг 5: Запуск приложения

### Первый запуск

```bash
# Сборка образов
docker-compose -f docker-compose.prod.yml build

# Запуск контейнеров
docker-compose -f docker-compose.prod.yml up -d

# Проверка статуса
docker-compose -f docker-compose.prod.yml ps

# Просмотр логов
docker-compose -f docker-compose.prod.yml logs -f
```

### Применение миграций БД

```bash
# Вход в контейнер backend
docker-compose -f docker-compose.prod.yml exec backend bash

# Применение миграций
alembic upgrade head

# Выход
exit
```

---

## Шаг 6: Настройка firewall

```bash
# Установка UFW (если не установлен)
sudo apt install ufw -y

# Разрешение SSH
sudo ufw allow 22/tcp

# Разрешение HTTP и HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Включение firewall
sudo ufw enable

# Проверка статуса
sudo ufw status
```

---

## Шаг 7: Настройка автоматического обновления SSL (если используется)

```bash
# Создание cron задачи для обновления сертификатов
sudo crontab -e

# Добавить строку (обновление каждый месяц):
0 0 1 * * certbot renew --quiet && docker-compose -f /opt/trusted-recommender/docker-compose.prod.yml restart nginx
```

---

## Шаг 8: Мониторинг и логи

### Просмотр логов

```bash
# Все сервисы
docker-compose -f docker-compose.prod.yml logs -f

# Конкретный сервис
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f nginx
```

### Проверка здоровья

```bash
# Проверка API
curl http://localhost/api/v1/health

# Проверка БД
docker-compose -f docker-compose.prod.yml exec db pg_isready -U trusted_user
```

---

## Обновление приложения

```bash
# Остановка контейнеров
docker-compose -f docker-compose.prod.yml down

# Обновление кода (git pull или загрузка новых файлов)
# git pull

# Пересборка образов
docker-compose -f docker-compose.prod.yml build

# Применение новых миграций (если есть)
docker-compose -f docker-compose.prod.yml run --rm backend alembic upgrade head

# Запуск
docker-compose -f docker-compose.prod.yml up -d
```

---

## Резервное копирование

### Бэкап БД

```bash
# Создание бэкапа
docker-compose -f docker-compose.prod.yml exec db pg_dump -U trusted_user trusted_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Восстановление из бэкапа
cat backup_YYYYMMDD_HHMMSS.sql | docker-compose -f docker-compose.prod.yml exec -T db psql -U trusted_user trusted_db
```

### Автоматический бэкап (cron)

```bash
# Добавить в crontab
0 2 * * * docker-compose -f /opt/trusted-recommender/docker-compose.prod.yml exec -T db pg_dump -U trusted_user trusted_db > /opt/backups/trusted_db_$(date +\%Y\%m\%d).sql
```

---

## Безопасность

### Рекомендации:
1. ✅ Использовать сильные пароли в .env
2. ✅ Включить HTTPS (SSL)
3. ✅ Настроить firewall (UFW)
4. ✅ Регулярно обновлять систему и Docker
5. ✅ Не хранить .env в git
6. ✅ Ограничить доступ к БД (только внутренняя сеть)
7. ✅ Настроить rate limiting в nginx
8. ✅ Регулярно делать бэкапы

---

## Troubleshooting

### Проблема: Контейнеры не запускаются
```bash
# Проверка логов
docker-compose -f docker-compose.prod.yml logs

# Проверка конфигурации
docker-compose -f docker-compose.prod.yml config
```

### Проблема: БД недоступна
```bash
# Проверка статуса
docker-compose -f docker-compose.prod.yml ps db

# Проверка подключения
docker-compose -f docker-compose.prod.yml exec db pg_isready -U trusted_user
```

### Проблема: Nginx не работает
```bash
# Проверка конфигурации
docker-compose -f docker-compose.prod.yml exec nginx nginx -t

# Перезапуск
docker-compose -f docker-compose.prod.yml restart nginx
```

---

## Полезные команды

```bash
# Остановка всех сервисов
docker-compose -f docker-compose.prod.yml down

# Остановка с удалением volumes (ОСТОРОЖНО!)
docker-compose -f docker-compose.prod.yml down -v

# Перезапуск конкретного сервиса
docker-compose -f docker-compose.prod.yml restart backend

# Просмотр использования ресурсов
docker stats

# Очистка неиспользуемых образов
docker system prune -a
```
