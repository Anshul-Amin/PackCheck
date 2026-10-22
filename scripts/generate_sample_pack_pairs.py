"""Generate 10 realistic packaging artwork PDF dielines and matching Excel specification content sheets.

DO NOT test these against the compliance model; they are generated for manual user inspection and testing.
"""

from pathlib import Path

import openpyxl
from openpyxl.styles import Border, Font, PatternFill, Side
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas

SAMPLES_DIR = Path("data/samples")
SAMPLES_DIR.mkdir(parents=True, exist_ok=True)

# Define 10 realistic FMCG packaging test cases
SAMPLE_SPECS = [
    {
        "id": "Sample01_OatMilk_Vanilla_Carton",
        "brand": "PureOat Co.",
        "product_name": "Organic Oat Milk Vanilla",
        "legal_name": "ORGANIC OAT MILK - VANILLA",
        "category": "Plant-Based Dairy Alternative",
        "net_wt_str": "32 FL OZ (1 QT) 946 mL",
        "net_wt_g": 946.0,
        "upc": "0 12345 67890 5",
        "servings_per_container": "4",
        "serving_size": "1 cup (240 mL)",
        "claims": [
            "USDA Organic",
            "Non-GMO Project Verified",
            "Certified Vegan",
            "Gluten-Free",
            "Dairy-Free",
        ],
        "ingredients": "Organic Oat Base (Water, Organic Whole Grain Oats), Organic Cane Sugar, Contains 2% or less of: High-Oleic Sunflower Oil, Dipotassium Phosphate, Calcium Carbonate, Sea Salt, Natural Vanilla Flavor, Gellan Gum, Ergocalciferol (Vitamin D2).",
        "allergens": "None declared. Manufactured in a certified gluten-free, peanut-free facility.",
        "distributor": "Distributed by PureOat Beverages LLC, Portland, OR 97201",
        "storage": "Keep refrigerated after opening and consume within 7 to 10 days.",
        "nutrition": [
            ("Calories", "120", None),
            ("Total Fat", "5g", "6%"),
            ("Saturated Fat", "0.5g", "3%"),
            ("Trans Fat", "0g", None),
            ("Cholesterol", "0mg", "0%"),
            ("Sodium", "100mg", "4%"),
            ("Total Carbohydrate", "16g", "6%"),
            ("Dietary Fiber", "2g", "7%"),
            ("Total Sugars", "7g", None),
            ("Incl. Added Sugars", "4g", "8%"),
            ("Protein", "3g", None),
            ("Vitamin D", "3mcg", "15%"),
            ("Calcium", "350mg", "25%"),
            ("Iron", "0.5mg", "2%"),
            ("Potassium", "390mg", "8%"),
        ],
    },
    {
        "id": "Sample02_ProteinBar_ChocPeanut_Wrapper",
        "brand": "Apex Nutrition",
        "product_name": "High Protein Bar Chocolate Peanut Butter",
        "legal_name": "HIGH PROTEIN BAR - CHOCOLATE PEANUT BUTTER",
        "category": "Sports Nutrition Bar",
        "net_wt_str": "2.12 OZ (60g)",
        "net_wt_g": 60.0,
        "upc": "8 50012 34567 1",
        "servings_per_container": "1",
        "serving_size": "1 bar (60g)",
        "claims": ["20g Protein", "1g Total Sugar", "Certified Gluten-Free", "Keto Friendly"],
        "ingredients": "Protein Blend (Whey Protein Isolate, Milk Protein Isolate), Soluble Tapioca Fiber, Roasted Peanuts, Unsweetened Chocolate, Cocoa Butter, Erythritol, Natural Flavor, Sea Salt, Steviol Glycosides.",
        "allergens": "CONTAINS: Milk, Peanuts. Manufactured in a facility that also processes tree nuts, soy, and eggs.",
        "distributor": "Manufactured for Apex Performance LLC, Boulder, CO 80301",
        "storage": "Store in a cool, dry place away from direct sunlight.",
        "nutrition": [
            ("Calories", "210", None),
            ("Total Fat", "7g", "9%"),
            ("Saturated Fat", "2.5g", "13%"),
            ("Trans Fat", "0g", None),
            ("Cholesterol", "5mg", "2%"),
            ("Sodium", "180mg", "8%"),
            ("Total Carbohydrate", "22g", "8%"),
            ("Dietary Fiber", "10g", "36%"),
            ("Total Sugars", "1g", None),
            ("Incl. Added Sugars", "0g", "0%"),
            ("Protein", "20g", "40%"),
            ("Vitamin D", "0mcg", "0%"),
            ("Calcium", "90mg", "6%"),
            ("Iron", "1.8mg", "10%"),
            ("Potassium", "140mg", "2%"),
        ],
    },
    {
        "id": "Sample03_OrganicKombucha_Ginger_Bottle",
        "brand": "VitalFlora",
        "product_name": "Raw Organic Kombucha Ginger Lemon",
        "legal_name": "RAW ORGANIC FERMENTED TEA - GINGER LEMON",
        "category": "Functional Beverage",
        "net_wt_str": "16 FL OZ (473 mL)",
        "net_wt_g": 473.0,
        "upc": "0 41234 56789 2",
        "servings_per_container": "1",
        "serving_size": "16 fl oz (473 mL)",
        "claims": [
            "USDA Organic",
            "Non-GMO Project Verified",
            "Live Probiotics",
            "Vegan",
            "Raw & Unpasteurized",
        ],
        "ingredients": "Raw Organic Kombucha (Purified Water, Organic Cane Sugar, Organic Black Tea, Organic Green Tea, Active Kombucha Culture), Organic Cold-Pressed Ginger Juice, Organic Lemon Juice.",
        "allergens": "None.",
        "distributor": "Crafted by VitalFlora Organics Inc., Austin, TX 78701",
        "storage": "Keep refrigerated at 34-38°F (1-3°C). Do not shake.",
        "nutrition": [
            ("Calories", "50", None),
            ("Total Fat", "0g", "0%"),
            ("Saturated Fat", "0g", "0%"),
            ("Trans Fat", "0g", None),
            ("Cholesterol", "0mg", "0%"),
            ("Sodium", "10mg", "0%"),
            ("Total Carbohydrate", "12g", "4%"),
            ("Dietary Fiber", "0g", "0%"),
            ("Total Sugars", "10g", None),
            ("Incl. Added Sugars", "10g", "20%"),
            ("Protein", "0g", None),
            ("Vitamin D", "0mcg", "0%"),
            ("Calcium", "15mg", "2%"),
            ("Iron", "0.2mg", "0%"),
            ("Potassium", "65mg", "2%"),
        ],
    },
    {
        "id": "Sample04_DarkChocolate_SeaSalt_Box",
        "brand": "Velvet Cacao",
        "product_name": "72% Dark Chocolate Artisan Sea Salt",
        "legal_name": "72% CACAO DARK CHOCOLATE WITH SEA SALT",
        "category": "Confectionery",
        "net_wt_str": "3.5 OZ (100g)",
        "net_wt_g": 100.0,
        "upc": "7 93573 19283 4",
        "servings_per_container": "3",
        "serving_size": "30g (approx. 4 squares)",
        "claims": ["Fair Trade Certified", "USDA Organic", "Certified Vegan", "Non-GMO"],
        "ingredients": "Organic Cacao Beans, Organic Cane Sugar, Organic Cocoa Butter, Flaked Maldon Sea Salt, Organic Ground Vanilla Beans.",
        "allergens": "May contain traces of milk, hazelnuts, and almonds due to shared equipment.",
        "distributor": "Imported and packaged by Velvet Cacao Ltd, San Francisco, CA 94107",
        "storage": "Store in a cool dry place between 60°F and 68°F (15-20°C).",
        "nutrition": [
            ("Calories", "170", None),
            ("Total Fat", "12g", "15%"),
            ("Saturated Fat", "7g", "35%"),
            ("Trans Fat", "0g", None),
            ("Cholesterol", "0mg", "0%"),
            ("Sodium", "85mg", "4%"),
            ("Total Carbohydrate", "15g", "5%"),
            ("Dietary Fiber", "3g", "11%"),
            ("Total Sugars", "10g", None),
            ("Incl. Added Sugars", "10g", "20%"),
            ("Protein", "2g", None),
            ("Vitamin D", "0mcg", "0%"),
            ("Calcium", "20mg", "2%"),
            ("Iron", "2.4mg", "15%"),
            ("Potassium", "180mg", "4%"),
        ],
    },
    {
        "id": "Sample05_GlutenFreeCookies_Almond_Pouch",
        "brand": "Hearth & Oven",
        "product_name": "Gluten-Free Almond Shortbread Cookies",
        "legal_name": "GLUTEN-FREE ALMOND SHORTBREAD COOKIES",
        "category": "Bakery & Biscuits",
        "net_wt_str": "6 OZ (170g)",
        "net_wt_g": 170.0,
        "upc": "6 10293 84756 1",
        "servings_per_container": "6",
        "serving_size": "2 cookies (28g)",
        "claims": [
            "Certified Gluten-Free",
            "Non-GMO Project Verified",
            "No Artificial Preservatives",
        ],
        "ingredients": "Blanched Almond Flour, Grass-Fed Sweet Cream Butter (Cream, Salt), Organic Tapioca Starch, Pure Cane Sugar, Cage-Free Whole Eggs, Natural Almond Extract, Himalayan Pink Salt.",
        "allergens": "CONTAINS: Almonds, Milk, Eggs. Produced in a certified gluten-free facility.",
        "distributor": "Baked by Hearth & Oven Artisans, Burlington, VT 05401",
        "storage": "Reseal pouch tightly after opening to preserve freshness.",
        "nutrition": [
            ("Calories", "140", None),
            ("Total Fat", "8g", "10%"),
            ("Saturated Fat", "3g", "15%"),
            ("Trans Fat", "0g", None),
            ("Cholesterol", "15mg", "5%"),
            ("Sodium", "95mg", "4%"),
            ("Total Carbohydrate", "16g", "6%"),
            ("Dietary Fiber", "1g", "4%"),
            ("Total Sugars", "7g", None),
            ("Incl. Added Sugars", "6g", "12%"),
            ("Protein", "2g", None),
            ("Vitamin D", "0mcg", "0%"),
            ("Calcium", "30mg", "2%"),
            ("Iron", "0.6mg", "4%"),
            ("Potassium", "70mg", "2%"),
        ],
    },
    {
        "id": "Sample06_ColdBrewCoffee_Can",
        "brand": "Driftwood Roasters",
        "product_name": "Nitro Cold Brew Coffee Black Unsweetened",
        "legal_name": "NITRO COLD BREWED ARABICA COFFEE",
        "category": "Ready-To-Drink Beverage",
        "net_wt_str": "11 FL OZ (325 mL)",
        "net_wt_g": 325.0,
        "upc": "8 60001 23456 7",
        "servings_per_container": "1",
        "serving_size": "1 can (325 mL)",
        "claims": [
            "Zero Sugar",
            "180mg Natural Caffeine",
            "Rainforest Alliance Certified Coffee",
            "Vegan",
        ],
        "ingredients": "Nitrogen-Infused Cold Brewed Coffee (Purified Water, 100% Single-Origin Colombian Arabica Coffee).",
        "allergens": "None.",
        "distributor": "Driftwood Specialty Coffee Roasters, Seattle, WA 98101",
        "storage": "Serve chilled or over ice. Invert gently before pouring.",
        "nutrition": [
            ("Calories", "5", None),
            ("Total Fat", "0g", "0%"),
            ("Saturated Fat", "0g", "0%"),
            ("Trans Fat", "0g", None),
            ("Cholesterol", "0mg", "0%"),
            ("Sodium", "5mg", "0%"),
            ("Total Carbohydrate", "1g", "0%"),
            ("Dietary Fiber", "0g", "0%"),
            ("Total Sugars", "0g", None),
            ("Incl. Added Sugars", "0g", "0%"),
            ("Protein", "0g", None),
            ("Vitamin D", "0mcg", "0%"),
            ("Calcium", "10mg", "0%"),
            ("Iron", "0.1mg", "0%"),
            ("Potassium", "160mg", "4%"),
        ],
    },
    {
        "id": "Sample07_GreekYogurt_HoneyBerry_Tub",
        "brand": "Alpine Meadow",
        "product_name": "Whole Milk Greek Yogurt Wild Honey & Blackberry",
        "legal_name": "WHOLE MILK STRAINED GREEK YOGURT - WILD HONEY & BLACKBERRY",
        "category": "Cultured Dairy",
        "net_wt_str": "5.3 OZ (150g)",
        "net_wt_g": 150.0,
        "upc": "0 71111 22233 4",
        "servings_per_container": "1",
        "serving_size": "1 container (150g)",
        "claims": ["Kosher Dairy", "All Natural", "Live & Active Probiotic Cultures", "Grade A"],
        "ingredients": "Grade A Pasteurized Whole Milk, Cream, Wildflower Honey, Wild Blackberries, Cane Sugar, Pectin, Live Active Cultures (S. thermophilus, L. bulgaricus, L. acidophilus, Bifidus).",
        "allergens": "CONTAINS: Milk.",
        "distributor": "Alpine Meadow Dairy Co-Op, Montpelier, VT 05602",
        "storage": "Keep refrigerated. Do not freeze.",
        "nutrition": [
            ("Calories", "140", None),
            ("Total Fat", "5g", "6%"),
            ("Saturated Fat", "3g", "15%"),
            ("Trans Fat", "0g", None),
            ("Cholesterol", "20mg", "7%"),
            ("Sodium", "65mg", "3%"),
            ("Total Carbohydrate", "14g", "5%"),
            ("Dietary Fiber", "1g", "4%"),
            ("Total Sugars", "12g", None),
            ("Incl. Added Sugars", "8g", "16%"),
            ("Protein", "11g", "22%"),
            ("Vitamin D", "0mcg", "0%"),
            ("Calcium", "150mg", "10%"),
            ("Iron", "0.2mg", "0%"),
            ("Potassium", "190mg", "4%"),
        ],
    },
    {
        "id": "Sample08_ArtisanPasta_Spelt_Box",
        "brand": "Bella Terra",
        "product_name": "Organic Spelt Penne Rigate",
        "legal_name": "ORGANIC WHOLE GRAIN SPELT PENNE RIGATE",
        "category": "Dry Pasta",
        "net_wt_str": "16 OZ (1 LB) 454g",
        "net_wt_g": 454.0,
        "upc": "8 12345 67891 2",
        "servings_per_container": "8",
        "serving_size": "2 oz (56g / about 3/4 cup dry)",
        "claims": [
            "USDA Organic",
            "Non-GMO Project Verified",
            "Bronze Die Extruded",
            "Good Source of Fiber",
        ],
        "ingredients": "100% Organic Stone-Ground Whole Grain Spelt Flour (Triticum spelta), Mountain Spring Water.",
        "allergens": "CONTAINS: Wheat (Spelt). May contain soy and eggs.",
        "distributor": "Crafted in Italy for Bella Terra Foods, New York, NY 10013",
        "storage": "Store in a cool dry place.",
        "nutrition": [
            ("Calories", "200", None),
            ("Total Fat", "1g", "1%"),
            ("Saturated Fat", "0g", "0%"),
            ("Trans Fat", "0g", None),
            ("Cholesterol", "0mg", "0%"),
            ("Sodium", "0mg", "0%"),
            ("Total Carbohydrate", "41g", "15%"),
            ("Dietary Fiber", "4g", "14%"),
            ("Total Sugars", "1g", None),
            ("Incl. Added Sugars", "0g", "0%"),
            ("Protein", "7g", None),
            ("Vitamin D", "0mcg", "0%"),
            ("Calcium", "18mg", "2%"),
            ("Iron", "1.8mg", "10%"),
            ("Potassium", "170mg", "4%"),
        ],
    },
    {
        "id": "Sample09_SparklingWater_Lime_Can",
        "brand": "Sparkle Springs",
        "product_name": "Sparkling Spring Water Key Lime",
        "legal_name": "NATURAL SPARKLING SPRING WATER WITH KEY LIME ESSENCE",
        "category": "Flavored Carbonated Water",
        "net_wt_str": "12 FL OZ (355 mL)",
        "net_wt_g": 355.0,
        "upc": "0 54321 98765 4",
        "servings_per_container": "1",
        "serving_size": "1 can (355 mL)",
        "claims": ["Zero Calories", "Zero Sodium", "Zero Sweeteners", "Non-GMO Project Verified"],
        "ingredients": "Carbonated Natural Spring Water, Natural Key Lime Essence.",
        "allergens": "None.",
        "distributor": "Bottled at the Source by Sparkle Springs Water Co., Saratoga Springs, NY 12866",
        "storage": "Store in a clean, cool, and odorless place away from direct sunlight.",
        "nutrition": [
            ("Calories", "0", None),
            ("Total Fat", "0g", "0%"),
            ("Saturated Fat", "0g", "0%"),
            ("Trans Fat", "0g", None),
            ("Cholesterol", "0mg", "0%"),
            ("Sodium", "0mg", "0%"),
            ("Total Carbohydrate", "0g", "0%"),
            ("Dietary Fiber", "0g", "0%"),
            ("Total Sugars", "0g", None),
            ("Incl. Added Sugars", "0g", "0%"),
            ("Protein", "0g", None),
            ("Vitamin D", "0mcg", "0%"),
            ("Calcium", "0mg", "0%"),
            ("Iron", "0mg", "0%"),
            ("Potassium", "0mg", "0%"),
        ],
    },
    {
        "id": "Sample10_EnergyBar_MatchaBerry_Foil",
        "brand": "ZenBite",
        "product_name": "Organic Raw Energy Bar Japanese Ceremonial Matcha & Cranberry",
        "legal_name": "ORGANIC RAW FRUIT & NUT ENERGY BAR - MATCHA & CRANBERRY",
        "category": "Organic Raw Snack Bar",
        "net_wt_str": "1.76 OZ (50g)",
        "net_wt_g": 50.0,
        "upc": "8 98765 43210 9",
        "servings_per_container": "1",
        "serving_size": "1 bar (50g)",
        "claims": [
            "USDA Organic",
            "Certified Vegan",
            "Raw & Unprocessed",
            "Gluten-Free",
            "No Added Sugar",
            "35mg Natural Caffeine",
        ],
        "ingredients": "Organic Deglet Noor Dates, Organic Raw Cashews, Organic Dried Cranberries (Sweetened with Organic Apple Juice Concentrate), Organic Japanese Ceremonial Matcha Green Tea Powder, Organic Chia Seeds.",
        "allergens": "CONTAINS: Cashews (Tree Nuts). May contain occasional date pit fragments.",
        "distributor": "ZenBite Organics PBC, San Diego, CA 92101",
        "storage": "Keep in a cool, dry pantry.",
        "nutrition": [
            ("Calories", "190", None),
            ("Total Fat", "6g", "8%"),
            ("Saturated Fat", "1g", "5%"),
            ("Trans Fat", "0g", None),
            ("Cholesterol", "0mg", "0%"),
            ("Sodium", "40mg", "2%"),
            ("Total Carbohydrate", "29g", "11%"),
            ("Dietary Fiber", "4g", "14%"),
            ("Total Sugars", "18g", None),
            ("Incl. Added Sugars", "0g", "0%"),
            ("Protein", "5g", None),
            ("Vitamin D", "0mcg", "0%"),
            ("Calcium", "35mg", "2%"),
            ("Iron", "1.2mg", "6%"),
            ("Potassium", "210mg", "4%"),
        ],
    },
]


def generate_dieline_pdf(spec: dict, output_path: Path) -> None:
    """Create a packaging dieline proof PDF matching Esko / print-prep standards."""
    c = canvas.Canvas(str(output_path), pagesize=(842, 595))  # Landscape A4 dieline
    w, h = 842, 595

    # 1. Background paper
    c.setFillColor(HexColor("#FAFAFB"))
    c.rect(0, 0, w, h, fill=1, stroke=0)

    # 2. Dieline Technical Guides & Borders
    # Bleed outline (Blue)
    c.setStrokeColor(HexColor("#0072BC"))
    c.setLineWidth(0.5)
    c.rect(20, 20, w - 40, h - 40, fill=0, stroke=1)
    c.setFont("Helvetica", 6)
    c.setFillColor(HexColor("#0072BC"))
    c.drawString(25, h - 30, "TECHNICAL BLEED LINE (+3mm)")

    # Dieline Cut Lines (Magenta)
    c.setStrokeColor(HexColor("#E6007E"))
    c.setLineWidth(1.2)
    c.rect(35, 35, w - 70, h - 70, fill=0, stroke=1)
    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(HexColor("#E6007E"))
    c.drawString(42, h - 48, f"DIELINE CUT CONTOUR - {spec['id']} (100% SCALE)")
    c.drawString(w - 210, h - 48, "ARTWORK PROOF - NOT FOR PRODUCTION")

    # Panel Crease / Fold Lines (Dashed Green)
    c.setStrokeColor(HexColor("#00A651"))
    c.setLineWidth(0.8)
    c.setDash(4, 3)

    # 4-panel dieline coordinates
    panel_y0, panel_y1 = 45, h - 55
    x_glue = 90
    x_left = 270
    x_front = 550
    x_right = 730

    # Draw vertical fold lines
    c.line(x_glue, panel_y0, x_glue, panel_y1)
    c.line(x_left, panel_y0, x_left, panel_y1)
    c.line(x_front, panel_y0, x_front, panel_y1)
    c.line(x_right, panel_y0, x_right, panel_y1)
    c.setDash()  # Reset dash

    c.setFont("Helvetica", 7)
    c.setFillColor(HexColor("#00A651"))
    c.drawString(x_glue + 10, panel_y1 + 4, "FOLD CREASE")
    c.drawString(x_left + 10, panel_y1 + 4, "FOLD CREASE")
    c.drawString(x_front + 10, panel_y1 + 4, "FOLD CREASE")
    c.drawString(x_right + 10, panel_y1 + 4, "FOLD CREASE")

    # Panel Guide Labels (Filtered out by dieline filter)
    c.setFont("Helvetica-Oblique", 8)
    c.setFillColor(HexColor("#888888"))
    c.drawString(45, panel_y1 - 15, "GLUE FLAP")
    c.drawString(140, panel_y1 - 15, "SIDE PANEL (LEFT)")
    c.drawString(380, panel_y1 - 15, "PRINCIPAL DISPLAY PANEL (PDP / FRONT)")
    c.drawString(610, panel_y1 - 15, "BACK PANEL / NUTRITION")
    c.drawString(745, panel_y1 - 15, "RIGHT FLAP")

    # 3. PRINCIPAL DISPLAY PANEL (PDP / FRONT) Content (x: 270 to 550)
    pdp_center = (x_left + x_front) / 2.0  # 410.0

    # Brand Title
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(HexColor("#1A1A1A"))
    c.drawCentredString(pdp_center, 440, spec["brand"].upper())

    # Product Title (Centered horizontally)
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(HexColor("#0D47A1"))
    c.drawCentredString(pdp_center, 400, spec["product_name"].split()[0].upper())
    c.setFont("Helvetica-Bold", 15)
    c.setFillColor(HexColor("#1565C0"))
    c.drawCentredString(pdp_center, 375, " ".join(spec["product_name"].split()[1:]).upper())

    # Statement of Identity / Legal Name
    c.setFont("Helvetica", 8)
    c.setFillColor(HexColor("#333333"))
    c.drawCentredString(pdp_center, 345, spec["legal_name"])

    # Claims Badges on PDP
    y_claim = 300
    for clm in spec["claims"][:3]:
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(HexColor("#2E7D32"))
        c.drawCentredString(pdp_center, y_claim, f"★ {clm.upper()} ★")
        y_claim -= 18

    # Net Quantity of Contents (Bottom of PDP)
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(HexColor("#111111"))
    c.drawCentredString(pdp_center, 80, f"NET WT {spec['net_wt_str']}")

    # 4. BACK PANEL CONTENT (x: 550 to 730) - Nutrition Facts & Ingredients
    # Nutrition Facts Box
    nf_x = 565
    nf_w = 150
    nf_top = 460
    c.setStrokeColor(HexColor("#111111"))
    c.setLineWidth(1.5)
    c.rect(nf_x, 150, nf_w, 315, fill=0, stroke=1)

    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(HexColor("#000000"))
    c.drawString(nf_x + 6, nf_top - 18, "Nutrition Facts")

    c.setLineWidth(0.5)
    c.line(nf_x + 6, nf_top - 22, nf_x + nf_w - 6, nf_top - 22)

    c.setFont("Helvetica", 7.5)
    c.drawString(nf_x + 6, nf_top - 32, f"{spec['servings_per_container']} servings per container")
    c.setFont("Helvetica-Bold", 8)
    c.drawString(nf_x + 6, nf_top - 44, f"Serving size  {spec['serving_size']}")

    c.setLineWidth(3.0)
    c.line(nf_x + 6, nf_top - 48, nf_x + nf_w - 6, nf_top - 48)

    # Calories bar
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(nf_x + 6, nf_top - 58, "Amount per serving")
    c.setFont("Helvetica-Bold", 12)
    c.drawString(nf_x + 6, nf_top - 72, "Calories")
    c.setFont("Helvetica-Bold", 16)
    c.drawRightString(nf_x + nf_w - 6, nf_top - 72, spec["nutrition"][0][1])

    c.setLineWidth(1.5)
    c.line(nf_x + 6, nf_top - 76, nf_x + nf_w - 6, nf_top - 76)

    # % Daily Value Header
    c.setFont("Helvetica-Bold", 7)
    c.drawRightString(nf_x + nf_w - 6, nf_top - 85, "% Daily Value*")

    c.setLineWidth(0.5)
    c.line(nf_x + 6, nf_top - 88, nf_x + nf_w - 6, nf_top - 88)

    # Nutrients rows
    y_row = nf_top - 99
    for item, amt, dv in spec["nutrition"][1:]:
        c.setFont("Helvetica-Bold" if "Total" in item or "Protein" in item else "Helvetica", 7)
        c.drawString(nf_x + 6, y_row, f"{item} {amt}")
        if dv:
            c.setFont("Helvetica-Bold", 7)
            c.drawRightString(nf_x + nf_w - 6, y_row, dv)
        c.line(nf_x + 6, y_row - 2, nf_x + nf_w - 6, y_row - 2)
        y_row -= 11

    # Footnote
    c.setFont("Helvetica", 5.5)
    c.drawString(nf_x + 6, y_row - 4, "* The % Daily Value (DV) tells you how much a")
    c.drawString(nf_x + 6, y_row - 11, "nutrient in a serving contributes to a daily diet.")
    c.drawString(nf_x + 6, y_row - 18, "2,000 calories a day is used for nutrition advice.")

    # Barcode UPC (Bottom Back Panel)
    c.setFont("Helvetica", 9)
    c.setFillColor(HexColor("#000000"))
    c.drawString(nf_x + 10, 80, f"UPC: {spec['upc']}")
    c.rect(nf_x + 10, 95, 120, 30, fill=0, stroke=1)
    c.setFont("Helvetica", 6)
    c.drawString(nf_x + 15, 105, "|||| | ||||| ||||| |||| |||||| |||")

    # 5. LEFT SIDE PANEL CONTENT (x: 90 to 270) - Ingredients & Allergens
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(HexColor("#111111"))
    c.drawString(100, 440, "INGREDIENTS:")

    # Wrap ingredients text
    c.setFont("Helvetica", 7)
    y_ing = 425
    words = spec["ingredients"].split()
    curr_line = []
    for w_word in words:
        curr_line.append(w_word)
        if len(" ".join(curr_line)) > 36:
            c.drawString(100, y_ing, " ".join(curr_line))
            y_ing -= 10
            curr_line = []
    if curr_line:
        c.drawString(100, y_ing, " ".join(curr_line))
        y_ing -= 14

    # Allergen Statement
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(100, y_ing, "ALLERGEN INFORMATION:")
    y_ing -= 10
    c.setFont("Helvetica", 7)
    c.drawString(100, y_ing, spec["allergens"][:45])
    if len(spec["allergens"]) > 45:
        y_ing -= 9
        c.drawString(100, y_ing, spec["allergens"][45:90])
    y_ing -= 16

    # Storage & Distributor
    c.setFont("Helvetica-Bold", 7)
    c.drawString(100, y_ing, "STORAGE & HANDLING:")
    y_ing -= 9
    c.setFont("Helvetica", 6.5)
    c.drawString(100, y_ing, spec["storage"][:45])
    y_ing -= 14
    c.setFont("Helvetica", 6.5)
    c.drawString(100, y_ing, spec["distributor"][:45])

    c.save()


def generate_content_sheet_xlsx(spec: dict, output_path: Path) -> None:
    """Create an approved product specification workbook matching enterprise PLM / content sheets."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Content Sheet - US"

    # Header styling
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    section_font = Font(name="Calibri", size=10, bold=True, color="0D47A1")
    header_fill = PatternFill(start_color="1565C0", end_color="1565C0", fill_type="solid")
    section_fill = PatternFill(start_color="E3F2FD", end_color="E3F2FD", fill_type="solid")
    thin_border = Border(
        left=Side(style="thin", color="D0D7DE"),
        right=Side(style="thin", color="D0D7DE"),
        top=Side(style="thin", color="D0D7DE"),
        bottom=Side(style="thin", color="D0D7DE"),
    )

    rows = [
        ("Label Information", "", "", "", "", ""),
        ("Label Identifier", spec["id"], "Approved packaging specification release", "", "", ""),
        (
            "Portions Selected",
            f"{int(spec['net_wt_g'])}g",
            "",
            "Status",
            "Approved / Released",
            "Final approved master packaging spec",
        ),
        ("Product Overview", "", "", "", "", ""),
        ("Brand", spec["brand"], "", "Product Name", spec["product_name"], ""),
        ("Country of Market", "United States", "", "Category", spec["category"], ""),
        ("Language(s)", "English (US)", "", "UPC / Barcode", spec["upc"], ""),
        ("Legal Name & Ingredient Information", "", "", "", "", ""),
        ("Legal Name / Statement of Identity", spec["legal_name"], "", "", "", ""),
        (
            "Ingredient List",
            f"INGREDIENTS: {spec['ingredients']}",
            "Approved formulation word-for-word copy",
            "",
            "",
            "",
        ),
        (
            "Allergen Information",
            spec["allergens"],
            "FALCPA / FASTER Act compliant declarations",
            "",
            "",
            "",
        ),
        ("Storage Instructions", spec["storage"], "", "Distributor", spec["distributor"], ""),
        (
            "Front/Back Panel Claims & Certifications",
            "; ".join(spec["claims"]),
            "Verified legal marketing claims",
            "",
            "",
            "",
        ),
        ("Nutrition Information", "", "", "", "", ""),
        ("Nutrition Panel Format", "US FDA Standard (Vertical)", "", "", "", ""),
        ("Number of Servings per Package", spec["servings_per_container"], "", "", "", ""),
        ("Package Size / Net Weight", spec["net_wt_str"], "", "", "", ""),
        ("Serving Size", spec["serving_size"], "", "", "", ""),
        (
            "Nutrition Panel Bottom Statement",
            "The % Daily Value (DV) tells you how much a nutrient in a serving of food contributes to a daily diet. 2,000 calories a day is used for general nutrition advice.",
            "",
            "",
            "",
            "",
        ),
        ("Nutrient Composition", f"{int(spec['net_wt_g'])}g", "100g", "", "", ""),
    ]

    for r in rows:
        ws.append(list(r))

    # Add nutrition items
    for item, amt, dv in spec["nutrition"]:
        ws.append([item, amt, dv or "–", "", "", ""])

    # Apply styling
    for row in range(1, ws.max_row + 1):
        c1 = ws.cell(row=row, column=1)
        val = str(c1.value or "")
        if val in (
            "Label Information",
            "Product Overview",
            "Legal Name & Ingredient Information",
            "Nutrition Information",
        ):
            for col in range(1, 7):
                cell = ws.cell(row=row, column=col)
                cell.font = header_font
                cell.fill = header_fill
        elif val in ("Nutrient Composition",):
            for col in range(1, 7):
                cell = ws.cell(row=row, column=col)
                cell.font = section_font
                cell.fill = section_fill

        for col in range(1, 7):
            cell = ws.cell(row=row, column=col)
            cell.border = thin_border
            if col == 1:
                cell.font = Font(name="Calibri", size=9, bold=True)
            else:
                cell.font = Font(name="Calibri", size=9)

    ws.column_dimensions["A"].width = 32
    ws.column_dimensions["B"].width = 38
    ws.column_dimensions["C"].width = 30
    ws.column_dimensions["D"].width = 24
    ws.column_dimensions["E"].width = 32
    ws.column_dimensions["F"].width = 30

    wb.save(str(output_path))


def main() -> None:
    print(f"Generating 10 realistic sample packaging pairs in {SAMPLES_DIR}...")
    for idx, spec in enumerate(SAMPLE_SPECS, 1):
        pdf_path = SAMPLES_DIR / f"{spec['id']}.pdf"
        xlsx_path = SAMPLES_DIR / f"{spec['id']}_Content_Sheet.xlsx"

        print(f"[{idx}/10] Generating {spec['id']}...")
        generate_dieline_pdf(spec, pdf_path)
        generate_content_sheet_xlsx(spec, xlsx_path)

    print("\nSuccessfully generated all 10 sample pairs.")
    print("CRITICAL: Per user instructions, these files have NOT been tested against the model.")


if __name__ == "__main__":
    main()
