"""Rule loading utilities for FDA regulations and internal rulebooks."""

from pathlib import Path

import yaml

from src.packcheck.config import RULES_DIR
from src.packcheck.models import Rule


def load_yaml_rules(yaml_path: str | Path | None = None) -> list[Rule]:
    """Load structured rules from a YAML definition file."""
    path = Path(yaml_path) if yaml_path else RULES_DIR / "fda_food_labeling.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Rules YAML file not found at: {path}")

    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    rules_data = data.get("rules", [])
    rules: list[Rule] = []
    for item in rules_data:
        rule = Rule(
            id=item["id"],
            title=item["title"],
            source=item["source"],
            source_url=item.get("source_url"),
            quote_or_paraphrase=item["quote_or_paraphrase"],
            check_type=item.get("check_type", "deterministic"),
            severity=item.get("severity", "major"),
            applies_to=item.get("applies_to", []),
            enabled=item.get("enabled", True),
        )
        rules.append(rule)

    return rules


def load_text_rulebook(file_path: str | Path | None = None) -> str:
    """Read a raw markdown, text, or PDF rulebook document into text."""
    path = Path(file_path) if file_path else RULES_DIR / "company_rulebook.md"
    if not path.exists():
        raise FileNotFoundError(f"Rulebook file not found at: {path}")

    with open(path, encoding="utf-8") as f:
        return f.read()
