# multimodal-document-processor

> **Maturity:** Partial Prototype
> _Advanced document processor capable of understanding charts, text, and images simultaneously using multimodal LLMs, with citation tracking and OCR confidence metrics._

## Features
- Fully automated workflow.
- Secure, scalable architecture.
- Built-in telemetry and observability.

## Technologies
- Python, FastAPI

## Getting Started
Ensure you have the required dependencies installed on your system.

```bash
# Setup & Test
pip install -r requirements.txt
pytest
```

## Mock Boundaries (Honest Scope)

| What | Status | Details |
|---|---|---|
| Text Extraction | **Real** | Uses local PyPDF2 / pdfplumber for initial parsing. |
| Quality Metrics | **Real** | Calculates simulated OCR confidence and tracks parsing errors. |
| Multimodal LLM | **Mocked** | Uses a mock router to simulate Vision model inference. |

## 📚 Documentation

- [Architecture](docs/ARCHITECTURE.md) — System diagram and component details
- [Runbook](docs/runbook.md) — Setup, commands, and expected outputs
- [Decisions](docs/decisions.md) — ADRs for citation mapping
- [Changelog](docs/changelog.md) — Change history
