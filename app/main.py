from fastapi import FastAPI, UploadFile, File, HTTPException
from io import BytesIO
import pdfplumber
import unicodedata

from .schemas import LabRequest, LabResponse
from .parser import parse_lab_text
from .language_detector import detect_language
from .risk_engine import calculate_risk
from .ai_service import generate_explanation

app = FastAPI(title="Health AI API")


def _normalize_text(t: str) -> str:
    return unicodedata.normalize("NFKC", t or "")


@app.post("/analyze-text", response_model=LabResponse)
async def analyze_text(request: LabRequest):
    if not request.raw_text.strip():
        raise HTTPException(status_code=400, detail="Empty lab text")

    normalized_text = _normalize_text(request.raw_text)
    detected_language = detect_language(normalized_text)

    parameters = parse_lab_text(normalized_text)
    if not parameters:
        raise HTTPException(status_code=400, detail="No lab parameters detected")

    risk = calculate_risk(parameters)
    explanation = generate_explanation(parameters, risk, detected_language)

    return {
        "detected_language": detected_language,
        "parsed_parameters": parameters,
        "risk": risk,
        "analysis": explanation,
    }


@app.post("/analyze-pdf", response_model=LabResponse)
async def analyze_pdf(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Empty PDF file")

    text = ""
    try:
        with pdfplumber.open(BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
    except Exception:
        raise HTTPException(status_code=500, detail="PDF processing error")

    if not text.strip():
        raise HTTPException(status_code=400, detail="No readable text found in PDF")

    normalized_text = _normalize_text(text)
    detected_language = detect_language(normalized_text)

    parameters = parse_lab_text(normalized_text)
    if not parameters:
        raise HTTPException(status_code=400, detail="No lab parameters detected")

    risk = calculate_risk(parameters)
    explanation = generate_explanation(parameters, risk, detected_language)

    return {
        "detected_language": detected_language,
        "parsed_parameters": parameters,
        "risk": risk,
        "analysis": explanation,
    }
