# Быстрый старт для Article Service

## Необходимые шаги для запуска

### 1. Получите OpenAI API ключ

1. Перейдите на https://platform.openai.com/
2. Создайте аккаунт или войдите
3. Перейдите в раздел API Keys: https://platform.openai.com/api-keys
4. Создайте новый секретный ключ
5. Скопируйте его (он больше не будет показан!)

### 2. Настройте переменные окружения

Скопируйте `.env.example` в `.env`:
```bash
cp .env.example .env
```

Отредактируйте `.env` и установите:

```env
# OpenAI (обязательно!)
OPENAI_API_KEY=sk-...ваш_ключ_здесь...

# Пароли MySQL (измените на свои!)
MYSQL_ROOT_PASSWORD=ваш_надежный_пароль
MYSQL_PASSWORD=ваш_надежный_пароль
WORDPRESS_DB_PASSWORD=ваш_надежный_пароль
```

### 3. Настройте список сайтов

Отредактируйте `article-service/config/sites.json`:

```json
{
  "sites": [
    {
      "name": "Ваш источник 1",
      "url": "https://example.com/blog",
      "max_articles": 3
    }
  ]
}
```

### 4. Запустите сервисы

```bash
docker compose up -d
```

### 5. Настройте WordPress

1. Откройте http://localhost:8080
2. Завершите установку WordPress
3. Войдите в админку
4. Перейдите в **Пользователи → Профиль**
5. Прокрутите вниз до **Application Passwords**
6. Создайте новый пароль (например, "Article Service")
7. Скопируйте сгенерированный пароль

### 6. Обновите настройки WordPress API

Добавьте в `.env`:

```env
WORDPRESS_API_USER=ваш_username_wp
WORDPRESS_API_PASSWORD=скопированный_application_password
```

Перезапустите article-service:
```bash
docker compose restart article-service
```

### 7. Проверьте работу

Просмотрите логи:
```bash
docker compose logs -f article-service
```

## Тестовый запуск

Для тестирования установите в `.env`:

```env
RUN_ON_STARTUP=true
WORDPRESS_POST_STATUS=draft
```

Перезапустите сервис:
```bash
docker compose restart article-service
```

Сервис сразу начнет обработку статей и создаст черновики в WordPress.

## Важные замечания

⚠️ **Используйте черновики** (`WORDPRESS_POST_STATUS=draft`) для тестирования!

⚠️ **OpenAI API платный** - проверьте ваш баланс на https://platform.openai.com/account/billing

⚠️ **Соблюдайте авторские права** - используйте только разрешенные источники

⚠️ **SEO требует времени** - не публикуйте слишком много статей сразу

## Полезные команды

```bash
# Просмотр всех сервисов
docker compose ps

# Логи
docker compose logs -f article-service

# Перезапуск
docker compose restart article-service

# Пересборка после изменений
docker compose up -d --build article-service

# Остановка всех сервисов
docker compose down
```

## Дополнительная информация

Полная документация: [article-service/README.md](article-service/README.md)
