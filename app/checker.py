from app.extractor import extract_text_from_pdf
from app.parser import extract_invoice_number, extract_invoice_date


def check_invoice(file_path: str, expected_number: str, expected_date: str) -> dict:
    file_name = file_path.split("/")[-1]

    try:
        text = extract_text_from_pdf(file_path)
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
    found_date = extract_invoice_date(text)

    if found_number is None or found_date is None:
        status = "not_found"
    else:
        number_match = found_number == expected_number
        date_match = found_date == expected_date

        if number_match and date_match:
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
        "number_match": found_number == expected_number if found_number else False,
        "date_match": found_date == expected_date if found_date else False,
        "status": status
    }
