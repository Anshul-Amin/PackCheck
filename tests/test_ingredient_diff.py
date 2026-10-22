"""Tests for ingredient normalization and discrepancy detection."""

from src.packcheck.checks.deterministic.consistency import ConsistencyCheck
from src.packcheck.ingest.contentsheet import _clean_ingredients_list
from src.packcheck.models import ApprovedData, ArtworkDoc, TextBlock


def test_clean_ingredients_list():
    """Verify parsing of comma-separated ingredient strings with parenthetical commas."""
    raw = "INGREDIENTS: Organic Oats (79%), Almonds, Vegetable Oil (Soy, Corn), Honey (9%)."
    items = _clean_ingredients_list(raw)
    assert len(items) == 4
    assert items[0] == "Organic Oats (79%)"
    assert items[1] == "Almonds"
    assert items[2] == "Vegetable Oil (Soy, Corn)"
    assert items[3] == "Honey (9%)"


def test_duplicate_ingredient_detection():
    """Verify that duplicate ingredients in formulation or artwork are flagged."""
    approved = ApprovedData(
        ingredients=["Oats", "Sunflower Seeds", "Cranberries", "Sunflower Seeds"],
    )
    chk = ConsistencyCheck()
    doc = ArtworkDoc(filename="art.pdf")
    findings = chk.run(doc, approved, [])
    fail_ids = [f.id for f in findings if f.verdict == "FAIL"]
    assert "CONSIST-DUPLICATE-APPROVED-SUNFLOWER_SEEDS" in fail_ids


def test_honey_percentage_mismatch():
    """Verify honey percentage difference between artwork and approved sheet is flagged."""
    approved = ApprovedData(
        raw_ingredients_text="Ingredients: Oats, Honey (9%), Salt.",
    )
    doc = ArtworkDoc(
        filename="art.pdf",
        text_blocks=[
            TextBlock(
                text="INGREDIENTS: Oats, Honey (1%), Salt.",
                bbox=(10, 10, 100, 100),
            )
        ],
    )
    chk = ConsistencyCheck()
    findings = chk.run(doc, approved, [])
    fail_ids = [f.id for f in findings if f.verdict == "FAIL"]
    assert "CONSIST-HONEY-PCT-MISMATCH" in fail_ids
