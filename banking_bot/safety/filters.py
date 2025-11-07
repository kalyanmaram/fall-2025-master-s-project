# banking_bot/safety/filters.py
from typing import Dict
from ..models import SafetyResult
from .. import config


class SafetyFilter:
    """
    Single-responsibility: classify a message as allowed / risky / sensitive.
    """

    def __init__(self) -> None:
        self._risky_keywords = config.RISKY_KEYWORDS
        self._sensitive_keywords = config.SENSITIVE_KEYWORDS

    def check(self, text: str) -> SafetyResult:
        t = text.lower()
        flags: Dict[str, bool] = {"risky": False, "sensitive": False}

        if any(k in t for k in self._risky_keywords):
            flags["risky"] = True
            return SafetyResult(
                allowed=False,
                category="risky",
                message=config.REFUSAL_MSG_RISKY,
                flags=flags,
            )

        if any(k in t for k in self._sensitive_keywords):
            flags["sensitive"] = True
            return SafetyResult(
                allowed=False,
                category="sensitive",
                message=config.REFUSAL_MSG_SENSITIVE,
                flags=flags,
            )

        return SafetyResult(
            allowed=True,
            category="allowed",
            message=None,
            flags=flags,
        )
