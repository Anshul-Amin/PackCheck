"""End-to-end golden verification test on the real DancingFish sample files."""

import pytest

from src.packcheck.config import SAMPLES_DIR
from src.packcheck.engine import run_compliance_check


def test_golden_sample_compliance_check():
    """Verify end-to-end execution on real sample files and assert key expected compliance issues."""
    art_path = SAMPLES_DIR / "DancingFish_Granola_Berry_US_Carton.pdf"
    sheet_path = SAMPLES_DIR / "DancingFish_Granola_BerryCrunch_US_Content_Sheet.xlsx"

    if not art_path.exists() or not sheet_path.exists():
        pytest.skip("Sample files not found.")

    report, art, approved = run_compliance_check(
        artwork_path=art_path,
        content_sheet_path=sheet_path,
        enable_semantic=False,  # Test deterministic core without network dependency
        enable_vision=False,
    )

    # 1. Artwork must not be approved for printing
    assert report.ready_to_print is False
    assert report.fail_count > 0

    finding_ids = {f.id for f in report.findings}

    # 2. Servings x serving size vs 480g net weight flagged for review
    assert "MATH-SERVING-NET-MISMATCH" in finding_ids
    serving_finding = next(f for f in report.findings if f.id == "MATH-SERVING-NET-MISMATCH")
    assert serving_finding.verdict == "NEEDS_REVIEW"

    # 3. %DV mismatches detected
    assert "MATH-DV-MISMATCH-TOTAL_FAT" in finding_ids
    assert "MATH-DV-MISMATCH-CALCIUM" in finding_ids
    assert "MATH-DV-MISMATCH-VITAMIN_D" in finding_ids

    # 4. Honey in ingredients contradicts 'Certified Vegan' (deterministic FAIL)
    assert "CLAIM-VEGAN-HONEY-CONFLICT" in finding_ids
    vegan_finding = next(f for f in report.findings if f.id == "CLAIM-VEGAN-HONEY-CONFLICT")
    assert vegan_finding.verdict == "FAIL"

    # 5. Sweeteners in ingredients contradicts 'No Added Sugar'
    assert "CLAIM-NO-ADDED-SUGAR-CONTRADICTION" in finding_ids

    # 6. Duplicated ingredient 'Sunflower Seeds'
    assert any("DUPLICATE" in fid for fid in finding_ids)

    # 7. Allergen advisory misuse (nuts in formulation labeled only as 'May Contain')
    assert "REQ-ALLERGEN-ADVISORY-MISUSE" in finding_ids

    # 8. Net quantity lacks US customary ounce declaration
    assert "REQ-NET-QUANTITY-DUAL-UNIT-FAIL" in finding_ids
