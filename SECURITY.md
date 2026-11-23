# Security Policy (`SECURITY.md`)

## Supported Versions

| Version | Supported | Notes |
| :--- | :--- | :--- |
| `0.2.x` (`main`) | Yes | Active research scaffold, `Swahili-Bench` evaluation harness & FastAPI gateway |
| `0.1.x` | Security fixes only | Initial prototype |

---

## Reporting a Vulnerability

If you discover a security vulnerability, CORS misconfiguration, authentication bypass, SQLite injection vector, or prompt-injection escalation in **`creova-gif/swahili-llm`**, please report it privately:

- **Email:** `security@creova.one`
- **GitHub Private Vulnerability Reporting:** Use the [Security Advisories](https://github.com/creova-gif/swahili-llm/security/advisories) tab on this repository.

Please **do not** open a public GitHub issue for unpatched security vulnerabilities. We acknowledge reports within **48 hours** and aim to publish a remediation within **7 days**.

---

## Security Architecture & Boundaries

1. **Strict Origin-Allowlisted CORS (`lughallm/src/api/cors_policy.py`, `lughallm/src/api/main.py`):**
   - `CORSMiddleware` reads explicit origins from `CORS_ALLOWED_ORIGINS` (defaulting to localhost developer origins) with `CORS_ALLOW_CREDENTIALS=false` by default, and strips bare `"*"` wildcards so wildcard origins are **never** combined with `allow_credentials=True`.
2. **API Key & Parameterized SQLite Token Ledger (`lughallm/src/db/storage.py`, `lughallm/src/api/auth.py`):**
   - API keys (`lug_live_*`) enforce pre-execution token balance verification before dispatching requests to configured inference providers (`Ollama`, `NVIDIA NIM`).
   - All SQLite ledger queries use parameterized SQL statements (`?` placeholders) to prevent SQL injection across API key, thread memory, and sandbox billing tables.
3. **Non-Root Container Execution (`Dockerfile`, `lughallm/infra/Dockerfile`):**
   - Runtime container images execute under unprivileged UID `10001` (`USER lughallm`).
4. **Zero Committed Secrets & Offline Scaffold Honesty:**
   - All downstream model and telecom credentials (`NVIDIA_API_KEY`, `MPESA_CONSUMER_KEY`, `MPESA_CONSUMER_SECRET`, `WHATSAPP_VERIFY_TOKEN`) are injected via environment variables at runtime (`.env.example`) and excluded by `.gitignore`.
   - No pre-trained model weights are bundled in git; offline orchestrator, `<fikiri>` template, and `.ogg` transcription stubs operate purely in-memory without external telemetry egress.
