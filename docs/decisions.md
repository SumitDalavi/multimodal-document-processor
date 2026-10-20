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

## ADR-002: Progressive Credential Loading (PCL) Architecture
- **Context:** Production hardening required live backends (PostgreSQL, Redis, OpenAI, Anthropic), but removing mocks would break CI pipelines and create high developer onboarding friction.
- **Decision:** Implement Progressive Credential Loading. Keep in-memory and local mock heuristics as the default safe baseline, while wrapping external integrations in auto-promoting factory adapters triggered by environment variables.
- **Consequences:** 
  - *Pros:* 100% CI pass rate without requiring external secrets; zero setup friction for new contributors; progressive upgrade to production clusters.
  - *Cons:* Adds lightweight factory abstraction layers and runtime credential detection logic.
