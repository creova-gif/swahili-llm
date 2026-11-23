# ADR 0001: Dialect-Aware Orchestration Gateway & `<fikiri>` Reasoning Pipeline over Pluggable Inference Backends

- **Status:** Accepted
- **Date:** 2026-11-23
- **Author:** Justin Mafie (`@creova-gif`)

## Context

Serving Swahili and regional East/Central African sociolects (`Kiswahili Sanifu`, Nairobi `Sheng`, DRC `Kingwana`, Ugandan trade Swahili, and Coastal `Kiunguja`/`Kimvita`) in production faces three structural challenges:
1. **Dialect & Figurative Mismatch in Off-the-Shelf LLMs:** General-purpose LLMs frequently mistranslate Swahili proverbs (*methali*) literally, misinterpret Sheng code-switching, and hallucinate non-existent East African statutory authorities or currencies.
2. **Heterogeneous Compute Environments:** Developers and enterprises across Tanzania, Kenya, Uganda, DRC, and Rwanda deploy across vastly different environments—ranging from air-gapped developer laptops running `Ollama` (`llama3:8b`) to cloud GPU endpoints (`NVIDIA NIM` / `vLLM` / `Vertex AI`) and 2G USSD (`*149*00#`) feature-phone channels.
3. **Separation of Runtime Gateway from GPU Training Infrastructure:** A lightweight, zero-GPU orchestration gateway and evaluation harness must be installable and testable in standard CI environments (`pip install . && pytest`), while still providing a reproducible QLoRA fine-tuning and GGUF quantization pipeline (`lughallm/src/training/`) for teams with CUDA GPUs.

## Decision

We architect **LughaLLM** (`swahili-llm`) as a **modular AI orchestration gateway and evaluation harness** decoupled from any single model weight checkpoint:

1. **Ingress Dialect Classification (`lughallm/src/orchestrator/agent.py`):**
   - `DialectDetector` scores incoming prompts against lexical marker sets for `sheng_nairobi`, `kingwana_drc`, `swahili_uganda`, `coastal_swahili`, and `kiswahili_sanifu` before routing to domain agents (Agriculture, Legal/Tax, Finance/Mobile Money, Healthcare, or General).
2. **Explicit `<fikiri>` System-2 Reasoning & *Adabu* Cultural Filter (`lughallm/src/reasoning/thinker.py`):**
   - Every request generates a structured Swahili chain-of-thought trace (`<fikiri>...</fikiri>`) covering problem identification, dialect disambiguation, statutory/geographic fact-checking (e.g., `TRA` vs `KRA` vs `URA` vs `DGI`), and cultural etiquette (*Adabu na Heshima*, such as elder greeting reciprocity `"Shikamoo" -> "Marahaba"`).
3. **Pluggable Inference Execution (`Ollama`, `NVIDIA NIM`, or Deterministic Knowledge Router):**
   - When `LUGHALLM_LOCAL_URL` (local `Ollama` daemon) or `NVIDIA_NIM_ENDPOINT` + `NVIDIA_API_KEY` is configured, the orchestrator dispatches dialect-enriched prompts to the live model server.
   - When no external model server is reachable, the orchestrator falls back to a deterministic domain knowledge router so local CLI tools, USSD sessions, and CI test suites remain 100% functional offline.
4. **Decoupled QLoRA Fine-Tuning Scaffold (`lughallm/src/training/`, `lughallm/checkpoints/`):**
   - Dataset preparation (`prepare_dataset.py`), 4-bit QLoRA `SFTTrainer` fine-tuning (`finetune_lora.py`), and GGUF `Q4_K_M` export (`export_model.py`) are isolated in `lughallm/src/training/` with graceful `--dry-run` / CPU fallbacks when `torch`/`peft`/`trl`/`bitsandbytes` are not installed.
   - `lughallm/checkpoints/lughallm-llama3-8b-lora/adapter_config.json` stores the target PEFT adapter specification (`meta-llama/Meta-Llama-3-8B-Instruct`, `r=16`, `lora_alpha=32`) without committing multi-gigabyte `.safetensors` weights to git.

## Consequences

- **Positive:** The gateway, FastAPI server, SQLite multi-currency ledger, React frontend, USSD/voice bridges, and `Swahili-Bench` evaluator run out-of-the-box on any machine and verify in seconds in CI (`68 passed`).
- **Negative / Trade-off:** Achieving neural open-weights inference quality requires either connecting a live `Ollama` / `NVIDIA NIM` backend or running `lughallm/src/training/finetune_lora.py` on a CUDA GPU to materialize the LoRA `.safetensors` weights.
