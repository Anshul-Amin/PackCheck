"""BM25 Rule Retriever for grounded semantic search without heavy embedding models."""

import re

from rank_bm25 import BM25Okapi

from src.packcheck.models import Rule


def _tokenize(text: str) -> list[str]:
    """Simple alphanumeric tokenizer for BM25."""
    clean = re.sub(r"[^\w\s]", " ", text.lower())
    return [token for token in clean.split() if len(token) > 1]


class RuleRetriever:
    """In-memory BM25 index over compliance rules."""

    def __init__(self, rules: list[Rule]):
        self.rules = [r for r in rules if r.enabled]
        self.corpus = [
            _tokenize(f"{r.title} {r.source} {r.quote_or_paraphrase} {' '.join(r.applies_to)}")
            for r in self.rules
        ]
        self.bm25 = BM25Okapi(self.corpus) if self.corpus else None

    def retrieve(self, query: str, top_k: int = 3) -> list[Rule]:
        """Retrieve the top-k most relevant rules for a given query text."""
        if not self.bm25 or not self.rules:
            return []

        tokens = _tokenize(query)
        if not tokens:
            return self.rules[:top_k]

        scores = self.bm25.get_scores(tokens)
        scored_pairs = list(zip(self.rules, scores))
        # Sort descending by score
        scored_pairs.sort(key=lambda x: x[1], reverse=True)

        return [pair[0] for pair in scored_pairs[:top_k] if pair[1] > 0.0]
