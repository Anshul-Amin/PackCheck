"""Vision verification check using Gemini to inspect cropped artwork regions."""

import base64
import io
import logging

from PIL import Image

from src.packcheck.llm.client import GeminiClient
from src.packcheck.llm.prompts import VISION_VERIFY_PROMPT
from src.packcheck.models import ArtworkDoc, Finding

logger = logging.getLogger(__name__)


def crop_bbox_from_rendered_page(
    doc: ArtworkDoc,
    page_idx: int,
    bbox: tuple[float, float, float, float],
    padding: float = 10.0,
) -> bytes | None:
    """Crop an artwork region given its PDF point coordinates."""
    if page_idx >= len(doc.rendered_pages_png) or page_idx >= len(doc.page_dimensions):
        return None

    try:
        png_data = base64.b64decode(doc.rendered_pages_png[page_idx])
        img = Image.open(io.BytesIO(png_data))

        doc_w, doc_h = doc.page_dimensions[page_idx]
        img_w, img_h = img.size

        scale_x = img_w / doc_w
        scale_y = img_h / doc_h

        x0, y0, x1, y1 = bbox
        px0 = max(0, int((x0 - padding) * scale_x))
        py0 = max(0, int((y0 - padding) * scale_y))
        px1 = min(img_w, int((x1 + padding) * scale_x))
        py1 = min(img_h, int((y1 + padding) * scale_y))

        if px1 <= px0 or py1 <= py0:
            return None

        cropped = img.crop((px0, py0, px1, py1))
        out_buf = io.BytesIO()
        cropped.save(out_buf, format="PNG")
        return out_buf.getvalue()

    except Exception as e:
        logger.warning("Failed to crop page image: %s", e)
        return None


class VisionVerifier:
    """Verifies low-confidence text blocks or ambiguous findings using visual inspection."""

    def __init__(self, llm_client: GeminiClient | None = None):
        self.llm = llm_client or GeminiClient()

    def verify_finding(self, doc: ArtworkDoc, finding: Finding) -> Finding:
        """Attempt visual verification on a finding that has an artwork bbox."""
        if not self.llm.is_available() or not finding.evidence:
            return finding

        target_ev = None
        for ev in finding.evidence:
            if ev.artwork_bbox is not None:
                target_ev = ev
                break

        if not target_ev or not target_ev.artwork_bbox:
            return finding

        page_idx = target_ev.artwork_page or 0
        crop_bytes = crop_bbox_from_rendered_page(doc, page_idx, target_ev.artwork_bbox)
        if not crop_bytes:
            return finding

        res = self.llm.generate_json(
            prompt=VISION_VERIFY_PROMPT,
            content=f"Verify text in finding: {finding.title}",
            image_bytes=crop_bytes,
        )

        if res and "transcribed_text" in res:
            transcribed = res["transcribed_text"].strip()
            confidence = float(res.get("confidence", 0.9))
            finding.metadata["vision_transcribed"] = transcribed
            finding.metadata["vision_confidence"] = confidence
            finding.verified_by = "llm+vision"

        return finding
