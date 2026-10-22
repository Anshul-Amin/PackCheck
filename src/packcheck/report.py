"""Export compliance reports to JSON, CSV, and self-contained HTML."""

import csv
import io

from src.packcheck.models import ArtworkDoc, Report


def export_json(report: Report) -> str:
    """Export report as formatted JSON string."""
    return report.model_dump_json(indent=2)


def export_csv(report: Report) -> str:
    """Export findings table as CSV string."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "Finding ID",
            "Title",
            "Verdict",
            "Category",
            "Confidence",
            "Verified By",
            "Why It Matters",
            "Human Action Needed",
            "Dismissed",
            "Dismiss Reason",
        ]
    )

    for f in report.findings:
        writer.writerow(
            [
                f.id,
                f.title,
                f.verdict,
                f.category,
                f"{f.confidence:.2f}",
                f.verified_by,
                f.why_it_matters,
                f.human_check_needed or "",
                "Yes" if f.dismissed else "No",
                f.dismiss_reason or "",
            ]
        )

    return output.getvalue()


def export_html(report: Report, artwork: ArtworkDoc | None = None) -> str:
    """Export a self-contained HTML compliance report with inline styles and preview."""
    preview_img_tag = ""
    if artwork and artwork.rendered_pages_png:
        preview_img_tag = f"""
        <div class="artwork-preview">
            <h3>Artwork Proof Preview</h3>
            <img src="data:image/png;base64,{artwork.rendered_pages_png[0]}" alt="Artwork Proof" />
        </div>
        """

    findings_rows = ""
    for f in report.findings:
        badge_class = f.verdict.lower()
        evidence_html = ""
        for ev in f.evidence:
            evidence_html += f"<li><code>{ev.artwork_text or ev.approved_value or ''}</code> {f'<em>(Rule {ev.rule_id})</em>' if ev.rule_id else ''}</li>"

        findings_rows += f"""
        <tr class="{badge_class}">
            <td><span class="badge {badge_class}">{f.verdict}</span></td>
            <td><strong>{f.title}</strong><br/><small>{f.category} | Verified by {f.verified_by} ({int(f.confidence * 100)}%)</small></td>
            <td>{f.why_it_matters}</td>
            <td><ul>{evidence_html}</ul></td>
            <td>{f.human_check_needed or "-"}</td>
        </tr>
        """

    limitations_list = "".join(f"<li>{lim}</li>" for lim in report.unverified_limitations)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>PackCheck Compliance Report - {report.artwork_filename}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 30px; background: #f8f9fa; color: #212529; }}
        .header {{ background: #ffffff; padding: 25px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 25px; }}
        .banner {{ font-size: 20px; font-weight: bold; padding: 15px; border-radius: 6px; margin-top: 15px; }}
        .banner.fail {{ background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}
        .banner.review {{ background: #fff3cd; color: #856404; border: 1px solid #ffeeba; }}
        .banner.pass {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
        .stats {{ display: flex; gap: 20px; margin-top: 15px; }}
        .stat-box {{ background: #f1f3f5; padding: 12px 20px; border-radius: 6px; text-align: center; }}
        .stat-num {{ font-size: 24px; font-weight: bold; }}
        table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-top: 20px; }}
        th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #dee2e6; }}
        th {{ background: #e9ecef; font-weight: 600; }}
        .badge {{ display: inline-block; padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 12px; }}
        .badge.fail {{ background: #dc3545; color: white; }}
        .badge.needs_review {{ background: #ffc107; color: #212529; }}
        .badge.pass {{ background: #28a745; color: white; }}
        .artwork-preview img {{ max-width: 100%; height: auto; border: 1px solid #ced4da; border-radius: 4px; }}
        .limitations {{ background: #e9ecef; padding: 15px 25px; border-radius: 6px; margin-top: 25px; font-size: 13px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>PackCheck Packaging Artwork Compliance Report</h1>
        <p><strong>Artwork File:</strong> {report.artwork_filename} | <strong>Specification:</strong> {report.content_sheet_filename or "N/A"}</p>
        <p><strong>Timestamp:</strong> {report.timestamp}</p>
        <div class="banner {"fail" if report.fail_count > 0 else "review" if report.needs_review_count > 0 else "pass"}">
            {report.summary_banner}
        </div>
        <div class="stats">
            <div class="stat-box"><div class="stat-num" style="color:#dc3545">{report.fail_count}</div><div>FAIL</div></div>
            <div class="stat-box"><div class="stat-num" style="color:#ffc107">{report.needs_review_count}</div><div>NEEDS REVIEW</div></div>
            <div class="stat-box"><div class="stat-num" style="color:#28a745">{report.pass_count}</div><div>PASS</div></div>
            <div class="stat-box"><div class="stat-num">{report.total_checks}</div><div>TOTAL CHECKS</div></div>
        </div>
    </div>

    {preview_img_tag}

    <h2>Compliance Findings</h2>
    <table>
        <thead>
            <tr>
                <th>Verdict</th>
                <th>Finding</th>
                <th>Why It Matters</th>
                <th>Evidence</th>
                <th>Human Action Needed</th>
            </tr>
        </thead>
        <tbody>
            {findings_rows}
        </tbody>
    </table>

    <div class="limitations">
        <h3>Regulatory Scope & Technical Limitations</h3>
        <ul>{limitations_list}</ul>
    </div>
</body>
</html>
"""
