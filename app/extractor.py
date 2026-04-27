import pdfplumber


def extract_text_from_pdf(file_path: str) -> str:
    """Возвращает весь текст из PDF одной строкой"""
    text_parts = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)


def extract_words_with_coords(file_path: str) -> list:
    """
    Возвращает список всех слов с координатами и номером страницы.
    Каждый элемент: {text, x0, y0, x1, y1, page, page_height}
    """
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
