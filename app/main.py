import shutil
import os

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from typing import List

from app.checker import check_invoice, _is_pdf
from app.database import save_result
from app.highlighter import highlight_pdf


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

app.mount("/static", StaticFiles(directory="frontend"), name="static")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Раздаём папку uploads как статику — чтобы фронтенд мог скачать PDF по ссылке.
# Без этого GET /uploads/highlighted_... вернёт 404.
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.post("/check")
async def check(
        file: UploadFile = File(...),
        expected_number: str = Form(...),
        expected_date: str = Form(...)
):
    file_path = f"{UPLOAD_DIR}/{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = check_invoice(file_path, expected_number, expected_date)
    save_result(result)

    # Подсветка возможна только для PDF.
    # Для CSV/Excel pdf_url не добавляем — фронтенд покажет только JSON-результат.
    if _is_pdf(file_path):
        highlighted_filename = f"highlighted_{file.filename}"
        output_path = f"{UPLOAD_DIR}/{highlighted_filename}"

        highlight_result = highlight_pdf(
            input_path=file_path,
            output_path=output_path,
            number=expected_number,
            date=expected_date
        )

        result["pdf_url"]             = f"/uploads/{highlighted_filename}"
        result["number_found_in_pdf"] = highlight_result["number_found"]
        result["date_found_in_pdf"]   = highlight_result["date_found"]

    return result


@app.post("/check-batch")
async def check_batch(
        files: List[UploadFile] = File(...),
        expected_number: str = Form(...),
        expected_date: str = Form(...)
):
    results = []

    for file in files:
        file_path = f"{UPLOAD_DIR}/{file.filename}"

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        result = check_invoice(file_path, expected_number, expected_date)
        save_result(result)

        if _is_pdf(file_path):
            highlighted_filename = f"highlighted_{file.filename}"
            output_path = f"{UPLOAD_DIR}/{highlighted_filename}"

            highlight_result = highlight_pdf(
                input_path=file_path,
                output_path=output_path,
                number=expected_number,
                date=expected_date
            )

            result["pdf_url"]             = f"/uploads/{highlighted_filename}"
            result["number_found_in_pdf"] = highlight_result["number_found"]
            result["date_found_in_pdf"]   = highlight_result["date_found"]

        results.append(result)

    return {"total": len(results), "results": results}
