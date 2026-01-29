# Article Service - Сервис парсинга и публикации статей

Этот сервис автоматически парсит статьи с указанных сайтов, делает их рерайт с использованием AI и публикует на WordPress по расписанию.

## Возможности

- **Автоматический парсинг** статей с различных сайтов
- **AI-рерайт** контента для уникальности и SEO-оптимизации (OpenAI API)
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

#### OpenAI API (обязательно)
```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
```

Получите API ключ на https://platform.openai.com/api-keys

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

### 3. Активация WordPress REST API

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

### Проблема: API ключ OpenAI не работает
- Проверьте баланс на https://platform.openai.com/account/billing
- Убедитесь, что ключ правильно скопирован в `.env`
- Проверьте лимиты API

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
