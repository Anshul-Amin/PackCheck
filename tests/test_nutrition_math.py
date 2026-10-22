"""Tests for deterministic nutrition mathematics checks."""

from src.packcheck.checks.deterministic.nutrition_math import NutritionMathCheck
from src.packcheck.models import ApprovedData, ArtworkDoc, NutritionData, NutritionItem


def _make_sample_doc(nut: NutritionData) -> ArtworkDoc:
    doc = ArtworkDoc(filename="test.pdf")
    doc.nutrition = nut
    return doc


def test_trans_fat_exceeds_total_fat():
    """Verify that trans fat > total fat triggers a FAIL finding."""
    nut = NutritionData(
        calories=200,
        nutrients={
            "total_fat": NutritionItem(name="Total Fat", amount=5.0, unit="g"),
            "trans_fat": NutritionItem(name="Trans Fat", amount=8.0, unit="g"),
        },
    )
    chk = NutritionMathCheck()
    findings = chk.run(_make_sample_doc(nut), ApprovedData(), [])
    fail_ids = [f.id for f in findings if f.verdict == "FAIL"]
    assert "MATH-TRANS-EXCEEDS-FAT" in fail_ids


def test_fat_subcomponents_exceed_total_fat():
    """Verify that sat_fat + trans_fat > total_fat triggers a FAIL finding."""
    nut = NutritionData(
        calories=200,
        nutrients={
            "total_fat": NutritionItem(name="Total Fat", amount=10.0, unit="g"),
            "saturated_fat": NutritionItem(name="Saturated Fat", amount=7.0, unit="g"),
            "trans_fat": NutritionItem(name="Trans Fat", amount=5.0, unit="g"),
        },
    )
    chk = NutritionMathCheck()
    findings = chk.run(_make_sample_doc(nut), ApprovedData(), [])
    fail_ids = [f.id for f in findings if f.verdict == "FAIL"]
    assert "MATH-FAT-SUBCOMPONENTS-EXCEED" in fail_ids


def test_sugars_exceed_carbohydrates():
    """Verify that sugars > total carbs triggers a FAIL finding."""
    nut = NutritionData(
        calories=200,
        nutrients={
            "total_carbohydrate": NutritionItem(name="Total Carbohydrate", amount=15.0, unit="g"),
            "total_sugars": NutritionItem(name="Total Sugars", amount=18.0, unit="g"),
        },
    )
    chk = NutritionMathCheck()
    findings = chk.run(_make_sample_doc(nut), ApprovedData(), [])
    fail_ids = [f.id for f in findings if f.verdict == "FAIL"]
    assert "MATH-SUGARS-EXCEEDS-CARB" in fail_ids


def test_dv_discrepancy_check():
    """Verify that a large discrepancy in printed %DV vs FDA reference %DV fails."""
    # Total fat 15g against FDA 78g reference is 19.2% DV. Printed 2.2% should FAIL.
    nut = NutritionData(
        calories=200,
        nutrients={
            "total_fat": NutritionItem(name="Total Fat", amount=15.0, unit="g", dv_percent=2.2),
        },
    )
    chk = NutritionMathCheck()
    findings = chk.run(_make_sample_doc(nut), ApprovedData(), [])
    fail_ids = [f.id for f in findings if f.verdict == "FAIL"]
    assert "MATH-DV-MISMATCH-TOTAL_FAT" in fail_ids


def test_servings_math_mismatch():
    """Verify servings * serving_size vs net_weight mismatch triggers NEEDS_REVIEW due to unconfirmed units."""
    nut = NutritionData(
        servings_per_container=8.0,
        serving_size_g=85.0,  # 8 * 85 = 680g
    )
    approved = ApprovedData(net_weight_g=480.0)
    chk = NutritionMathCheck()
    findings = chk.run(_make_sample_doc(nut), approved, [])
    review_ids = [f.id for f in findings if f.verdict == "NEEDS_REVIEW"]
    assert "MATH-SERVING-NET-MISMATCH" in review_ids
