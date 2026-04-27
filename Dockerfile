# 1. Какой язык и какая версия
FROM python:3.10-slim

# 2. Рабочая папка внутри контейнера
WORKDIR /app

# 3. Сначала только зависимости (для кэша)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Теперь весь код
COPY . .

# 5. Создаем нужные папки
RUN mkdir -p uploads

# 6. Документируем порт
EXPOSE 8000

# 7. Команда запуска
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
