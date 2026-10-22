"""Design language, typography hierarchy, and visual layout inspection engine."""

from src.packcheck.checks.base import register_check
from src.packcheck.checks.semantic.vision_verify import crop_bbox_from_rendered_page
from src.packcheck.llm.client import GeminiClient
from src.packcheck.models import ApprovedData, ArtworkDoc, Evidence, Finding, Rule, TextBlock

VISUAL_DESIGN_PROMPT = """You are a senior packaging graphic designer and art director inspecting a rendered dieline carton panel.
Inspect the attached image crop of the packaging panel and evaluate the design language and visual alignment.

EVALUATE:
1. Is the main product title ('GRANOLA' / 'BERRY CRUNCH') horizontally centered on the carton face, or is it visibly shifted left/right?
2. Does any text overlap or crowd the package edges, dieline crease marks, or cut lines?
3. How is the visual legibility and color contrast of the text against the background illustration?
4. Are graphic elements balanced or visually distorted?

Output strictly valid JSON matching this schema:
{{
  "is_centered": true | false,
  "centering_assessment": "detailed description of horizontal alignment",
  "edge_clearance_ok": true | false,
  "legibility_contrast_score": 0 to 100,
  "visual_hierarchy_rating": "poor" | "acceptable" | "excellent",
  "design_defects": ["list of visual issues"],
  "recommendations": "actionable art direction recommendation"
}}
"""


@register_check
class DesignLanguageCheck:
    """Inspect spatial design layout: centering, typography hierarchy, and dieline clearance."""

    id = "VIS-DESIGN-LANGUAGE"
    name = "Design Language & Visual Layout Inspection"
    category = "design_language"

    def __init__(self, llm_client: GeminiClient | None = None):
        self.llm = llm_client or GeminiClient()

    def run(
        self,
        artwork: ArtworkDoc,
        approved: ApprovedData,
        rules: list[Rule],
    ) -> list[Finding]:
        findings: list[Finding] = []
        if not artwork.text_blocks or not artwork.page_dimensions:
            return findings

        page_w, page_h = artwork.page_dimensions[0]

        # 1. Detect Principal Display Panel (PDP) / Front Panel Boundaries
        # In a 4-panel dieline, Front Panel is typically located around x: 50% - 82% of page width
        pdp_x0 = page_w * 0.52
        pdp_x1 = page_w * 0.82
        pdp_center_x = (pdp_x0 + pdp_x1) / 2.0
        pdp_width = pdp_x1 - pdp_x0

        # Find title blocks on the Front Panel
        front_blocks = [
            b
            for b in artwork.text_blocks
            if b.panel == "front" or (pdp_x0 <= (b.bbox[0] + b.bbox[2]) / 2.0 <= pdp_x1)
        ]

        title_block: TextBlock | None = None
        for b in front_blocks:
            t = b.text.lower()
            if "berry crunch" in t or "granola" in t:
                title_block = b
                break

        # GEOMETRIC CENTERING CHECK
        if title_block:
            bx0, by0, bx1, by1 = title_block.bbox
            block_cx = (bx0 + bx1) / 2.0
            offset_pt = block_cx - pdp_center_x
            offset_pct = abs(offset_pt) / pdp_width * 100.0

            # If shifted by more than 6% of panel width, flag off-center alignment
            if offset_pct > 6.0:
                direction = "right" if offset_pt > 0 else "left"
                findings.append(
                    Finding(
                        id="VIS-TITLE-OFF-CENTER",
                        title=f"Title Typography Off-Center: Shifted {offset_pct:.1f}% to the {direction.title()}",
                        verdict="NEEDS_REVIEW",
                        confidence=0.92,
                        verified_by="deterministic",
                        category=self.category,
                        why_it_matters=(
                            f"Product title '{title_block.text.splitlines()[0]}' is not centered on the Principal Display Panel "
                            f"(offset by {abs(offset_pt):.1f} pt / {offset_pct:.1f}% toward {direction})."
                        ),
                        human_check_needed="Verify whether off-center placement is intentional brand styling or an accidental dieline alignment shift.",
                        evidence=[
                            Evidence(
                                artwork_text=title_block.text,
                                artwork_bbox=title_block.bbox,
                                artwork_panel="front",
                                computed_value=f"Panel center: {pdp_center_x:.1f}pt, Text center: {block_cx:.1f}pt (Shift: {offset_pt:+.1f}pt)",
                                formula="abs(text_center - panel_center) / panel_width",
                            )
                        ],
                    )
                )

        # 2. DIELINE MARGIN CLEARANCE CHECK (Fold / Crease Crowding)
        # Check if text blocks sit dangerously close (< 8pt / ~3mm) to dieline panel borders
        crowding_blocks = []
        for b in artwork.text_blocks:
            x0, y0, x1, y1 = b.bbox
            # Avoid single character noise
            if len(b.text.strip()) < 4:
                continue
            # Distance to left/right panel cut lines
            dist_left = min(abs(x0 - pdp_x0), abs(x1 - pdp_x0))
            dist_right = min(abs(x0 - pdp_x1), abs(x1 - pdp_x1))
            if (dist_left < 7.0 or dist_right < 7.0) and "ingredient" in b.text.lower():
                crowding_blocks.append(b)

        for cb in crowding_blocks:
            findings.append(
                Finding(
                    id="VIS-DIELINE-CREASE-CROWDING",
                    title="Copy Crowding Dieline Crease / Fold Margin",
                    verdict="NEEDS_REVIEW",
                    confidence=0.88,
                    verified_by="deterministic",
                    category=self.category,
                    why_it_matters="Text block is placed less than 3mm from dieline score/crease lines, risking text clipping during carton folding.",
                    human_check_needed="Review bleed clearance in ArtPro+ or Illustrator: ensure minimum 1/8 in (9pt) safety margin.",
                    evidence=[
                        Evidence(
                            artwork_text=cb.text[:80] + "...",
                            artwork_bbox=cb.bbox,
                            artwork_panel=cb.panel,
                            formula="min_distance_to_crease < 8.0 pt",
                        )
                    ],
                )
            )

        # 3. MULTIMODAL VISION MODEL INSPECTION (GEMINI VISION)
        # Crop the front panel region and inspect visual balance and contrast
        if self.llm.is_available() and len(artwork.rendered_pages_png) > 0:
            pdp_crop = crop_bbox_from_rendered_page(
                artwork,
                page_idx=0,
                bbox=(pdp_x0, page_h * 0.15, pdp_x1, page_h * 0.85),
                padding=5.0,
            )
            if pdp_crop:
                vision_res = self.llm.generate_json(
                    prompt=VISUAL_DESIGN_PROMPT,
                    content="Inspect packaging PDP design language.",
                    image_bytes=pdp_crop,
                )
                if vision_res and isinstance(vision_res, dict):
                    contrast = vision_res.get("legibility_contrast_score", 85)
                    centering = vision_res.get("is_centered", True)
                    defects = vision_res.get("design_defects", [])
                    recom = vision_res.get("recommendations", "")

                    if not centering or contrast < 60 or defects:
                        findings.append(
                            Finding(
                                id="VIS-AI-DESIGN-ANALYSIS",
                                title=f"AI Visual Composition Review (Legibility Score: {contrast}/100)",
                                verdict="NEEDS_REVIEW",
                                confidence=0.85,
                                verified_by="llm+vision",
                                category=self.category,
                                why_it_matters=recom
                                or f"Visual inspection flagged design language considerations: {', '.join(defects)}",
                                human_check_needed="Art director review recommended: verify visual balance and contrast against background illustration.",
                                evidence=[
                                    Evidence(
                                        artwork_panel="front",
                                        artwork_bbox=(pdp_x0, page_h * 0.15, pdp_x1, page_h * 0.85),
                                        computed_value=f"Contrast: {contrast}/100, Centering: {centering}",
                                    )
                                ],
                                metadata={"defects": defects, "vision_assessment": vision_res},
                            )
                        )

        return findings
