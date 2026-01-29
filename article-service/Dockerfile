FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем requirements и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt

# Копируем код приложения
COPY *.py .

# Создаем директории для данных и логов
RUN mkdir -p /app/data /var/log

# Запускаем приложение
CMD ["python", "-u", "main.py"]
