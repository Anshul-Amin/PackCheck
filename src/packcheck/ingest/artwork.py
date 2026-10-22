"""PDF Artwork ingestion module using PyMuPDF."""

import base64
from pathlib import Path

import fitz  # PyMuPDF

from src.packcheck.ingest.dieline_filter import is_guide_text
from src.packcheck.ingest.panels import assign_panels
from src.packcheck.models import ArtworkDoc, TextBlock


def render_page_to_png(page: fitz.Page, dpi: int = 200) -> bytes:
    """Render a PyMuPDF page to PNG bytes at the specified DPI."""
    zoom = dpi / 72.0
    matrix = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=matrix, alpha=False)
    return pix.tobytes(output="png")


def extract_text_blocks_from_page(
    page: fitz.Page, page_index: int = 0
) -> tuple[list[TextBlock], list[TextBlock]]:
    """Extract text and dieline guide blocks from a PDF page using PyMuPDF dict structure."""
    text_blocks: list[TextBlock] = []
    guide_blocks: list[TextBlock] = []

    page_dict = page.get_text("dict")
    raw_blocks = page_dict.get("blocks", [])

    for b in raw_blocks:
        if b.get("type") != 0:  # Skip image blocks
            continue

        bbox = tuple(float(x) for x in b.get("bbox", (0, 0, 0, 0)))
        lines_text = []
        fonts = set()
        font_sizes = []
        has_rotation = False

        for line in b.get("lines", []):
            dir_val = line.get("dir", (1.0, 0.0))
            if abs(dir_val[0] - 1.0) > 0.01 or abs(dir_val[1]) > 0.01:
                has_rotation = True

            line_spans = []
            for span in line.get("spans", []):
                stext = span.get("text", "")
                if stext:
                    line_spans.append(stext)
                    fonts.add(span.get("font", ""))
                    font_sizes.append(span.get("size", 0.0))

            line_str = "".join(line_spans).strip()
            if line_str:
                lines_text.append(line_str)

        block_text = "\n".join(lines_text).strip()
        if not block_text:
            continue

        primary_font = list(fonts)[0] if fonts else None
        avg_font_size = sum(font_sizes) / len(font_sizes) if font_sizes else None

        # Check for dieline / printer guide annotations
        guide = is_guide_text(block_text)

        tb = TextBlock(
            text=block_text,
            bbox=(bbox[0], bbox[1], bbox[2], bbox[3]),
            page=page_index,
            low_confidence=has_rotation or len(block_text) <= 1,
            font=primary_font,
            font_size=avg_font_size,
            is_guide_text=guide,
        )

        if guide:
            guide_blocks.append(tb)
        else:
            text_blocks.append(tb)

    # Deduplicate exact overlapping blocks (often present in dieline proof layer copies)
    deduped_text_blocks = _deduplicate_blocks(text_blocks)

    return deduped_text_blocks, guide_blocks


def _deduplicate_blocks(blocks: list[TextBlock]) -> list[TextBlock]:
    """Remove exact or near-identical stacked duplicates from layered artwork proofs."""
    unique: list[TextBlock] = []
    seen = set()

    for b in blocks:
        norm_text = b.text.strip().lower()
        # Round bbox to 2 decimal places to cluster stacked layers
        key = (
            norm_text,
            round(b.bbox[0], 0),
            round(b.bbox[1], 0),
            round(b.bbox[2], 0),
            round(b.bbox[3], 0),
        )
        if key in seen:
            continue
        seen.add(key)
        unique.append(b)

    return unique


def ingest_artwork_pdf(pdf_path: str | Path) -> ArtworkDoc:
    """Ingest a PDF dieline artwork file, extracting text blocks, guides, and rendering page previews."""
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"Artwork PDF file not found at: {path}")

    doc = fitz.open(str(path))
    num_pages = len(doc)
    dimensions: list[tuple[float, float]] = []
    all_text_blocks: list[TextBlock] = []
    all_guide_blocks: list[TextBlock] = []
    rendered_pngs: list[str] = []

    for i in range(num_pages):
        page = doc[i]
        dimensions.append((float(page.rect.width), float(page.rect.height)))

        t_blocks, g_blocks = extract_text_blocks_from_page(page, page_index=i)
        assign_panels(t_blocks, g_blocks, page.rect.width, page.rect.height)

        all_text_blocks.extend(t_blocks)
        all_guide_blocks.extend(g_blocks)

        png_bytes = render_page_to_png(page, dpi=150)
        png_b64 = base64.b64encode(png_bytes).decode("ascii")
        rendered_pngs.append(png_b64)

    doc.close()

    return ArtworkDoc(
        filename=path.name,
        num_pages=num_pages,
        page_dimensions=dimensions,
        text_blocks=all_text_blocks,
        guide_blocks=all_guide_blocks,
        rendered_pages_png=rendered_pngs,
    )
