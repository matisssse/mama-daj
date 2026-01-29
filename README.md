# mama-daj

WordPress сайт с MySQL в Docker Compose и автоматическим сервисом парсинга и публикации статей.

## Компоненты

- **WordPress** - CMS для сайта
- **MySQL** - база данных
- **Article Service** - автоматический парсинг, рерайт и публикация статей

## Требования

- Docker
- Docker Compose

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

Для запуска WordPress сайта выполните:

```bash
docker compose up -d
```

Сайт будет доступен по адресу: http://localhost:8080

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

## Article Service - Автоматический парсинг и публикация статей

Проект включает в себя сервис для автоматического парсинга статей с сайтов, их рерайта с использованием AI и публикации на WordPress.

### Возможности

- 🤖 Автоматический парсинг статей с различных сайтов
- ✍️ AI-рерайт для создания уникального контента (OpenAI)
- 📝 Автоматическая публикация на WordPress
- ⏰ Публикация по расписанию
- 🎯 SEO-оптимизация
- 🖼️ Автоматическая загрузка изображений

### Быстрый старт

1. Добавьте сайты для парсинга в `article-service/config/sites.json`:
```json
{
  "sites": [
    {
      "name": "Название сайта",
      "url": "https://example.com/blog",
      "max_articles": 5
    }
  ]
}
```

2. Настройте переменные окружения в `.env`:
```env
# OpenAI API (получите на https://platform.openai.com/)
OPENAI_API_KEY=your_openai_api_key

# WordPress API (создайте Application Password в профиле WordPress)
WORDPRESS_API_USER=your_username
WORDPRESS_API_PASSWORD=your_application_password

# Расписание (время запуска парсинга)
SCHEDULE_TIME=03:00
```

3. Запустите все сервисы:
```bash
docker compose up -d
```

### Подробная документация

Полная документация по настройке и использованию Article Service находится в [article-service/README.md](article-service/README.md).

**Важные темы:**
- Настройка OpenAI API
- Создание Application Password в WordPress
- Конфигурация сайтов для парсинга
- SEO-оптимизация и лучшие практики
- Устранение неполадок

## Дополнительная информация

### Порты
- WordPress: http://localhost:8080
- MySQL: порт 3306 (доступен только внутри Docker сети)

### Volumes
- `db_data` - данные MySQL
- `wordpress_data` - файлы WordPress
- `article_service_data` - данные сервиса парсинга статей

### Логи
```bash
# Все сервисы
docker compose logs -f

# Только article-service
docker compose logs -f article-service

# Только WordPress
docker compose logs -f wordpress
```