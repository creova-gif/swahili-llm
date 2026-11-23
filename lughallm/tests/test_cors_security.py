"""
Security unit tests verifying strict CORS origin handling without wildcard credentials.
"""

from __future__ import annotations
import unittest
from lughallm.src.api.cors_policy import DEFAULT_LOCALHOST_ORIGINS, resolve_cors_policy

try:
    from fastapi.testclient import TestClient
    from lughallm.src.api.main import app
    _client = TestClient(app)
    HAS_FASTAPI = True
except ImportError:
    _client = None
    HAS_FASTAPI = False


class TestCorsSecurity(unittest.TestCase):
    def test_defaults_to_localhost_without_wildcard_or_credentials(self):
        origins, creds = resolve_cors_policy(raw_origins="", allow_credentials=None)
        self.assertEqual(origins, list(DEFAULT_LOCALHOST_ORIGINS))
        self.assertNotIn("*", origins)
        self.assertFalse(creds)

    def test_strips_bare_wildcard_even_when_credentials_requested(self):
        origins, creds = resolve_cors_policy(raw_origins="*", allow_credentials=True)
        self.assertNotIn("*", origins)
        self.assertEqual(origins, list(DEFAULT_LOCALHOST_ORIGINS))
        self.assertTrue(creds)

    def test_parses_explicit_allowlist_origins(self):
        origins, creds = resolve_cors_policy(
            raw_origins="https://app.example.co.tz/, *, http://localhost:5173",
            allow_credentials=True,
        )
        self.assertEqual(origins, ["https://app.example.co.tz", "http://localhost:5173"])
        self.assertNotIn("*", origins)
        self.assertTrue(creds)

    @unittest.skipUnless(HAS_FASTAPI, "FastAPI not installed in active Python environment")
    def test_fastapi_cors_rejects_arbitrary_untrusted_origin(self):
        res_untrusted = _client.options(
            "/v1/models",
            headers={
                "Origin": "https://evil.attacker.example",
                "Access-Control-Request-Method": "GET",
            },
        )
        self.assertNotEqual(res_untrusted.headers.get("access-control-allow-origin"), "*")
        self.assertNotEqual(
            res_untrusted.headers.get("access-control-allow-origin"),
            "https://evil.attacker.example",
        )

        res_localhost = _client.options(
            "/v1/models",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )
        self.assertEqual(res_localhost.status_code, 200)
        self.assertEqual(
            res_localhost.headers.get("access-control-allow-origin"),
            "http://localhost:5173",
        )


if __name__ == "__main__":
    unittest.main()
