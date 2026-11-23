# `lughallm` Python Package Overview

See the root [**README.md**](../README.md) for full architecture diagrams, implementation status (real vs. simulated vs. planned), configuration variables, and security documentation.

> [!IMPORTANT]
> **Status:** `lughallm` is an open-source **research scaffold and evaluation harness**. **No trained model checkpoint weights (`.safetensors` / `.gguf`) are published yet.** Without an external `Ollama` or `NVIDIA NIM` server configured, `orchestrator/agent.py`, `reasoning/thinker.py`, and `audio/voice.py` run as deterministic offline simulation stubs.

## Package Layout

- `lughallm/src/training/` — Real PyTorch / `peft` / `trl` QLoRA fine-tuning script (`finetune_lora.py`), dataset splitter (`prepare_dataset.py`), and 62-item seed JSONL (`swahili_instructions_seed.jsonl`).
- `lughallm/src/benchmark/` — 40-item `Swahili-Bench` dataset (`dataset.json`), keyword/hallucination scorer (`evaluator.py`), and live endpoint / synthetic self-test runner (`swahili_bench.py`).
- `lughallm/src/api/` — FastAPI OpenAI-compatible gateway (`main.py`), strict origin-allowlisted CORS policy (`cors_policy.py`), API-key auth (`auth.py`), and Pydantic schemas (`schemas.py`).
- `lughallm/src/db/storage.py` — Parameterized SQLite API-key, thread, and multi-currency token ledger.
- `lughallm/src/channels/ussd.py` & `lughallm/src/agents/tools.py` — 2G USSD (`*149*00#`) state machine and deterministic East African tax/loan/crop calculators.
- `lughallm/src/orchestrator/agent.py`, `reasoning/thinker.py`, `audio/voice.py` — Lexical dialect detector plus offline mock orchestration, `<fikiri>` template, and voice transcription stubs.

## Verification Commands

```bash
python3 -m unittest discover -s lughallm/tests -p "test_*.py" -v
python3 -m lughallm.src.benchmark.swahili_bench
```

## License

[MIT License](../LICENSE)
