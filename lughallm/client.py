"""
LughaLLM Official Python SDK.
Standard library based (urllib.request) with zero external dependencies.
Drop-in integration for East African developers.
"""

import json
import urllib.request
import urllib.error
from typing import Optional, Dict, Any, List


class LughaError(Exception):
    """Base exception for LughaLLM API errors."""
    pass


class LughaClient:
    """Official Python Client for LughaLLM."""

    def __init__(self, api_key: str = "lug_live_demo12345", base_url: str = "http://localhost:8000"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def _request(self, endpoint: str, method: str = "GET", payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "LughaLLM-Python-SDK/0.1.0"
        }
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        req = urllib.request.Request(url, data=data, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = resp.read().decode("utf-8")
                return json.loads(body)
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            try:
                err_json = json.loads(err_body)
                msg = err_json.get("detail", err_body)
            except Exception:
                msg = err_body
            raise LughaError(f"API Error {e.code}: {msg}")
        except urllib.error.URLError as e:
            raise LughaError(f"Connection failed to {url}: {e.reason}")

    def chat(self, message: str, dialect: str = "auto", model: str = "lughallm-llama3-8b", include_thinking: bool = False) -> Dict[str, Any]:
        """
        Sends a single prompt to LughaLLM and returns the assistant's reply and dialect metadata.
        Set include_thinking=True to retrieve explicit <fikiri> System-2 reasoning traces.
        """
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": message}
            ],
            "dialect": dialect,
            "include_thinking": include_thinking
        }
        res = self._request("/v1/chat/completions", method="POST", payload=payload)
        return {
            "content": res["choices"][0]["message"]["content"],
            "detected_dialect": res.get("detected_dialect"),
            "tokens_used": res["usage"]["total_tokens"],
            "cost_tzs": res["usage"]["estimated_cost_tzs"],
            "raw_response": res
        }

    def list_tools(self) -> List[Dict[str, Any]]:
        """List registered agentic tools available for function calling."""
        res = self._request("/v1/tools", method="GET")
        return res.get("tools", [])

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a registered agentic tool."""
        return self._request(f"/v1/tools/execute?tool_name={tool_name}", method="POST", payload=arguments)

    def check_balance(self) -> Dict[str, Any]:
        """Check the token balance and account status of the active API key."""
        return self._request("/v1/keys/balance", method="GET")

    def topup_mpesa(self, phone_number: str, amount_tzs: float) -> Dict[str, Any]:
        """Initiate an M-Pesa Daraja STK Push token top-up."""
        payload = {
            "phone_number": phone_number,
            "amount_tzs": amount_tzs,
            "account_reference": self.api_key
        }
        return self._request("/v1/payments/mpesa/simulate", method="POST", payload=payload)

    def run_benchmark(self, model: str = "lughallm") -> Dict[str, Any]:
        """Run SWAHILI-BENCH evaluation and retrieve category scores."""
        return self._request(f"/v1/benchmark/run?model_profile={model}", method="POST")
