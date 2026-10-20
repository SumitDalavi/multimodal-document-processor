> **NOTE:** This repository is an archival lab or partial prototype. It is not actively maintained and should not be used as a reference for production-grade deployments or performance benchmarks.

# multimodal-document-processor

[![CI Pipeline](https://github.com/SumitDalavi/multimodal-document-processor/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/SumitDalavi/multimodal-document-processor/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/SumitDalavi/multimodal-document-processor?color=0969da&label=release&logo=github)](https://github.com/SumitDalavi/multimodal-document-processor/releases)
[![Release Workflow](https://github.com/SumitDalavi/multimodal-document-processor/actions/workflows/release.yml/badge.svg)](https://github.com/SumitDalavi/multimodal-document-processor/actions/workflows/release.yml)
[![GHCR Container](https://img.shields.io/badge/ghcr.io-v0.2.0-blue?logo=docker&logoColor=white)](https://github.com/SumitDalavi/multimodal-document-processor/pkgs/container/multimodal-document-processor)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org)
[![SBOM](https://img.shields.io/badge/SBOM-SPDX%202.3-blueviolet?logo=spdx)](https://github.com/SumitDalavi/multimodal-document-processor/releases/tag/v0.2.0)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

> **Maturity:** Functional Prototype
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

## 🚀 Progressive Credential Loading & Execution Tiers

This project implements **Progressive Credential Loading (PCL)**, allowing it to run immediately out-of-the-box without external dependencies while seamlessly upgrading as credentials are provided.

### Tier 1: Zero-Config Mock Mode (Default)
Ideal for CI, testing, and rapid local evaluation.
- **Execution:** Run with default configuration (`cp .env.example .env`). Zero API keys, databases, or cloud credentials required.
- **Fallback Behavior:** In-memory caches, deterministic offline heuristics, mock vector embeddings, and local mock storage are automatically used.
- **Health Verification:** Endpoints report `{"mode": "mock"}` for unconfigured dependencies.

### Tier 2: Local Development with Live Services
Connect specific external services while keeping others mocked.
- **Execution:** Provide credentials in `.env` for the services you want active (e.g., `OPENAI_API_KEY, TESSERACT_CMD, MAX_FILE_SIZE_MB`).
- **Progressive Upgrade:** The runtime inspects environment variables on boot and dynamically promotes only configured modules to live mode.
- **Safe Fallback:** Any missing credentials automatically remain on mock fallbacks with no crashes or missing service errors.

### Tier 3: Production Hardened
Enterprise deployment with production-grade backends, security scans, and container distributions.
- **OCI Container Image:** Pre-built, multi-arch image on GitHub Container Registry:
  ```bash
  docker pull ghcr.io/sumitdalavi/multimodal-document-processor:v0.2.0
  ```
- **Production Orchestration:** Mount secrets via Kubernetes Secrets or cloud secret managers with atomic config reload support.
- **Release Verification:** Checksums and SPDX SBOM available on [GitHub Releases](https://github.com/SumitDalavi/multimodal-document-processor/releases).

## 📚 Documentation

- [Architecture](docs/ARCHITECTURE.md) — System diagram and component details
- [Runbook](docs/runbook.md) — Setup, commands, and expected outputs
- [Decisions](docs/decisions.md) — ADRs for citation mapping
- [Changelog](docs/changelog.md) — Change history

## Release & Security Verification

The project includes an automated DevSecOps release pipeline (`.github/workflows/release.yml`) triggered on semantic version tags (`v*.*.*`).

Each release automatically:
1. Executes test suite gates.
2. Builds the container image.
3. Performs vulnerability scanning via Trivy.
4. Generates an SPDX SBOM (`sbom.spdx.json`) using Anchore Syft.
5. Publishes a GitHub Release with attached SBOM.

### Verifying the Release
```bash
# Verify release via GitHub CLI
gh release view v0.1.0 --repo SumitDalavi/multimodal-document-processor

# Download and inspect SBOM
gh release download v0.1.0 --repo SumitDalavi/multimodal-document-processor --pattern "sbom.spdx.json"
cat sbom.spdx.json | jq .
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Runbook](docs/runbook.md)
- [Decisions](docs/decisions.md)
- [Changelog](docs/changelog.md)
