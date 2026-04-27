from app.extractor import extract_text_from_pdf

text = extract_text_from_pdf("../files/25_02_2026_200446111304164766_Счет_фактура_1349_1277_от_23_07_2025.pdf")
print(text[:1000])
