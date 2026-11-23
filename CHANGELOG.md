# Changelog

All notable changes to **LughaLLM** (`creova-gif/swahili-llm`) are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-11-23

### Added
- Root `SECURITY.md`, `.env.example`, `.ai/project.yaml`, `AGENTS.md`, and `docs/adr/0001-dialect-routing-and-fikiri-reasoning-gateway.md`.
- Least-privilege `permissions: contents: read` configuration in `.github/workflows/ci.yml`.
- Pinned Python dependencies in `requirements.txt` and `lughallm/requirements.txt` plus automated `.github/dependabot.yml` configuration.
- `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `LICENSE` (MIT), and GitHub issue/PR templates.

### Changed
- Rewrote `README.md` with an explicit subsystem implementation matrix distinguishing the verified orchestration gateway, dialect router, `<fikiri>` reasoning pipeline, React playground, and `Swahili-Bench` harness from the QLoRA fine-tuning scaffold (`lughallm/src/training/`, `lughallm/checkpoints/`).

## [0.1.0] - 2026-11-03

### Added
- Multi-dialect Swahili & Sheng orchestrator (`lughallm/src/orchestrator/agent.py`) supporting `kiswahili_sanifu`, `sheng_nairobi`, `kingwana_drc`, `swahili_uganda`, and `coastal_swahili`.
- `<fikiri>` System-2 chain-of-thought reasoning pipeline and cultural etiquette (*Adabu na Heshima*) post-processor (`lughallm/src/reasoning/thinker.py`).
- OpenAI-compatible FastAPI server (`lughallm/src/api/main.py`) with SSE streaming, multi-turn thread memory, offline codebase search RAG, and SQLite multi-currency token ledger (`TZS`, `KES`, `UGX`, `CDF`, `RWF`, `BIF`).
- 2G USSD (`*149*00#`) session state machine (`lughallm/src/channels/ussd.py`) and WhatsApp `.ogg` voice note processor (`lughallm/src/audio/voice.py`).
- `Swahili-Bench` evaluation harness and 40-item curated dataset (`lughallm/src/benchmark/`).
- React + TypeScript + Tailwind CSS developer playground (`frontend/`) and portable QLoRA training/export pipeline (`lughallm/src/training/`).
