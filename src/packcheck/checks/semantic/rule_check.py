"""Semantic rule verification check powered by Gemini."""

from src.packcheck.checks.base import register_check
from src.packcheck.llm.client import GeminiClient
from src.packcheck.llm.prompts import RULE_CHECK_PROMPT
from src.packcheck.models import ApprovedData, ArtworkDoc, Evidence, Finding, Rule
from src.packcheck.verdict_policy import apply_verdict_policy


@register_check
class SemanticRuleCheck:
    """Evaluate non-deterministic and interpretation-heavy rules via Gemini."""

    id = "SEM-RULE-CHECK"
    name = "Semantic Rule Interpretation"
    category = "semantic"

    def __init__(self, llm_client: GeminiClient | None = None):
        self.llm = llm_client or GeminiClient()

    def run(
        self,
        artwork: ArtworkDoc,
        approved: ApprovedData,
        rules: list[Rule],
    ) -> list[Finding]:
        findings: list[Finding] = []
        if not self.llm.is_available():
            # Graceful degradation when no key is set
            return findings

        # Filter to semantic rules
        semantic_rules = [r for r in rules if r.check_type == "semantic" and r.enabled]
        if not semantic_rules:
            return findings

        full_artwork_text = "\n".join(b.text for b in artwork.text_blocks)
        rule_texts = {r.id: f"{r.title} - {r.quote_or_paraphrase}" for r in rules}

        for rule in semantic_rules:
            # Build context prompt
            prompt = RULE_CHECK_PROMPT.format(
                rule_id=rule.id,
                rule_title=rule.title,
                rule_source=rule.source,
                rule_requirement=rule.quote_or_paraphrase,
                artwork_evidence=full_artwork_text[:3000],  # Window to stay within token limits
                approved_context=(
                    f"Product: {approved.product_name}\n"
                    f"Claims: {', '.join(approved.claims)}\n"
                    f"Dietary: {approved.dietary_info}"
                ),
            )

            res = self.llm.generate_json(
                prompt=prompt,
                content=f"Verify rule {rule.id}: {rule.title}",
            )

            if not res or "verdict" not in res:
                continue

            verdict = res.get("verdict", "NEEDS_REVIEW")
            if verdict not in ("FAIL", "NEEDS_REVIEW", "PASS"):
                verdict = "NEEDS_REVIEW"

            confidence = float(res.get("confidence", 0.8))
            q_art = res.get("quoted_artwork_text", "").strip()
            q_rule = res.get("quoted_rule_text", "").strip()
            reasoning = res.get("reasoning", "")
            needs_human = res.get("needs_human_because", "")

            # Create candidate finding
            candidate = Finding(
                id=f"SEM-{rule.id}",
                title=f"{rule.title} ({verdict})",
                verdict=verdict,
                confidence=confidence,
                verified_by="llm",
                category=self.category,
                why_it_matters=reasoning or f"Compliance review against {rule.source}.",
                evidence=[
                    Evidence(
                        artwork_text=q_art if q_art else None,
                        rule_id=rule.id,
                        rule_quote=q_rule if q_rule else rule.quote_or_paraphrase,
                    )
                ],
                human_check_needed=needs_human if verdict == "NEEDS_REVIEW" else None,
            )

            # Apply strict verdict policy (hallucination rejection + unverified FAIL downgrade)
            checked = apply_verdict_policy(
                candidate,
                artwork_text=full_artwork_text,
                rule_texts=rule_texts,
            )
            if checked:
                findings.append(checked)

        return findings
