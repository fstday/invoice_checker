import pdfplumber
import pandas as pd


def extract_text_from_pdf(file_path: str) -> str:
    """Возвращает весь текст из PDF одной строкой"""
    text_parts = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)


def extract_text_from_csv_excel(file_path: str) -> str:
    """
    Извлекает текст из CSV или Excel для последующего парсинга регулярками.

    CSV — читаем как сырой текст: CSV и так является текстовым форматом,
    все значения включая "№ 1349/1277" и "от 23.07.2025" уже есть в файле
    как есть. Гонять через pandas нет смысла — он структурирует данные,
    а нам нужна просто строка.

    Excel — pandas читает все листы и склеивает значения ячеек в текст,
    потому что xlsx бинарный и как сырой текст не читается.
    """
    lower = file_path.lower()

    if lower.endswith(".csv"):
        for encoding in ("utf-8-sig", "utf-8", "cp1251"):
            try:
                with open(file_path, encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        raise ValueError(f"Не удалось прочитать CSV: {file_path}")

    elif lower.endswith((".xlsx", ".xls")):
        # Читаем все листы, склеиваем все ненулевые ячейки через пробел
        all_sheets = pd.read_excel(file_path, sheet_name=None, dtype=str)
        parts = []
        for df in all_sheets.values():
            parts.append(
                " ".join(
                    str(val)
                    for val in df.values.flatten()
                    if pd.notna(val) and str(val).strip()
                )
            )
        return " ".join(parts)

    else:
        raise ValueError(f"Неподдерживаемый формат: {file_path}")


def extract_words_with_coords(file_path: str) -> list:
    result = []
    with pdfplumber.open(file_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            words = page.extract_words()
            for word in words:
                result.append({
                    "text":        word["text"],
                    "x0":          word["x0"],
                    "y0":          word["top"],
                    "x1":          word["x1"],
                    "y1":          word["bottom"],
                    "page":        page_num,
                    "page_height": page.height
                })
    return result
