# banking_bot/core/prompt_builder.py
from typing import List
from ..models import ChatMessage, Snippet
from .. import config


def build_prompt(user_msg: str, history: List[ChatMessage], context_snippets: List[Snippet]) -> str:
    # context
    if context_snippets:
        ctx_block = "Relevant banking context (RBI/bank-aligned snippets):\n"
        for snip in context_snippets:
            ctx_block += f"- {snip.text}\n"
    else:
        ctx_block = "No specific context found; answer only if you are confident and stay general.\n"

    # history
    hist_block = ""
    for turn in history[-6:]:
        if turn.role not in ("user", "assistant"):
            continue
        hist_block += f"{turn.role.capitalize()}: {turn.content}\n"

    prompt = f"""{config.SYSTEM_PROMPT}

{ctx_block}

Conversation so far:
{hist_block}
User: {user_msg}
Assistant:"""
    return prompt
