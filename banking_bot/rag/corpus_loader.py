# banking_bot/rag/corpus_loader.py
import os
import glob
from typing import List
from ..models import Snippet
from .. import config


def load_policy_snippets() -> List[Snippet]:
    policy_dir = os.path.join("data", "policies")
    snippets: List[Snippet] = []

    if os.path.isdir(policy_dir):
        for path in glob.glob(os.path.join(policy_dir, "*.txt")):
            with open(path, "r", encoding="utf-8") as f:
                text = f.read().strip()
            if not text:
                continue
            base = os.path.basename(path)
            for i, chunk in enumerate(text.split("\n\n")):
                chunk = chunk.strip()
                if len(chunk) < 40:
                    continue
                snippets.append(
                    Snippet(
                        id=f"{base}_{i}",
                        text=chunk,
                        source=base
                    )
                )
    else:
        snippets = list(config.DEFAULT_SNIPPETS)

    return snippets
