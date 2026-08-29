# Runbook — multimodal-document-processor
> Last updated: 2026-08-29

## Quick Start
```bash
pip install -r requirements.txt
uvicorn src.main:app --reload
```
API runs on `http://localhost:8000`.

## Run Tests
```bash
pytest
bash tests/e2e/test_document_processing.sh
```

## Environment Variables
| Variable | Default | Purpose |
|---|---|---|
| MIN_OCR_CONFIDENCE | `80` | Threshold for routing to failure queue |
