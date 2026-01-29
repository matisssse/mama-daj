# mama-daj

WordPress сайт с MySQL в Docker Compose.

## Требования

- Docker
- Docker Compose

## Запуск

Для запуска WordPress сайта выполните:

```bash
docker-compose up -d
```

Сайт будет доступен по адресу: http://localhost:8080

## Остановка

Для остановки сервисов:

```bash
docker-compose down
```

## Персистентность данных

База данных MySQL и файлы WordPress сохраняются в Docker volumes:
- `db_data` - данные MySQL базы
- `wordpress_data` - файлы WordPress

Данные сохраняются даже после перезапуска контейнеров.

## Удаление данных

Для полного удаления всех данных:

```bash
docker-compose down -v
```

## Конфигурация

Настройки базы данных можно изменить в файле `docker-compose.yml`:
- `MYSQL_ROOT_PASSWORD` - пароль root пользователя MySQL
- `MYSQL_DATABASE` - имя базы данных
- `MYSQL_USER` - имя пользователя базы данных
- `MYSQL_PASSWORD` - пароль пользователя базы данных