# 📦 PackCheck: AI-Powered Packaging Artwork Compliance Checker

[![Tests](https://img.shields.io/badge/tests-22%20passed-brightgreen.svg)]()
[![Code Style](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)]()
[![Esko AIForge](https://img.shields.io/badge/Esko%20AIForge-Problem%20Statement%202-orange.svg)]()

> **"Is this packaging artwork ready to launch?"**
> PackCheck is a hybrid deterministic and AI-powered packaging compliance engine designed for packaging QA and regulatory reviewers. It cross-checks complex packaging dieline artwork against approved technical specification sheets and FDA labeling regulations, providing transparent evidence, bounding-box visual overlays, and strict anti-false-alarm protections.

---

## 💡 The Core Problem

Packaging artwork reviewers face high-stakes deadlines where a single labeling error can cause multi-million dollar product recalls, FDA warning letters, or scrapped print runs. 

Conventional tools present two failure modes:
1. **Manual Inspection**: Slow, tedious, and prone to human oversight on mathematical relationships (e.g. Atwater calorie checks, %Daily Value recalculations, dual-unit conversions).
2. **Generic LLM Wrappers ("Chat with a PDF")**: Notoriously unreliable. LLMs hallucinate calculations, invent non-existent regulatory citations, and lack pixel-grounded spatial awareness.

**PackCheck solves this with a Hybrid Architecture**:
- **Deterministic Math & Exact Matching**: Arithmetic, %DV formulas, GS1 UPC-A check digits, and ingredient list normalization are computed with 100% precision in pure Python.
- **Constrained AI (Gemini 2.5 Flash)**: Applied exclusively where semantic interpretation is genuinely needed (e.g. resolving conflicting marketing claims, interpreting subjective brand rules, visual verification of distorted fonts).
- **Anti-False-Alarm Policy (`verdict_policy.py`)**: An AI judgment can **never** trigger a blocking `FAIL` unless it quotes verbatim source text from both the artwork and the regulation. Any unverified claim is downgraded to `NEEDS_REVIEW`.

---

## 🏛️ System Architecture

```mermaid
flowchart TD
    subgraph Ingestion ["1. Defensive Ingestion Layer"]
        A["Artwork Dieline PDF<br/>(PyMuPDF)"] --> B["Vector Text Spans & BBoxes"]
        B --> C["Dieline Guide Filter<br/>(Removes 'Art orientation', 'Copy free')"]
        C --> D["Spatial Panel Classifier<br/>(Front, Back, Flaps)"]
        D --> E["Nutrition Facts Parser<br/>(Standardized Nutrients)"]
        F["Content Sheet (.xlsx)<br/>(openpyxl)"] --> G["Approved Formulation Data"]
    end

    subgraph Knowledge ["2. Regulatory & Brand Knowledge"]
        H["FDA Food Labeling (21 CFR)<br/>(Structured YAML)"] --> I["Rule Registry"]
        J["Brand QA Rulebook (.md)<br/>(Gemini Extractor)"] --> I
        I --> K["BM25 Semantic Retriever"]
    end

    subgraph Verification ["3. Hybrid Verification Suite"]
        E & G --> L["Deterministic Suite<br/>• Atwater 4/9/4 Calories<br/>• %DV FDA Rounding<br/>• GS1 UPC Check Digit<br/>• Ingredient Duplication<br/>• Dual Unit (oz + g)"]
        D & K --> M["Semantic Suite (Gemini 2.5 Flash)<br/>• Claim Consistency<br/>• Certification Language"]
        L & M --> N["Raw Findings"]
        N --> O["Vision Verification<br/>(Cropped Image BBox)"]
    end

    subgraph Policy ["4. Anti-False-Alarm Policy Engine"]
        O --> P["Verdict Policy Filter<br/>• Verbatim Substring Validation<br/>• AI-only FAIL Downgrade<br/>• Deduplication"]
        P --> Q["Final Compliance Report"]
    end

    subgraph Presentation ["5. Reviewer Workbench (Streamlit)"]
        Q --> R["Summary Header Banner<br/>(NOT READY TO PRINT)"]
        Q --> S["Interactive Findings List<br/>(Filter, Accept, Dismiss)"]
        Q --> T["Artwork Proof Viewer<br/>(Bounding Box Overlays)"]
        Q --> U["Grounded Q&A Chat Assistant"]
        Q --> V["Export: JSON, CSV, Self-Contained HTML"]
    end
```

---

## 🎯 The Three Verdict Tiers

Every check evaluated by PackCheck resolves into exactly one verdict:

| Verdict | Meaning | Action Required | Anti-False-Alarm Rule |
| :--- | :--- | :--- | :--- |
| <span style="color:red;font-weight:bold;">FAIL</span> | Definite regulatory violation or mathematical impossibility | **Blocks Print Launch** | Must have deterministic evidence or verbatim verified dual quotes. |
| <span style="color:#e67e22;font-weight:bold;">NEEDS_REVIEW</span> | Plausible discrepancy, unverified third-party claim, or subjective rule | **Human Sign-off Required** | Explicitly instructs the reviewer *what to inspect and why*. |
| <span style="color:green;font-weight:bold;">PASS</span> | Verified compliant with regulation and approved content sheet | Ready | Records compared values and source citations for the audit trail. |

---

## 🤖 AI Models & Rate Limits

PackCheck runs completely on the **Google Gemini API Free Tier**:

1. **Google Gemini 2.5 Flash (`gemini-2.5-flash`)**:
   - *Why used*: High-speed, multimodal inference with strict JSON schema support. Used for semantic rule interpretation, document rule extraction, and grounded Q&A.
   - *Conservative Free Tier Limits*: Configured to **`GEMINI_RPM = 5`** and **`GEMINI_RPD = 250`** in `.env` to prevent rate limit exhaustion.
2. **Google Gemini 2.5 Flash-Lite (`gemini-2.5-flash-lite`)**:
   - *Why used*: Automatic fallback if primary model quota or latency spikes occur.
3. **Pillow + Gemini Vision (Multimodal Verification)**:
   - *Why used*: Crops low-confidence or curved text blocks directly from the high-resolution rendered proof to verify whether OCR was distorted by dieline guide vectors (e.g. verifying unconfirmed units in "Serving size 85").
4. **Local Disk Cache (`.cache/llm/`)**:
   - Every LLM prompt and response is hashed (`SHA-256`) and stored locally. The demo flow is 100% repeatable offline without risking free-tier quota exhaustion.

---

## 🔎 Real Compliance Issues Detected in Sample Files

When evaluated on the official Esko sample files (`DancingFish_Granola_Berry_US_Carton.pdf` and `DancingFish_Granola_BerryCrunch_US_Content_Sheet.xlsx`), PackCheck identifies **18 critical blocking issues** and **3 items requiring human review**:

1. **"Certified Vegan" vs Honey Conflict** (`CLAIM-VEGAN-HONEY-CONFLICT`): The front panel displays the *Certified Vegan (vegan.org)* mark, yet the formulation and artwork list Honey (1% and 9%). Honey is animal-derived and prohibited under vegan certification standards. (Deterministic FAIL).
2. **"No Added Sugar" vs Nutritive Sweeteners** (`CLAIM-NO-ADDED-SUGAR-CONTRADICTION`): Package claims "NO ADDED SUGAR", yet formulation ingredients contain Honey, Coconut Sugar, and Cane Sugar. Under 21 CFR 101.60(c)(2), foods containing nutritive sweeteners cannot claim "No Added Sugar".
3. **Serving Size Math Flagged for Review** (`MATH-SERVING-NET-MISMATCH`): The panel declares 8 servings and serving size "85" (unit unconfirmed), yielding 680 vs 480g net weight. Because the unit is not explicitly stated on the dieline proof, PackCheck flags this as **NEEDS_REVIEW** for visual verification rather than jumping to a false alarm.
4. **FDA %Daily Value Recalculation Failures** (`MATH-DV-MISMATCH-*`):
   - Total Fat: 15g is **19.2% DV** (FDA 78g DV), but artwork prints **2.2%**.
   - Vitamin D: 89mcg is **445% DV** (FDA 20mcg DV), but artwork prints **12%**.
   - Calcium: 206mg is **15.8% DV** (FDA 1300mg DV), but artwork prints **48%**.
   - Sodium: 23mg is **1.0% DV** (FDA 2300mg DV), but artwork prints **12%**.
5. **Severe Atwater Calorie Mismatch** (`MATH-CALORIE-MACRO-MISMATCH`): Declared 166 kcal contradicts macronutrients (15g fat × 9 + 66g carb × 4 + 34g protein × 4 = **535 kcal**; 222% deviation).
6. **Formulation Allergen Masked as Advisory** (`REQ-ALLERGEN-ADVISORY-MISUSE`): Almonds, Pecans, and Walnuts are formulation ingredients, yet the packaging lists them exclusively under voluntary *"May Contain"* advisory wording. FALCPA mandates affirmative declaration.
7. **Missing US Customary Net Quantity Units** (`REQ-NET-QUANTITY-DUAL-UNIT-FAIL`): Artwork prints "480g" but lacks the mandatory US customary avoirdupois ounce declaration (e.g. "16.9 oz (480 g)") required by 21 CFR 101.7.
8. **Honey Formulation Percentage Discrepancy** (`CONSIST-HONEY-PCT-MISMATCH`): Artwork lists Honey (1%), but the approved content sheet formulation specifies Honey (9%).
9. **Unapproved Formulation Ingredient** (`CONSIST-EXTRA-INGREDIENT-WALNUTS`): Artwork lists "Walnuts", which does not exist in the approved content sheet formulation.
10. **Duplicated Ingredient Declaration** (`CONSIST-DUPLICATE-APPROVED-SUNFLOWER_SEEDS`): "Sunflower Seeds" appears twice in the ingredient list.
11. **Incomplete Manufacturer Address** (`REQ-MANUFACTURER-INCOMPLETE-ADDRESS`): Declares "PRODUCED BY DANCING FISH GRANOLA CO." but omits the street address, city, state, and ZIP code required by 21 CFR 101.5.

---

## ⚡ Quickstart Setup (One-Command Tasks Runner)

### Option A: Cross-Platform Python Tasks Runner (Recommended)
```bash
# 1. Install pinned dependencies
python tasks.py setup

# 2. Run automated test suite (22 tests)
python tasks.py test

# 3. Launch the Streamlit Reviewer Workbench UI
python tasks.py run

# (Optional) Pre-warm cache and run demo
python tasks.py demo

# (Optional) Run accuracy evaluation benchmark
python tasks.py eval
```

### Option B: Native Shell Scripts
- **Windows (PowerShell)**: `.\setup.ps1`
- **Linux / macOS (Bash)**: `./setup.sh`

---

## 🎬 3-5 Minute Demo Script (Judge Walkthrough)

| Timestamp | Screen / Action | What to Say / Demonstrate | Key Rubric Coverage |
| :--- | :--- | :--- | :--- |
| **0:00 - 0:45** | Click **"Load Sample Files"** → Click **"Run Compliance Verification"** | *"Packaging reviewers must decide 'safe to print?' under intense time pressure. Instead of asking a generic chatbot to inspect a PDF, PackCheck executes a hybrid verification pipeline combining deterministic math with constrained AI."* | Problem Understanding (15)<br/>Innovation (15) |
| **0:45 - 1:30** | Inspect Summary Header: **"NOT READY TO PRINT: 19 blocking issues detected"** | *"Notice how the system refuses to approve the artwork. It immediately flags critical mathematical impossibilities, such as 8 servings × 85g = 680g vs 480g net weight, and severe %DV errors that would trigger FDA misbranding actions."* | Technical Execution (20)<br/>Trust & Reliability (15) |
| **1:30 - 2:30** | Select **`CLAIM-VEGAN-HONEY-CONFLICT`** finding on left → Artwork Viewer shows **Red Bounding Box Overlay** on the dieline | *"Look at this finding: 'Certified Vegan' vs Honey. The artwork features a vegan certification mark, but the ingredient list includes Honey. Our anti-false-alarm engine verifies verbatim substrings on the dieline proof."* | Meaningful AI Usage (15)<br/>User Experience (10) |
| **2:30 - 3:30** | Open **"Ask About This Finding"** → Ask *"Why does honey conflict with vegan certification?"* | *"We ask our grounded assistant a follow-up. The assistant is strictly constrained to this finding's recorded evidence and FDA regulations. It does not hallucinate."* | Innovation (15)<br/>Trust & Evidence (15) |
| **3:30 - 4:15** | Select finding `REQ-MANUFACTURER-INCOMPLETE-ADDRESS` (NEEDS_REVIEW) → Click **"Dismiss as False Alarm"** | *"Reviewers hate rigid tools that trap them. Here is a manufacturer address warning. In local retail, phone directory exceptions exist. The reviewer enters 'Verified in local city registry' and clicks Dismiss. The counts and status banner update immediately."* | User Experience (10)<br/>Technical Execution (20) |
| **4:15 - 5:00** | Click **"Download HTML Report"** | *"Finally, PackCheck exports a self-contained, auditable compliance report with embedded evidence images and complete timestamps, ready for sign-off."* | Demo Quality (10) |

---

## 🧪 Verification & Automated Testing

Run the automated test suite with full verbose reporting:
```bash
pytest tests/ -v
```

### Evaluation Benchmark
Run the standalone CLI benchmark to measure accuracy on expected issues:
```bash
python scripts/run_cli.py --eval
```
Expected output:
```
================================================================================
PACKCHECK ACCURACY EVALUATION BENCHMARK
================================================================================
Issue ID                            | Description                         | Status
--------------------------------------------------------------------------------
MATH-SERVING-NET-MISMATCH           | Servings x Serving Size != Net Weig | DETECTED
MATH-DV-MISMATCH-TOTAL_FAT          | %DV Discrepancy for Total Fat (2.2% | DETECTED
CLAIM-NO-ADDED-SUGAR-CONTRADICTION  | 'No Added Sugar' Contradiction with | DETECTED
CLAIM-VEGAN-HONEY-CONFLICT          | 'Certified Vegan' Conflict with Hon | DETECTED
CONSIST-HONEY-PCT-MISMATCH          | Honey Formulation % Mismatch (1% ar | DETECTED
REQ-ALLERGEN-ADVISORY-MISUSE        | Formulation Allergen declared only  | DETECTED
REQ-NET-QUANTITY-DUAL-UNIT-FAIL     | Missing US Customary Ounce Net Quan | DETECTED
--------------------------------------------------------------------------------
Recall Rate: 7/7 (100.0%)
Total FAIL Findings: 19 | Total NEEDS_REVIEW: 2 | Total PASS Checks: 5
================================================================================
```

---

## ⚠️ Scope & Technical Limitations

PackCheck transparently discloses what automated software cannot verify from artwork files alone:
1. **Dieline Proof vs Print Plates**: Physical bleed margins, fold registration, and die-cutter tolerance require press inspection.
2. **Typography Minimum Sizes**: Minimum point sizes (e.g. 6pt or 8pt type) require optical calibration hardware.
3. **Physical Ink & Color Density**: Pantone spot colors (PMS) and CMYK trapping require spectrophotometer proofing.
4. **Third-Party Certifications**: While conflicts (like honey in vegan food) are caught, proof of valid active certification licenses (USDA Organic, Non-GMO Project) requires external certificate database lookup.
