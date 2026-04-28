# 🧾 Invoice Checker

Инструмент для автоматической проверки счёт-фактур. Принимает PDF, CSV или Excel файл, извлекает номер и дату документа, сравнивает с ожидаемыми значениями и возвращает результат проверки. Для PDF дополнительно генерирует копию с визуальной подсветкой найденных фрагментов.

---

## Возможности

- Поддержка форматов: **PDF**, **CSV**, **Excel (xlsx, xls)**
- Извлечение номера и даты с учётом разных вариантов написания
- Пять статусов проверки: `matched`, `partial_match`, `not_matched`, `not_found`, `error`
- Визуальная подсветка найденного номера (синяя рамка) и даты (зелёная рамка) прямо в PDF
- Пакетная обработка нескольких файлов одновременно
- Веб-интерфейс — загрузка файлов и просмотр результата прямо в браузере
- Сохранение всех проверок в базу данных SQLite
- Docker-поддержка

---

## Структура проекта

```
invoice_checker/
├── app/
│   ├── checker.py      # Оркестратор: вызывает extractor и parser, выставляет статус
│   ├── database.py     # Сохранение результатов в SQLite через SQLAlchemy
│   ├── extractor.py    # Извлечение текста из PDF / CSV / Excel
│   ├── highlighter.py  # Рисует рамки в PDF через PyMuPDF
│   ├── main.py         # FastAPI: эндпоинты /check и /check-batch
│   └── parser.py       # Регулярки для извлечения номера и даты
├── frontend/
│   └── index.html      # Веб-интерфейс
├── tests/
│   └── test_checker.py # Unit-тесты
├── Dockerfile
├── requirements.txt
└── conftest.py
```

---

## Поддерживаемые форматы номера и даты

**Номер счёт-фактуры:**
```
1349/1277
№ 1349/1277
№ 1349 / 1277
№ 1349 1277
SL000000448
```

**Дата:**
```
23.07.2025
2025-07-23
23/07/2025
от 23 июля 2025
```

---

## Результат проверки

```json
{
  "file_name": "invoice.pdf",
  "expected_number": "1349/1277",
  "expected_date": "23.07.2025",
  "found_number": "1349/1277",
  "found_date": "23.07.2025",
  "number_match": true,
  "date_match": true,
  "status": "matched",
  "pdf_url": "/uploads/highlighted_invoice.pdf",
  "number_found_in_pdf": true,
  "date_found_in_pdf": true
}
```

| Статус | Описание |
|---|---|
| `matched` | Номер и дата совпали |
| `partial_match` | Совпало только одно из двух |
| `not_matched` | Найдены, но не совпали |
| `not_found` | Номер или дата не найдены в документе |
| `error` | Файл не удалось обработать |

---

## Запуск через Docker

```bash
# 1. Клонировать репозиторий
git clone https://github.com/fstday/invoice_checker.git
cd invoice_checker

# 2. Собрать образ
docker build -t invoice-checker .

# 3. Запустить контейнер
# Без сохранения данных между перезапусками:
docker run -p 8000:8000 invoice-checker

# С сохранением БД и загруженных файлов:
touch invoices.db
docker run -p 8000:8000 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/invoices.db:/app/invoices.db \
  invoice-checker
```

Открыть в браузере: [http://localhost:8000](http://localhost:8000)

---

## Запуск локально

```bash
# 1. Клонировать репозиторий
git clone https://github.com/fstday/invoice_checker.git
cd invoice_checker

# 2. Создать и активировать виртуальное окружение
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Запустить сервер
uvicorn app.main:app --reload
```

Открыть в браузере: [http://localhost:8000](http://localhost:8000)

---

## Запуск тестов

```bash
pytest
```

Тесты покрывают нормализацию номера и даты, извлечение из текста, все статусы проверки.

---

## API

### `POST /check`
Проверка одного файла.

| Поле | Тип | Описание |
|---|---|---|
| `file` | file | PDF, CSV или Excel |
| `expected_number` | string | Ожидаемый номер счёт-фактуры |
| `expected_date` | string | Ожидаемая дата в формате DD.MM.YYYY |

### `POST /check-batch`
Пакетная проверка нескольких файлов с одинаковыми ожидаемыми значениями.

| Поле | Тип | Описание |
|---|---|---|
| `files` | file[] | Список файлов |
| `expected_number` | string | Ожидаемый номер |
| `expected_date` | string | Ожидаемая дата |

Интерактивная документация API доступна по адресу [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Стек

- **FastAPI** — веб-фреймворк
- **pdfplumber** — извлечение текста из PDF
- **PyMuPDF (fitz)** — подсветка фрагментов в PDF
- **pandas + openpyxl** — обработка CSV и Excel
- **SQLAlchemy** — ORM для работы с базой данных
- **SQLite** — база данных
- **Docker** — контейнеризация