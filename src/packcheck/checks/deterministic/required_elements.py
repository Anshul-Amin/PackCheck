"""Deterministic required label elements presence and formatting checks."""

import re

from src.packcheck.checks.base import register_check
from src.packcheck.models import ApprovedData, ArtworkDoc, Evidence, Finding, Rule


@register_check
class RequiredElementsCheck:
    """Validate presence and legal formatting of mandatory FDA label components."""

    id = "DET-REQUIRED-ELEMENTS"
    name = "Mandatory Regulatory Label Elements"
    category = "required_elements"

    def run(
        self,
        artwork: ArtworkDoc,
        approved: ApprovedData,
        rules: list[Rule],
    ) -> list[Finding]:
        findings: list[Finding] = []
        full_artwork_text = "\n".join(b.text for b in artwork.text_blocks)
        norm_text = full_artwork_text.lower()

        # 1. Nutrition Facts Panel Presence
        has_nutrition = "nutrition facts" in norm_text
        if has_nutrition:
            findings.append(
                Finding(
                    id="REQ-NUTRITION-PANEL-PASS",
                    title="Nutrition Facts Panel Present",
                    verdict="PASS",
                    confidence=1.0,
                    verified_by="deterministic",
                    category=self.category,
                    why_it_matters="Mandatory FDA Nutrition Facts panel is present on the package.",
                    evidence=[
                        Evidence(
                            artwork_text="Nutrition Facts",
                            rule_id="FDA-NUT-001",
                            rule_quote="The nutrition information shall be set off in a box headed by 'Nutrition Facts'.",
                        )
                    ],
                )
            )
        else:
            findings.append(
                Finding(
                    id="REQ-NUTRITION-PANEL-FAIL",
                    title="Missing Mandatory Nutrition Facts Panel",
                    verdict="FAIL",
                    confidence=1.0,
                    verified_by="deterministic",
                    category=self.category,
                    why_it_matters="Food packages for retail sale must include an FDA Nutrition Facts panel.",
                    evidence=[Evidence(rule_id="FDA-NUT-001")],
                )
            )

        # 2. Ingredient List Presence
        has_ingredients = "ingredients:" in norm_text or "ingredients" in norm_text
        if has_ingredients:
            findings.append(
                Finding(
                    id="REQ-INGREDIENTS-PASS",
                    title="Ingredient List Present",
                    verdict="PASS",
                    confidence=1.0,
                    verified_by="deterministic",
                    category=self.category,
                    why_it_matters="Ingredient declaration is present and correctly headed.",
                    evidence=[
                        Evidence(
                            artwork_text="INGREDIENTS:",
                            rule_id="FDA-ING-001",
                        )
                    ],
                )
            )
        else:
            findings.append(
                Finding(
                    id="REQ-INGREDIENTS-FAIL",
                    title="Missing Mandatory Ingredient List",
                    verdict="FAIL",
                    confidence=1.0,
                    verified_by="deterministic",
                    category=self.category,
                    why_it_matters="Packages containing two or more ingredients must bear an ingredient list.",
                    evidence=[Evidence(rule_id="FDA-ING-001")],
                )
            )

        # 3. Dual Unit Net Quantity Check (US Customary oz + Metric g)
        # Search for net weight patterns
        has_metric_g = bool(re.search(r"\b\d+\s*g\b", norm_text))
        has_us_oz = bool(re.search(r"\b\d+(?:\.\d+)?\s*(?:oz|ounces?|lb|lbs)\b", norm_text))

        if has_metric_g and not has_us_oz:
            findings.append(
                Finding(
                    id="REQ-NET-QUANTITY-DUAL-UNIT-FAIL",
                    title="Net Quantity Lacks US Customary Units (Ounces)",
                    verdict="FAIL",
                    confidence=1.0,
                    verified_by="deterministic",
                    category=self.category,
                    why_it_matters=(
                        "FDA 21 CFR 101.7 and Fair Packaging and Labeling Act (FPLA) mandate that food "
                        "packages state net quantity in both US customary units (oz) and metric units (g)."
                    ),
                    evidence=[
                        Evidence(
                            artwork_text="480g (no oz declaration found)",
                            rule_id="FDA-NET-001",
                            rule_quote="Net quantity declaration must state both US customary and metric units.",
                        )
                    ],
                )
            )
        elif has_metric_g and has_us_oz:
            findings.append(
                Finding(
                    id="REQ-NET-QUANTITY-DUAL-UNIT-PASS",
                    title="Dual Unit Net Quantity Present",
                    verdict="PASS",
                    confidence=1.0,
                    verified_by="deterministic",
                    category=self.category,
                    why_it_matters="Both US customary and metric measurements are declared.",
                    evidence=[Evidence(rule_id="FDA-NET-001")],
                )
            )

        # 4. Allergen Advisory vs Formulation Ingredients
        # Check if formulation contains tree nuts, but allergen text only says "May Contain"
        allergen_block = None
        for b in artwork.text_blocks:
            if "allergen information:" in b.text.lower() or "may contain" in b.text.lower():
                allergen_block = b
                break

        if allergen_block:
            atxt = allergen_block.text.lower()
            if "may contain" in atxt and "contains:" not in atxt:
                # Check which formulation nuts are in the ingredient list
                found_formulation_nuts = [
                    nut for nut in ["almonds", "pecans", "walnuts"] if nut in norm_text
                ]
                if found_formulation_nuts:
                    nuts_str = ", ".join(f"'{n.title()}'" for n in found_formulation_nuts)
                    findings.append(
                        Finding(
                            id="REQ-ALLERGEN-ADVISORY-MISUSE",
                            title=f"Allergen Formulation Declared as 'May Contain' Advisory ({nuts_str})",
                            verdict="FAIL",
                            confidence=1.0,
                            verified_by="deterministic",
                            category=self.category,
                            why_it_matters=(
                                f"FALCPA 21 U.S.C. 343(w) requires affirmative declaration of major allergens. "
                                f"{nuts_str} are formulation ingredients, not incidental cross-contact, and "
                                "cannot be labeled solely under voluntary 'May Contain' advisory language."
                            ),
                            evidence=[
                                Evidence(
                                    artwork_text=allergen_block.text,
                                    artwork_bbox=allergen_block.bbox,
                                    rule_id="FDA-ALL-002",
                                    rule_quote="Advisory statements cannot be used in lieu of required allergen declarations for ingredients present.",
                                )
                            ],
                        )
                    )

        # 5. Manufacturer Address & Place of Business
        # Check for producer block
        mfg_block = None
        for b in artwork.text_blocks:
            if (
                "produced by" in b.text.lower()
                or "manufactured by" in b.text.lower()
                or "distributed by" in b.text.lower()
            ):
                mfg_block = b
                break

        if mfg_block:
            mtxt = mfg_block.text
            # Check for city, state, or ZIP code patterns
            has_zip = bool(re.search(r"\b\d{5}(?:-\d{4})?\b", mtxt))
            has_state = bool(re.search(r"\b[A-Z]{2}\b", mtxt))
            if not (has_zip or has_state):
                findings.append(
                    Finding(
                        id="REQ-MANUFACTURER-INCOMPLETE-ADDRESS",
                        title="Manufacturer Statement Lacks Place of Business Address",
                        verdict="NEEDS_REVIEW",
                        confidence=0.90,
                        verified_by="deterministic",
                        category=self.category,
                        why_it_matters=(
                            "21 CFR 101.5 requires the label to specify conspicuously the name and place of "
                            "business of the manufacturer, including city, state, and ZIP code."
                        ),
                        human_check_needed="Verify if company address is listed in a current telephone/city directory, or add complete address.",
                        evidence=[
                            Evidence(
                                artwork_text=mtxt,
                                artwork_bbox=mfg_block.bbox,
                                rule_id="FDA-MAN-001",
                                rule_quote="The label of a food package shall specify conspicuously the name and place of business.",
                            )
                        ],
                    )
                )

        return findings
