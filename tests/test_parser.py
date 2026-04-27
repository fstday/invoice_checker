from app.extractor import extract_text_from_pdf
from app.parser import extract_invoice_number, extract_invoice_date

text = extract_text_from_pdf("../files/25_02_2026_200446111304164766_Счет_фактура_1349_1277_от_23_07_2025.pdf")

print("Номер:", extract_invoice_number(text))
print("Дата:", extract_invoice_date(text))
