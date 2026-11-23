"""
Strict CORS policy parser for LughaLLM.
Prevents combining wildcard origins ('*') with credentialed requests.
"""

from __future__ import annotations
import os
from typing import List, Optional, Tuple

DEFAULT_LOCALHOST_ORIGINS: Tuple[str, ...] = (
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
)


def resolve_cors_policy(
    raw_origins: Optional[str] = None,
    allow_credentials: Optional[bool] = None,
) -> Tuple[List[str], bool]:
    """
    Resolve allowed CORS origins and credential policy from environment configuration.

    - Defaults to explicit localhost developer origins when CORS_ALLOWED_ORIGINS is unset.
    - Strips bare '*' wildcards so wildcard origins can never be paired with credentials.
    """
    env_origins = raw_origins if raw_origins is not None else os.getenv("CORS_ALLOWED_ORIGINS", "")
    parsed = [
        item.strip().rstrip("/")
        for item in env_origins.split(",")
        if item.strip() and item.strip() != "*"
    ]
    origins = parsed if parsed else list(DEFAULT_LOCALHOST_ORIGINS)

    if allow_credentials is None:
        raw_creds = os.getenv("CORS_ALLOW_CREDENTIALS", "false").strip().lower()
        creds = raw_creds in ("1", "true", "yes")
    else:
        creds = bool(allow_credentials)

    # Hard invariant: never allow credentials if '*' were ever present
    if "*" in origins:
        creds = False

    return origins, creds
