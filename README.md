> **NOTE:** This repository is an archival lab or partial prototype. It is not actively maintained and should not be used as a reference for production-grade deployments or performance benchmarks.


# multimodal-document-processor

[![Release](https://img.shields.io/github/v/release/SumitDalavi/multimodal-document-processor?color=blue&logo=github)](https://github.com/SumitDalavi/multimodal-document-processor/releases)
[![Release Workflow](https://github.com/SumitDalavi/multimodal-document-processor/actions/workflows/release.yml/badge.svg)](https://github.com/SumitDalavi/multimodal-document-processor/actions/workflows/release.yml)
[![SBOM](https://img.shields.io/badge/SBOM-SPDX%20JSON-blueviolet?logo=spdx)](https://github.com/SumitDalavi/multimodal-document-processor/releases)

[![Release](https://img.shields.io/github/v/release/SumitDalavi/multimodal-document-processor?color=blue&logo=github)](https://github.com/SumitDalavi/multimodal-document-processor/releases)
[![SBOM](https://img.shields.io/badge/SBOM-SPDX%20JSON-blueviolet?logo=spdx)](https://github.com/SumitDalavi/multimodal-document-processor/releases)

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