# banking_bot/intent/classifier.py
from .. import config


class IntentClassifier:
    """
    Single-responsibility: map user text → high-level intent label.
    """

    def __init__(self) -> None:
        self._intent_keywords = config.INTENT_KEYWORDS

    def classify(self, text: str) -> str:
        t = text.lower().strip()

        # follow-up / filler intents
        if t in ("i have a question", "i have another question", "i have a question to ask",
                "i have another question to ask", "i want to ask something"):
            return "followup"

        for intent, keywords in self._intent_keywords.items():
            if any(kw in t for kw in keywords):
                return intent

        if t in ("hi", "hello", "hey", "namaste"):
            return "greetings"

        return "general"
