"""Extract structured rules from unstructured policy documents via Gemini."""

import logging

from src.packcheck.llm.client import GeminiClient
from src.packcheck.llm.prompts import RULE_EXTRACT_PROMPT
from src.packcheck.models import Rule

logger = logging.getLogger(__name__)


def extract_rules_from_text(
    document_text: str,
    llm_client: GeminiClient | None = None,
) -> list[Rule]:
    """Extract structured Rule objects from unstructured markdown/text documents.

    Every rule is validated against Pydantic and must include a verifiable quote
    from the original document; rules lacking quotes are discarded.
    """
    if not document_text.strip():
        return []

    client = llm_client or GeminiClient()
    if not client.is_available():
        # Fallback heuristic parser for markdown bullet points when LLM is offline
        return _fallback_markdown_extractor(document_text)

    prompt = RULE_EXTRACT_PROMPT.format(document_text=document_text[:6000])
    res = client.generate_json(
        prompt=prompt,
        content="Extract packaging compliance rules.",
    )

    if not res or "rules" not in res:
        return _fallback_markdown_extractor(document_text)

    extracted_rules: list[Rule] = []
    norm_doc = document_text.lower()

    for item in res["rules"]:
        quote = item.get("quote", "").strip()
        # Drop rules lacking an exact or near-exact quote from the document
        if not quote or quote.lower() not in norm_doc:
            logger.info(
                "Dropping extracted rule lacking verified source quote: %s", item.get("title")
            )
            continue

        try:
            rule = Rule(
                id=item.get("id", f"COMP-{len(extracted_rules) + 1:03d}"),
                title=item.get("title", "Extracted Rule"),
                source=item.get("source", "Uploaded Document"),
                quote_or_paraphrase=quote,
                check_type="semantic",
                severity=item.get("severity", "major"),
                applies_to=item.get("applies_to", ["general"]),
                enabled=True,
            )
            extracted_rules.append(rule)
        except Exception as e:
            logger.warning("Failed to validate extracted rule model: %s", e)

    return extracted_rules or _fallback_markdown_extractor(document_text)


def _fallback_markdown_extractor(doc_text: str) -> list[Rule]:
    """Deterministic fallback parser for structured markdown rulebooks when offline."""
    rules: list[Rule] = []
    lines = doc_text.splitlines()
    rule_idx = 1

    for line in lines:
        line_s = line.strip()
        # Look for numbered or bulleted items
        if line_s.startswith(("- ", "* ", "1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.")):
            clean_text = line_s.lstrip("-*0123456789. ")
            if len(clean_text) > 15:
                rules.append(
                    Rule(
                        id=f"DOC-RULE-{rule_idx:03d}",
                        title=clean_text[:40].rstrip(":") + "...",
                        source="Internal Rulebook",
                        quote_or_paraphrase=clean_text,
                        check_type="semantic",
                        severity="major",
                        applies_to=["general"],
                        enabled=True,
                    )
                )
                rule_idx += 1

    return rules
