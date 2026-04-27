import fitz


def find_coords_in_words(words: list, search: str) -> list:
    """
    Ищет точное совпадение search среди слов с координатами.
    Проверяет одно слово и пары соседних слов.
    """
    # Нормализуем поисковый запрос
    clean = search.strip().lower().replace(" ", "")
    found = []

    for i, word in enumerate(words):
        # Точное совпадение одного слова
        word_clean = word["text"].strip().lower().replace(" ", "")
        if word_clean == clean:
            found.append(word)
            continue

        # Точное совпадение двух соседних слов
        if i + 1 < len(words) and words[i]["page"] == words[i+1]["page"]:
            combined = (word["text"] + words[i+1]["text"]).strip().lower().replace(" ", "")
            if combined == clean:
                merged = {
                    "x0":          word["x0"],
                    "y0":          min(word["y0"], words[i+1]["y0"]),
                    "x1":          words[i+1]["x1"],
                    "y1":          max(word["y1"], words[i+1]["y1"]),
                    "page":        word["page"],
                    "page_height": word["page_height"]
                }
                found.append(merged)

    return found


def highlight_pdf(input_path: str, output_path: str, words: list, number: str, date: str):
    """
    Рисует прямоугольники вокруг номера (синий) и даты (зелёный).
    words — список слов с координатами из extract_words_with_coords()
    """
    number_coords = find_coords_in_words(words, number)
    date_coords   = find_coords_in_words(words, date)

    doc = fitz.open(input_path)

    for coord in number_coords:
        page = doc[coord["page"]]
        h = coord["page_height"]
        rect = fitz.Rect(coord["x0"], h - coord["y1"], coord["x1"], h - coord["y0"])
        page.draw_rect(rect, color=(0, 0, 1), width=2)  # синий

    for coord in date_coords:
        page = doc[coord["page"]]
        h = coord["page_height"]
        rect = fitz.Rect(coord["x0"], h - coord["y1"], coord["x1"], h - coord["y0"])
        page.draw_rect(rect, color=(0, 0.7, 0), width=2)  # зелёный

    doc.save(output_path)
    doc.close()

    return {
        "number_found": len(number_coords) > 0,
        "date_found":   len(date_coords) > 0
    }
