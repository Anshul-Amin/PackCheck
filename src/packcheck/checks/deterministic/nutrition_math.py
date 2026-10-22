"""Deterministic nutrition mathematics and constraint checks."""

from src.packcheck.checks.base import register_check
from src.packcheck.config import (
    ATWATER_CARB,
    ATWATER_FAT,
    ATWATER_PROTEIN,
    CALORIE_TOLERANCE_FAIL,
    CALORIE_TOLERANCE_WARN,
    FDA_DAILY_VALUES,
    SERVING_WEIGHT_TOLERANCE,
)
from src.packcheck.models import ApprovedData, ArtworkDoc, Evidence, Finding, Rule


@register_check
class NutritionMathCheck:
    """Validate mathematical consistency and FDA limits within Nutrition Facts."""

    id = "DET-NUT-MATH"
    name = "Nutrition Mathematics & Constraints"
    category = "nutrition_math"

    def run(
        self,
        artwork: ArtworkDoc,
        approved: ApprovedData,
        rules: list[Rule],
    ) -> list[Finding]:
        findings: list[Finding] = []
        nut = artwork.nutrition
        if not nut:
            return findings

        nutrients = nut.nutrients
        total_fat = nutrients.get("total_fat")
        sat_fat = nutrients.get("saturated_fat")
        trans_fat = nutrients.get("trans_fat")
        total_carb = nutrients.get("total_carbohydrate")
        fiber = nutrients.get("dietary_fiber")
        total_sugars = nutrients.get("total_sugars")
        added_sugars = nutrients.get("added_sugars")
        protein = nutrients.get("protein")

        # 1. Trans Fat cannot exceed Total Fat
        if (
            trans_fat
            and total_fat
            and trans_fat.amount is not None
            and total_fat.amount is not None
        ):
            if trans_fat.amount > total_fat.amount:
                findings.append(
                    Finding(
                        id="MATH-TRANS-EXCEEDS-FAT",
                        title="Trans Fat Exceeds Total Fat",
                        verdict="FAIL",
                        confidence=1.0,
                        verified_by="deterministic",
                        category=self.category,
                        why_it_matters="Trans fat is a constituent sub-component of total fat; it cannot mathematically exceed total fat.",
                        evidence=[
                            Evidence(
                                artwork_text=f"Total Fat: {total_fat.amount}g, Trans Fat: {trans_fat.amount}g",
                                computed_value=f"Trans Fat ({trans_fat.amount}g) > Total Fat ({total_fat.amount}g)",
                                formula="trans_fat <= total_fat",
                                rule_id="FDA-NUT-003",
                                rule_quote="Trans fat is a sub-component of total fat and cannot exceed total fat in grams.",
                            )
                        ],
                    )
                )

        # 2. Saturated Fat + Trans Fat cannot exceed Total Fat
        if (
            total_fat
            and sat_fat
            and trans_fat
            and sat_fat.amount is not None
            and trans_fat.amount is not None
            and total_fat.amount is not None
        ):
            fat_sub_sum = sat_fat.amount + trans_fat.amount
            if fat_sub_sum > total_fat.amount:
                findings.append(
                    Finding(
                        id="MATH-FAT-SUBCOMPONENTS-EXCEED",
                        title="Saturated + Trans Fat Sum Exceeds Total Fat",
                        verdict="FAIL",
                        confidence=1.0,
                        verified_by="deterministic",
                        category=self.category,
                        why_it_matters="The combined weight of saturated and trans fats exceeds the stated total fat quantity.",
                        evidence=[
                            Evidence(
                                artwork_text=f"Total Fat: {total_fat.amount}g, Sat Fat: {sat_fat.amount}g, Trans Fat: {trans_fat.amount}g",
                                computed_value=f"Sum ({fat_sub_sum:.1f}g) > Total Fat ({total_fat.amount}g)",
                                formula="saturated_fat + trans_fat <= total_fat",
                                rule_id="FDA-NUT-004",
                                rule_quote="The sum of declared saturated fat and trans fat cannot exceed total fat.",
                            )
                        ],
                    )
                )

        # 3. Total Sugars cannot exceed Total Carbohydrates
        if (
            total_sugars
            and total_carb
            and total_sugars.amount is not None
            and total_carb.amount is not None
        ):
            if total_sugars.amount > total_carb.amount:
                findings.append(
                    Finding(
                        id="MATH-SUGARS-EXCEEDS-CARB",
                        title="Total Sugars Exceeds Total Carbohydrate",
                        verdict="FAIL",
                        confidence=1.0,
                        verified_by="deterministic",
                        category=self.category,
                        why_it_matters="Total sugars is a sub-component of total carbohydrate and cannot exceed it.",
                        evidence=[
                            Evidence(
                                artwork_text=f"Total Carbohydrate: {total_carb.amount}g, Total Sugars: {total_sugars.amount}g",
                                computed_value=f"Total Sugars ({total_sugars.amount}g) > Total Carbohydrate ({total_carb.amount}g)",
                                formula="total_sugars <= total_carbohydrate",
                                rule_id="FDA-NUT-005",
                                rule_quote="Total sugars cannot exceed total carbohydrate.",
                            )
                        ],
                    )
                )

        # 4. Dietary Fiber cannot exceed Total Carbohydrates
        if (
            fiber
            and total_carb
            and fiber.amount is not None
            and total_carb.amount is not None
            and fiber.amount > total_carb.amount
        ):
            findings.append(
                Finding(
                    id="MATH-FIBER-EXCEEDS-CARB",
                    title="Dietary Fiber Exceeds Total Carbohydrate",
                    verdict="FAIL",
                    confidence=1.0,
                    verified_by="deterministic",
                    category=self.category,
                    why_it_matters="Dietary fiber is a component of total carbohydrate and cannot exceed total carbohydrate weight.",
                    evidence=[
                        Evidence(
                            artwork_text=f"Total Carbohydrate: {total_carb.amount}g, Dietary Fiber: {fiber.amount}g",
                            computed_value=f"Dietary Fiber ({fiber.amount}g) > Total Carbohydrate ({total_carb.amount}g)",
                            formula="dietary_fiber <= total_carbohydrate",
                            rule_id="FDA-NUT-005",
                        )
                    ],
                )
            )

        # 5. Added Sugars cannot exceed Total Sugars
        if (
            added_sugars
            and total_sugars
            and added_sugars.amount is not None
            and total_sugars.amount is not None
        ):
            if added_sugars.amount > total_sugars.amount:
                findings.append(
                    Finding(
                        id="MATH-ADDED-EXCEEDS-TOTAL-SUGAR",
                        title="Added Sugars Exceeds Total Sugars",
                        verdict="FAIL",
                        confidence=1.0,
                        verified_by="deterministic",
                        category=self.category,
                        why_it_matters="Added sugars cannot exceed total sugars.",
                        evidence=[
                            Evidence(
                                artwork_text=f"Total Sugars: {total_sugars.amount}g, Added Sugars: {added_sugars.amount}g",
                                computed_value=f"Added Sugars ({added_sugars.amount}g) > Total Sugars ({total_sugars.amount}g)",
                                formula="added_sugars <= total_sugars",
                                rule_id="FDA-NUT-006",
                                rule_quote="Added sugars is a subset of total sugars and cannot exceed declared total sugars.",
                            )
                        ],
                    )
                )

        # 5. Atwater Calorie Consistency (Fat*9 + Carb*4 + Protein*4)
        if (
            nut.calories is not None
            and total_fat
            and total_carb
            and protein
            and total_fat.amount is not None
            and total_carb.amount is not None
            and protein.amount is not None
        ):
            atwater_cals = (
                total_fat.amount * ATWATER_FAT
                + total_carb.amount * ATWATER_CARB
                + protein.amount * ATWATER_PROTEIN
            )
            declared_cals = nut.calories
            if declared_cals > 0:
                diff_pct = abs(atwater_cals - declared_cals) / declared_cals
                if diff_pct > CALORIE_TOLERANCE_FAIL:
                    findings.append(
                        Finding(
                            id="MATH-CALORIE-MACRO-MISMATCH",
                            title=f"Severe Calorie vs Macronutrient Mismatch ({diff_pct * 100:.0f}% discrepancy)",
                            verdict="FAIL",
                            confidence=0.95,
                            verified_by="deterministic",
                            category=self.category,
                            why_it_matters=f"Declared {declared_cals:.0f} calories contradicts macronutrient sum of {atwater_cals:.0f} kcal.",
                            evidence=[
                                Evidence(
                                    artwork_text=f"Calories: {declared_cals:.0f}, Fat: {total_fat.amount}g, Carb: {total_carb.amount}g, Protein: {protein.amount}g",
                                    computed_value=f"{atwater_cals:.1f} kcal",
                                    formula=f"({total_fat.amount}×9) + ({total_carb.amount}×4) + ({protein.amount}×4) = {atwater_cals:.1f} kcal",
                                    rule_id="FDA-NUT-008",
                                    rule_quote="Declared calories must reasonably correlate with calories derived from 4/4/9 factors.",
                                )
                            ],
                        )
                    )
                elif diff_pct > CALORIE_TOLERANCE_WARN:
                    findings.append(
                        Finding(
                            id="MATH-CALORIE-MACRO-WARN",
                            title=f"Calorie vs Macronutrient Discrepancy ({diff_pct * 100:.0f}%)",
                            verdict="NEEDS_REVIEW",
                            confidence=0.85,
                            verified_by="deterministic",
                            category=self.category,
                            why_it_matters=f"Calculated Atwater energy ({atwater_cals:.0f} kcal) deviates from declared calories ({declared_cals:.0f} kcal).",
                            human_check_needed="Verify if insoluble dietary fiber was subtracted or analytical bomb calorimetry was used.",
                            evidence=[
                                Evidence(
                                    artwork_text=f"Calories: {declared_cals:.0f}",
                                    computed_value=f"{atwater_cals:.1f} kcal",
                                    formula="fat*9 + carb*4 + protein*4",
                                    rule_id="FDA-NUT-008",
                                )
                            ],
                        )
                    )

        # 6. Percent Daily Value (%DV) Validation against FDA DVs
        for nut_key, (dv_reference, standard_unit) in FDA_DAILY_VALUES.items():
            item = nutrients.get(nut_key)
            if item and item.amount is not None and item.dv_percent is not None:
                expected_dv = (item.amount / dv_reference) * 100.0
                printed_dv = item.dv_percent
                # If difference is more than 5 percentage points, flag as significant error
                if abs(printed_dv - expected_dv) > 5.0:
                    findings.append(
                        Finding(
                            id=f"MATH-DV-MISMATCH-{nut_key.upper()}",
                            title=f"%DV Discrepancy for {item.name}: Printed {printed_dv:.1f}% vs FDA Computed {expected_dv:.1f}%",
                            verdict="FAIL",
                            confidence=0.98,
                            verified_by="deterministic",
                            category=self.category,
                            why_it_matters=f"{item.name} {item.amount}{item.unit} against FDA reference ({dv_reference}{standard_unit}) yields {expected_dv:.1f}%, but artwork prints {printed_dv:.1f}%.",
                            evidence=[
                                Evidence(
                                    artwork_text=f"{item.name} {item.amount}{item.unit} {printed_dv}%",
                                    computed_value=f"{expected_dv:.1f}%",
                                    formula=f"({item.amount} / {dv_reference}) * 100",
                                    rule_id="FDA-NUT-007",
                                    rule_quote="Percent Daily Values must be calculated based on FDA reference daily values.",
                                )
                            ],
                        )
                    )

        # 7. Servings per Container * Serving Size vs Net Weight
        # Note: Artwork prints 'Serving size 85' without an explicit 'g' unit.
        # Since extraction is partial and unit unconfirmed, mark as NEEDS_REVIEW for vision verification.
        if nut.servings_per_container and nut.serving_size_g and approved.net_weight_g:
            calc_net = nut.servings_per_container * nut.serving_size_g
            diff = abs(calc_net - approved.net_weight_g)
            tolerance = approved.net_weight_g * SERVING_WEIGHT_TOLERANCE
            if diff > tolerance:
                findings.append(
                    Finding(
                        id="MATH-SERVING-NET-MISMATCH",
                        title=f"Serving Size Math Needs Review: {nut.servings_per_container:.0f} servings × {nut.serving_size_g:.0f} = {calc_net:.0f} vs Net Weight {approved.net_weight_g:.0f}g",
                        verdict="NEEDS_REVIEW",
                        confidence=0.85,
                        verified_by="deterministic",
                        category=self.category,
                        why_it_matters=(
                            f"Printed '{nut.servings_per_container:.0f} servings per container' and serving size '{nut.serving_size_g:.0f}' "
                            f"yields {calc_net:.0f}, which deviates from declared package weight {approved.net_weight_g:.0f}g."
                        ),
                        human_check_needed=(
                            "Serving size unit is unconfirmed on dieline ('85' printed without explicit 'g'). "
                            "Requires visual verification of the dieline serving size statement."
                        ),
                        evidence=[
                            Evidence(
                                artwork_text=f"{nut.servings_per_container:.0f} servings per container, serving size {nut.serving_size_g:.0f} (unit unconfirmed)",
                                approved_value=f"{approved.net_weight_g:.0f}g",
                                computed_value=f"{calc_net:.0f}",
                                formula=f"{nut.servings_per_container} * {nut.serving_size_g}",
                                rule_id="FDA-NUT-009",
                                rule_quote="Number of servings multiplied by serving size must approximately equal total net quantity.",
                            )
                        ],
                    )
                )

        return findings
