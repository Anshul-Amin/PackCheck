"""Tests for real sample content sheet parsing."""

import pytest

from src.packcheck.config import SAMPLES_DIR
from src.packcheck.ingest.contentsheet import ingest_content_sheet


def test_real_content_sheet_ingestion():
    """Verify ingestion of DancingFish_Granola_BerryCrunch_US_Content_Sheet.xlsx."""
    sheet_path = SAMPLES_DIR / "DancingFish_Granola_BerryCrunch_US_Content_Sheet.xlsx"
    if not sheet_path.exists():
        pytest.skip("Sample content sheet not found.")

    data = ingest_content_sheet(sheet_path)
    assert data.product_name == "Granola Berry Crunch"
    assert data.net_weight_g == 480.0
    assert data.upc == "1 20000 00003 6"
    assert len(data.ingredients) > 5
    assert "Almonds" in data.ingredients
    assert "Pecans" in data.ingredients
    assert len(data.allergens) > 0
    assert data.nutrition is not None
    assert data.nutrition.calories == 166.0
    assert "trans_fat" in data.nutrition.nutrients
    assert data.nutrition.nutrients["trans_fat"].amount == 8.0
