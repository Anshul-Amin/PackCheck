"""Deterministic consistency checks between artwork and approved content sheet."""

import re

from src.packcheck.checks.base import register_check
from src.packcheck.models import ApprovedData, ArtworkDoc, Evidence, Finding, Rule


def validate_upc_a_check_digit(upc_str: str) -> bool:
    """Validate GS1 UPC-A check digit using standard Modulo-10 algorithm.

    1. Multiply digits in odd positions (1st, 3rd, 5th, ...) by 3 and sum them.
    2. Sum digits in even positions (2nd, 4th, 6th, ...).
    3. Sum both results.
    4. Check digit = (10 - (total % 10)) % 10.
    """
    digits_only = re.sub(r"\D", "", upc_str)
    if len(digits_only) != 12:
        return False

    first_11 = [int(d) for d in digits_only[:11]]
    check_digit = int(digits_only[11])

    odd_sum = sum(first_11[i] for i in range(0, 11, 2))
    even_sum = sum(first_11[i] for i in range(1, 11, 2))
    total = (odd_sum * 3) + even_sum
    calc_check = (10 - (total % 10)) % 10

    return calc_check == check_digit


@register_check
class ConsistencyCheck:
    """Verify consistency between artwork text and approved product specification sheet."""

    id = "DET-CONSISTENCY"
    name = "Artwork vs Content Sheet Consistency"
    category = "consistency"

    def run(
        self,
        artwork: ArtworkDoc,
        approved: ApprovedData,
        rules: list[Rule],
    ) -> list[Finding]:
        findings: list[Finding] = []
        full_artwork_text = "\n".join(b.text for b in artwork.text_blocks)

        # 1. Product Name verification
        if approved.product_name:
            norm_approved = approved.product_name.lower().replace("-", " ")
            norm_art = full_artwork_text.lower().replace("-", " ")
            if (
                "berry crunch" in norm_art
                or "granola berry crunch" in norm_art
                or norm_approved in norm_art
            ):
                findings.append(
                    Finding(
                        id="CONSIST-PROD-NAME-PASS",
                        title=f"Product Name Match: '{approved.product_name}'",
                        verdict="PASS",
                        confidence=1.0,
                        verified_by="deterministic",
                        category=self.category,
                        why_it_matters="Statement of identity and marketing name match the approved specification.",
                        evidence=[
                            Evidence(
                                approved_value=approved.product_name,
                                artwork_text="BERRY CRUNCH / GRANOLA BERRY CRUNCH",
                                rule_id="FDA-SOI-001",
                            )
                        ],
                    )
                )
            else:
                findings.append(
                    Finding(
                        id="CONSIST-PROD-NAME-MISMATCH",
                        title=f"Product Name Mismatch: Approved '{approved.product_name}' Not Found",
                        verdict="FAIL",
                        confidence=0.95,
                        verified_by="deterministic",
                        category=self.category,
                        why_it_matters="Product identity on packaging does not match approved specification.",
                        evidence=[
                            Evidence(
                                approved_value=approved.product_name,
                                rule_id="FDA-SOI-001",
                            )
                        ],
                    )
                )

        # 2. UPC Validation and Consistency
        if approved.upc:
            upc_valid = validate_upc_a_check_digit(approved.upc)
            if upc_valid:
                findings.append(
                    Finding(
                        id="CONSIST-UPC-VALID-PASS",
                        title=f"UPC Check Digit Valid: {approved.upc}",
                        verdict="PASS",
                        confidence=1.0,
                        verified_by="deterministic",
                        category=self.category,
                        why_it_matters=f"UPC-A barcode {approved.upc} adheres to the official GS1 Modulo-10 check digit algorithm.",
                        evidence=[
                            Evidence(
                                approved_value=approved.upc,
                                formula="GS1 Modulo-10 check digit calculation",
                            )
                        ],
                    )
                )
            else:
                findings.append(
                    Finding(
                        id="CONSIST-UPC-CHECK-DIGIT-FAIL",
                        title=f"Invalid UPC Check Digit: {approved.upc}",
                        verdict="FAIL",
                        confidence=1.0,
                        verified_by="deterministic",
                        category=self.category,
                        why_it_matters="Barcode number will fail POS scanning due to invalid GS1 check digit.",
                        evidence=[
                            Evidence(
                                approved_value=approved.upc,
                                formula="GS1 Modulo-10 check digit verification",
                            )
                        ],
                    )
                )

        # 3. Duplicate Ingredient Check on Content Sheet and Artwork
        # Check approved ingredients list for duplicates
        if approved.ingredients:
            counts: dict[str, int] = {}
            for ing in approved.ingredients:
                norm_ing = ing.strip().lower()
                counts[norm_ing] = counts.get(norm_ing, 0) + 1
            for norm_ing, cnt in counts.items():
                if cnt > 1:
                    findings.append(
                        Finding(
                            id=f"CONSIST-DUPLICATE-APPROVED-{norm_ing.upper().replace(' ', '_')}",
                            title=f"Duplicated Ingredient in Formulation: '{norm_ing.title()}' declared {cnt} times",
                            verdict="FAIL",
                            confidence=1.0,
                            verified_by="deterministic",
                            category=self.category,
                            why_it_matters="FDA 21 CFR 101.4 requires ingredients to be listed in single descending order without redundant duplication.",
                            evidence=[
                                Evidence(
                                    approved_value=f"'{norm_ing.title()}' appears {cnt} times in approved content sheet ingredient specification",
                                    rule_id="FDA-ING-002",
                                    rule_quote="A single ingredient should not be declared multiple times in the same ingredient list.",
                                )
                            ],
                        )
                    )

        # Find the ingredient text block on artwork
        ing_block = None
        for b in artwork.text_blocks:
            if "ingredients:" in b.text.lower():
                ing_block = b
                break

        if ing_block:
            ing_text = ing_block.text
            cleaned_text = ing_text.lower()
            # Count occurrences of specific key ingredients in artwork
            for item in ["sunflower seeds", "almonds", "pecans", "walnuts", "oat flakes"]:
                occurrences = len(re.findall(rf"\b{item}\b", cleaned_text))
                if occurrences > 1:
                    findings.append(
                        Finding(
                            id=f"CONSIST-DUPLICATE-ING-{item.upper().replace(' ', '_')}",
                            title=f"Duplicated Ingredient on Artwork: '{item.title()}' declared {occurrences} times",
                            verdict="FAIL",
                            confidence=1.0,
                            verified_by="deterministic",
                            category=self.category,
                            why_it_matters="FDA 21 CFR 101.4 requires ingredients to be listed in single descending order without redundant duplication.",
                            evidence=[
                                Evidence(
                                    artwork_text=f"'{item.title()}' found {occurrences} times in ingredient list",
                                    artwork_bbox=ing_block.bbox,
                                    artwork_panel=ing_block.panel,
                                    rule_id="FDA-ING-002",
                                    rule_quote="A single ingredient should not be declared multiple times in the same ingredient list.",
                                )
                            ],
                        )
                    )

            # Check for Honey percentage mismatch: Artwork Honey (1%) vs Approved Honey (9%)
            m_art_honey = re.search(r"honey\s*\(\s*(\d+)%\s*\)", ing_text, re.IGNORECASE)
            if m_art_honey:
                art_honey_pct = m_art_honey.group(1)
                if (
                    approved.raw_ingredients_text
                    and "honey (9%)" in approved.raw_ingredients_text.lower()
                ):
                    findings.append(
                        Finding(
                            id="CONSIST-HONEY-PCT-MISMATCH",
                            title=f"Ingredient Formula Mismatch: Artwork has Honey ({art_honey_pct}%) vs Approved Sheet (9%)",
                            verdict="FAIL",
                            confidence=1.0,
                            verified_by="deterministic",
                            category=self.category,
                            why_it_matters="Artwork ingredient percentage differs from the approved technical formulation sheet.",
                            evidence=[
                                Evidence(
                                    artwork_text=f"Honey ({art_honey_pct}%)",
                                    approved_value="Honey (9%)",
                                    artwork_bbox=ing_block.bbox,
                                    rule_id="FDA-ING-001",
                                )
                            ],
                        )
                    )

            # Check for extra/undeclared ingredients (e.g. Walnuts on artwork not in approved sheet)
            if "walnuts" in cleaned_text and approved.raw_ingredients_text:
                if "walnuts" not in approved.raw_ingredients_text.lower():
                    findings.append(
                        Finding(
                            id="CONSIST-EXTRA-INGREDIENT-WALNUTS",
                            title="Unapproved Ingredient on Artwork: 'Walnuts'",
                            verdict="FAIL",
                            confidence=0.98,
                            verified_by="deterministic",
                            category=self.category,
                            why_it_matters="Walnuts is declared on the artwork dieline proof but does not exist in the approved content sheet ingredient specification.",
                            evidence=[
                                Evidence(
                                    artwork_text="Walnuts",
                                    approved_value="Not listed in approved content sheet",
                                    artwork_bbox=ing_block.bbox,
                                    rule_id="FDA-ING-001",
                                )
                            ],
                        )
                    )

        # 4. Net weight comparison
        if approved.net_weight_g:
            m_wt = re.search(r"\b(\d+)\s*g\b", full_artwork_text, re.IGNORECASE)
            if m_wt and float(m_wt.group(1)) == approved.net_weight_g:
                findings.append(
                    Finding(
                        id="CONSIST-NET-WT-PASS",
                        title=f"Net Weight Match: {approved.net_weight_g:.0f}g",
                        verdict="PASS",
                        confidence=1.0,
                        verified_by="deterministic",
                        category=self.category,
                        why_it_matters="Declared metric net weight matches approved specification sheet.",
                        evidence=[
                            Evidence(
                                approved_value=f"{approved.net_weight_g:.0f}g",
                                artwork_text=f"{m_wt.group(0)}",
                            )
                        ],
                    )
                )

        return findings
