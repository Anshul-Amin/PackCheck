"""Parser to extract structured Nutrition Facts from artwork text blocks."""

import re

from src.packcheck.models import ArtworkDoc, NutritionData, NutritionItem, TextBlock


def parse_artwork_nutrition(doc: ArtworkDoc) -> NutritionData | None:
    """Identify Nutrition Facts blocks on artwork and parse into NutritionData."""
    # Find blocks belonging to the Nutrition Facts section
    nutrition_blocks: list[TextBlock] = []
    found_title = False

    for b in doc.text_blocks:
        t = b.text.lower()
        if "nutrition facts" in t:
            found_title = True
            nutrition_blocks.append(b)
        elif found_title and (
            "servings per container" in t
            or "calories" in t
            or "daily value" in t
            or "total fat" in t
            or "protein" in t
            or "added sugars" in t
            or "vitamin d" in t
            or "calcium" in t
            or "iron" in t
            or "potassium" in t
        ):
            nutrition_blocks.append(b)

    if not nutrition_blocks:
        return None

    # Combine text for holistic parsing
    full_text = "\n".join(b.text for b in nutrition_blocks)
    data = NutritionData(raw_text=full_text)

    # Servings per container
    m_servings = re.search(r"(\d+)\s+servings\s+per\s+container", full_text, re.IGNORECASE)
    if m_servings:
        data.servings_per_container = float(m_servings.group(1))

    # Serving size
    m_size = re.search(r"serving\s+size\s*[:\n\s]*([^\n]+)", full_text, re.IGNORECASE)
    if m_size:
        size_raw = m_size.group(1).strip()
        data.serving_size_household = size_raw
        m_g = re.search(r"(\d+(\.\d+)?)\s*g", size_raw, re.IGNORECASE)
        if m_g:
            data.serving_size_g = float(m_g.group(1))
        else:
            # Check if next token is numeric
            m_num = re.search(r"^(\d+)", size_raw)
            if m_num:
                data.serving_size_g = float(m_num.group(1))

    # Calories
    m_cal = re.search(r"calories\s*[:\s]*(\d+)", full_text, re.IGNORECASE)
    if m_cal:
        data.calories = float(m_cal.group(1))

    # Nutrients mapping
    nutrients_to_search = [
        ("total fat", "total_fat", "g"),
        ("saturated fat", "saturated_fat", "g"),
        ("trans fat", "trans_fat", "g"),
        ("cholesterol", "cholesterol", "mg"),
        ("sodium", "sodium", "mg"),
        ("total carbohydrate", "total_carbohydrate", "g"),
        ("dietary fiber", "dietary_fiber", "g"),
        ("total sugars", "total_sugars", "g"),
        ("incl.*added sugars", "added_sugars", "g"),
        ("protein", "protein", "g"),
        ("vitamin d", "vitamin_d", "mcg"),
        ("calcium", "calcium", "mg"),
        ("iron", "iron", "mg"),
        ("potassium", "potassium", "mg"),
    ]

    for label_pattern, key, default_unit in nutrients_to_search:
        if key == "added_sugars":
            # Handles "Incl. 0g Added Sugars \n0%" or "Includes 0g Added Sugars"
            m = re.search(
                r"incl[a-z.]*\s*(\d+(?:\.\d+)?)\s*([a-zA-Z]+)?\s*added\s+sugars(?:\s*\n?\s*(\d+(?:\.\d+)?)\s*%)?",
                full_text,
                re.IGNORECASE,
            )
            if m:
                amt = float(m.group(1))
                unit = m.group(2) or default_unit
                dv = float(m.group(3)) if m.group(3) else None
                data.nutrients[key] = NutritionItem(
                    name="Added Sugars",
                    amount=amt,
                    unit=unit,
                    dv_percent=dv,
                )
            continue

        # Regex to find nutrient name followed by amount and optionally %DV
        # Example 1: Total Fat 15g \n 2.2%
        pattern = (
            rf"{label_pattern}\s*[:\s]*(\d+(?:\.\d+)?)\s*([a-zA-Z]+)?"
            rf"(?:[^\d\n]*\n?\s*(\d+(?:\.\d+)?)\s*%)?"
        )
        m = re.search(pattern, full_text, re.IGNORECASE)
        if m:
            amt = float(m.group(1))
            unit = m.group(2) or default_unit
            dv = float(m.group(3)) if m.group(3) else None

            data.nutrients[key] = NutritionItem(
                name=key.replace("_", " ").title(),
                amount=amt,
                unit=unit,
                dv_percent=dv,
            )

    # Attach to document
    doc.nutrition = data
    return data
