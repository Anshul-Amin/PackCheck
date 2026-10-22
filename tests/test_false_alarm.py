"""Test false alarm prevention on a clean, compliant synthetic label fixture."""

from src.packcheck.checks.deterministic.claims import ClaimsCheck
from src.packcheck.checks.deterministic.consistency import ConsistencyCheck
from src.packcheck.checks.deterministic.nutrition_math import NutritionMathCheck
from src.packcheck.checks.deterministic.required_elements import RequiredElementsCheck
from src.packcheck.models import (
    ApprovedData,
    ArtworkDoc,
    NutritionData,
    NutritionItem,
    TextBlock,
)


def test_clean_synthetic_label_produces_zero_fails():
    """Verify that a compliant label fixture generates 0 FAIL findings."""
    # Compliant Nutrition Data:
    # Fat 10g (90 kcal), Carb 20g (80 kcal), Protein 10g (40 kcal) = 210 kcal
    # %DVs: Fat 10/78=12.8%, Carb 20/275=7.3%, Fiber 4/28=14.3%
    nut = NutritionData(
        servings_per_container=4.0,
        serving_size_g=50.0,
        calories=210.0,
        nutrients={
            "total_fat": NutritionItem(name="Total Fat", amount=10.0, unit="g", dv_percent=13.0),
            "saturated_fat": NutritionItem(
                name="Saturated Fat", amount=2.0, unit="g", dv_percent=10.0
            ),
            "trans_fat": NutritionItem(name="Trans Fat", amount=0.0, unit="g"),
            "total_carbohydrate": NutritionItem(
                name="Total Carbohydrate", amount=20.0, unit="g", dv_percent=7.0
            ),
            "dietary_fiber": NutritionItem(
                name="Dietary Fiber", amount=4.0, unit="g", dv_percent=14.0
            ),
            "total_sugars": NutritionItem(name="Total Sugars", amount=5.0, unit="g"),
            "added_sugars": NutritionItem(
                name="Added Sugars", amount=0.0, unit="g", dv_percent=0.0
            ),
            "protein": NutritionItem(name="Protein", amount=10.0, unit="g"),
            "sodium": NutritionItem(name="Sodium", amount=115.0, unit="mg", dv_percent=5.0),
        },
    )

    approved = ApprovedData(
        product_name="Golden Granola",
        net_weight_g=200.0,
        upc="049000028904",  # Valid UPC
        ingredients=["Rolled Oats", "Almonds", "Cinnamon", "Sea Salt"],
        raw_ingredients_text="Ingredients: Rolled Oats, Almonds, Cinnamon, Sea Salt.",
        allergens=["Contains: Almonds."],
        claims=["All Natural"],
    )

    text_blocks = [
        TextBlock(text="Golden Granola", bbox=(10, 10, 100, 30)),
        TextBlock(
            text="Nutrition Facts\n4 servings per container\nServing size 50g\nCalories 210",
            bbox=(10, 40, 100, 150),
        ),
        TextBlock(
            text="INGREDIENTS: Rolled Oats, Almonds, Cinnamon, Sea Salt.", bbox=(10, 160, 100, 200)
        ),
        TextBlock(text="CONTAINS: Almonds.", bbox=(10, 210, 100, 230)),
        TextBlock(text="Net Wt 7.05 oz (200 g)", bbox=(10, 240, 100, 260)),
        TextBlock(
            text="Distributed by Acme Foods LLC, 100 Market St, Austin, TX 78701",
            bbox=(10, 270, 100, 300),
        ),
    ]

    doc = ArtworkDoc(filename="clean_art.pdf", text_blocks=text_blocks)
    doc.nutrition = nut

    all_findings = []
    for chk in [NutritionMathCheck(), ConsistencyCheck(), ClaimsCheck(), RequiredElementsCheck()]:
        findings = chk.run(doc, approved, [])
        all_findings.extend(findings)

    fail_findings = [f for f in all_findings if f.verdict == "FAIL"]
    assert len(fail_findings) == 0, f"False alarms detected: {[f.title for f in fail_findings]}"
