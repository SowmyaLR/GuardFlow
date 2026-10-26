from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SanitizationFinding:
    finding_type: str
    position: int | None
    modified: bool


@dataclass(frozen=True, slots=True)
class SanitizationResult:
    text: str
    findings: tuple[SanitizationFinding, ...]

    @property
    def modified(self) -> bool:
        return any(
            finding.modified
            for finding in self.findings
        )

    @property
    def has_suspicious_findings(self) -> bool:
        return any(
            not finding.modified
            for finding in self.findings
        )


class SanitizerEngine(ABC):
    @abstractmethod
    def sanitize(self, text: str) -> SanitizationResult:
        raise NotImplementedError