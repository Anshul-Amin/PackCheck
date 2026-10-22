"""Command line interface and evaluation benchmark runner for PackCheck."""

import argparse
import sys
from pathlib import Path

# Ensure repository root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.packcheck.config import SAMPLES_DIR
from src.packcheck.engine import run_compliance_check
from src.packcheck.report import export_csv, export_json
from src.packcheck.rules.loader import load_yaml_rules

# Expected compliance issues in the Dancing Fish Granola sample
EXPECTED_ISSUES = [
    ("MATH-SERVING-NET-MISMATCH", "Servings x Serving Size vs Net Weight (unconfirmed unit)"),
    ("MATH-DV-MISMATCH-TOTAL_FAT", "%DV Discrepancy for Total Fat (2.2% vs 19.2%)"),
    (
        "CLAIM-NO-ADDED-SUGAR-CONTRADICTION",
        "'No Added Sugar' Contradiction with Nutritive Sweeteners",
    ),
    ("CLAIM-VEGAN-HONEY-CONFLICT", "'Certified Vegan' Conflict with Honey (FAIL)"),
    ("CONSIST-HONEY-PCT-MISMATCH", "Honey Formulation % Mismatch (1% artwork vs 9% sheet)"),
    (
        "REQ-ALLERGEN-ADVISORY-MISUSE",
        "Formulation Allergen declared only as 'May Contain' advisory",
    ),
    ("REQ-NET-QUANTITY-DUAL-UNIT-FAIL", "Missing US Customary Ounce Net Quantity"),
]


def run_evaluation(report) -> None:
    """Print an evaluation benchmark table comparing expected vs detected issues."""
    print("\n" + "=" * 80)
    print("PACKCHECK ACCURACY EVALUATION BENCHMARK")
    print("=" * 80)

    found_ids = {f.id for f in report.findings}
    detected_count = 0

    print(f"{'Issue ID':<35} | {'Description':<35} | {'Status'}")
    print("-" * 80)
    for issue_id, desc in EXPECTED_ISSUES:
        status = "DETECTED" if issue_id in found_ids else "MISSED"
        if status == "DETECTED":
            detected_count += 1
        print(f"{issue_id:<35} | {desc[:35]:<35} | {status}")

    print("-" * 80)
    recall = (detected_count / len(EXPECTED_ISSUES)) * 100
    print(f"Recall Rate: {detected_count}/{len(EXPECTED_ISSUES)} ({recall:.1f}%)")
    print(f"Total FAIL Findings: {report.fail_count}")
    print(f"Total NEEDS_REVIEW: {report.needs_review_count}")
    print(f"Total PASS Checks: {report.pass_count}")
    print("=" * 80 + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="PackCheck Packaging Artwork Compliance Checker CLI"
    )
    parser.add_argument(
        "--art",
        type=str,
        default=str(SAMPLES_DIR / "DancingFish_Granola_Berry_US_Carton.pdf"),
        help="Path to artwork PDF",
    )
    parser.add_argument(
        "--sheet",
        type=str,
        default=str(SAMPLES_DIR / "DancingFish_Granola_BerryCrunch_US_Content_Sheet.xlsx"),
        help="Path to specification Excel sheet",
    )
    parser.add_argument("--rules", type=str, default=None, help="Path to custom rules YAML")
    parser.add_argument("--eval", action="store_true", help="Print benchmark evaluation table")
    parser.add_argument("--json", type=str, default=None, help="Save report to JSON file path")
    parser.add_argument("--csv", type=str, default=None, help="Save findings to CSV file path")

    args = parser.parse_args()

    art_path = Path(args.art)
    sheet_path = Path(args.sheet)

    if not art_path.exists():
        print(f"Error: Artwork file not found at {art_path}", file=sys.stderr)
        sys.exit(1)
    if not sheet_path.exists():
        print(f"Error: Specification sheet not found at {sheet_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Running PackCheck on: {art_path.name} vs {sheet_path.name}...")
    rules = load_yaml_rules(args.rules) if args.rules else None

    report, artwork, approved = run_compliance_check(
        artwork_path=art_path,
        content_sheet_path=sheet_path,
        rules=rules,
        enable_semantic=True,
        enable_vision=True,
    )

    print(f"\n{report.summary_banner}")
    print(
        f"Total Checks: {report.total_checks} | FAIL: {report.fail_count} | NEEDS_REVIEW: {report.needs_review_count} | PASS: {report.pass_count}"
    )

    if args.eval:
        run_evaluation(report)

    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            f.write(export_json(report))
        print(f"Saved JSON report to {args.json}")

    if args.csv:
        with open(args.csv, "w", encoding="utf-8") as f:
            f.write(export_csv(report))
        print(f"Saved CSV findings to {args.csv}")


if __name__ == "__main__":
    main()
