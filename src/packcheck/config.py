"""Configuration, constants, and environment settings for PackCheck."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env if present
load_dotenv()

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
SAMPLES_DIR = DATA_DIR / "samples"
RULES_DIR = DATA_DIR / "rules"
CACHE_DIR = Path(os.getenv("LLM_CACHE_DIR", str(BASE_DIR / ".cache" / "llm")))

# LLM Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_FALLBACK_MODEL = os.getenv("GEMINI_FALLBACK_MODEL", "gemini-2.5-flash-lite")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5vl:7b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Free-tier rate limiting settings (conservative defaults)
GEMINI_RPM = int(os.getenv("GEMINI_RPM", "5"))
GEMINI_RPD = int(os.getenv("GEMINI_RPD", "250"))
REQUEST_TIMEOUT_SECONDS = 30

# Official FDA Daily Values (2,000 kcal diet)
# Reference: 21 CFR 101.9(c)(9); FDA Food Labeling Guide Appendix C
# https://www.fda.gov/food/nutrition-facts-label/daily-value-nutrient-labeling
FDA_DAILY_VALUES: dict[str, tuple[float, str]] = {
    "total_fat": (78.0, "g"),
    "saturated_fat": (20.0, "g"),
    "cholesterol": (300.0, "mg"),
    "sodium": (2300.0, "mg"),
    "total_carbohydrate": (275.0, "g"),
    "dietary_fiber": (28.0, "g"),
    "added_sugars": (50.0, "g"),
    "vitamin_d": (20.0, "mcg"),
    "calcium": (1300.0, "mg"),
    "iron": (18.0, "mg"),
    "potassium": (4700.0, "mg"),
}

# Atwater specific energy conversion factors (kcal/g)
# Reference: USDA Agriculture Handbook No. 74 / FDA 21 CFR 101.9(c)(1)(i)
ATWATER_FAT = 9.0
ATWATER_CARB = 4.0
ATWATER_PROTEIN = 4.0

# Calorie comparison tolerances
# < 20% difference is permitted due to fiber deductions, general rounding, and moisture variation
CALORIE_TOLERANCE_WARN = 0.20  # > 20% triggers NEEDS_REVIEW
CALORIE_TOLERANCE_FAIL = 0.50  # > 50% triggers definite FAIL

# Serving size vs net weight tolerance
# Labeled servings_per_container * serving_size_g vs net_weight_g
SERVING_WEIGHT_TOLERANCE = 0.10  # 10% tolerance for rounding conventions

# Major food allergens under FALCPA + FASTER Act (9 major food allergens)
MAJOR_ALLERGENS = {
    "milk",
    "eggs",
    "peanuts",
    "tree nuts",  # includes almonds, pecans, walnuts, cashews, etc.
    "wheat",
    "soy",
    "fish",
    "crustacean shellfish",
    "sesame",
}

# Common tree nuts recognized by FDA guidance
TREE_NUTS = {
    "almond",
    "almonds",
    "pecan",
    "pecans",
    "walnut",
    "walnuts",
    "cashew",
    "cashews",
    "brazil nut",
    "brazil nuts",
    "hazelnut",
    "hazelnuts",
    "pistachio",
    "pistachios",
    "macadamia",
    "macadamias",
}
