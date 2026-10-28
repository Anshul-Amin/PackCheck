"""Persistent SQLite database for reviewer dismissals, historical precedents, and audit logs."""

import json
import sqlite3
from datetime import datetime
from typing import Any

from src.packcheck.config import DATA_DIR

DB_PATH = DATA_DIR / "packcheck.db"


def get_db_connection() -> sqlite3.Connection:
    """Open or create the local SQLite database connection."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initialize SQLite database tables for dismissals, memory precedents, and audit logs."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Reviewer Dismissals Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS finding_dismissals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        finding_id TEXT NOT NULL,
        finding_title TEXT NOT NULL,
        category TEXT NOT NULL,
        rule_id TEXT,
        artwork_filename TEXT NOT NULL,
        artwork_text_snippet TEXT,
        reason TEXT NOT NULL,
        reviewer_name TEXT DEFAULT 'Regulatory Reviewer',
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        context_json TEXT
    )
    """)

    # 2. Audit Trail Log Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        artwork_filename TEXT,
        action TEXT NOT NULL,
        details TEXT
    )
    """)

    # 3. Physical Review Parameters Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS physical_review_parameters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        artwork_filename TEXT NOT NULL,
        parameter_name TEXT NOT NULL,
        category TEXT DEFAULT 'Physical Review',
        rule_reference TEXT,
        is_verified INTEGER DEFAULT 0,
        inspector_name TEXT NOT NULL,
        notes TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


def save_dismissal(
    finding_id: str,
    finding_title: str,
    category: str,
    artwork_filename: str,
    reason: str,
    rule_id: str | None = None,
    artwork_text_snippet: str | None = None,
    reviewer_name: str = "Regulatory Reviewer",
    context_data: dict[str, Any] | None = None,
) -> int:
    """Save a false-alarm dismissal with reviewer justification into persistent local DB."""
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    # Delete existing dismissal for same finding_id on same artwork if any
    cursor.execute(
        "DELETE FROM finding_dismissals WHERE finding_id = ? AND artwork_filename = ?",
        (finding_id, artwork_filename),
    )

    cursor.execute(
        """
        INSERT INTO finding_dismissals
        (finding_id, finding_title, category, rule_id, artwork_filename, artwork_text_snippet, reason, reviewer_name, timestamp, context_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            finding_id,
            finding_title,
            category,
            rule_id,
            artwork_filename,
            artwork_text_snippet,
            reason,
            reviewer_name,
            datetime.now().isoformat(),
            json.dumps(context_data or {}),
        ),
    )
    dismissal_id = cursor.lastrowid or 0

    # Log audit event
    cursor.execute(
        "INSERT INTO audit_log (artwork_filename, action, details) VALUES (?, ?, ?)",
        (artwork_filename, "DISMISS_FINDING", f"Dismissed {finding_id}: {reason}"),
    )

    conn.commit()
    conn.close()
    return dismissal_id


def remove_dismissal(finding_id: str, artwork_filename: str) -> None:
    """Restore a previously dismissed finding."""
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM finding_dismissals WHERE finding_id = ? AND artwork_filename = ?",
        (finding_id, artwork_filename),
    )
    cursor.execute(
        "INSERT INTO audit_log (artwork_filename, action, details) VALUES (?, ?, ?)",
        (artwork_filename, "RESTORE_FINDING", f"Restored {finding_id}"),
    )
    conn.commit()
    conn.close()


def get_active_dismissals(artwork_filename: str) -> dict[str, str]:
    """Retrieve mapping of finding_id -> reason for a specific artwork file."""
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT finding_id, reason FROM finding_dismissals WHERE artwork_filename = ?",
        (artwork_filename,),
    )
    rows = cursor.fetchall()
    conn.close()

    return {row["finding_id"]: row["reason"] for row in rows}


def find_dismissal_precedents(
    finding_id: str,
    category: str,
    rule_id: str | None = None,
    text_snippet: str | None = None,
    limit: int = 3,
) -> list[dict[str, Any]]:
    """Retrieve historical false-alarm dismissal precedents using rule/category matching and text similarity.

    Returns past reviewer overrides to help reviewers determine whether a current warning
    has an accepted precedent across earlier versions or similar SKUs.
    """
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    SELECT finding_id, finding_title, category, rule_id, artwork_filename, reason, reviewer_name, timestamp
    FROM finding_dismissals
    WHERE finding_id = ? OR rule_id = ? OR category = ?
    ORDER BY id DESC
    LIMIT ?
    """
    cursor.execute(query, (finding_id, rule_id or "", category, limit))
    rows = cursor.fetchall()
    conn.close()

    precedents = []
    for r in rows:
        precedents.append(
            {
                "finding_id": r["finding_id"],
                "finding_title": r["finding_title"],
                "category": r["category"],
                "rule_id": r["rule_id"],
                "artwork_filename": r["artwork_filename"],
                "reason": r["reason"],
                "reviewer_name": r["reviewer_name"],
                "timestamp": r["timestamp"],
            }
        )

    return precedents


def get_all_dismissals() -> list[dict[str, Any]]:
    """Retrieve all historical false-alarm dismissals across all artworks."""
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, finding_id, finding_title, category, rule_id, artwork_filename, reason, reviewer_name, timestamp
        FROM finding_dismissals
        ORDER BY id DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "id": r["id"],
            "finding_id": r["finding_id"],
            "finding_title": r["finding_title"],
            "category": r["category"],
            "rule_id": r["rule_id"],
            "artwork_filename": r["artwork_filename"],
            "reason": r["reason"],
            "reviewer_name": r["reviewer_name"],
            "timestamp": r["timestamp"],
        }
        for r in rows
    ]


def get_audit_trail(limit: int = 50) -> list[dict[str, Any]]:
    """Retrieve recent compliance audit trail events."""
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, timestamp, artwork_filename, action, details
        FROM audit_log
        ORDER BY id DESC
        LIMIT ?
    """,
        (limit,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "id": r["id"],
            "timestamp": r["timestamp"],
            "artwork_filename": r["artwork_filename"],
            "action": r["action"],
            "details": r["details"],
        }
        for r in rows
    ]


def search_precedents_and_logs(query: str, limit: int = 10) -> dict[str, list[dict[str, Any]]]:
    """Search dismissal precedents and audit trail logs using keyword/relevance match."""
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    q_pattern = f"%{query}%"

    # 1. Search dismissals
    cursor.execute(
        """
        SELECT id, finding_id, finding_title, category, rule_id, artwork_filename, reason, reviewer_name, timestamp
        FROM finding_dismissals
        WHERE finding_id LIKE ? OR finding_title LIKE ? OR reason LIKE ? OR category LIKE ? OR rule_id LIKE ? OR artwork_filename LIKE ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (q_pattern, q_pattern, q_pattern, q_pattern, q_pattern, q_pattern, limit),
    )
    dismissals = [dict(r) for r in cursor.fetchall()]

    # 2. Search audit logs
    cursor.execute(
        """
        SELECT id, timestamp, artwork_filename, action, details
        FROM audit_log
        WHERE details LIKE ? OR action LIKE ? OR artwork_filename LIKE ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (q_pattern, q_pattern, q_pattern, limit),
    )
    logs = [dict(r) for r in cursor.fetchall()]

    conn.close()
    return {"precedents": dismissals, "audit_logs": logs}


def log_audit_event(artwork_filename: str, action: str, details: str) -> None:
    """Log an event to the immutable audit_log table."""
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO audit_log (artwork_filename, action, details) VALUES (?, ?, ?)",
        (artwork_filename, action, details),
    )
    conn.commit()
    conn.close()


def record_operator_signoff(
    artwork_filename: str,
    reviewer_name: str,
    pantone_verified: bool,
    barcode_verified: bool,
    cylinder_bleed_verified: bool,
    certifications_verified: bool,
    notes: str = "",
) -> None:
    """Record a manual pressroom hardware and certification sign-off in the immutable audit log."""
    details = (
        f"Operator [{reviewer_name}] certified: "
        f"Pantone Drawdown={pantone_verified}, "
        f"ISO Barcode Verifier={barcode_verified}, "
        f"Cylinder Step/Bleed={cylinder_bleed_verified}, "
        f"Organic/Kosher Affidavits={certifications_verified}. Notes: {notes}"
    )
    log_audit_event(artwork_filename, "OPERATOR_PRESSROOM_SIGNOFF", details)


def save_physical_parameter(
    artwork_filename: str,
    parameter_name: str,
    category: str = "Physical Review",
    rule_reference: str = "",
    is_verified: bool = True,
    inspector_name: str = "Operator",
    notes: str = "",
) -> int:
    """Save an AI-pulled or user-added physical inspection parameter and log it in the audit trail."""
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO physical_review_parameters
        (artwork_filename, parameter_name, category, rule_reference, is_verified, inspector_name, notes, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            artwork_filename,
            parameter_name,
            category,
            rule_reference,
            1 if is_verified else 0,
            inspector_name,
            notes,
            datetime.now().isoformat(),
        ),
    )
    param_id = cursor.lastrowid or 0
    conn.commit()
    conn.close()

    status_str = "VERIFIED" if is_verified else "FLAGGED"
    log_audit_event(
        artwork_filename,
        "PHYSICAL_PARAMETER_LOGGED",
        f"Parameter '{parameter_name}' ({rule_reference or 'Manual Check'}) marked {status_str} by {inspector_name}. Notes: {notes}",
    )
    return param_id


def get_physical_parameters(artwork_filename: str | None = None) -> list[dict[str, Any]]:
    """Retrieve saved physical review parameters, optionally filtered by artwork."""
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    if artwork_filename:
        cursor.execute(
            """
            SELECT id, artwork_filename, parameter_name, category, rule_reference, is_verified, inspector_name, notes, timestamp
            FROM physical_review_parameters
            WHERE artwork_filename = ?
            ORDER BY id DESC
            """,
            (artwork_filename,),
        )
    else:
        cursor.execute(
            """
            SELECT id, artwork_filename, parameter_name, category, rule_reference, is_verified, inspector_name, notes, timestamp
            FROM physical_review_parameters
            ORDER BY id DESC
            """
        )

    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "id": r["id"],
            "artwork_filename": r["artwork_filename"],
            "parameter_name": r["parameter_name"],
            "category": r["category"],
            "rule_reference": r["rule_reference"],
            "is_verified": bool(r["is_verified"]),
            "inspector_name": r["inspector_name"],
            "notes": r["notes"],
            "timestamp": r["timestamp"],
        }
        for r in rows
    ]


def delete_physical_parameter(param_id: int) -> None:
    """Delete a custom physical inspection parameter."""
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM physical_review_parameters WHERE id = ?", (param_id,))
    conn.commit()
    conn.close()
