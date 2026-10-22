"""Tests for real sample artwork PDF ingestion."""

import pytest

from src.packcheck.config import SAMPLES_DIR
from src.packcheck.ingest.artwork import ingest_artwork_pdf
from src.packcheck.ingest.nutrition_parser import parse_artwork_nutrition


def test_real_artwork_pdf_ingestion():
    """Verify ingestion of DancingFish_Granola_Berry_US_Carton.pdf."""
    pdf_path = SAMPLES_DIR / "DancingFish_Granola_Berry_US_Carton.pdf"
    if not pdf_path.exists():
        pytest.skip("Sample artwork PDF not found.")

    doc = ingest_artwork_pdf(pdf_path)
    assert doc.num_pages == 1
    assert len(doc.text_blocks) > 30
    assert len(doc.guide_blocks) > 5

    full_text = "\n".join(b.text for b in doc.text_blocks).lower()
    assert "nutrition facts" in full_text
    assert "480g" in full_text
    assert "ingredients:" in full_text
    assert "dancing fish" in full_text

    nut = parse_artwork_nutrition(doc)
    assert nut is not None
    assert nut.calories == 166.0
    assert nut.servings_per_container == 8.0
    assert "total_fat" in nut.nutrients
    assert nut.nutrients["total_fat"].amount == 15.0
    assert "trans_fat" in nut.nutrients
    assert nut.nutrients["trans_fat"].amount == 8.0
