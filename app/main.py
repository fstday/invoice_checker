import shutil
import os

from fastapi.responses import FileResponse
from app.highlighter import highlight_pdf
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.checker import check_invoice
from app.database import save_result
from typing import List


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
        results.append(result)

    return {"total": len(results), "results": results}


@app.post("/check-and-highlight")
async def check_and_highlight(
        file: UploadFile = File(...),
        expected_number: str = Form(...),
        expected_date: str = Form(...)
):
    file_path = f"{UPLOAD_DIR}/{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = check_invoice(file_path, expected_number, expected_date)
    save_result(result)

    # Достаём слова с координатами — один раз
    from app.extractor import extract_words_with_coords
    words = extract_words_with_coords(file_path)

    output_path = f"{UPLOAD_DIR}/highlighted_{file.filename}"
    highlight_pdf(file_path, output_path, words, expected_number, expected_date)

    return FileResponse(
        path=output_path,
        media_type="application/pdf",
        filename=f"highlighted_{file.filename}",
        headers={"X-Result": str(result["status"])}
    )
