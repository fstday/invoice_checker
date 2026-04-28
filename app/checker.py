from app.extractor import extract_text_from_pdf, extract_text_from_csv_excel
from app.parser import extract_invoice_number, extract_invoice_date


def _is_pdf(file_path: str) -> bool:
    return file_path.lower().endswith(".pdf")


def _is_table(file_path: str) -> bool:
    return file_path.lower().endswith((".csv", ".xlsx", ".xls"))


def check_invoice(file_path: str, expected_number: str, expected_date: str) -> dict:
    file_name = file_path.split("/")[-1]

    try:
        # Определяем тип файла и выбираем нужный экстрактор.
        # Логика проверки одна и та же — меняется только способ извлечения текста.
        if _is_pdf(file_path):
            text = extract_text_from_pdf(file_path)
        elif _is_table(file_path):
            text = extract_text_from_csv_excel(file_path)
        else:
            raise ValueError(f"Неподдерживаемый тип файла. Ожидается PDF, CSV или Excel.")
    except Exception as e:
        return {
            "file_name": file_name,
            "expected_number": expected_number,
            "expected_date": expected_date,
            "found_number": None,
            "found_date": None,
            "number_match": False,
            "date_match": False,
            "status": "error",
            "error": str(e)
        }

    found_number = extract_invoice_number(text)
    found_date   = extract_invoice_date(text)

    number_match = found_number == expected_number if found_number is not None else False
    date_match   = found_date   == expected_date   if found_date   is not None else False

    if found_number is None or found_date is None:
        status = "not_found"
    elif number_match and date_match:
        status = "matched"
    elif number_match or date_match:
        status = "partial_match"
    else:
        status = "not_matched"

    return {
        "file_name": file_name,
        "expected_number": expected_number,
        "expected_date": expected_date,
        "found_number": found_number,
        "found_date": found_date,
        "number_match": number_match,
        "date_match": date_match,
        "status": status
    }
