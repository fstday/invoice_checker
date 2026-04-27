from app.parser import (
    normalize_number,
    normalize_date,
    extract_invoice_number,
    extract_invoice_date
)


# --- normalize_number ---

def test_normalize_number_slash():
    assert normalize_number("№ 1349/1277") == "1349/1277"

def test_normalize_number_spaces():
    assert normalize_number("№ 1349 / 1277") == "1349/1277"

def test_normalize_number_no_slash():
    assert normalize_number("№ 1349 1277") == "1349/1277"

def test_normalize_number_letters():
    assert normalize_number("№ SL000000448") == "SL000000448"


# --- normalize_date ---

def test_normalize_date_dots():
    assert normalize_date("23.07.2025") == "23.07.2025"

def test_normalize_date_iso():
    assert normalize_date("2025-07-23") == "23.07.2025"

def test_normalize_date_slashes():
    assert normalize_date("23/07/2025") == "23.07.2025"


# --- extract_invoice_number ---

def test_extract_number_found():
    text = "Счет-фактура № 1349/1277 от 23.07.2025"
    assert extract_invoice_number(text) == "1349/1277"

def test_extract_number_not_found():
    text = "Просто какой-то текст без номера"
    assert extract_invoice_number(text) is None


# --- extract_invoice_date ---

def test_extract_date_found():
    text = "Счет-фактура № 1349/1277 от 23.07.2025"
    assert extract_invoice_date(text) == "23.07.2025"

def test_extract_date_not_found():
    text = "Просто какой-то текст"
    assert extract_invoice_date(text) is None
