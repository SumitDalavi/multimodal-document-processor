# Decisions

## ADR-001: Failure Routing via OCR Confidence
**Date:** 2026-08-29  
**Status:** Accepted

**Context:**  
Poorly scanned PDFs result in hallucinated extraction by downstream models.

**Decision:**  
We implemented a Quality Engine that scores OCR confidence. If confidence is below 80%, the document is routed to a SQLite-backed "Failure Queue" for human review, entirely skipping the expensive multimodal LLM step.

**Consequences:**  
- ✅ Prevents garbage-in/garbage-out (GIGO) scenarios.
- ✅ Saves API costs on unreadable documents.
- ⚠️ Requires human-in-the-loop for the failure queue.
