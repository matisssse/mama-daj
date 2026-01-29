# Article Service - Сервис парсинга и публикации статей

Этот сервис автоматически парсит статьи с указанных сайтов, делает их рерайт с использованием **локальной LLM через Ollama** и публикует на WordPress по расписанию.

## Возможности

- **Автоматический парсинг** статей с различных сайтов
- **AI-рерайт** с помощью локальной LLM (Ollama) для уникальности и SEO
- **Автоматическая публикация** на WordPress через REST API
- **Планировщик** для публикации по расписанию
- **Умная обработка**:
  - Извлечение заголовков, контента и изображений
  - Загрузка изображений в медиабиблиотеку WordPress
  - Отслеживание уже обработанных статей
  - Задержки между публикациями для естественности
- **SEO-оптимизация**:
  - Уникальный контент после рерайта
  - Естественное распределение публикаций
  - Оптимизированные заголовки

## Преимущества локальной LLM

🆓 **Бесплатно** - не нужно платить за OpenAI API  
🔒 **Приватность** - все данные остаются на вашем сервере  
♾️ **Без лимитов** - нет ограничений на количество запросов  
📴 **Офлайн работа** - не требуется интернет после загрузки модели  
⚙️ **Настраиваемость** - выбирайте любую модель из библиотеки Ollama

## Конфигурация

### 1. Настройка сайтов для парсинга

Отредактируйте файл `article-service/config/sites.json`:

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

Параметры:
- `name` - название сайта (для логов)
- `url` - URL страницы со списком статей (главная, блог, раздел новостей)
- `max_articles` - максимальное количество статей для парсинга за один раз

### 2. Переменные окружения

Настройте следующие переменные в файле `.env`:

#### Ollama (локальная LLM)
```env
OLLAMA_URL=http://ollama:11434
OLLAMA_MODEL=llama3.2
```

**Доступные модели:**
- `llama3.2` (3B) - Быстрая и легкая
- `mistral` (7B) - Отличное качество
- `qwen2.5` (7B) - Превосходно для текста
- `llama3.1` (8B) - Очень качественная

**Загрузка модели:**
```bash
docker compose exec ollama ollama pull llama3.2
```

Проверка установленных моделей:
```bash
docker compose exec ollama ollama list
```

#### WordPress API (обязательно)
```env
WORDPRESS_URL=http://wordpress
WORDPRESS_API_USER=your_username
WORDPRESS_API_PASSWORD=your_application_password
```

**Важно:** Для `WORDPRESS_API_PASSWORD` используйте Application Password, а не обычный пароль:
1. Войдите в WordPress админку
2. Перейдите в Пользователи → Профиль
3. Прокрутите вниз до раздела "Application Passwords"
4. Создайте новый Application Password
5. Используйте его в конфигурации

#### Настройки публикации
```env
WORDPRESS_POST_STATUS=draft          # draft или publish
WORDPRESS_DEFAULT_CATEGORY=1         # ID категории
PUBLISH_DELAY_SECONDS=300           # Задержка между постами (секунды)
```

#### Расписание
```env
SCHEDULE_TIME=03:00                  # Время запуска (HH:MM)
RUN_ON_STARTUP=false                 # Запуск при старте контейнера
```

### 3. Выбор модели для Ollama

#### Рекомендации по выбору:

**Для слабых серверов (4-8GB RAM):**
- `llama3.2` (3B) - ~2GB памяти
- `phi3` (3.8B) - ~2.5GB памяти

**Оптимальный баланс (8-16GB RAM):**
- `mistral` (7B) - ~4.5GB памяти, отличное качество
- `qwen2.5` (7B) - ~4.5GB памяти, превосходно для текста
- `gemma2` (9B) - ~5.5GB памяти

**Для мощных серверов (16GB+ RAM):**
- `llama3.1` (8B) - ~5GB памяти
- `mixtral` (47B) - ~26GB памяти (требует много ресурсов)

#### Смена модели:

1. Загрузите новую модель:
```bash
docker compose exec ollama ollama pull qwen2.5
```

2. Обновите `.env`:
```env
OLLAMA_MODEL=qwen2.5
```

3. Перезапустите сервис:
```bash
docker compose restart article-service
```

### 4. Активация WordPress REST API

Убедитесь, что WordPress REST API активен:

1. Перейдите в Настройки → Постоянные ссылки
2. Выберите любую структуру кроме "Простые"
3. Сохраните изменения

Проверьте доступность API:
```bash
curl http://localhost:8080/wp-json/wp/v2/posts
```

## Запуск

### Вместе с WordPress

Запустите все сервисы:
```bash
docker compose up -d
```

Просмотр логов article-service:
```bash
docker compose logs -f article-service
```

### Только article-service

Пересобрать и перезапустить только article-service:
```bash
docker compose up -d --build article-service
```

## Как это работает

1. **Планировщик** запускается по расписанию (настраивается через `SCHEDULE_TIME`)
2. **Парсер** обходит каждый сайт из списка и извлекает статьи
3. **Рерайтер** использует OpenAI API для создания уникального контента
4. **Публикатор** загружает изображения и публикует статью на WordPress
5. **Отслеживание** предотвращает повторную обработку одних и тех же статей
6. **Задержки** между публикациями делают процесс более естественным

## Безопасность и SEO

### SEO-оптимизация
- ✅ Полностью уникальный контент после рерайта
- ✅ Естественное распределение публикаций во времени
- ✅ Оптимизированные заголовки и мета-описания
- ✅ Задержки между публикациями (настраиваемые)

### Рекомендации
1. **Публикуйте в черновики** (`WORDPRESS_POST_STATUS=draft`) и проверяйте качество перед публикацией
2. **Используйте задержки** между публикациями (`PUBLISH_DELAY_SECONDS`) не менее 300 секунд
3. **Планируйте публикации** в ночное время (`SCHEDULE_TIME=03:00`)
4. **Не парсите слишком много** - лучше качество, чем количество (`max_articles: 3-5`)
5. **Проверяйте контент** - AI может допускать ошибки
6. **Используйте легальные источники** - убедитесь, что у вас есть права на использование контента

### Этические соображения
⚠️ **Важно:** Этот инструмент предназначен для легального использования:
- Используйте только открытые источники, разрешающие переиспользование
- Соблюдайте авторские права и лицензии
- Добавляйте ссылки на источники (установите `ADD_SOURCE_LINK=true`)
- Проверяйте и редактируйте контент перед публикацией

## Мониторинг и отладка

### Просмотр логов
```bash
# Все логи сервиса
docker compose logs article-service

# Следить за логами в реальном времени
docker compose logs -f article-service

# Последние 100 строк
docker compose logs --tail=100 article-service
```

### Проверка статуса
```bash
# Статус контейнера
docker compose ps article-service

# Войти в контейнер
docker compose exec article-service /bin/bash
```

### Ручной запуск для тестирования

Временно измените `.env`:
```env
RUN_ON_STARTUP=true
```

Затем перезапустите:
```bash
docker compose restart article-service
docker compose logs -f article-service
```

## Структура данных

Сервис сохраняет данные в Docker volume `article_service_data`:
- `/app/data/processed_articles.json` - список обработанных статей

## Устранение неполадок

### Проблема: Ollama недоступен
```bash
# Проверьте статус
docker compose ps ollama

# Посмотрите логи
docker compose logs ollama

# Перезапустите
docker compose restart ollama
```

### Проблема: Модель не найдена
```bash
# Проверьте установленные модели
docker compose exec ollama ollama list

# Загрузите нужную модель
docker compose exec ollama ollama pull llama3.2
```

### Проблема: Медленная генерация текста
**Причины и решения:**
- **Модель слишком большая** → Используйте более легкую модель (llama3.2 вместо mistral)
- **Недостаточно RAM** → Добавьте больше памяти или используйте модель меньшего размера
- **Нет GPU** → Настройте GPU поддержку в docker-compose.yml
- **Первый запрос** → Первая генерация всегда медленнее (модель загружается в память)

**Оптимизация:**
1. Используйте GPU если доступно
2. Выбирайте модели 3-7B для лучшей производительности
3. Убедитесь, что у сервера достаточно RAM
4. Закройте другие приложения, потребляющие память

### Проблема: Out of memory (не хватает памяти)
```bash
# Проверьте использование памяти
docker stats mama-daj-ollama

# Решения:
# 1. Используйте более легкую модель
docker compose exec ollama ollama pull llama3.2

# 2. Удалите неиспользуемые модели
docker compose exec ollama ollama list
docker compose exec ollama ollama rm <model_name>
```

### Проблема: Плохое качество рерайта
**Решения:**
1. Используйте более качественную модель (mistral, qwen2.5)
2. Проверьте, что модель правильно загружена
3. Увеличьте температуру генерации (в rewriter.py)

### Проблема: API ключ OpenAI не работает
Этот вопрос больше не актуален - сервис использует локальную LLM через Ollama!

### Проблема: Не могу опубликовать на WordPress
- Убедитесь, что используете Application Password, а не обычный пароль
- Проверьте доступность REST API: `curl http://localhost:8080/wp-json/wp/v2/posts`
- Проверьте, что пользователь имеет права на публикацию

### Проблема: Не парсятся статьи
- Проверьте структуру сайта - некоторые сайты могут использовать нестандартную разметку
- Добавьте больше логирования для отладки
- Проверьте, не блокирует ли сайт парсинг (User-Agent, rate limiting)

### Проблема: Сервис не запускается по расписанию
- Проверьте формат `SCHEDULE_TIME` (должен быть HH:MM)
- Посмотрите логи на ошибки
- Убедитесь, что контейнер запущен: `docker compose ps`

## Системные требования

### Минимальные требования:
- **CPU:** 4 ядра
- **RAM:** 8GB (для моделей 3-7B)
- **Диск:** 10GB свободного места
- **Интернет:** Только для загрузки моделей

### Рекомендуемые требования:
- **CPU:** 8 ядер
- **RAM:** 16GB (для моделей 7-13B)
- **GPU:** Опционально, значительно ускоряет генерацию
- **Диск:** 20GB свободного места

### GPU поддержка (опционально):

Для использования GPU раскомментируйте секцию в `docker-compose.yml`:

```yaml
  ollama:
    # ...
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

**Требования для GPU:**
- NVIDIA GPU с поддержкой CUDA
- Установленный nvidia-docker2
- Драйверы NVIDIA

**Установка nvidia-docker (Ubuntu):**
```bash
# Добавить репозиторий
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

# Установить
sudo apt-get update
sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```

## Мониторинг производительности

### Использование ресурсов:
```bash
# Все контейнеры
docker stats

# Только Ollama
docker stats mama-daj-ollama

# Проверка доступной памяти на хосте
free -h
```

### Логи для отладки:
```bash
# Логи article-service
docker compose logs -f article-service

# Логи Ollama
docker compose logs -f ollama

# Последние ошибки
docker compose logs --tail=50 article-service | grep ERROR
```

## Разработка

### Локальное тестирование без Docker

```bash
cd article-service
pip install -r requirements.txt

# Установите переменные окружения
export OPENAI_API_KEY="your_key"
export WORDPRESS_URL="http://localhost:8080"
# ... другие переменные

python main.py
```

### Тестирование отдельных компонентов

Создайте тестовый скрипт:
```python
from scraper import ArticleScraper
from rewriter import ArticleRewriter
from publisher import WordPressPublisher

# Тест парсера
scraper = ArticleScraper()
articles = scraper.scrape_site("https://example.com", max_articles=1)
print(articles)

# Тест рерайтера
rewriter = ArticleRewriter()
rewritten = rewriter.rewrite(articles[0])
print(rewritten)

# Тест публикатора
publisher = WordPressPublisher()
publisher.test_connection()
```

## Лицензия

Используйте ответственно и в соответствии с законодательством вашей страны.
