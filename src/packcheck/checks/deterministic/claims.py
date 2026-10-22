"""Deterministic marketing and regulatory claim checks."""

import re

from src.packcheck.checks.base import register_check
from src.packcheck.models import ApprovedData, ArtworkDoc, Evidence, Finding, Rule

SWEETENERS = {
    "honey",
    "coconut sugar",
    "cane sugar",
    "sugar",
    "brown sugar",
    "maple syrup",
    "agave",
    "corn syrup",
    "molasses",
}

ANIMAL_DERIVED = {
    "honey",
    "beeswax",
    "milk",
    "whey",
    "casein",
    "gelatin",
    "carmine",
    "egg",
    "eggs",
}


@register_check
class ClaimsCheck:
    """Validate truthfulness and regulatory consistency of packaging claims."""

    id = "DET-CLAIMS"
    name = "Product Claims Consistency"
    category = "claims"

    def run(
        self,
        artwork: ArtworkDoc,
        approved: ApprovedData,
        rules: list[Rule],
    ) -> list[Finding]:
        findings: list[Finding] = []
        full_artwork_text = "\n".join(b.text for b in artwork.text_blocks)
        norm_text = full_artwork_text.lower()

        # Find ingredient list text
        ing_text = ""
        ing_bbox = None
        for b in artwork.text_blocks:
            if "ingredients:" in b.text.lower():
                ing_text = b.text.lower()
                ing_bbox = b.bbox
                break

        # 1. "No Added Sugar" Claim vs Ingredients & Nutrition
        # Check approved claims as well as artwork text (accounting for stacked badges like NO / ADDED / SUGAR)
        has_approved_no_sugar = any("no added sugar" in c.lower() for c in approved.claims)
        has_art_no_sugar = (
            "no added sugar" in norm_text
            or "no added sugars" in norm_text
            or ("no" in norm_text and "added" in norm_text and "sugar" in norm_text)
        )
        has_no_added_sugar_claim = has_approved_no_sugar or has_art_no_sugar
        if has_no_added_sugar_claim and ing_text:
            found_sweeteners = [s for s in SWEETENERS if re.search(rf"\b{s}\b", ing_text)]
            if found_sweeteners:
                sweetener_names = ", ".join(f"'{s.title()}'" for s in found_sweeteners)
                findings.append(
                    Finding(
                        id="CLAIM-NO-ADDED-SUGAR-CONTRADICTION",
                        title=f"'No Added Sugar' Contradiction: Contains Nutritive Sweeteners ({sweetener_names})",
                        verdict="FAIL",
                        confidence=1.0,
                        verified_by="deterministic",
                        category=self.category,
                        why_it_matters=(
                            f"21 CFR 101.60(c)(2) prohibits 'No Added Sugar' claims when nutritive "
                            f"sweeteners like {sweetener_names} are added during processing."
                        ),
                        evidence=[
                            Evidence(
                                artwork_text=f"Claim: 'NO ADDED SUGAR' | Ingredients contain: {sweetener_names}",
                                artwork_bbox=ing_bbox,
                                rule_id="FDA-CLM-001",
                                rule_quote="The claim 'No Added Sugar' may only be made if no sugar or ingredient containing sugar is added.",
                            )
                        ],
                    )
                )

        # 2. "Certified Vegan" Claim vs Honey / Animal Ingredients
        has_vegan_claim = (
            "certified vegan" in norm_text
            or "suitable for vegans" in norm_text
            or "suitable for vegetarians (vegan)" in norm_text
        )
        if has_vegan_claim and ing_text:
            found_animal = [a for a in ANIMAL_DERIVED if re.search(rf"\b{a}\b", ing_text)]
            if found_animal:
                animal_names = ", ".join(f"'{a.title()}'" for a in found_animal)
                findings.append(
                    Finding(
                        id="CLAIM-VEGAN-HONEY-CONFLICT",
                        title=f"'Certified Vegan' Conflict: Contains Animal Product ({animal_names})",
                        verdict="FAIL",
                        confidence=1.0,
                        verified_by="deterministic",
                        category=self.category,
                        why_it_matters=(
                            f"Product claims 'Certified Vegan' / 'Suitable for Vegans' but includes "
                            f"{animal_names} in ingredients. Honey is bee-derived and prohibited under vegan standards."
                        ),
                        evidence=[
                            Evidence(
                                artwork_text=f"Claim: 'Certified Vegan' | Ingredient: {animal_names}",
                                artwork_bbox=ing_bbox,
                                rule_id="FDA-CLM-002",
                                rule_quote="A food labeled as 'Certified Vegan' must not contain animal-derived ingredients such as honey.",
                            )
                        ],
                    )
                )

        # 3. "USDA Organic" Certification Verification Check
        if "organic" in norm_text:
            findings.append(
                Finding(
                    id="CLAIM-ORGANIC-CERT-REVIEW",
                    title="USDA Organic Claim Present: Certifier Statement Required",
                    verdict="NEEDS_REVIEW",
                    confidence=0.90,
                    verified_by="deterministic",
                    category=self.category,
                    why_it_matters="USDA NOP 7 CFR 205 requires identifying the accredited organic certifying agent (e.g. 'Certified Organic by...').",
                    human_check_needed="Verify organic certifying agency name and valid USDA Organic certificate on file.",
                    evidence=[
                        Evidence(
                            artwork_text="USDA Organic / Certified Organic",
                            rule_id="FDA-CLM-003",
                        )
                    ],
                )
            )

        # 4. "GMO Free" Claim Verification Check
        if "gmo free" in norm_text or "non-gmo" in norm_text:
            findings.append(
                Finding(
                    id="CLAIM-GMO-FREE-REVIEW",
                    title="Non-GMO Claim Present: Third-Party Documentation Required",
                    verdict="NEEDS_REVIEW",
                    confidence=0.85,
                    verified_by="deterministic",
                    category=self.category,
                    why_it_matters="FDA voluntary labeling guidance requires verifiable supply chain documentation for non-GE/GMO claims.",
                    human_check_needed="Verify Non-GMO Project certificate or identity preservation affidavits from suppliers.",
                    evidence=[
                        Evidence(
                            artwork_text="GMO FREE",
                            rule_id="FDA-CLM-004",
                        )
                    ],
                )
            )

        return findings
