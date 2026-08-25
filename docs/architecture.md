# Architecture: Multi-Modal Document Processor

## System Diagram
The following Mermaid.js sequence diagram maps the core workflow and interactions:

```mermaid
sequenceDiagram
PDF->>Router: Native Text or Scan?
Router->>Tesseract: OCR
Router->>EasyOCR: OCR
Tesseract->>Merge: Ensemble
Merge->>LLM: Extract Pydantic Schema
LLM->>Validator: Enforce rules
Validator-->>HumanQueue: Low confidence
```

## Component Breakdown
- **Core Technology**: Python, Tesseract, EasyOCR, Pydantic
- **Design Paradigm**: Emphasizes high availability, fault tolerance, and security.
