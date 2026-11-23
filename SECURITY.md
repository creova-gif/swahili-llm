# Security Policy

## Supported Versions

| Version | Supported | Notes |
| :--- | :--- | :--- |
| `0.2.x` (`main`) | ✅ Supported | Active orchestration gateway, `Swahili-Bench` harness & React playground |
| `0.1.x` | ⚠️ Security fixes only | Initial release |

---

## Reporting a Vulnerability

If you discover a security vulnerability, authentication bypass, SQLite injection vector, or prompt-injection escalation in **LughaLLM** (`creova-gif/swahili-llm`), please report it privately:

- **Email:** `creativeinnovationspace@gmail.com`
- **GitHub Private Vulnerability Reporting:** Use the [Security Advisories](https://github.com/creova-gif/swahili-llm/security/advisories) tab on this repository.

Please **do not** open a public GitHub issue for unpatched security vulnerabilities. We acknowledge reports within **48 hours** and aim to publish a fix within **7 days**.

---

## Security Architecture & Boundaries

1. **API Key Hashing & Multi-Currency Token Ledger (`lughallm/src/db/storage.py`, `lughallm/src/api/auth.py`):**
   - API keys (`lug_live_*`) enforce pre-execution token balance verification and rate-limiting before dispatching requests to downstream inference providers (`Ollama`, `NVIDIA NIM`, `Vertex AI`).
   - SQLite ledger queries use parameterized SQL statements exclusively to prevent SQL injection across API key, thread memory, and mobile-money top-up tables.
2. **Zero Committed Secrets (`.env.example`):**
   - All downstream model and telecom credentials (`NVIDIA_API_KEY`, `MPESA_CONSUMER_KEY`, `MPESA_CONSUMER_SECRET`, `MPESA_PASSKEY`, `WHATSAPP_VERIFY_TOKEN`) are injected via environment variables at runtime and excluded by `.gitignore`.
3. **Sovereign / Air-Gapped Execution Mode:**
   - When `LUGHALLM_LOCAL_URL` points to a local `Ollama` or `vLLM` daemon (or when running in offline fallback mode), zero user prompts or telemetry leave the host machine, supporting compliance with the Tanzania Personal Data Protection Act (PDPA) and Kenya Data Protection Act (DPA).
