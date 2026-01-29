FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем requirements и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY *.py .

# Создаем директории для данных и логов
RUN mkdir -p /app/data /var/log

# Запускаем приложение
CMD ["python", "-u", "main.py"]
