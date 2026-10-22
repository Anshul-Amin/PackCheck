"""Centralized and versioned prompt templates for PackCheck."""

# Version: 1.0.0

RULE_CHECK_PROMPT = """You are a senior packaging compliance reviewer.
Analyze the provided artwork text against the specific regulatory or brand rule.

RULE DETAILS:
ID: {rule_id}
Title: {rule_title}
Source: {rule_source}
Requirement: {rule_requirement}

EXTRACTED ARTWORK TEXT EVIDENCE:
{artwork_evidence}

APPROVED PRODUCT DATA CONTEXT:
{approved_context}

INSTRUCTIONS:
1. Determine if the artwork text complies with the rule.
2. Return verdict: 'PASS' if compliant, 'FAIL' if definite violation, or 'NEEDS_REVIEW' if ambiguous, subjective, or requires human inspection.
3. If FAIL, you MUST provide an exact quote from the artwork and an exact quote from the rule. If you cannot quote both verbatim, return 'NEEDS_REVIEW'.
4. Explain clearly why it matters in one concise sentence.
5. If NEEDS_REVIEW, state specifically what a human reviewer should look at.

Output strictly valid JSON with this schema:
{{
  "verdict": "FAIL" | "NEEDS_REVIEW" | "PASS",
  "confidence": 0.0 to 1.0,
  "quoted_artwork_text": "exact verbatim substring from artwork or empty",
  "quoted_rule_text": "exact verbatim substring from rule or empty",
  "reasoning": "brief explanation",
  "needs_human_because": "human action needed or empty"
}}
"""

RULE_EXTRACT_PROMPT = """You are an expert regulatory analyst for packaging artwork.
Extract actionable compliance rules from the following rulebook document.

DOCUMENT TEXT:
{document_text}

INSTRUCTIONS:
Extract each discrete packaging rule into a structured object.
Every single rule MUST include an exact verbatim quote from the document text. Do not invent or summarize without an exact quote.

Output strictly valid JSON matching this schema:
{{
  "rules": [
    {{
      "id": "COMP-001",
      "title": "Short descriptive rule title",
      "source": "Document section or paragraph",
      "quote": "Exact verbatim quote from the document text",
      "severity": "critical" | "major" | "advisory",
      "applies_to": ["claims" | "nutrition" | "ingredients" | "allergens" | "barcode" | "front_panel" | "general"]
    }}
  ]
}}
"""

VISION_VERIFY_PROMPT = """You are an OCR and packaging inspection expert.
Inspect the attached image crop of a packaging artwork panel.
Transcribe all printed text visible in the crop exactly as printed, preserving capitalization and numbers.
If there are numbers, verify them with 100% precision.

Output strictly valid JSON:
{{
  "transcribed_text": "exact text visible in image",
  "confidence": 0.0 to 1.0,
  "notes": "any legibility or orientation notes"
}}
"""

QA_PROMPT = """You are PackCheck AI Assistant, an expert in packaging QA and FDA food labeling.
Answer the user's question about this specific compliance finding.

FINDING DETAILS:
Finding ID: {finding_id}
Title: {finding_title}
Verdict: {verdict}
Why It Matters: {why_it_matters}

EVIDENCE CITED:
{evidence_details}

RELEVANT RULE CONTEXT:
{rule_context}

USER QUESTION:
{user_question}

STRICT GROUNDING RULES:
1. Answer using ONLY the evidence and rule context provided above.
2. Cite specific evidence items (e.g. [Evidence 1], [Rule 21 CFR 101.9]).
3. If the evidence provided is insufficient to answer the question, you MUST say:
   "There is not enough evidence in this finding to answer that question."
   Do NOT speculate or extrapolate beyond the recorded evidence.
"""
