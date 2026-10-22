"""Tests for dieline filter identifying technical print-guide markers."""

from src.packcheck.ingest.dieline_filter import is_guide_text


def test_dieline_guide_patterns():
    """Verify standard printer annotations are identified as guide text."""
    assert is_guide_text("Art orientation") is True
    assert is_guide_text("Orientation") is True
    assert is_guide_text("Copy free") is True
    assert is_guide_text("Front panel") is True
    assert is_guide_text("Back panel") is True
    assert is_guide_text("Left panel") is True
    assert is_guide_text("Right panel") is True
    assert is_guide_text("Bottom panel") is True
    assert is_guide_text("Principal Display Panel") is True
    assert is_guide_text("Packaging powered by Esko") is True
    assert is_guide_text("gl1") is True
    assert is_guide_text("2,1M2S1I0O0 1B2") is True


def test_real_packaging_copy_not_filtered():
    """Verify actual marketing and regulatory packaging copy is not marked as guide text."""
    assert is_guide_text("Nutrition Facts") is False
    assert is_guide_text("Granola Berry Crunch") is False
    assert is_guide_text("INGREDIENTS: Organic Oats, Almonds") is False
    assert is_guide_text("Net Wt 480g") is False
    assert is_guide_text("Certified Vegan") is False
    assert is_guide_text("Start tapping, swishing & shaking your tail fins!") is False
