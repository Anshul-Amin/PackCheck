"""Tests for deterministic FSSAI compliance checks."""

from src.packcheck.checks.deterministic.fssai_check import FSSAICheck
from src.packcheck.models import ApprovedData, ArtworkDoc, NutritionData, NutritionItem, TextBlock


def test_fssai_license_missing_fails():
    """Verify that artwork missing a 14-digit FSSAI license number flags a FAIL."""
    doc = ArtworkDoc(filename="test_pack.pdf")
    doc.text_blocks = [
        TextBlock(text="Brand Name Berry Granola Net Wt 500g", bbox=(0, 0, 100, 100)),
    ]
    chk = FSSAICheck()
    findings = chk.run(doc, ApprovedData(), [])
    fail_ids = [f.id for f in findings if f.verdict == "FAIL"]
    assert "FSSAI-LIC-MISSING-FAIL" in fail_ids


def test_fssai_license_present_passes():
    """Verify that artwork containing a valid 14-digit FSSAI license passes."""
    doc = ArtworkDoc(filename="test_pack.pdf")
    doc.text_blocks = [
        TextBlock(text="fssai Lic. No. 10012011000014", bbox=(0, 0, 100, 100)),
    ]
    chk = FSSAICheck()
    findings = chk.run(doc, ApprovedData(), [])
    pass_ids = [f.id for f in findings if f.verdict == "PASS"]
    assert "FSSAI-LIC-PASS" in pass_ids


def test_fssai_trans_fat_cap_fail():
    """Verify that trans fat > 2% of total fat triggers an FSSAI FAIL."""
    doc = ArtworkDoc(filename="test_pack.pdf")
    doc.nutrition = NutritionData(
        nutrients={
            "total_fat": NutritionItem(name="Total Fat", amount=10.0, unit="g"),
            "trans_fat": NutritionItem(name="Trans Fat", amount=1.0, unit="g"),  # 10% of fat > 2%
        }
    )
    chk = FSSAICheck()
    findings = chk.run(doc, ApprovedData(), [])
    fail_ids = [f.id for f in findings if f.verdict == "FAIL"]
    assert "FSSAI-TRANS-FAT-CAP-FAIL" in fail_ids
