# banking_bot/core/orchestrator.py
import time
import uuid
from typing import List, Dict, Any

from ..models import ChatMessage, Snippet, InteractionLog
from .. import config
from ..safety import SafetyFilter
from ..intent import IntentClassifier
from ..rag import load_policy_snippets, EmbeddingProvider, Retriever
from ..llm import build_llm_provider, LLMProvider
from ..logging import InteractionLogger
from .prompt_builder import build_prompt


class ChatOrchestrator:
    """
    Facade/Coordinator for the whole banking chatbot pipeline.

    Depends on abstractions:
    - SafetyFilter
    - IntentClassifier
    - Retriever
    - LLMProvider
    - InteractionLogger
    """

    def __init__(
        self,
        safety_filter: SafetyFilter,
        intent_classifier: IntentClassifier,
        retriever: Retriever,
        llm: LLMProvider,
        logger: InteractionLogger,
    ) -> None:
        self._safety = safety_filter
        self._intent_classifier = intent_classifier
        self._retriever = retriever
        self._llm = llm
        self._logger = logger

    def handle_message(self, user_msg: str, history: List[ChatMessage]) -> Dict[str, Any]:
        t0 = time.time()
        interaction_id = str(uuid.uuid4())
        msg = user_msg.strip()

        # 1) Safety
        safety_result = self._safety.check(msg)
        if not safety_result.allowed:
            latency = int((time.time() - t0) * 1000)
            log_entry = InteractionLog(
                id=interaction_id,
                user_msg=msg,
                intent=safety_result.category,
                response=safety_result.message or "",
                model=config.OLLAMA_MODEL if config.USE_OLLAMA else "dummy",
                latency_ms=latency,
                risk_flag=bool(safety_result.flags and safety_result.flags.get("risky")),
                sensitive_flag=bool(safety_result.flags and safety_result.flags.get("sensitive")),
                retrieved_doc_ids=[],
                guardrail_triggered=safety_result.category,
            )
            self._logger.log(log_entry)

            return {
                "id": interaction_id,
                "intent": safety_result.category,
                "response": safety_result.message,
                "sources": [],
                "latency_ms": latency,
            }

        # 2) Intent
        intent = self._intent_classifier.classify(msg)

        # 3) Retrieval
        context_snippets: List[Snippet] = self._retriever.retrieve(msg, top_k=3)

        # 4) Prompt + LLM
        prompt = build_prompt(msg, history, context_snippets)
        answer = self._llm.generate(prompt)

        latency = int((time.time() - t0) * 1000)

        log_entry = InteractionLog(
            id=interaction_id,
            user_msg=msg,
            intent=intent,
            response=answer,
            model=config.OLLAMA_MODEL if config.USE_OLLAMA else "dummy",
            latency_ms=latency,
            risk_flag=False,
            sensitive_flag=False,
            retrieved_doc_ids=[s.id for s in context_snippets],
            guardrail_triggered=None,
        )
        self._logger.log(log_entry)

        return {
            "id": interaction_id,
            "intent": intent,
            "response": answer,
            "sources": [
                    {"id": s.id, "text": s.text, "score": s.score, "source": s.source}
                    for s in context_snippets
                ],
            "latency_ms": latency,
        }


def build_orchestrator() -> ChatOrchestrator:
    """
    Factory that wires together concrete implementations.
    Allows us to keep app.py very thin.
    """
    safety_filter = SafetyFilter()
    intent_classifier = IntentClassifier()
    snippets = load_policy_snippets()
    embedder = EmbeddingProvider()
    retriever = Retriever(snippets, embedder)
    llm = build_llm_provider()
    logger = InteractionLogger()
    return ChatOrchestrator(
        safety_filter=safety_filter,
        intent_classifier=intent_classifier,
        retriever=retriever,
        llm=llm,
        logger=logger,
    )
