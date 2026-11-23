# AGENTS.md

Project facts, stack, and verification commands: [`.ai/project.yaml`](./.ai/project.yaml).
Architecture Decision Records: [`docs/adr/0001-dialect-routing-and-fikiri-reasoning-gateway.md`](./docs/adr/0001-dialect-routing-and-fikiri-reasoning-gateway.md).

## Engineering Rules

1. **Architectural Honesty:** Always distinguish between the **implemented and verified orchestration gateway, dialect router, `<fikiri>` reasoning pipeline, and `Swahili-Bench` evaluation harness** (`lughallm/src/`, `frontend/`) and the **QLoRA training & GGUF export scaffold** (`lughallm/src/training/`, `lughallm/checkpoints/`). Never claim pre-trained model weights are bundled in git or that scripted `run_mock_simulation()` outputs are live neural benchmark scores.
2. **Offline & Stdlib Portability:** Core unit tests (`lughallm/tests/`) and `Swahili-Bench` must pass in clean Python 3.10–3.12 environments without requiring a GPU or live external API keys.
3. **Zero Artifacts or Secrets in Git:** Never commit `.env` files, `*.sqlite3` ledger files, `build/`, or `*.egg-info/` directories.
4. **Definition of Done:** Run the commands under `verification:` in `.ai/project.yaml`; if any gate is `null` or cannot run, report `NOT VERIFIED` with the reason. Never push, force-push, or modify remotes without explicit approval.
