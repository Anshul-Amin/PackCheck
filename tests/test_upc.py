"""Tests for UPC-A barcode validation and GS1 Modulo-10 check digit algorithm."""

from src.packcheck.checks.deterministic.consistency import validate_upc_a_check_digit


def test_valid_upc_from_sample():
    """Verify sample content sheet UPC '1 20000 00003 6' passes check digit validation."""
    assert validate_upc_a_check_digit("1 20000 00003 6") is True
    assert validate_upc_a_check_digit("120000000036") is True


def test_standard_valid_upcs():
    """Verify known standard valid GS1 UPC-A barcodes."""
    # Coca Cola 12 fl oz can: 049000028904
    assert validate_upc_a_check_digit("049000028904") is True
    # Campbell's Tomato Soup: 051000012517
    assert validate_upc_a_check_digit("051000012517") is True


def test_invalid_check_digit():
    """Verify that an altered last digit fails check digit validation."""
    # Altered check digit from 6 to 5
    assert validate_upc_a_check_digit("1 20000 00003 5") is False
    assert validate_upc_a_check_digit("049000028909") is False


def test_invalid_lengths():
    """Verify non-12-digit strings are rejected."""
    assert validate_upc_a_check_digit("12345") is False
    assert validate_upc_a_check_digit("123456789012345") is False
    assert validate_upc_a_check_digit("") is False
