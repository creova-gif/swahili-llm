# Repository Engineering & AI Agent Contract

## 1. Decision Hierarchy
1. Verified repository code, lockfiles, and passing tests (`.ai/project.yaml`, `lughallm/tests/`)
2. Accepted ADRs in `docs/adr/` (`docs/adr/0001-dialect-routing-and-fikiri-reasoning-gateway.md`)
3. Repository-specific constraints in this file
4. Shared Engineering Governance Standard (`v1.0`)

## 2. Hard Invariants for All Agents (Antigravity, Devin, Claude, Codex, GStack)
- **Epistemic Honesty:** Never claim trained neural checkpoint weights (`.safetensors` / `.gguf`) are published in this repository until real fine-tuned weights and reproducible inference logs exist. Always separate real training/evaluation code (`finetune_lora.py`, `dataset.json`, `evaluator.py`, FastAPI gateway, SQLite ledger) from offline simulation stubs (`orchestrator/agent.py` fallback strings, `reasoning/thinker.py` static `<fikiri>` template, `audio/voice.py` sample transcript stub, and `swahili_bench.py::run_mock_simulation()`). Never present `run_mock_simulation()` `100.0% vs 0.0%` reference-echo scores as empirical LLM benchmark results.
- **No Unapproved Dependencies:** Do not add runtime packages without explicit task approval and lockfile updates.
- **No Harness or Asset Pollution:** Never commit `.claude/`, `.agents/`, `.cursor/`, `gstack/`, `attached_assets/`, `archive/`, `dist/`, `*.sqlite3`, or `.env` files.
- **Security Fail-Closed:** Never combine `allow_origins=["*"]` with `allow_credentials=True` (`lughallm/src/api/cors_policy.py`), never run containers as `root`, and never commit fallback production secrets.
- **PR & Verification Discipline:** Place imports at module top. Every change must pass automated tests locally and land via an atomic Conventional Commit pull request.
