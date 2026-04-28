import re

MONTHS_RU = {
    "января": "01", "февраля": "02", "марта": "03",
    "апреля": "04", "мая": "05", "июня": "06",
    "июля": "07", "августа": "08", "сентября": "09",
    "октября": "10", "ноября": "11", "декабря": "12"
}


def normalize_number(raw: str) -> str:
    result = raw.strip().lstrip("№").strip()
    result = re.sub(r'\s*/\s*', '/', result)
    result = re.sub(r'(\d+)\s+(\d+)', r'\1/\2', result)
    return result.strip()


def normalize_date(raw: str) -> str:
    m = re.match(r'^(\d{2})\.(\d{2})\.(\d{4})$', raw.strip())
    if m:
        return raw.strip()

    m = re.match(r'^(\d{4})-(\d{2})-(\d{2})$', raw.strip())
    if m:
        return f"{m.group(3)}.{m.group(2)}.{m.group(1)}"

    m = re.match(r'^(\d{2})/(\d{2})/(\d{4})$', raw.strip())
    if m:
        return f"{m.group(1)}.{m.group(2)}.{m.group(3)}"

    return raw.strip()


def extract_invoice_number(text: str) -> str | None:
    # ФИШ: добавлен паттерн без обязательного знака "№".
    # В оригинале все паттерны требовали "№" — если в PDF написано
    # "Счет-фактура 1349/1277 от ..." без знака №, функция возвращала None.
    # Новый паттерн ловит номер после слова "счет-фактур" (в любом падеже).
    # Паттерны отсортированы от самого строгого к самому мягкому —
    # это важно, иначе мягкий паттерн может захватить лишнее.
    patterns = [
        r'№\s+(\d+\s*/\s*\d+)',         # № 1349/1277  или  № 1349 / 1277
        r'№\s+(\d+\s+\d+)',             # № 1349 1277
        r'счет-фактур[ауе]\s+(?:№\s*)?(\d+[/\s]\d+)',  # без обязательного №
        r'счет-фактур[ауе]\s+(?:№\s*)?([\w\d]+)',       # буквенно-цифровой (SL000000448)
        r'№\s+([\w\d]+)',               # любой символьный номер после №
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            return normalize_number(matches[0])

    return None


def extract_invoice_date(text: str) -> str | None:
    # Приоритет 1: дата РЯДОМ с номером — "№ 1349/1277 от 23.07.2025"
    # Это самый надёжный паттерн: контекст однозначно указывает на дату счёт-фактуры,
    # а не на дату поставки, дату платежа или другие даты внутри документа.
    pattern = r'№\s+[\w\d/\s]+\s+от\s+(\d{2}[./]\d{2}[./]\d{4})'
    m = re.search(pattern, text)
    if m:
        return normalize_date(m.group(1))

    # Приоритет 2: русский формат — "от 28 февраля 2026"
    pattern_ru = r'от\s+(\d{1,2})\s+(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)\s+(\d{4})'
    m = re.search(pattern_ru, text)
    if m:
        day   = m.group(1).zfill(2)
        month = MONTHS_RU[m.group(2)]
        year  = m.group(3)
        return f"{day}.{month}.{year}"

    # Приоритет 3 (запасной): первая цифровая дата в документе.
    # ИЗВЕСТНОЕ ОГРАНИЧЕНИЕ: в счёт-фактуре может быть несколько дат
    # (дата поставки, дата платежа и т.д.). Берём первую — в реальных
    # узбекских/российских счёт-фактурах дата документа идёт первой.
    # В production-версии здесь стоит использовать LLM или брать дату
    # из конкретной позиции шаблона (координаты на странице).
    pattern2 = r'\b(\d{2}[./]\d{2}[./]\d{4})\b'
    matches = re.findall(pattern2, text)
    if matches:
        return normalize_date(matches[0])

    return None
