"""
API Key Authentication and Authorization for LughaLLM.
"""

from fastapi import Header, HTTPException, status
from typing import Optional, Dict, Any

from lughallm.src.db.storage import ledger


def verify_api_key(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """
    Validates API key from Authorization header.
    Format: 'Bearer lug_live_...'
    Falls back to 'lug_live_demo12345' if no header is supplied in development.
    """
    api_key = "lug_live_demo12345"
    if authorization and authorization.startswith("Bearer "):
        api_key = authorization.split("Bearer ", 1)[1].strip()

    key_info = ledger.get_key_info(api_key)
    if not key_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or revoked API key: '{api_key}'. Request a valid key via /v1/keys/create."
        )

    if not key_info["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This API key is deactivated. Please contact support."
        )

    return key_info
