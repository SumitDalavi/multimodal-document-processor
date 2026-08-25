from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import uuid

app = FastAPI(title="Multimodal Document Processor")

class AnalysisResponse(BaseModel):
    id: str
    filename: str
    file_size: int
    content_type: str
    ocr_text_preview: str
    status: str

def mock_ocr_process(filename: str) -> str:
    """Mock OCR processing for demonstration."""
    if filename.endswith('.pdf'):
        return "Simulated extracted text from PDF document."
    elif filename.endswith('.png') or filename.endswith('.jpg'):
        return "Simulated text extracted from Image."
    return "Unsupported format for OCR."

@app.post("/api/v1/process", response_model=AnalysisResponse)
async def process_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")
        
    content = await file.read()
    file_size = len(content)
    
    ocr_result = mock_ocr_process(file.filename)
    
    return AnalysisResponse(
        id=str(uuid.uuid4()),
        filename=file.filename,
        file_size=file_size,
        content_type=file.content_type,
        ocr_text_preview=ocr_result,
        status="processed"
    )

@app.get("/health")
def health_check():
    return {"status": "healthy"}
