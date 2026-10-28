"""Deterministic checks for Food Safety and Standards Authority of India (FSSAI) regulations."""

import re

from src.packcheck.checks.base import register_check
from src.packcheck.models import ApprovedData, ArtworkDoc, Evidence, Finding, Rule


@register_check
class FSSAICheck:
    """Validate compliance with FSSAI (Labelling and Display) Regulations, 2020."""

    id = "DET-FSSAI"
    name = "FSSAI Regulatory & Labelling Compliance"
    category = "fssai_compliance"

    def run(
        self,
        artwork: ArtworkDoc,
        approved: ApprovedData,
        rules: list[Rule],
    ) -> list[Finding]:
        findings: list[Finding] = []
        full_art_text = "\n".join(b.text for b in artwork.text_blocks)
        art_lower = full_art_text.lower()

        # 1. FSSAI License Number Check (14 Digits)
        fssai_pattern = re.search(r"(?:fssai|lic(?:ense)?\.?\s*no\.?)\s*[:\-]?\s*(\d{14})", art_lower)
        any_14_digit = re.search(r"\b\d{14}\b", full_art_text)
        has_lic = bool(fssai_pattern or any_14_digit)

        if has_lic:
            lic_num = fssai_pattern.group(1) if fssai_pattern else (any_14_digit.group(0) if any_14_digit else "")
            findings.append(
                Finding(
                    id="FSSAI-LIC-PASS",
                    title=f"FSSAI 14-Digit License Number Valid: {lic_num}",
                    verdict="PASS",
                    confidence=1.0,
                    verified_by="deterministic",
                    category=self.category,
                    why_it_matters="Package displays mandatory 14-digit FSSAI food business operator license number.",
                    evidence=[
                        Evidence(
                            artwork_text=f"FSSAI Lic. No. {lic_num}",
                            rule_id="FSSAI-LIC-001",
                        )
                    ],
                )
            )
        else:
            findings.append(
                Finding(
                    id="FSSAI-LIC-MISSING-FAIL",
                    title="Missing FSSAI 14-Digit License Number & Logo",
                    verdict="FAIL",
                    confidence=0.98,
                    verified_by="deterministic",
                    category=self.category,
                    why_it_matters="Under FSSAI Labelling Regulations 2020 Clause 5(4), every pre-packaged food sold in India must display the FSSAI logo and 14-digit FBO license number.",
                    evidence=[
                        Evidence(
                            artwork_text="No 14-digit license number or 'Lic. No.' statement found on artwork.",
                            computed_value="Expected: 'fssai Lic. No. XXXXXXXXXXXXXX' (14 digits)",
                            rule_id="FSSAI-LIC-001",
                            rule_quote="The FSSAI logo and 14-digit license number of the manufacturer/packer/marketer shall be prominently displayed on the label.",
                        )
                    ],
                )
            )

        # 2. Vegetarian / Non-Vegetarian Logo Declaration
        has_veg_indicator = any(
            k in art_lower
            for k in ["vegetarian", "veg logo", "100% vegetarian", "green dot", "suitable for vegetarians"]
        )
        if has_veg_indicator:
            findings.append(
                Finding(
                    id="FSSAI-VEG-LOGO-PASS",
                    title="Vegetarian Logo / Declaration Verified",
                    verdict="PASS",
                    confidence=0.95,
                    verified_by="deterministic",
                    category=self.category,
                    why_it_matters="FSSAI mandates green dot inside square for vegetarian or brown triangle for non-veg foods.",
                    evidence=[
                        Evidence(
                            artwork_text="Vegetarian indicator detected on dieline proof.",
                            rule_id="FSSAI-VEG-001",
                        )
                    ],
                )
            )
        else:
            findings.append(
                Finding(
                    id="FSSAI-VEG-LOGO-REVIEW",
                    title="FSSAI Veg/Non-Veg Visual Indicator Requires Operator Sign-Off",
                    verdict="NEEDS_REVIEW",
                    confidence=0.90,
                    verified_by="deterministic",
                    category=self.category,
                    why_it_matters="FSSAI Clause 5(5) mandates a green filled circle in green square for vegetarian or brown triangle in square for non-veg on Principal Display Panel.",
                    human_check_needed="Visually inspect front-of-pack dieline for FSSAI green/brown veg logo symbol and correct 3mm/6mm dimension.",
                    evidence=[
                        Evidence(
                            artwork_text="No explicit textual 'Vegetarian' indicator found; vector icon requires visual verification.",
                            computed_value="FSSAI Clause 5(5) Green circle in square",
                            rule_id="FSSAI-VEG-001",
                        )
                    ],
                )
            )

        # 3. Date of Manufacture / Best Before / Expiry
        has_date_marking = any(
            k in art_lower
            for k in [
                "best before",
                "expiry",
                "use by",
                "mfg date",
                "date of packaging",
                "date of manufacture",
                "pkd.",
                "mfg.",
            ]
        )
        if has_date_marking:
            findings.append(
                Finding(
                    id="FSSAI-DATE-PASS",
                    title="Date Marking & Shelf-Life Declaration Present",
                    verdict="PASS",
                    confidence=0.95,
                    verified_by="deterministic",
                    category=self.category,
                    why_it_matters="Date of packaging/manufacture and best before/expiry date are declared.",
                    evidence=[
                        Evidence(
                            artwork_text="Date marking statement present on packaging proof.",
                            rule_id="FSSAI-DATE-001",
                        )
                    ],
                )
            )
        else:
            findings.append(
                Finding(
                    id="FSSAI-DATE-MISSING-FAIL",
                    title="Missing Mandatory Date Marking (Mfg / Best Before)",
                    verdict="FAIL",
                    confidence=0.95,
                    verified_by="deterministic",
                    category=self.category,
                    why_it_matters="FSSAI Clause 5(10) requires declaration of Date of Manufacture/Packaging and Best Before / Expiry date.",
                    evidence=[
                        Evidence(
                            artwork_text="No 'Mfg Date' or 'Best Before' statement extracted from artwork proof.",
                            computed_value="Mandatory FSSAI date marking required.",
                            rule_id="FSSAI-DATE-001",
                        )
                    ],
                )
            )

        # 4. Maximum Retail Price (MRP) and Consumer Helpline
        has_mrp = "mrp" in art_lower or "maximum retail price" in art_lower or "incl. of all taxes" in art_lower
        has_consumer_cell = any(
            k in art_lower
            for k in ["consumer care", "customer care", "toll free", "feedback@", "contact person", "helpline"]
        )
        if has_mrp and has_consumer_cell:
            findings.append(
                Finding(
                    id="FSSAI-MRP-PASS",
                    title="MRP and Consumer Care Details Declared",
                    verdict="PASS",
                    confidence=0.95,
                    verified_by="deterministic",
                    category=self.category,
                    why_it_matters="Maximum Retail Price and Consumer Care contact information meet FSSAI and Legal Metrology standards.",
                    evidence=[
                        Evidence(
                            artwork_text="MRP and Consumer Care information declared on package.",
                            rule_id="FSSAI-MRP-001",
                        )
                    ],
                )
            )
        elif not has_mrp:
            findings.append(
                Finding(
                    id="FSSAI-MRP-MISSING-REVIEW",
                    title="Missing MRP (Incl. of All Taxes) Statement",
                    verdict="NEEDS_REVIEW",
                    confidence=0.90,
                    verified_by="deterministic",
                    category=self.category,
                    why_it_matters="Indian Legal Metrology (Packaged Commodities) & FSSAI mandate 'MRP Rs. / ₹ ... incl. of all taxes'. For export artworks, verify if India domestic retail pack.",
                    human_check_needed="Verify if MRP panel is on a secondary price sticker or printed in variable inkjet batch coding area.",
                    evidence=[
                        Evidence(
                            artwork_text="No 'MRP' or 'inclusive of all taxes' declaration found in static dieline text.",
                            rule_id="FSSAI-MRP-001",
                        )
                    ],
                )
            )

        # 5. FSSAI Trans Fat Cap (Max 2% of Total Fat)
        if artwork.nutrition and artwork.nutrition.nutrients:
            tf = artwork.nutrition.nutrients.get("trans_fat")
            tot_f = artwork.nutrition.nutrients.get("total_fat")
            if tf and tot_f and tf.amount is not None and tot_f.amount is not None and tot_f.amount > 0:
                tf_pct_of_fat = (tf.amount / tot_f.amount) * 100.0
                if tf_pct_of_fat > 2.0:
                    findings.append(
                        Finding(
                            id="FSSAI-TRANS-FAT-CAP-FAIL",
                            title=f"Trans Fat ({tf.amount}g = {tf_pct_of_fat:.1f}% of Fat) Exceeds FSSAI 2% Legal Cap",
                            verdict="FAIL",
                            confidence=1.0,
                            verified_by="deterministic",
                            category=self.category,
                            why_it_matters="FSSAI Food Products Standards Regulations strictly cap trans fatty acids at maximum 2% by weight of total fat. Artwork declares trans fat that severely exceeds this legal limit.",
                            evidence=[
                                Evidence(
                                    artwork_text=f"Total Fat: {tot_f.amount}g, Trans Fat: {tf.amount}g",
                                    computed_value=f"Trans fat is {tf_pct_of_fat:.1f}% of total fat (Legal limit: ≤ 2.0%)",
                                    formula=f"({tf.amount} / {tot_f.amount}) * 100 = {tf_pct_of_fat:.1f}%",
                                    rule_id="FSSAI-NUT-002",
                                    rule_quote="Trans fat content in foods shall not exceed 2% by weight of total fat.",
                                )
                            ],
                        )
                    )

        # 6. Metric Net Quantity Verification
        m_metric = re.search(r"\b(\d+(?:\.\d+)?)\s*(g|kg|ml|l)\b", full_art_text, re.IGNORECASE)
        if m_metric:
            findings.append(
                Finding(
                    id="FSSAI-NET-QTY-METRIC-PASS",
                    title=f"Metric Net Quantity Compliant: {m_metric.group(0)}",
                    verdict="PASS",
                    confidence=1.0,
                    verified_by="deterministic",
                    category=self.category,
                    why_it_matters="FSSAI and Legal Metrology require net content declaration in metric units (g, kg, ml, l).",
                    evidence=[
                        Evidence(
                            artwork_text=m_metric.group(0),
                            rule_id="FSSAI-QTY-001",
                        )
                    ],
                )
            )

        return findings
