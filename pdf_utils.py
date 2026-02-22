import pdfplumber
import unicodedata
from pdf2image import convert_from_bytes
import pytesseract
from io import BytesIO


def extract_text_from_pdf(file_bytes: bytes) -> str:

    text = ""

    # 1️⃣ Önce normal extraction dene
    with pdfplumber.open(BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"

    # 2️⃣ Eğer boşsa OCR yap
    if not text.strip():
        images = convert_from_bytes(file_bytes)
        for image in images:
            ocr_text = pytesseract.image_to_string(image)
            text += ocr_text + "\n"

    # 3️⃣ Unicode normalize
    text = unicodedata.normalize("NFKD", text)

    return text