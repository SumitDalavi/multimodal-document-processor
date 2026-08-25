from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI()

class Document(BaseModel):
    id: str
    text: str = ""
    image_url: str = ""

def process_multimodal(doc: Document) -> dict:
    # Mocking a multimodal processing logic
    # In reality this would pass image and text to an LLM like GPT-4V or Gemini Pro Vision
    summary = f"Processed document {doc.id} with length {len(doc.text)}"
    if doc.image_url:
        summary += " and an image."
    
    return {
        "summary": summary,
        "entities": ["mock_entity_1", "mock_entity_2"],
        "sentiment": "neutral"
    }

@app.post("/process")
async def process_document(doc: Document):
    if not doc.text and not doc.image_url:
        raise HTTPException(status_code=400, detail="Must provide text or image_url")
    return process_multimodal(doc)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
