# mama-daj

WordPress сайт с MySQL в Docker Compose. Nginx работает на хосте в качестве reverse proxy с HTTPS.

## Требования

- Docker
- Docker Compose
- nginx (установлен на хосте)
- SSL сертификаты Let's Encrypt (расположены в `/etc/letsencrypt/live/mama-daj.ru/`)

## Настройка

### Первичная установка

1. Скопируйте файл с примером переменных окружения:
```bash
cp .env.example .env
```

2. **ВАЖНО: Измените пароли в файле .env перед запуском в продакшене!** Отредактируйте файл `.env` и установите безопасные пароли:
```bash
nano .env
```

## Запуск

### Настройка nginx на хосте

1. Скопируйте конфигурацию nginx на хост:
```bash
sudo cp nginx/nginx.conf /etc/nginx/sites-available/mama-daj.ru
sudo ln -s /etc/nginx/sites-available/mama-daj.ru /etc/nginx/sites-enabled/
```

2. Убедитесь, что SSL сертификаты установлены в `/etc/letsencrypt/live/mama-daj.ru/`:
   - `fullchain.pem`
   - `privkey.pem`

3. Проверьте конфигурацию nginx:
```bash
sudo nginx -t
```

4. Перезапустите nginx:
```bash
sudo systemctl restart nginx
```

### Запуск Docker контейнеров

Для запуска WordPress и MySQL выполните:

```bash
docker compose up -d
```

WordPress контейнер будет доступен на `localhost:8080`, а nginx на хосте проксирует запросы к нему.

Сайт будет доступен по адресу:
- https://mama-daj.ru (основной домен)
- http://mama-daj.ru (автоматически перенаправляется на HTTPS)
- https://www.mama-daj.ru (автоматически перенаправляется на https://mama-daj.ru)
- http://www.mama-daj.ru (автоматически перенаправляется на https://mama-daj.ru)

### Архитектура

Система состоит из следующих компонентов:
- **nginx** (на хосте) - reverse proxy с SSL терминацией (порты 80, 443)
- **wordpress** (Docker) - WordPress приложение (порт 8080 → 80)
- **db** (Docker) - MySQL база данных (внутренний порт 3306)

## Остановка

Для остановки сервисов:

```bash
docker compose down
```

## Персистентность данных

База данных MySQL и файлы WordPress сохраняются в Docker volumes:
- `db_data` - данные MySQL базы
- `wordpress_data` - файлы WordPress

Данные сохраняются даже после перезапуска контейнеров.

## Удаление данных

Для полного удаления всех данных:

```bash
docker compose down -v
```

## Конфигурация

### Переменные окружения

Настройки хранятся в файле `.env` (создается из `.env.example`):

**Настройки MySQL:**
- `MYSQL_ROOT_PASSWORD` - пароль root пользователя MySQL
- `MYSQL_DATABASE` - имя базы данных
- `MYSQL_USER` - имя пользователя базы данных
- `MYSQL_PASSWORD` - пароль пользователя базы данных

**Настройки WordPress:**
- `WORDPRESS_DB_HOST` - хост базы данных (обычно `db:3306`)
- `WORDPRESS_DB_NAME` - имя базы данных WordPress
- `WORDPRESS_DB_USER` - имя пользователя базы данных
- `WORDPRESS_DB_PASSWORD` - пароль пользователя базы данных

### Безопасность

⚠️ **ВНИМАНИЕ:** Файл `.env` содержит конфиденциальные данные и не должен коммититься в Git. Он уже добавлен в `.gitignore`.

Перед развертыванием в продакшене обязательно измените все пароли по умолчанию на надежные!