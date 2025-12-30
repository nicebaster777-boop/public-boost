# Настройка отправки email для восстановления пароля

## Варианты настройки SMTP

### 1. Gmail (простой вариант для начала)

**Настройки:**
```env
SMTP_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password  # НЕ обычный пароль, а App Password!
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=Public Boost
```

**Как получить App Password для Gmail:**
1. Включите двухфакторную аутентификацию в Google аккаунте
2. Перейдите: https://myaccount.google.com/apppasswords
3. Создайте новый App Password для "Mail"
4. Используйте этот пароль в `SMTP_PASSWORD`

**Ограничения:**
- Максимум 500 писем в день для бесплатного аккаунта
- Письма могут попадать в спам

---

### 2. SendGrid (рекомендуется для продакшена)

**Регистрация:**
1. Зарегистрируйтесь на https://sendgrid.com
2. Верифицируйте домен или используйте Single Sender Verification
3. Создайте API Key

**Настройки:**
```env
SMTP_ENABLED=true
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USER=apikey
SMTP_PASSWORD=your-sendgrid-api-key
SMTP_FROM_EMAIL=noreply@yourdomain.com
SMTP_FROM_NAME=Public Boost
```

**Преимущества:**
- 100 писем в день бесплатно
- Хорошая доставляемость
- Статистика отправок
- API для более продвинутого использования

---

### 3. Mailgun (хорошо для транзакционных писем)

**Регистрация:**
1. Зарегистрируйтесь на https://www.mailgun.com
2. Верифицируйте домен
3. Получите SMTP credentials

**Настройки:**
```env
SMTP_ENABLED=true
SMTP_HOST=smtp.mailgun.org
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USER=postmaster@yourdomain.mailgun.org
SMTP_PASSWORD=your-mailgun-password
SMTP_FROM_EMAIL=noreply@yourdomain.com
SMTP_FROM_NAME=Public Boost
```

**Преимущества:**
- 5000 писем в месяц бесплатно
- Отличная доставляемость
- API для webhooks и событий

---

### 4. Собственный SMTP сервер

Если у вас есть свой почтовый сервер:

```env
SMTP_ENABLED=true
SMTP_HOST=mail.yourdomain.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USER=your-email@yourdomain.com
SMTP_PASSWORD=your-password
SMTP_FROM_EMAIL=noreply@yourdomain.com
SMTP_FROM_NAME=Public Boost
```

---

## Рекомендации

### Для разработки (MVP):
- Используйте Gmail с App Password
- Или оставьте `SMTP_ENABLED=false` и просто логируйте письма

### Для продакшена:
- **Рекомендуется:** SendGrid или Mailgun
- Обязательно верифицируйте домен
- Настройте SPF, DKIM, DMARC записи в DNS
- Используйте поддомен для отправки (например, `noreply@mail.yourdomain.com`)

---

## Пример адреса отправителя

Рекомендуемый формат:
- **Email:** `noreply@yourdomain.com` или `support@yourdomain.com`
- **Имя:** `Public Boost` или `Public Boost Support`

**Важно:** 
- Используйте домен, который вы контролируете
- Настройте обратные DNS записи
- Это улучшит доставляемость и снизит вероятность попадания в спам

---

## Безопасность

1. **Никогда не коммитьте** `.env` файл с реальными паролями
2. Используйте **App Passwords** вместо обычных паролей
3. Храните секреты в переменных окружения на сервере
4. Используйте разные учетные данные для dev/prod

---

## Проверка работы

После настройки SMTP, при запросе восстановления пароля:
1. Письмо должно быть отправлено на указанный email
2. Проверьте папку "Спам", если письмо не пришло
3. Проверьте логи бэкенда на наличие ошибок SMTP
