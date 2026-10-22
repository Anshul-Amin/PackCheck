"""Base check protocol and registry for compliance suites."""

from typing import Protocol

from src.packcheck.models import ApprovedData, ArtworkDoc, Finding, Rule


class Check(Protocol):
    """Protocol for all compliance checks."""

    id: str
    name: str
    category: str

    def run(
        self,
        artwork: ArtworkDoc,
        approved: ApprovedData,
        rules: list[Rule],
    ) -> list[Finding]:
        """Execute check and return list of compliance findings."""
        ...


# Global registry of active check instances
CHECK_REGISTRY: list[Check] = []


def register_check(check_cls: type[Check]) -> type[Check]:
    """Decorator to register a check in the global compliance suite."""
    instance = check_cls()
    CHECK_REGISTRY.append(instance)
    return check_cls
