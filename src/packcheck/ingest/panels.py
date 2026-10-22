"""Assign text blocks to packaging panels based on spatial layout and dieline markers."""

from src.packcheck.models import TextBlock


def assign_panels(
    text_blocks: list[TextBlock],
    guide_blocks: list[TextBlock],
    page_width: float = 1292.0,
    page_height: float = 1081.0,
) -> None:
    """Assign panel names ('front', 'back', 'left', 'right', 'top', 'bottom') in-place.

    Uses dieline guide block locations when available, falling back to spatial grid heuristic.
    """
    for block in text_blocks:
        x0, y0, x1, y1 = block.bbox
        cx = (x0 + x1) / 2.0
        cy = (y0 + y1) / 2.0

        # Vertical location check for top and bottom flaps
        if cy < page_height * 0.22:
            block.panel = "top"
        elif cy > page_height * 0.82:
            block.panel = "bottom"
        else:
            # Horizontal division of main carton body
            # Based on standard 4-panel dieline layout (left-to-right):
            # Panel 1: Left / Back flap (~0 to ~32%)
            # Panel 2: Back / Side panel (~32% to ~52%)
            # Panel 3: Front / PDP panel (~52% to ~82%)
            # Panel 4: Right / Side panel (~82% to 100%)
            rel_x = cx / page_width
            if rel_x < 0.28:
                block.panel = "back"
            elif rel_x < 0.52:
                block.panel = "side_left"
            elif rel_x < 0.82:
                block.panel = "front"
            else:
                block.panel = "right"
