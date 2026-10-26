from collections import Counter
from time import perf_counter

from guardflow.core.base import TextGuard
from guardflow.core.enums import GuardAction
from guardflow.core.result import GuardResult
from guardflow.engines.sanitizer.base import SanitizerEngine
from guardflow.engines.sanitizer.unicode_engine import (
    UnicodeSanitizerEngine,
)


class InputSanitizer(TextGuard):
    def __init__(
        self,
        engine: SanitizerEngine | None = None,
        block_on_suspicious_controls: bool = False,
    ) -> None:
        self._engine = engine or UnicodeSanitizerEngine()
        self._block_on_suspicious_controls = (
            block_on_suspicious_controls
        )

    def evaluate(self, text: str) -> GuardResult:
        started_at = perf_counter()

        sanitized = self._engine.sanitize(text)

        latency_ms = (
            perf_counter() - started_at
        ) * 1000

        findings = Counter(
            finding.finding_type
            for finding in sanitized.findings
        )

        metadata = {
            "modified": sanitized.modified,
            "findings": dict(findings),
        }

        if (
            sanitized.has_suspicious_findings
            and self._block_on_suspicious_controls
        ):
            return GuardResult(
                guard_name="input_sanitizer",
                passed=False,
                action=GuardAction.BLOCK,
                reason=(
                    "Suspicious Unicode control characters detected"
                ),
                latency_ms=latency_ms,
                output_text=sanitized.text,
                metadata=metadata,
            )

        if sanitized.modified:
            return GuardResult(
                guard_name="input_sanitizer",
                passed=False,
                action=GuardAction.SANITIZE,
                reason="Input was normalized",
                latency_ms=latency_ms,
                output_text=sanitized.text,
                metadata=metadata,
            )

        if sanitized.has_suspicious_findings:
            return GuardResult(
                guard_name="input_sanitizer",
                passed=False,
                action=GuardAction.WARN,
                reason=(
                    "Suspicious Unicode control characters detected"
                ),
                latency_ms=latency_ms,
                output_text=sanitized.text,
                metadata=metadata,
            )

        return GuardResult(
            guard_name="input_sanitizer",
            passed=True,
            action=GuardAction.ALLOW,
            latency_ms=latency_ms,
            output_text=text,
            metadata=metadata,
        )