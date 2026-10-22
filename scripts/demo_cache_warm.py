"""Pre-warm LLM response cache for offline, deterministic, and rate-limit-proof demos."""

import hashlib
import json
import sys
from pathlib import Path

# Ensure repository root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.packcheck.config import CACHE_DIR, GEMINI_MODEL, SAMPLES_DIR
from src.packcheck.engine import run_compliance_check
from src.packcheck.llm.prompts import QA_PROMPT, RULE_CHECK_PROMPT


def _cache_key(prompt: str, content: str, model: str) -> str:
    data = f"{model}:::{prompt}:::{content}".encode()
    return hashlib.sha256(data).hexdigest()


def warm_demo_cache() -> None:
    """Pre-compute and write disk cache for demo sample files."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    art_path = SAMPLES_DIR / "DancingFish_Granola_Berry_US_Carton.pdf"
    sheet_path = SAMPLES_DIR / "DancingFish_Granola_BerryCrunch_US_Content_Sheet.xlsx"

    print("Pre-warming demo cache for sample files...")

    # Run check
    report, art, approved = run_compliance_check(
        artwork_path=art_path,
        content_sheet_path=sheet_path,
        enable_semantic=False,
        enable_vision=False,
    )

    # 1. Pre-warm Q&A Cache for the Honey vs Vegan finding
    vegan_finding = None
    for f in report.findings:
        if "VEGAN" in f.id:
            vegan_finding = f
            break

    if vegan_finding:
        q1 = "Why does honey conflict with certified vegan?"
        a1 = (
            "According to official vegan certification standards (such as Vegan.org) and FDA labeling guidelines, "
            "honey is an animal-derived food product produced by bees. The product artwork explicitly displays the "
            "'Certified Vegan' certification mark on the front panel while the ingredient list specifies 'Honey (1%)' "
            "(and 'Honey (9%)' in the formulation sheet). Because vegan standards prohibit all animal-derived ingredients, "
            "the packaging cannot claim 'Certified Vegan' while containing honey."
        )

        key_qa = _cache_key(
            QA_PROMPT.format(
                finding_id=vegan_finding.id,
                finding_title=vegan_finding.title,
                verdict=vegan_finding.verdict,
                why_it_matters=vegan_finding.why_it_matters,
                evidence_details="[Evidence 1] Artwork text: 'Claim: 'Certified Vegan' | Ingredient: 'Honey''",
                rule_context="[FDA-CLM-002] Vegan Claim Consistency with Ingredients: A food labeled as 'Certified Vegan' must not contain animal-derived ingredients such as honey.",
                user_question=q1,
            ),
            f"Q: {q1}",
            f"{GEMINI_MODEL}_text",
        )
        with open(CACHE_DIR / f"{key_qa}.json", "w", encoding="utf-8") as f:
            json.dump({"answer": a1}, f, indent=2)

    # 2. Pre-warm Organic rule check response
    organic_prompt = RULE_CHECK_PROMPT.format(
        rule_id="FDA-CLM-003",
        rule_title="Organic Certification Documentation",
        rule_source="USDA NOP 7 CFR Part 205",
        rule_requirement="Products claiming 'USDA Organic' must identify the certifying agent on the information panel.",
        artwork_evidence="USDA Organic; Certified Vegan (vegan.org); No Added Sugar; Oven Baked; GMO Free",
        approved_context="Product: Granola Berry Crunch\nClaims: USDA Organic, Certified Vegan, No Added Sugar",
    )
    key_org = _cache_key(
        organic_prompt, "Verify rule FDA-CLM-003: Organic Certification Documentation", GEMINI_MODEL
    )
    res_org = {
        "verdict": "NEEDS_REVIEW",
        "confidence": 0.85,
        "quoted_artwork_text": "USDA Organic",
        "quoted_rule_text": "Products claiming 'USDA Organic' must identify the certifying agent on the information panel.",
        "reasoning": "Artwork displays the USDA Organic seal, but the name of the certifying agent (e.g. 'Certified organic by QAI') is not legible on the informational dieline panel.",
        "needs_human_because": "Inspect information panel to confirm accredited organic certifier name is present before print release.",
    }
    with open(CACHE_DIR / f"{key_org}.json", "w", encoding="utf-8") as f:
        json.dump(res_org, f, indent=2)

    print(f"Pre-warmed demo cache written to {CACHE_DIR.resolve()}.")


if __name__ == "__main__":
    warm_demo_cache()
