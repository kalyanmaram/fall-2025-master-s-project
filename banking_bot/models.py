# banking_bot/models.py
from dataclasses import dataclass
from typing import List, Optional, Dict, Any


@dataclass
class ChatMessage:
    role: str          # "user" or "assistant"
    content: str


@dataclass
class Snippet:
    id: str
    text: str
    score: float = 0.0
    source: str | None = None  # e.g. filename or "builtin"


@dataclass
class SafetyResult:
    allowed: bool
    category: str                 # "allowed" | "risky" | "sensitive"
    message: Optional[str] = None  # refusal message if not allowed
    flags: Optional[Dict[str, bool]] = None


@dataclass
class InteractionLog:
    id: str
    user_msg: str
    intent: str
    response: str
    model: str
    latency_ms: int
    risk_flag: bool = False
    sensitive_flag: bool = False
    retrieved_doc_ids: Optional[List[str]] = None
    guardrail_triggered: Optional[str] = None
    extra: Optional[Dict[str, Any]] = None
