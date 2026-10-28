"""PackCheck compliance orchestration engine."""

from collections.abc import Callable
from datetime import datetime
from pathlib import Path

from src.packcheck.checks.deterministic.claims import ClaimsCheck
from src.packcheck.checks.deterministic.consistency import ConsistencyCheck
from src.packcheck.checks.deterministic.fssai_check import FSSAICheck
from src.packcheck.checks.deterministic.nutrition_math import NutritionMathCheck
from src.packcheck.checks.deterministic.required_elements import RequiredElementsCheck
from src.packcheck.checks.semantic.rule_check import SemanticRuleCheck
from src.packcheck.checks.semantic.vision_verify import VisionVerifier
from src.packcheck.checks.visual.design_language import DesignLanguageCheck
from src.packcheck.config import RULES_DIR
from src.packcheck.db.storage import find_dismissal_precedents, get_active_dismissals
from src.packcheck.ingest.artwork import ingest_artwork_pdf
from src.packcheck.ingest.contentsheet import ingest_content_sheet
from src.packcheck.ingest.nutrition_parser import parse_artwork_nutrition
from src.packcheck.llm.client import GeminiClient
from src.packcheck.models import ApprovedData, ArtworkDoc, Finding, Report, Rule
from src.packcheck.rules.loader import load_yaml_rules
from src.packcheck.verdict_policy import apply_verdict_policy, deduplicate_findings

# Standard regulatory and technical limitations
UNVERIFIED_LIMITATIONS = [
    "Dieline cut, crease, and bleed margins are technical proofs, not certified print-ready plates.",
    "Type font sizes and point dimensions (e.g. 6pt / 8pt FDA minimums) were not optically micrometer-measured.",
    "Third-party organic, non-GMO, and kosher certifications cannot be legally verified from artwork alone.",
    "Color legibility, contrast ratios, and spot ink formulations (PMS Pantone) require physical proofing.",
    "Barcode quiet zone clearance and optical reflectance grade require ISO/IEC 15416 verifier hardware.",
]


def run_compliance_check(
    artwork_path: str | Path,
    content_sheet_path: str | Path,
    rules: list[Rule] | None = None,
    custom_rulebook_text: str | None = None,
    progress_callback: Callable[[float, str], None] | None = None,
    enable_semantic: bool = True,
    enable_vision: bool = True,
    gemini_key: str | None = None,
    jurisdiction: str = "US_FDA",
) -> tuple[Report, ArtworkDoc, ApprovedData]:
    """Execute end-to-end compliance check and produce validated Report."""
    if progress_callback:
        progress_callback(0.10, "Ingesting PDF artwork and rendering preview...")

    # 1. Ingest Artwork
    artwork = ingest_artwork_pdf(artwork_path)
    parse_artwork_nutrition(artwork)

    if progress_callback:
        progress_callback(0.25, "Parsing approved product specification sheet...")

    # 2. Ingest Content Sheet
    approved = ingest_content_sheet(content_sheet_path)

    # 3. Load Rules based on selected regulatory jurisdiction
    if rules is None:
        if jurisdiction == "INDIA_FSSAI":
            rules = load_yaml_rules(RULES_DIR / "fssai_food_labeling.yaml")
        elif jurisdiction == "DUAL_FDA_FSSAI":
            rules = load_yaml_rules(RULES_DIR / "fda_food_labeling.yaml")
            fssai_r = load_yaml_rules(RULES_DIR / "fssai_food_labeling.yaml")
            rules.extend(fssai_r)
        else:
            rules = load_yaml_rules(RULES_DIR / "fda_food_labeling.yaml")

    if progress_callback:
        progress_callback(0.40, "Executing deterministic regulatory checks...")

    # 4. Run Deterministic Checks
    raw_findings: list[Finding] = []
    deterministic_checks = [
        NutritionMathCheck(),
        ConsistencyCheck(),
        ClaimsCheck(),
        RequiredElementsCheck(),
        DesignLanguageCheck(llm_client=GeminiClient(api_key=gemini_key)),
    ]
    if jurisdiction in ("INDIA_FSSAI", "DUAL_FDA_FSSAI"):
        deterministic_checks.append(FSSAICheck())

    for chk in deterministic_checks:
        findings = chk.run(artwork, approved, rules)
        raw_findings.extend(findings)

    # 5. Run Semantic Checks (if enabled)
    llm_client = GeminiClient(api_key=gemini_key)
    if enable_semantic and llm_client.is_available():
        if progress_callback:
            progress_callback(0.65, "Evaluating semantic rules via Gemini...")
        sem_check = SemanticRuleCheck(llm_client=llm_client)
        sem_findings = sem_check.run(artwork, approved, rules)
        raw_findings.extend(sem_findings)

    # 6. Vision Verification on ambiguous / NEEDS_REVIEW findings
    if enable_vision and llm_client.is_available():
        if progress_callback:
            progress_callback(0.85, "Performing visual verification on artwork regions...")
        verifier = VisionVerifier(llm_client=llm_client)
        for i, f in enumerate(raw_findings):
            if f.verdict == "NEEDS_REVIEW" and f.evidence:
                raw_findings[i] = verifier.verify_finding(artwork, f)

    if progress_callback:
        progress_callback(0.95, "Applying verdict policy and compiling report...")

    # 7. Apply verdict policy and deduplicate
    full_art_text = "\n".join(b.text for b in artwork.text_blocks)
    rule_texts = {r.id: f"{r.title} - {r.quote_or_paraphrase}" for r in rules}

    validated_findings: list[Finding] = []
    for f in raw_findings:
        pol_finding = apply_verdict_policy(f, full_art_text, rule_texts)
        if pol_finding:
            validated_findings.append(pol_finding)

    deduped = deduplicate_findings(validated_findings)

    # 8. Check persistent database for prior dismissals & historical precedents
    active_dismissals = get_active_dismissals(artwork.filename)
    for f in deduped:
        if f.id in active_dismissals:
            f.dismissed = True
            f.dismiss_reason = active_dismissals[f.id]
        else:
            rule_id = f.evidence[0].rule_id if f.evidence else None
            precedents = find_dismissal_precedents(f.id, f.category, rule_id)
            if precedents:
                f.metadata["historical_precedents"] = precedents

    # Sort findings: FAIL first, then NEEDS_REVIEW, then PASS
    verdict_rank = {"FAIL": 0, "NEEDS_REVIEW": 1, "PASS": 2}
    deduped.sort(key=lambda x: verdict_rank.get(x.verdict, 99))

    # Calculate statistics
    fails = sum(1 for f in deduped if f.verdict == "FAIL" and not f.dismissed)
    reviews = sum(1 for f in deduped if f.verdict == "NEEDS_REVIEW" and not f.dismissed)
    passes = sum(1 for f in deduped if f.verdict == "PASS")

    ready = fails == 0
    if fails > 0:
        banner = f"NOT READY TO PRINT: {fails} blocking issue{'s' if fails > 1 else ''} detected"
    elif reviews > 0:
        banner = f"READY PENDING REVIEW: {reviews} item{'s' if reviews > 1 else ''} require human sign-off"
    else:
        banner = "VERIFIED: All automated checks passed"

    report = Report(
        artwork_filename=Path(artwork_path).name,
        content_sheet_filename=Path(content_sheet_path).name,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        total_checks=len(deduped),
        fail_count=fails,
        needs_review_count=reviews,
        pass_count=passes,
        findings=deduped,
        ready_to_print=ready,
        summary_banner=banner,
        unverified_limitations=UNVERIFIED_LIMITATIONS,
    )

    if progress_callback:
        progress_callback(1.0, "Check complete.")

    return report, artwork, approved
