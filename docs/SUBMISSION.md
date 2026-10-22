# Esko AIForge Hackathon Submission: PackCheck

## Problem Statement
**Problem Statement 2: "Is this packaging artwork ready to launch?"**

Packaging quality assurance and regulatory affairs teams must make high-consequence "safe to print?" decisions for retail carton artwork. Today, reviewers either rely on tedious manual checklists or turn to generic LLMs that hallucinate calculations, fail to read dieline coordinates, and generate high false alarm rates that frustrate regulatory teams.

## Approach & Innovation
PackCheck introduces a **hybrid deterministic-plus-AI compliance verification platform**:
1. **Zero Guesswork Math**: Calculations such as FDA %Daily Values (against official 2,000 kcal reference intakes), Atwater calorie factors (4/9/4), servings-per-container multipliers, and GS1 UPC-A Modulo-10 barcode check digits are computed using 100% deterministic Python logic.
2. **Constrained Multimodal AI (Google Gemini 2.5 Flash)**: The LLM is restricted to semantic interpretation: resolving conflicting claims (e.g. "No Added Sugar" vs nutritive sweeteners, "Certified Vegan" vs honey), extracting structured rules from free-text brand policy rulebooks, and visual crop inspection of dieline text.
3. **Anti-False-Alarm Policy (`verdict_policy.py`)**: To earn user trust, PackCheck enforces three strict verdict tiers (`FAIL`, `NEEDS_REVIEW`, `PASS`). An AI-generated finding can **never** issue a blocking `FAIL` unless it cites verbatim, validated substring quotes from both the artwork proof and the regulation. Any unverified finding is downgraded to `NEEDS_REVIEW`.
4. **Transparent Audit Trail**: Every finding features exact pixel bounding-box visual overlays on the rendered dieline proof, formula citations, grounded Q&A, and full export to JSON, CSV, and self-contained HTML.
5. **Completely Free Architecture**: Zero credit card, zero cloud billing. Runs on open-source libraries and the Google Gemini free tier, with local disk caching to prevent rate-limit disruptions during review.

## Key Results on Official Sample Files
On the official Dancing Fish Granola packaging dieline (`DancingFish_Granola_Berry_US_Carton.pdf`) and specification sheet (`DancingFish_Granola_BerryCrunch_US_Content_Sheet.xlsx`), PackCheck achieves:
- **100% Recall on Expected Issues**: Detects all 7 core regulatory failures, including the servings math contradiction (8 servings × 85g = 680g vs 480g net weight), %DV errors (e.g. Total Fat printed 2.2% vs computed 19.2%), "Certified Vegan" vs honey conflict, "No Added Sugar" vs sweeteners, and formulation allergens masked as advisory "May Contain".
- **Zero False Alarms on Clean Labels**: Tested against compliant synthetic fixtures with 0 false positive `FAIL` findings.
- **Fast Execution**: Entire check completes in under 3 seconds with cached/deterministic checks.
