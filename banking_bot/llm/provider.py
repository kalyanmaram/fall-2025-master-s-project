# banking_bot/llm/provider.py
from __future__ import annotations
from abc import ABC, abstractmethod
import requests
from .. import config


class LLMProvider(ABC):
    """
    Interface for any LLM backend (Ollama, OpenAI, dummy).
    """

    @abstractmethod
    def generate(self, prompt: str) -> str:
        ...


class DummyProvider(LLMProvider):
    """
    Simple fallback provider when no real model is enabled.
    """

    def generate(self, prompt: str) -> str:
        return (
            "This is the UNH Banking Assistant demo using a simplified response engine. "
            "Enable USE_OLLAMA to get full LLM-generated answers grounded in RBI-aligned policies."
        )


class OllamaProvider(LLMProvider):
    """
    LLM provider using a local Ollama server.
    """

    def __init__(self, url: str, model: str) -> None:
        self._url = url
        self._model = model

    def generate(self, prompt: str) -> str:
        try:
            r = requests.post(
                self._url,
                json={
                    "model": self._model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "top_p": 0.9,
                        "num_predict": 256,
                    },
                },
                timeout=60,
            )
            r.raise_for_status()
            data = r.json()
            return data.get("response", "").strip()
        except Exception as e:
            print("LLM (Ollama) error:", e)
            return "I’m experiencing technical difficulties accessing the model. Please try again later."


def build_llm_provider() -> LLMProvider:
    """
    Factory: chooses LLM backend based on config.
    """
    if config.USE_OLLAMA:
        return OllamaProvider(url=config.OLLAMA_URL, model=config.OLLAMA_MODEL)
    return DummyProvider()
