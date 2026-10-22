"""Dieline and print-guide noise filter for packaging artwork."""

import re

# Technical printer and dieline annotation patterns
GUIDE_PATTERNS = [
    re.compile(r"^\s*art\s+orientation\s*$", re.IGNORECASE),
    re.compile(r"^\s*orientation\s*$", re.IGNORECASE),
    re.compile(r"^\s*copy\s+free\s*$", re.IGNORECASE),
    re.compile(r"^\s*front\s+panel(\s+orientation)?\s*$", re.IGNORECASE),
    re.compile(r"^\s*back\s+panel\s*$", re.IGNORECASE),
    re.compile(r"^\s*left\s+panel\s*$", re.IGNORECASE),
    re.compile(r"^\s*right\s+panel\s*$", re.IGNORECASE),
    re.compile(r"^\s*bottom\s+panel(\s+orientation)?\s*$", re.IGNORECASE),
    re.compile(r"^\s*top\s+panel(\s+orientation)?\s*$", re.IGNORECASE),
    re.compile(r"^\s*principal\s+display\s+panel\s*$", re.IGNORECASE),
    re.compile(r"^\s*packaging\s+powered\s+by(\s+esko)?\s*$", re.IGNORECASE),
    re.compile(r"^\s*pac\s*k\s*ag\s*i\s*n\s*g\s+p\s*ow\s*e\s*r\s*e\s*d\s+by\s*$", re.IGNORECASE),
    re.compile(r"^\s*gl\d+\s*$", re.IGNORECASE),
    re.compile(r"^\s*\d+,\d+[A-Z0-9\s]+\s*$", re.IGNORECASE),  # e.g. "2,1M2S1I0O0 1B2"
]


def is_guide_text(text: str) -> bool:
    """Check if the given text represents dieline guide marks or printer instructions."""
    stripped = text.strip()
    if not stripped:
        return True

    for pattern in GUIDE_PATTERNS:
        if pattern.search(stripped):
            return True

    # Check for multi-line block composed entirely of guide text lines
    lines = [line.strip() for line in stripped.splitlines() if line.strip()]
    if lines and all(any(p.search(line) for p in GUIDE_PATTERNS) for line in lines):
        return True

    return False
