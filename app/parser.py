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
    patterns = [
        r'№\s+(\d+\s*/\s*\d+)',
        r'№\s+(\d+\s+\d+)',
        r'№\s+([\w\d]+)',
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text)
        if matches:
            return normalize_number(matches[0])

    return None


def extract_invoice_date(text: str) -> str | None:
    # Ищем дату рядом с номером в цифровом формате
    pattern = r'№\s+[\w\d/\s]+\s+от\s+(\d{2}[./]\d{2}[./]\d{4})'
    m = re.search(pattern, text)
    if m:
        return normalize_date(m.group(1))

    # Ищем русскую дату — "от 28 февраля 2026"
    pattern_ru = r'от\s+(\d{1,2})\s+(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)\s+(\d{4})'
    m = re.search(pattern_ru, text)
    if m:
        day = m.group(1).zfill(2)   # "3" превращаем в "03"
        month = MONTHS_RU[m.group(2)]
        year = m.group(3)
        return f"{day}.{month}.{year}"

    # Запасной вариант — любая цифровая дата
    pattern2 = r'\b(\d{2}\.\d{2}\.\d{4})\b'
    matches = re.findall(pattern2, text)
    if matches:
        return normalize_date(matches[0])

    return None
