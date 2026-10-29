"""
Configuration management for LughaLLM.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "LughaLLM Commercial API"
    app_version: str = "0.1.0"
    environment: str = "development"
    host: str = "0.0.0.0"
    port: int = 8000

    # Model Serving
    default_model: str = "lughallm-llama3-8b"
    nvidia_nim_endpoint: Optional[str] = None
    nvidia_api_key: Optional[str] = None
    gcp_project_id: Optional[str] = None
    gcp_location: str = "us-central1"
    google_vertex_endpoint: Optional[str] = None

    # Billing & Mobile Money
    mpesa_consumer_key: Optional[str] = None
    mpesa_consumer_secret: Optional[str] = None
    mpesa_passkey: Optional[str] = None
    mpesa_shortcode: str = "174379"
    # Regional Currency Rates per 1,000 Tokens (~$0.01 USD parity)
    rate_per_1k_tokens_tzs: float = 25.0   # Tanzania (TZS)
    rate_per_1k_tokens_kes: float = 1.30   # Kenya (KES)
    rate_per_1k_tokens_ugx: float = 37.0   # Uganda (UGX)
    rate_per_1k_tokens_cdf: float = 28.0   # DRC Congo (CDF)
    rate_per_1k_tokens_rwf: float = 13.5   # Rwanda (RWF)
    rate_per_1k_tokens_bif: float = 29.0   # Burundi (BIF)

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
