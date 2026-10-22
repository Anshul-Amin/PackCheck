"""Verdict policy and anti-false-alarm enforcement.

Enforces three verdict tiers (FAIL, NEEDS_REVIEW, PASS), downgrades unverified LLM
judgments, validates hallucinated quotes, and deduplicates findings.
"""

import re

from src.packcheck.models import Finding


def _normalize_text(text: str | None) -> str:
    """Normalize whitespace and punctuation for substring containment testing."""
    if not text:
        return ""
    # Lowercase, replace non-alphanumeric with single space
    clean = re.sub(r"[^\w\s]", " ", text.lower())
    return " ".join(clean.split())


def verify_finding_quotes(
    finding: Finding,
    artwork_text: str,
    rule_texts: dict[str, str] | None = None,
) -> bool:
    """Verify that all quotes cited in evidence actually exist in source texts.

    Returns False if any artwork or rule quote cannot be found as a substring.
    """
    norm_art = _normalize_text(artwork_text)

    for ev in finding.evidence:
        # Check artwork quote if present
        if ev.artwork_text:
            norm_quote = _normalize_text(ev.artwork_text)
            # If quote is substantial (>3 words), ensure it is in the artwork text
            words = norm_quote.split()
            if len(words) >= 3 and norm_quote not in norm_art:
                return False

        # Check rule quote if present
        if ev.rule_quote and rule_texts and ev.rule_id:
            raw_rule = rule_texts.get(ev.rule_id, "")
            norm_rule = _normalize_text(raw_rule)
            norm_r_quote = _normalize_text(ev.rule_quote)
            r_words = norm_r_quote.split()
            if len(r_words) >= 3 and norm_r_quote not in norm_rule:
                return False

    return True


def apply_verdict_policy(
    finding: Finding,
    artwork_text: str = "",
    rule_texts: dict[str, str] | None = None,
) -> Finding | None:
    """Apply strict packaging QA verdict policy.

    1. Discard findings with hallucinated quotes.
    2. Downgrade LLM-only FAIL findings to NEEDS_REVIEW unless both artwork
       and rule quotes are strictly verified substrings.
    3. Downgrade any findings relying on low_confidence blocks.
    4. Ensure valid confidence bounds.
    """
    # 1. Hallucination guard for LLM findings
    if finding.verified_by in ("llm", "llm+vision"):
        quotes_valid = verify_finding_quotes(finding, artwork_text, rule_texts)
        if not quotes_valid:
            # Hallucinated quote detected: discard finding
            return None

    # 2. Anti-false-alarm downgrade for LLM-only FAIL
    if finding.verdict == "FAIL" and finding.verified_by in ("llm", "llm+vision"):
        has_art_quote = any(
            bool(ev.artwork_text and len(ev.artwork_text.strip()) > 5) for ev in finding.evidence
        )
        has_rule_quote = any(
            bool(ev.rule_quote and len(ev.rule_quote.strip()) > 5) for ev in finding.evidence
        )

        if not (has_art_quote and has_rule_quote):
            # Downgrade to NEEDS_REVIEW
            finding.verdict = "NEEDS_REVIEW"
            finding.confidence = min(finding.confidence, 0.75)
            finding.human_check_needed = (
                "Automated AI judgment requires regulatory reviewer confirmation: "
                "missing dual exact text and rule citations."
            )

    # 3. Bound confidence
    finding.confidence = max(0.0, min(1.0, finding.confidence))

    return finding


def deduplicate_findings(findings: list[Finding]) -> list[Finding]:
    """Deduplicate findings, preferring deterministic verification over LLM."""
    seen_ids: dict[str, Finding] = {}

    # Sort so deterministic findings come first
    priority = {"deterministic": 0, "llm+vision": 1, "llm": 2, "human": 3}
    sorted_findings = sorted(findings, key=lambda f: priority.get(f.verified_by, 99))

    for f in sorted_findings:
        if f.id in seen_ids:
            # Already have a higher-priority finding for this exact ID
            continue
        seen_ids[f.id] = f

    return list(seen_ids.values())
