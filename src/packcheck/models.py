"""Pydantic v2 domain models for PackCheck."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class TextBlock(BaseModel):
    """A text block extracted from artwork PDF."""

    text: str
    bbox: tuple[float, float, float, float]  # x0, y0, x1, y1 in points
    page: int = 0
    panel: str | None = None  # "front", "back", "left", "right", "top", "bottom", etc.
    low_confidence: bool = False
    font: str | None = None
    font_size: float | None = None
    is_guide_text: bool = False


class NutritionItem(BaseModel):
    """A single nutrient entry."""

    name: str
    amount: float | None = None
    unit: str = "g"  # "g", "mg", "mcg", "kcal", etc.
    dv_percent: float | None = None  # e.g. 15.0 for 15%


class NutritionData(BaseModel):
    """Structured nutrition information from panel or content sheet."""

    servings_per_container: float | None = None
    serving_size_g: float | None = None
    serving_size_household: str | None = None
    calories: float | None = None
    nutrients: dict[str, NutritionItem] = Field(default_factory=dict)
    raw_text: str | None = None
    bottom_statement: str | None = None


class ApprovedData(BaseModel):
    """Approved product information from content sheet."""

    product_name: str | None = None
    net_weight_g: float | None = None
    net_weight_raw: str | None = None
    upc: str | None = None
    ingredients: list[str] = Field(default_factory=list)
    raw_ingredients_text: str | None = None
    allergens: list[str] = Field(default_factory=list)
    raw_allergens_text: str | None = None
    claims: list[str] = Field(default_factory=list)
    dietary_info: str | None = None
    manufacturer: str | None = None
    notes: dict[str, str] = Field(default_factory=dict)
    nutrition: NutritionData | None = None


class ArtworkDoc(BaseModel):
    """Extracted packaging artwork document."""

    filename: str
    num_pages: int = 1
    page_dimensions: list[tuple[float, float]] = Field(default_factory=list)
    text_blocks: list[TextBlock] = Field(default_factory=list)
    guide_blocks: list[TextBlock] = Field(default_factory=list)
    nutrition: NutritionData | None = None
    rendered_pages_png: list[str] = Field(default_factory=list)  # file paths or base64


class Rule(BaseModel):
    """A compliance rule from regulations or internal guidelines."""

    id: str
    title: str
    source: str
    source_url: str | None = None
    quote_or_paraphrase: str
    check_type: Literal["deterministic", "semantic"]
    severity: Literal["critical", "major", "advisory"] = "major"
    applies_to: list[str] = Field(default_factory=list)  # "nutrition", "claims", "allergens", etc.
    enabled: bool = True


class Evidence(BaseModel):
    """Specific piece of evidence supporting a finding."""

    artwork_text: str | None = None
    artwork_bbox: tuple[float, float, float, float] | None = None
    artwork_page: int | None = None
    artwork_panel: str | None = None
    approved_value: str | None = None
    computed_value: str | None = None
    formula: str | None = None
    rule_id: str | None = None
    rule_quote: str | None = None


class Finding(BaseModel):
    """A single compliance finding."""

    id: str
    title: str
    verdict: Literal["FAIL", "NEEDS_REVIEW", "PASS"]
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)
    verified_by: Literal["deterministic", "llm", "llm+vision", "human"]
    category: str  # "nutrition_math", "consistency", "claims", "required_elements", "semantic"
    why_it_matters: str
    evidence: list[Evidence] = Field(default_factory=list)
    human_check_needed: str | None = None
    dismissed: bool = False
    dismiss_reason: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class Report(BaseModel):
    """Overall compliance report."""

    artwork_filename: str
    content_sheet_filename: str | None = None
    timestamp: str
    total_checks: int = 0
    fail_count: int = 0
    needs_review_count: int = 0
    pass_count: int = 0
    findings: list[Finding] = Field(default_factory=list)
    ready_to_print: bool = False
    summary_banner: str = ""
    unverified_limitations: list[str] = Field(default_factory=list)
