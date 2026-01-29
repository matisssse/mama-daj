# mama-daj

WordPress сайт с MySQL в Docker Compose и автоматическим сервисом парсинга и публикации статей с использованием **локальной LLM**.

## Компоненты

- **WordPress** - CMS для сайта
- **MySQL** - база данных
- **Ollama** - локальный сервер для LLM моделей
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

Проект включает в себя сервис для автоматического парсинга статей с сайтов, их рерайта с использованием **локальной LLM (Ollama)** и публикации на WordPress.

### Возможности

- 🤖 Автоматический парсинг статей с различных сайтов
- ✍️ AI-рерайт с помощью **локальной LLM** (без OpenAI API!)
- 📝 Автоматическая публикация на WordPress
- ⏰ Публикация по расписанию
- 🎯 SEO-оптимизация
- 🖼️ Автоматическая загрузка изображений
- 🔒 **Приватность** - все данные остаются на вашем сервере
- 💰 **Бесплатно** - не нужно платить за API

### Быстрый старт

1. Запустите все сервисы:
```bash
docker compose up -d
```

2. Загрузите модель для Ollama:
```bash
docker compose exec ollama ollama pull llama3.2
```

3. Добавьте сайты для парсинга в `article-service/config/sites.json`:
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

4. Настройте переменные окружения в `.env`:
```env
# Модель Ollama
OLLAMA_MODEL=llama3.2

# WordPress API (создайте Application Password в профиле WordPress)
WORDPRESS_API_USER=your_username
WORDPRESS_API_PASSWORD=your_application_password

# Расписание (время запуска парсинга)
SCHEDULE_TIME=03:00
```

5. Перезапустите article-service:
```bash
docker compose restart article-service
```

### Подробная документация

Полная документация по настройке и использованию Article Service находится в [article-service/README.md](article-service/README.md).

**Важные темы:**
- Настройка локальной LLM (Ollama)
- Выбор и загрузка моделей
- Создание Application Password в WordPress
- Конфигурация сайтов для парсинга
- SEO-оптимизация и лучшие практики
- Устранение неполадок

## Преимущества локальной LLM

🆓 **Бесплатно** - не нужно платить за OpenAI API  
🔒 **Приватность** - данные не покидают ваш сервер  
♾️ **Без лимитов** - нет ограничений на количество запросов  
📴 **Офлайн работа** - не требуется интернет после загрузки модели  
⚙️ **Настраиваемость** - выбирайте любую модель из библиотеки Ollama

## Рекомендуемые модели

- **llama3.2** (3B) - Быстрая, легкая, идеальна для начала
- **mistral** (7B) - Отличное качество текста
- **qwen2.5** (7B) - Превосходно для работы с текстом
- **llama3.1** (8B) - Очень качественная генерация

Загрузка модели:
```bash
docker compose exec ollama ollama pull llama3.2
```

## Системные требования

**Минимальные:**
- CPU: 4 ядра
- RAM: 8GB (для моделей 3-7B)
- Диск: 10GB

**Рекомендуемые:**
- CPU: 8 ядер
- RAM: 16GB (для моделей 7-13B)
- GPU: Опционально (значительно ускоряет)
- Диск: 20GB

## Дополнительная информация

### Порты
- WordPress: http://localhost:8080
- MySQL: порт 3306 (доступен только внутри Docker сети)
- Ollama: http://localhost:11434 (API для управления моделями)

### Volumes
- `db_data` - данные MySQL
- `wordpress_data` - файлы WordPress
- `article_service_data` - данные сервиса парсинга статей
- `ollama_data` - модели и данные Ollama

### Логи
```bash
# Все сервисы
docker compose logs -f

# Только article-service
docker compose logs -f article-service

# Только WordPress
docker compose logs -f wordpress

# Только Ollama
docker compose logs -f ollama
```

### Управление моделями Ollama
```bash
# Список загруженных моделей
docker compose exec ollama ollama list

# Загрузить новую модель
docker compose exec ollama ollama pull mistral

# Удалить модель
docker compose exec ollama ollama rm mistral

# Информация о модели
docker compose exec ollama ollama show llama3.2
```