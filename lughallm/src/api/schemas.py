"""
Pydantic schemas for OpenAI compatibility, WhatsApp, and Billing.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
import time


class ChatMessage(BaseModel):
    role: str = Field(..., description="Role of the author: system, user, assistant")
    content: str = Field(..., description="Content of the message")


class ChatCompletionRequest(BaseModel):
    model: str = Field(default="lughallm-llama3-8b", description="Model identifier")
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 512
    stream: Optional[bool] = False
    include_thinking: Optional[bool] = Field(
        default=False,
        description="Enable explicit Swahili <fikiri>...</fikiri> System-2 reasoning traces"
    )
    tools: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Optional list of callable tools for agentic execution"
    )
    dialect: Optional[str] = Field(
        default="auto",
        description="Target Swahili dialect: auto, kiswahili_sanifu, sheng_nairobi, kingwana_drc, coastal"
    )


class ChatChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: str = "stop"


class UsageInfo(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost_tzs: float = 0.0


class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str
    choices: List[ChatChoice]
    usage: UsageInfo
    detected_dialect: Optional[str] = None


class WhatsAppWebhookPayload(BaseModel):
    phone_number: str
    message: str
    user_name: Optional[str] = "Mtumiaji"


class WhatsAppResponse(BaseModel):
    status: str
    reply: str
    dialect: str


class MPesaPaymentRequest(BaseModel):
    phone_number: str = Field(..., example="255712345678")
    amount_tzs: float = Field(..., example=5000.0)
    account_reference: str = Field(..., example="LUGHA-TOKENS-100K")


class MPesaPaymentResponse(BaseModel):
    status: str
    checkout_request_id: str
    message: str
    tokens_credited: int


class CreateKeyRequest(BaseModel):
    name: str = Field(..., example="E-commerce Chatbot Production")
    initial_tokens: Optional[int] = Field(default=50000, description="Free tier initial tokens")


class CreateKeyResponse(BaseModel):
    api_key: str
    name: str
    balance_tokens: int
    created_at: int


class KeyBalanceResponse(BaseModel):
    api_key: str
    name: str
    balance_tokens: int
    is_active: bool
    rate_per_1k_tokens_tzs: float = 25.0


class USSDPayload(BaseModel):
    sessionId: str = Field(..., example="ATUid_12345")
    serviceCode: str = Field(default="*149*00#", example="*149*00#")
    phoneNumber: str = Field(..., example="+255712345678")
    text: str = Field(default="", example="1*1")


class AudioTranscriptionRequest(BaseModel):
    filename: Optional[str] = "voice_note.ogg"
    language: Optional[str] = "sw"
    audio_content: Optional[str] = None


class AudioTranscriptionResponse(BaseModel):
    text: str
    language: str = "sw"
    duration: float = 0.0
    encoding: str = "audio/ogg-opus"


class ToolExecutionRequest(BaseModel):
    name: str = Field(..., description="Registered tool name", example="hesabu_kodi_kikanda")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Arguments dictionary for the tool")


class CreateThreadRequest(BaseModel):
    title: Optional[str] = "Mazungumzo Mapya"
    dialect: Optional[str] = "auto"
    user_id: Optional[str] = "guest"


class ThreadMessageRequest(BaseModel):
    content: str = Field(..., description="User message text")
    include_thinking: Optional[bool] = True
    dialect: Optional[str] = "auto"


