"""FastAPI application for the Multimodal Document Processor."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from src.api.routes import router

app = FastAPI(
    title="Multimodal Document Processor",
    description=(
        "Extract text, tables, charts, and figures from PDFs and images "
        "using OCR + GPT-4o vision analysis."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health")
def health():
    import os
    return {
        "status": "ok",
        "ocr_available": _check_ocr(),
        "vision_available": bool(os.getenv("OPENAI_API_KEY")),
    }


def _check_ocr() -> bool:
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False


if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
