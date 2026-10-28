"""Generate a comprehensive publication-quality PDF explaining the entire PackCheck project structure,
directory layout, module architecture, file-by-file technicalities, and algorithms.
"""

import sys
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
)

class NumberedCanvas(canvas.Canvas):
    """Canvas that computes total pages dynamically and prints headers and footers."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_pages: int):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))

        # Header (Pages 2+)
        if self._pageNumber > 1:
            self.drawString(
                36,
                11 * inch - 26,
                "PackCheck Enterprise | Comprehensive Project Architecture & Directory Specification",
            )
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(36, 11 * inch - 30, 8.5 * inch - 36, 11 * inch - 30)

        # Footer (All pages)
        footer_text = f"Page {self._pageNumber} of {total_pages}"
        self.drawRightString(8.5 * inch - 36, 22, footer_text)
        self.drawString(
            36, 22, "CONFIDENTIAL & PROPRIETARY — Esko AIForge Hackathon 2026 Submission Document"
        )
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(36, 32, 8.5 * inch - 36, 32)

        self.restoreState()


def build_pdf(output_path: Path):
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=38,
        bottomMargin=38,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "CoverTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=3,
    )
    subtitle_style = ParagraphStyle(
        "CoverSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#0284C7"),
        spaceAfter=8,
    )
    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True,
    )
    h2_style = ParagraphStyle(
        "Heading2_Custom",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=12.5,
        textColor=colors.HexColor("#1E293B"),
        spaceBefore=6,
        spaceAfter=3,
        keepWithNext=True,
    )
    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#334155"),
        spaceAfter=3.5,
    )
    code_style = ParagraphStyle(
        "Code_Custom",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=7,
        leading=9.5,
        textColor=colors.HexColor("#0F172A"),
    )
    callout_style = ParagraphStyle(
        "Callout_Text",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=10.5,
        textColor=colors.HexColor("#0F172A"),
    )

    story = []

    # =============================================================
    # PAGE 1: TITLE & EXECUTIVE ARCHITECTURE BREAKDOWN
    # =============================================================
    story.append(Paragraph("📦 PackCheck Enterprise", title_style))
    story.append(
        Paragraph(
            "Complete Project Structure, Codebase Directory & Engineering Architecture Specification",
            subtitle_style,
        )
    )

    meta_table_data = [
        [
            Paragraph("<b>Target System:</b> Esko AIForge Problem Statement 2 ('Ready to Launch?')", body_style),
            Paragraph("<b>Engineering Paradigm:</b> Zero-Hallucination Hybrid (Deterministic Math + Gemini 2.5 Vision)", body_style),
        ],
        [
            Paragraph("<b>Runtime Environment:</b> Python 3.11 - 3.13 / Streamlit 1.40+ / PyMuPDF 1.25+", body_style),
            Paragraph("<b>Persistent Storage:</b> Local SQLite Database (packcheck.db)", body_style),
        ],
    ]
    meta_table = Table(meta_table_data, colWidths=[270, 270])
    meta_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#E2E8F0")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ("PADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(meta_table)
    story.append(Spacer(1, 6))

    story.append(Paragraph("1. Codebase Root Architecture & Directory Map", h1_style))
    story.append(
        Paragraph(
            "The repository is organized into distinct, decoupled tiers separating configuration, ingestion, deterministic checking, "
            "multimodal visual AI, persistent storage, interactive UI, and unit test automation. Below is the complete directory taxonomy:",
            body_style,
        )
    )

    root_files_data = [
        ["Directory / File", "Role & Engineering Responsibility"],
        ["app/streamlit_app.py", "Production user interface with 5 operational sections: Findings Explorer, Physical Review, Spec Cross Checker, Precedents, and AI Assistant."],
        ["src/packcheck/", "Core engine package containing data models, PDF/Excel parsers, deterministic rules, SQLite storage, and LangGraph assistant."],
        ["data/packcheck.db", "Local persistent SQLite database storing reviewer finding waivers, pressroom sign-offs, and custom physical parameters."],
        ["data/rules/", "Statutory regulatory rulebooks in YAML/Markdown: FDA 21 CFR labeling, India FSSAI 2020 regulations, and corporate brand rules."],
        ["data/samples/", "Repository of 11 real-world packaging test pairs (folding cartons, wrappers, cans, bottles) + pre-press meeting transcripts."],
        ["tests/", "Comprehensive unit test suite with 28 automated tests across math, barcodes, dielines, FSSAI rules, and verdict policies."],
        [".env / .env.example", "Environment configuration for Google Gemini API keys, free-tier rate limits (5 RPM / 250 RPD), and offline fallback models."],
        ["pyproject.toml / requirements.txt", "Package dependencies (pymupdf, streamlit, openpyxl, reportlab, langgraph, pillow, google-genai, pytest)."],
    ]
    t_root = Table(root_files_data, colWidths=[140, 400])
    t_root.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 7.5),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F8FAFC")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F8FAFC")]),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 7),
                ("PADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    story.append(t_root)
    story.append(Spacer(1, 6))

    story.append(Paragraph("2. Top-Level Core Package: `src/packcheck/`", h1_style))
    story.append(
        Paragraph(
            "The `src/packcheck/` directory houses the primary engine modules orchestrating the verification pipeline:",
            body_style,
        )
    )

    core_modules_data = [
        ["Module Path", "Key Classes / Functions", "Detailed Description & Mechanics"],
        [
            "src/packcheck/engine.py",
            "run_compliance_check()\nComplianceEngine",
            "Central pipeline coordinator. Orchestrates artwork parsing, spec loading, rule selection (FDA vs FSSAI), "
            "runs deterministic and semantic checks, evaluates dieline geometry, and attaches precedent history.",
        ],
        [
            "src/packcheck/models.py",
            "ArtworkDocument, ApprovedSpecification,\nFinding, Evidence, NutritionTable, Rule",
            "Strongly typed Pydantic V2 data models enforcing strict schema boundaries across extracted text blocks, "
            "vector bounding boxes, nutrient values, and audit findings.",
        ],
        [
            "src/packcheck/config.py",
            "GEMINI_API_KEY, BASE_DIR,\nRULES_DIR, SAMPLES_DIR",
            "Loads environment variables from root `.env` file via `dotenv`, sets up free-tier safe API rate limits, and exports canonical file paths.",
        ],
        [
            "src/packcheck/verdict_policy.py",
            "enforce_dual_quote_policy()\ndeduplicate_findings()",
            "Anti-hallucination gate. Requires verbatim string matches from both artwork PDF and approved Excel before an LLM finding can issue a FAIL.",
        ],
        [
            "src/packcheck/qa.py",
            "ask_packaging_gemini_assistant()",
            "Multimodal Q&A assistant using Gemini 2.5 Flash with grounded fallbacks. Ingests artwork, specs, transcripts, logs, and rulebooks.",
        ],
        [
            "src/packcheck/report.py",
            "export_json(), export_csv(),\nexport_html()",
            "Generates certified pre-press artifacts: machine-readable JSON audit trails, tabular CSV findings, and standalone printable HTML certificates.",
        ],
    ]
    t_core = Table(core_modules_data, colWidths=[120, 130, 290])
    t_core.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 7.5),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F8FAFC")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F8FAFC")]),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 6.8),
                ("PADDING", (0, 0), (-1, -1), 2.5),
            ]
        )
    )
    story.append(t_core)

    story.append(PageBreak())

    # =============================================================
    # PAGE 2: INGESTION, DIELINE & GEOMETRY SUBSYSTEMS
    # =============================================================
    story.append(Paragraph("3. Ingestion & Dieline CAD Filtering Subsystem (`src/packcheck/ingest/`)", h1_style))
    story.append(
        Paragraph(
            "Packaging PDFs contain a mixture of printable consumer text and non-printing technical dieline guides. "
            "The `ingest` package cleanly separates these layers without raster distortion:",
            body_style,
        )
    )

    ingest_table_data = [
        ["Module File", "Core Functionality & Algorithmic Process"],
        [
            "src/packcheck/ingest/artwork.py",
            "Extracts vector text blocks, typeface point sizes, and bounding box coordinates using PyMuPDF (`fitz`). "
            "Renders high-resolution 200 DPI PNG proofs for visual overlays. Distinguishes Spot Color ink layers.",
        ],
        [
            "src/packcheck/ingest/dieline_filter.py",
            "Pattern-matching and regex filter that purges technical CAD dieline annotations (e.g. 'CREASE', 'DIE CUT', "
            "'GLUE FLAP', 'FOLD HERE', 'SCORE') so they are never misconstrued as unapproved ingredients or claims.",
        ],
        [
            "src/packcheck/ingest/contentsheet.py",
            "Parses approved master formulation Excel workbooks (.xlsx) using `openpyxl`. Extracts declared allergens, "
            "marketing claims, UPC/GTIN barcodes, serving size, and raw recipe ingredients into typed data structures.",
        ],
        [
            "src/packcheck/ingest/nutrition_parser.py",
            "Deterministic text tokenizer extracting tabular Nutrition Facts panels: identifies calories, servings per container, "
            "metric gram values, and stated % Daily Values across standard FDA and FSSAI tabular formats.",
        ],
        [
            "src/packcheck/ingest/panels.py",
            "Spatial panel segmentation algorithm dividing multi-panel carton dielines into Principal Display Panel (PDP), "
            "Information Panel, side panels, and top/bottom closure flaps based on vector geometry.",
        ],
    ]
    t_ingest = Table(ingest_table_data, colWidths=[150, 390])
    t_ingest.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 7.5),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F8FAFC")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F8FAFC")]),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 7),
                ("PADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    story.append(t_ingest)
    story.append(Spacer(1, 6))

    story.append(Paragraph("4. Vector Dieline CAD Geometry & Spatial Mechanics", h1_style))
    story.append(
        Paragraph(
            "Located in `src/packcheck/dieline/` and `src/packcheck/checks/vision/design_language.py`, this module measures physical package safety:",
            body_style,
        )
    )

    cad_box = [
        [
            Paragraph(
                "<b>1. Euclidean Crease Margin Safety:</b> Evaluates the perpendicular Euclidean distance from consumer copy vertices "
                "to dieline crease/score lines. Enforces a statutory safety margin of <b>&ge; 8.0 pt (~2.82 mm)</b> to prevent copy cracking "
                "or folding into structural carton seams on high-speed automated folding lines.<br/>"
                "<b>2. Front Panel Title Centering:</b> Computes the horizontal midpoint delta: &Delta; = |cx_text - cx_panel| / w_panel * 100%. "
                "Enforces &Delta; &le; 5.0% tolerance to guarantee visual balance on retail display shelves.<br/>"
                "<b>3. Minimum Typeface Sizing:</b> Inspects PDF font matrices to assert compliance with FDA 21 CFR &sect; 101.2(c) and "
                "FSSAI rules (minimum 6.0 pt / 1/16-inch letter height for mandatory informational text).",
                callout_style,
            )
        ]
    ]
    t_cad = Table(cad_box, colWidths=[540])
    t_cad.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EFF6FF")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#93C5FD")),
                ("PADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(t_cad)
    story.append(Spacer(1, 6))

    story.append(Paragraph("5. Deterministic Compliance Engines (`src/packcheck/checks/deterministic/`)", h1_style))
    story.append(
        Paragraph(
            "This package eliminates LLM hallucinations by calculating mathematical, barcode, and formulation checks in pure Python:",
            body_style,
        )
    )

    det_table_data = [
        ["Module File", "Inspection Authority", "Calculations & Regulatory Rules"],
        [
            "nutrition_math.py",
            "FDA 21 CFR § 101.9",
            "Calculates % Daily Values against FDA Reference Daily Values (DRVs). Recalculates caloric bounds using "
            "Atwater 4-4-9 factors (4*protein + 4*carbs + 9*fat). Checks fat/carb subcomponent constraints.",
        ],
        [
            "upc_check.py",
            "GS1 General Specs § 7.9.1",
            "Calculates Modulo-10 barcode check digits: (10 - ((3*Sum_odd + Sum_even) mod 10)) mod 10. Validates UPC-A length.",
        ],
        [
            "fssai_check.py",
            "India FSSAI Regulations 2020",
            "Validates 14-digit FSSAI license numbers (Central vs State codes), Veg/Non-Veg logo presence, Mfg/Best-Before dates, "
            "MRP inclusive of taxes, and enforces the statutory 2.0% Trans Fat cap relative to total fat.",
        ],
        [
            "ingredient_diff.py",
            "PLM Recipe Reconciliation",
            "Cross-checks ingredient percentages (e.g. 8% approved honey vs 12% printed claim), flags unapproved ingredients "
            "(e.g. walnuts on proof), and detects duplicate declarations (e.g. repeated sunflower seeds).",
        ],
        [
            "required_elements.py",
            "FDA & FSSAI Statutes",
            "Verifies presence of mandatory Statement of Identity, Net Quantity dual units (metric + imperial), manufacturer contact, "
            "and statutory allergen statements ('CONTAINS: ...').",
        ],
    ]
    t_det = Table(det_table_data, colWidths=[120, 110, 310])
    t_det.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 7.5),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F8FAFC")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F8FAFC")]),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 6.8),
                ("PADDING", (0, 0), (-1, -1), 2.5),
            ]
        )
    )
    story.append(t_det)

    story.append(PageBreak())

    # =============================================================
    # PAGE 3: PERSISTENCE, TRANSCRIPTS & APPLICATION LAYER
    # =============================================================
    story.append(Paragraph("6. Persistent Storage & Audit Subsystem (`src/packcheck/db/storage.py`)", h1_style))
    story.append(
        Paragraph(
            "PackCheck maintains a local persistent SQLite database at `data/packcheck.db` tracking compliance history across production runs:",
            body_style,
        )
    )

    db_schema_data = [
        ["Table Name", "Primary Columns", "Functional Role in Pre-Press QA"],
        [
            "finding_dismissals",
            "finding_id, finding_title, category,\nrule_id, artwork_filename, reason,\nreviewer_name, timestamp",
            "Stores reviewer manual sign-offs and regulatory waivers. Provides historical precedent retrieval when sibling SKUs are audited.",
        ],
        [
            "physical_review_parameters",
            "id, artwork_filename, param_name,\nspec_target, is_verified, checked_by,\nnotes, timestamp",
            "Stores custom physical packaging checks (e.g. Sutherland Rub Test, Hot Foil Stamping, Braille Height, Lamination Adhesion).",
        ],
        [
            "audit_log",
            "id, action, artwork_filename, details,\nreviewer_name, timestamp",
            "Immutable chronological system timeline tracking all scans, dismissals, restorations, and pressroom hardware sign-offs.",
        ],
    ]
    t_db = Table(db_schema_data, colWidths=[120, 150, 270])
    t_db.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 7.5),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F8FAFC")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F8FAFC")]),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 7),
                ("PADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    story.append(t_db)
    story.append(Spacer(1, 6))

    story.append(Paragraph("7. Pre-Press Transcript Intelligence (`src/packcheck/transcripts/`)", h1_style))
    story.append(
        Paragraph(
            "Parses pre-press meeting transcripts (`parser.py`) and executes BM25 semantic retrieval (`rag.py`) over alignment discussions. "
            "Crucially, it enforces the <b>Document Authority & Legal Precedence Hierarchy</b>:<br/>"
            "• <b>Tier 1: Statutory Law</b> (FDA 21 CFR / India FSSAI)<br/>"
            "• <b>Tier 2: Written Specification</b> (Master Content Sheet .xlsx v2.4)<br/>"
            "• <b>Tier 3: Dieline Artwork Proof</b> (.pdf)<br/>"
            "• <b>Tier 4: Meeting Transcripts</b> (Advisory Context Only - cannot legally override written specs)",
            body_style,
        )
    )
    story.append(Spacer(1, 4))

    story.append(Paragraph("8. Streamlit Production UI (`app/streamlit_app.py`) — The 5 Sections", h1_style))
    story.append(
        Paragraph(
            "The web dashboard is organized into exactly 5 consolidated production tabs post-investigation:",
            body_style,
        )
    )

    ui_sections_data = [
        ["Section Name", "Interactive Features & Engineering Capabilities"],
        [
            "1. Findings Explorer",
            "Displays all compliance findings with category filtering (Nutrition Math, Formulation, Claims, Regulatory, Design). "
            "Features the Root Cause Insight banner explaining the 60g calculation error, bounding box zoom, and persistent dismissal.",
        ],
        [
            "2. Physical Review",
            "Left: Dieline proof preview with bounding box overlay and centering metrics. "
            "Right: AI-pulled rulebook checks (minimum 6pt font size, 8pt crease margin clearance, GS1 barcode checksum). "
            "Bottom: Custom Parameter tool allowing operators to log missing tests (e.g. rub resistance, foil register) into SQLite.",
        ],
        [
            "3. Specification Cross Checker",
            "Side-by-side comparative reconciliation between approved PLM specifications (.xlsx) and printed dieline copy (.pdf). "
            "Highlights recipe mismatches (Honey 8% vs 12%), unapproved walnuts, duplicate sunflower seeds, and full nutrition table.",
        ],
        [
            "4. Precedent Logs of All Kinds",
            "Unified repository with a Global Search Bar and 4 sub-tabs: (1) Reviewer Dismissals, (2) Physical Review & Sign-Offs, "
            "(3) Meeting Transcript Decisions with the Legal Hierarchy, and (4) The immutable system audit trail.",
        ],
        [
            "5. AI Packaging Assistant",
            "Interactive conversational assistant powered by Google Gemini 2.5 Flash and grounded reasoning. Ingests full product context: "
            "specs, artwork, findings, transcripts, physical logs, and FDA/FSSAI rulebooks. Includes one-click quick inquiries.",
        ],
    ]
    t_ui = Table(ui_sections_data, colWidths=[140, 400])
    t_ui.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 7.5),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F8FAFC")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F8FAFC")]),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 7),
                ("PADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    story.append(t_ui)

    story.append(PageBreak())

    # =============================================================
    # PAGE 4: DATASETS, RULEBOOKS & TEST AUTOMATION
    # =============================================================
    story.append(Paragraph("9. Regulatory Rulebooks Repository (`data/rules/`)", h1_style))
    story.append(
        Paragraph(
            "Regulatory standards are defined declaratively in machine-readable YAML files loaded into Pydantic models:",
            body_style,
        )
    )

    rules_table_data = [
        ["Rulebook File", "Jurisdiction / Scope", "Defined Rules & Validation Logic"],
        [
            "data/rules/fda_food_labeling.yaml",
            "US FDA 21 CFR § 101",
            "Mandatory Statement of Identity (PDP), Net Quantity dual units, Nutrition Facts panel format, 21 CFR 101.9 %DV, "
            "Atwater caloric tolerance, Allergen 'Contains' declaration, and manufacturer street address.",
        ],
        [
            "data/rules/fssai_food_labeling.yaml",
            "India FSSAI Regulations 2020",
            "14-digit FSSAI License Number format (`FSSAI-LIC-001`), Veg/Non-Veg logo geometry (`FSSAI-VEG-001`), Date of Mfg/Expiry, "
            "MRP inclusive of taxes (`FSSAI-MRP-001`), and strict statutory 2.0% Trans Fat cap (`FSSAI-NUT-002`).",
        ],
        [
            "data/rules/company_rulebook.md",
            "Corporate Brand Guidelines",
            "Brand typography standards, minimum logo safety clearances, certified vegan restrictions against honey/whey, and tone of voice.",
        ],
    ]
    t_rules = Table(rules_table_data, colWidths=[150, 110, 280])
    t_rules.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 7.5),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F8FAFC")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F8FAFC")]),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 6.8),
                ("PADDING", (0, 0), (-1, -1), 2.5),
            ]
        )
    )
    story.append(t_rules)
    story.append(Spacer(1, 6))

    story.append(Paragraph("10. Automated Unit Test Suite (`tests/`) — 28/28 Passing", h1_style))
    story.append(
        Paragraph(
            "PackCheck maintains 100% pass rates across 28 unit tests verifying every mathematical formula, dieline filter, and regulatory check:",
            body_style,
        )
    )

    test_table_data = [
        ["Test Module", "Tests", "What It Mathematically & Operationally Verifies"],
        ["test_nutrition_math.py", "5", "Verifies %DV calculation against FDA DRVs, Atwater 4-4-9 caloric bounds, and fat/carb subcomponents."],
        ["test_fssai.py", "3", "Tests FSSAI 14-digit license regex, statutory 2% trans-fat cap enforcement, and valid/invalid passes."],
        ["test_upc.py", "4", "Tests GS1 Modulo-10 checksum algorithm, valid/invalid check digits, and length constraints."],
        ["test_ingredient_diff.py", "3", "Verifies recipe percentage mismatches (Honey 8% vs 12%), unapproved walnuts, and duplicate seeds."],
        ["test_dieline_filter.py", "2", "Asserts technical CAD guides are stripped while actual packaging copy is preserved."],
        ["test_meeting_transcripts.py", "3", "Verifies speaker turn parsing, RAG semantic search, and Written Spec Precedence enforcement."],
        ["test_verdict_policy.py", "4", "Tests anti-hallucination dual-quote policy (downgrading unverified LLM claims) and deduplication."],
        ["test_artwork_ingest.py", "1", "Tests PyMuPDF vector text extraction, font size calculations, and high-res rendering."],
        ["test_contentsheet.py", "1", "Tests openpyxl ingestion of master formulation Excel sheets and metadata mapping."],
        ["test_e2e_golden.py", "1", "End-to-end golden run on DancingFish Granola verifying comprehensive finding generation."],
        ["test_false_alarm.py", "1", "Verifies that a 100% clean compliant packaging sample produces zero false alarms."],
    ]
    t_test = Table(test_table_data, colWidths=[130, 40, 370])
    t_test.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 7.5),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F8FAFC")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F8FAFC")]),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 6.8),
                ("PADDING", (0, 0), (-1, -1), 2),
            ]
        )
    )
    story.append(t_test)
    story.append(Spacer(1, 6))

    story.append(Paragraph("11. Packaging Benchmark Samples (`data/samples/`)", h1_style))
    story.append(
        Paragraph(
            "The repository includes 11 complete packaging pairs for evaluation: 1 Golden Sample (DancingFish Granola) + "
            "10 un-tested FMCG benchmark pairs across folding cartons, flow wraps, glass bottles, metal cans, and dairy tubs.",
            body_style,
        )
    )

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated project structure PDF at: {output_path}")


if __name__ == "__main__":
    out_file = Path("PackCheck_Complete_Architecture_and_Project_Structure.pdf")
    build_pdf(out_file)
