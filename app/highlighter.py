import fitz  # PyMuPDF

MONTHS_RU = {
    "01": "января",  "02": "февраля", "03": "марта",
    "04": "апреля",  "05": "мая",     "06": "июня",
    "07": "июля",    "08": "августа", "09": "сентября",
    "10": "октября", "11": "ноября",  "12": "декабря"
}


def get_number_variants(number: str) -> list[str]:
    """
    Варианты написания номера.
    search_for ищет точное совпадение строки — перебираем все форматы.
    """
    variants = [number]

    if "/" in number:
        parts = number.split("/")
        variants += [
            f"{parts[0]} / {parts[1]}",
            f"{parts[0]}/ {parts[1]}",
            f"{parts[0]} /{parts[1]}",
            f"№ {number}",
            f"№{number}",
            f"№ {parts[0]} / {parts[1]}",
        ]

    return variants


def get_date_variants(date: str) -> list[str]:
    """
    Варианты написания даты — включая русский формат.
    Нужно потому что дата в шапке счёт-фактуры часто написана
    по-русски ("03 марта 2026"), а нормализованная дата цифровая.
    """
    variants = [date]

    if "." in date:
        parts = date.split(".")
        if len(parts) == 3:
            d, m, y = parts

            variants += [
                f"{d}/{m}/{y}",
                f"{y}-{m}-{d}",
            ]

            month_ru = MONTHS_RU.get(m)
            if month_ru:
                day_short = str(int(d))  # "03" → "3"
                variants += [
                    f"{d} {month_ru} {y}",
                    f"{day_short} {month_ru} {y}",
                    f"от {d} {month_ru} {y}",
                    f"от {day_short} {month_ru} {y}",
                ]

    return variants


def _hits_overlap(h1: tuple, h2: tuple, threshold: float = 10.0) -> bool:
    """
    Проверяет что два попадания (page_index, rect) указывают на одно место.
    threshold=10 — чуть шире чем раньше, т.к. разные варианты строки
    (с "от " и без) дают rect с немного разным x0.
    """
    i1, r1 = h1
    i2, r2 = h2
    return (
            i1 == i2 and
            abs(r1.x0 - r2.x0) < threshold and
            abs(r1.y0 - r2.y0) < threshold
    )


def _deduplicate_hits(hits: list[tuple]) -> list[tuple]:
    """Убирает дублирующие попадания на одно и то же место."""
    unique = []
    for h in hits:
        if not any(_hits_overlap(h, u) for u in unique):
            unique.append(h)
    return unique


def highlight_pdf(
        input_path: str,
        output_path: str,
        number: str,
        date: str
) -> dict:
    """
    Рисует РОВНО ОДНУ рамку для номера и РОВНО ОДНУ для даты —
    самые верхние вхождения во всём документе.

    Ключевое изменение: раньше на каждой странице рисовали
    по одному rect, теперь собираем ВСЕ совпадения по всем страницам,
    сортируем по (номер_страницы, y0) и берём глобально первое.

    Это решает проблему когда штамп внизу той же страницы тоже
    содержит дату — min() выбирает шапку, штамп остаётся без рамки.
    """
    doc = fitz.open(input_path)

    number_found = False
    date_found   = False

    # --- Собираем все попадания для номера ---
    number_hits = []
    for page_index, page in enumerate(doc):
        for variant in get_number_variants(number):
            for rect in page.search_for(variant, quads=False):
                number_hits.append((page_index, rect))

    number_hits = _deduplicate_hits(number_hits)

    if number_hits:
        # Самое верхнее во всём документе
        page_index, rect = min(number_hits, key=lambda x: (x[0], x[1].y0))
        doc[page_index].draw_rect(rect, color=(0, 0, 1), width=2)  # синий
        number_found = True

    # --- Собираем все попадания для даты ---
    date_hits = []
    for page_index, page in enumerate(doc):
        for variant in get_date_variants(date):
            for rect in page.search_for(variant, quads=False):
                date_hits.append((page_index, rect))

    date_hits = _deduplicate_hits(date_hits)

    if date_hits:
        # Самое верхнее во всём документе
        page_index, rect = min(date_hits, key=lambda x: (x[0], x[1].y0))
        doc[page_index].draw_rect(rect, color=(0, 0.7, 0), width=2)  # зелёный
        date_found = True

    doc.save(output_path)
    doc.close()

    return {
        "number_found": number_found,
        "date_found":   date_found
    }
