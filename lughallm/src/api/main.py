"""
LughaLLM Main Commercial API Server.
OpenAI-compatible inference server with Swahili cultural grounding and dialect awareness.
"""

import uuid
import os
import time
import asyncio
from fastapi import FastAPI, HTTPException, Request, Depends, Query, status
from fastapi.responses import JSONResponse, FileResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware

from lughallm.src.api.config import settings
from lughallm.src.db.storage import ledger
from lughallm.src.api.auth import verify_api_key
from lughallm.src.api.schemas import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatChoice,
    ChatMessage,
    UsageInfo,
    WhatsAppWebhookPayload,
    WhatsAppResponse,
    MPesaPaymentRequest,
    MPesaPaymentResponse,
    CreateKeyRequest,
    CreateKeyResponse,
    KeyBalanceResponse,
    USSDPayload,
    AudioTranscriptionRequest,
    AudioTranscriptionResponse
)
from lughallm.src.orchestrator.agent import LughaOrchestrator
from lughallm.src.benchmark.swahili_bench import SwahiliBenchRunner
from lughallm.src.channels.ussd import ussd_manager
from lughallm.src.audio.voice import voice_processor
from lughallm.src.reasoning.thinker import reasoning_engine
from lughallm.src.agents.tools import tool_registry

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Foundational Swahili LLM API for East Africa. Native support for Kiswahili Sanifu & Sheng."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = LughaOrchestrator()
benchmark_runner = SwahiliBenchRunner()


@app.get("/")
def get_index():
    static_file = os.path.join(os.path.dirname(__file__), "..", "..", "static", "index.html")
    if os.path.exists(static_file):
        return FileResponse(static_file)
    return {"message": "LughaLLM API is running. Explore docs at /docs."}


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "supported_dialects": [
            "kiswahili_sanifu",
            "sheng_nairobi",
            "kingwana_drc",
            "swahili_uganda",
            "coastal_swahili"
        ],
        "supported_countries": [
            "Tanzania",
            "Kenya",
            "Democratic Republic of Congo (DRC)",
            "Uganda",
            "Rwanda",
            "Burundi",
            "South Sudan"
        ],
        "regional_blocs": [
            "East African Community (EAC)",
            "African Union (AU)",
            "Southern African Development Community (SADC)"
        ]
    }


@app.get("/v1/models")
def list_models():
    return {
        "object": "list",
        "data": [
            {
                "id": "lughallm-llama3-8b",
                "object": "model",
                "created": 1729000000,
                "owned_by": "lughallm-east-africa",
                "description": "Llama-3-8B fine-tuned with East African cultural alignment and Sheng support."
            },
            {
                "id": "lughallm-llama3-70b-nim",
                "object": "model",
                "created": 1729000000,
                "owned_by": "lughallm-nvidia-nim",
                "description": "High-throughput enterprise model accelerated on NVIDIA H100 via NVIDIA NIM."
            }
        ]
    }


@app.post("/v1/keys/create", response_model=CreateKeyResponse)
def create_api_key(req: CreateKeyRequest):
    """
    Generate a new developer API key with free tier token allocation.
    """
    key = ledger.create_api_key(name=req.name, initial_tokens=req.initial_tokens or 50000)
    info = ledger.get_key_info(key)
    return CreateKeyResponse(
        api_key=info["api_key"],
        name=info["name"],
        balance_tokens=info["balance_tokens"],
        created_at=info["created_at"]
    )


@app.get("/v1/keys/balance", response_model=KeyBalanceResponse)
def check_balance(key_info: dict = Depends(verify_api_key)):
    """
    Check current token balance and status for the provided API key.
    """
    return KeyBalanceResponse(
        api_key=key_info["api_key"],
        name=key_info["name"],
        balance_tokens=key_info["balance_tokens"],
        is_active=bool(key_info["is_active"]),
        rate_per_1k_tokens_tzs=settings.rate_per_1k_tokens_tzs
    )


@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(req: ChatCompletionRequest, key_info: dict = Depends(verify_api_key)):
    """
    OpenAI-compatible chat completion endpoint.
    Automatically detects Swahili dialects and injects cultural context.
    Debits tokens from the authenticated API key.
    """
    if not req.messages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Messages list cannot be empty."
        )

    # Get last user message
    last_user_msg = next((m.content for m in reversed(req.messages) if m.role == "user"), "").strip()
    if not last_user_msg:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one user message with non-empty content is required."
        )
    
    # Process through orchestrator asynchronously to avoid blocking event loop
    result = await asyncio.to_thread(
        orchestrator.route_and_execute,
        last_user_msg,
        req.dialect or "auto"
    )
    response_content = result["response"]
    detected_dialect = result["detected_dialect"]

    # Inject System-2 <fikiri> reasoning traces if requested
    if req.include_thinking:
        response_content = reasoning_engine.process_with_reasoning(
            last_user_msg,
            detected_dialect,
            result.get("routed_domain", "general"),
            response_content,
            include_thinking=True
        )

    # Calculate token metrics
    prompt_tokens = sum(len(m.content.split()) for m in req.messages) * 2
    completion_tokens = len(response_content.split()) * 2
    total_tokens = prompt_tokens + completion_tokens
    cost_tzs = (total_tokens / 1000.0) * settings.rate_per_1k_tokens_tzs

    # Ledger debit check
    req_id = f"chatcmpl-{uuid.uuid4().hex[:12]}"
    has_balance = ledger.debit_tokens(
        api_key=key_info["api_key"],
        tokens=total_tokens,
        request_id=req_id,
        cost_tzs=cost_tzs,
        dialect=detected_dialect,
        domain=result.get("routed_domain", "general")
    )
    if not has_balance:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Salio lako la token halitoshi ({key_info['balance_tokens']} zimebaki, unahitaji {total_tokens}). Tafadhali ongeza salio kupitia M-Pesa."
        )

    return ChatCompletionResponse(
        id=req_id,
        model=req.model,
        choices=[
            ChatChoice(
                index=0,
                message=ChatMessage(role="assistant", content=response_content),
                finish_reason="stop"
            )
        ],
        usage=UsageInfo(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            estimated_cost_tzs=round(cost_tzs, 2)
        ),
        detected_dialect=detected_dialect
    )


@app.post("/v1/benchmark/run")
async def run_benchmark(model_profile: str = "lughallm"):
    """
    Execute SWAHILI-BENCH evaluation and return category scores and pass rates.
    """
    results = await asyncio.to_thread(
        benchmark_runner.run_mock_simulation,
        model_profile
    )
    return results


@app.get("/v1/webhooks/whatsapp")
def verify_whatsapp_webhook(
    hub_mode: Optional[str] = Query(None, alias="hub.mode"),
    hub_challenge: Optional[str] = Query(None, alias="hub.challenge"),
    hub_verify_token: Optional[str] = Query(None, alias="hub.verify_token")
):
    """
    Meta WhatsApp Cloud API webhook challenge verification handshake.
    """
    expected_token = os.getenv("WHATSAPP_VERIFY_TOKEN", "lughallm_verify_2026")
    if hub_mode == "subscribe" and hub_verify_token == expected_token:
        return PlainTextResponse(content=hub_challenge or "")
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="WhatsApp verify token mismatch."
    )


@app.post("/v1/webhooks/whatsapp", response_model=WhatsAppResponse)
async def whatsapp_webhook(payload: WhatsAppWebhookPayload):
    """
    Direct WhatsApp bot integration endpoint.
    """
    message_text = payload.message.strip()
    if not message_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incoming WhatsApp message cannot be empty."
        )

    result = await asyncio.to_thread(orchestrator.route_and_execute, message_text)
    return WhatsAppResponse(
        status="success",
        reply=result["response"],
        dialect=result["detected_dialect"]
    )


@app.post("/v1/payments/mpesa/simulate", response_model=MPesaPaymentResponse)
async def simulate_mpesa_payment(req: MPesaPaymentRequest, authorization: Optional[str] = None):
    """
    Simulates M-Pesa Daraja STK Push token top-up.
    Credits tokens directly to the user's API key.
    """
    if req.amount_tzs <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment amount must be greater than zero."
        )

    # Resolve target API key
    api_key = "lug_live_demo12345"
    if req.account_reference.startswith("lug_live_"):
        api_key = req.account_reference
    elif authorization and authorization.startswith("Bearer "):
        api_key = authorization.split("Bearer ", 1)[1].strip()

    # 25 TZS = 1,000 tokens
    tokens_to_credit = int((req.amount_tzs / settings.rate_per_1k_tokens_tzs) * 1000)
    checkout_id = f"ws_CO_{int(time.time())}_{uuid.uuid4().hex[:6]}"

    # Update ledger balance
    new_balance = ledger.credit_tokens(
        api_key=api_key,
        tokens=tokens_to_credit,
        checkout_id=checkout_id,
        phone=req.phone_number,
        amount_tzs=req.amount_tzs
    )

    return MPesaPaymentResponse(
        status="COMPLETED",
        checkout_request_id=checkout_id,
        message=f"Malipo ya TZS {req.amount_tzs:,.0f} yamethibitishwa. Salio jipya ni token {new_balance:,}.",
        tokens_credited=tokens_to_credit
    )


@app.post("/v1/channels/ussd", response_class=PlainTextResponse)
async def handle_ussd(payload: USSDPayload):
    """
    USSD gateway endpoint compatible with Africa's Talking / Twilio.
    Provides offline Swahili AI access for basic 2G feature phones.
    """
    response_text = await asyncio.to_thread(
        ussd_manager.process_ussd_request,
        payload.sessionId,
        payload.serviceCode,
        payload.phoneNumber,
        payload.text
    )
    return response_text


@app.post("/v1/audio/transcriptions", response_model=AudioTranscriptionResponse)
async def transcribe_audio(req: AudioTranscriptionRequest):
    """
    OpenAI-compatible Swahili audio & voice note transcription endpoint.
    Handles WhatsApp voice notes and regional accent phoneme alignment.
    """
    dummy_bytes = req.audio_content.encode("utf-8") if req.audio_content else b"audio_sample"
    result = await asyncio.to_thread(
        voice_processor.transcribe_audio_bytes,
        req.filename or "voice_note.ogg",
        dummy_bytes,
        req.language or "sw"
    )
    return AudioTranscriptionResponse(
        text=result["text"],
        language=result["language"],
        duration=result["duration"],
        encoding=result["encoding"]
    )


@app.get("/v1/tools")
def list_available_tools():
    """
    Returns the catalog of registered agentic tools available for function calling.
    """
    return {
        "object": "list",
        "tools": tool_registry.get_tool_definitions()
    }


@app.post("/v1/tools/execute")
async def execute_tool(tool_name: str, arguments: dict):
    """
    Executes a registered agentic tool by name with arguments.
    """
    res = await asyncio.to_thread(tool_registry.execute_tool, tool_name, arguments)
    return res
