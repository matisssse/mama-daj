# Быстрый старт для Article Service

## Необходимые шаги для запуска

### 1. Запустите сервисы

Сервис теперь использует **локальную LLM через Ollama** вместо OpenAI API!

```bash
docker compose up -d
```

### 2. Загрузите модель для Ollama

После запуска контейнеров, загрузите нужную модель:

```bash
# Рекомендуемая модель (легкая и быстрая, ~2GB)
docker compose exec ollama ollama pull llama3.2

# Альтернативные модели:
# docker compose exec ollama ollama pull mistral      # 7B модель, качественнее
# docker compose exec ollama ollama pull qwen2.5      # 7B модель, отлично для текста
# docker compose exec ollama ollama pull llama3.1     # 8B модель, очень качественная
```

**Важно:** Первая загрузка модели может занять несколько минут в зависимости от скорости интернета.

Проверьте установленные модели:
```bash
docker compose exec ollama ollama list
```

### 3. Настройте переменные окружения

Скопируйте `.env.example` в `.env`:
```bash
cp .env.example .env
```

Отредактируйте `.env` и установите:

```env
# Модель Ollama (должна быть загружена)
OLLAMA_MODEL=llama3.2

# Пароли MySQL (измените на свои!)
MYSQL_ROOT_PASSWORD=ваш_надежный_пароль
MYSQL_PASSWORD=ваш_надежный_пароль
WORDPRESS_DB_PASSWORD=ваш_надежный_пароль
```

### 4. Настройте список сайтов

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

Проверьте статус Ollama:
```bash
docker compose logs ollama
```

## Выбор модели Ollama

### Рекомендуемые модели для рерайта статей:

**Легкие модели (для слабых серверов):**
- `llama3.2` (3B) - Быстрая и легкая, хорошо для коротких текстов
- `phi3` (3.8B) - Компактная и эффективная

**Средние модели (оптимальный баланс):**
- `mistral` (7B) - Отличное качество текста
- `qwen2.5` (7B) - Превосходно для работы с текстом
- `gemma2` (9B) - Высокое качество от Google

**Мощные модели (для мощных серверов):**
- `llama3.1` (8B) - Очень качественная генерация
- `mixtral` (47B) - Профессиональное качество (требует много RAM)

### Смена модели:

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

## Системные требования

### Минимальные:
- CPU: 4 ядра
- RAM: 8GB (для моделей 3-7B)
- Диск: 10GB свободного места

### Рекомендуемые:
- CPU: 8 ядер
- RAM: 16GB (для моделей 7-13B)
- GPU: Опционально, значительно ускоряет генерацию
- Диск: 20GB свободного места

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

**Требования:**
- NVIDIA GPU
- Установленный nvidia-docker2

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

⚠️ **Локальная LLM требует ресурсов** - убедитесь, что у вас достаточно RAM

⚠️ **Первая генерация медленнее** - модель загружается в память

⚠️ **Соблюдайте авторские права** - используйте только разрешенные источники

⚠️ **SEO требует времени** - не публикуйте слишком много статей сразу

## Преимущества локальной LLM

✅ **Бесплатно** - не нужно платить за API
✅ **Приватность** - данные не покидают ваш сервер
✅ **Без лимитов** - нет ограничений на количество запросов
✅ **Офлайн работа** - не требуется интернет после загрузки модели
✅ **Настраиваемость** - можете выбрать любую модель

## Устранение неполадок

### Ollama не запускается
```bash
# Проверьте статус
docker compose ps ollama

# Посмотрите логи
docker compose logs ollama

# Перезапустите
docker compose restart ollama
```

### Модель не найдена
```bash
# Проверьте установленные модели
docker compose exec ollama ollama list

# Загрузите нужную модель
docker compose exec ollama ollama pull llama3.2
```

### Медленная генерация
- Используйте более легкую модель (llama3.2 вместо mistral)
- Добавьте больше RAM
- Настройте GPU поддержку

### Ошибка "Out of memory"
- Используйте более легкую модель
- Увеличьте RAM сервера
- Закройте другие приложения

## Полезные команды

```bash
# Просмотр всех сервисов
docker compose ps

# Логи
docker compose logs -f article-service
docker compose logs -f ollama

# Управление моделями Ollama
docker compose exec ollama ollama list              # Список моделей
docker compose exec ollama ollama pull llama3.2     # Загрузить модель
docker compose exec ollama ollama rm llama3.2       # Удалить модель

# Перезапуск
docker compose restart article-service
docker compose restart ollama

# Пересборка после изменений
docker compose up -d --build article-service

# Остановка всех сервисов
docker compose down
```

## Мониторинг производительности

```bash
# Использование ресурсов
docker stats

# Только для Ollama
docker stats mama-daj-ollama
```

## Дополнительная информация

Полная документация: [article-service/README.md](article-service/README.md)
