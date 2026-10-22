"""Tests for anti-false-alarm verdict policy and quote verification."""

from src.packcheck.models import Evidence, Finding
from src.packcheck.verdict_policy import apply_verdict_policy, deduplicate_findings


def test_llm_fail_downgraded_without_dual_quotes():
    """Verify that an LLM finding with verdict FAIL is downgraded to NEEDS_REVIEW if quotes are incomplete."""
    finding = Finding(
        id="TEST-LLM-001",
        title="Unverified AI Assertion",
        verdict="FAIL",
        confidence=0.9,
        verified_by="llm",
        category="semantic",
        why_it_matters="Model thinks something is wrong",
        evidence=[],  # No quotes provided
    )
    result = apply_verdict_policy(finding, artwork_text="some artwork text")
    assert result is not None
    assert result.verdict == "NEEDS_REVIEW"
    assert result.human_check_needed is not None


def test_hallucinated_quote_discarded():
    """Verify that an LLM finding with a hallucinated quote is completely discarded (returns None)."""
    finding = Finding(
        id="TEST-LLM-HALLUCINATED",
        title="Hallucinated Finding",
        verdict="NEEDS_REVIEW",
        confidence=0.8,
        verified_by="llm",
        category="semantic",
        why_it_matters="Fabricated evidence",
        evidence=[
            Evidence(
                artwork_text="This specific sentence was never printed on the artwork package anywhere.",
            )
        ],
    )
    result = apply_verdict_policy(
        finding, artwork_text="Real artwork text with Granola Berry Crunch"
    )
    assert result is None  # Discarded!


def test_deterministic_fail_preserved():
    """Verify that deterministic FAIL findings are strictly preserved."""
    finding = Finding(
        id="MATH-TRANS-EXCEEDS-FAT",
        title="Trans Fat Exceeds Total Fat",
        verdict="FAIL",
        confidence=1.0,
        verified_by="deterministic",
        category="nutrition_math",
        why_it_matters="Physically impossible formulation",
        evidence=[],
    )
    result = apply_verdict_policy(finding, artwork_text="anything")
    assert result is not None
    assert result.verdict == "FAIL"
    assert result.confidence == 1.0


def test_deduplication_prefers_deterministic():
    """Verify deduplication keeps deterministic finding when duplicate IDs occur."""
    det = Finding(
        id="SHARED-ID",
        title="Deterministic Check",
        verdict="FAIL",
        confidence=1.0,
        verified_by="deterministic",
        category="math",
        why_it_matters="Deterministic math proof",
    )
    llm = Finding(
        id="SHARED-ID",
        title="LLM Check",
        verdict="NEEDS_REVIEW",
        confidence=0.7,
        verified_by="llm",
        category="math",
        why_it_matters="LLM judgment",
    )
    deduped = deduplicate_findings([llm, det])
    assert len(deduped) == 1
    assert deduped[0].verified_by == "deterministic"
    assert deduped[0].verdict == "FAIL"
