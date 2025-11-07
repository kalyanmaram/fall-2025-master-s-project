# banking_bot/logging/logger.py
import json
from datetime import datetime, timezone
from ..models import InteractionLog
from .. import config


class InteractionLogger:
    """
    Single-responsibility: persist InteractionLog entries.
    """

    def __init__(self, path: str | None = None) -> None:
        self._path = path or config.LOG_FILE

    def log(self, entry: InteractionLog) -> None:
        record = {
            "id": entry.id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_msg": entry.user_msg,
            "intent": entry.intent,
            "response": entry.response,
            "model": entry.model,
            "latency_ms": entry.latency_ms,
            "risk_flag": entry.risk_flag,
            "sensitive_flag": entry.sensitive_flag,
            "retrieved_doc_ids": entry.retrieved_doc_ids,
            "guardrail_triggered": entry.guardrail_triggered,
            "extra": entry.extra,
        }
        with open(self._path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
