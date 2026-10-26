from time import perf_counter

from guardflow.core.base import TextGuard
from guardflow.core.enums import GuardAction
from guardflow.core.result import GuardResult
from guardflow.engines.secrets.base import (
    SecretDetection,
    SecretsEngine,
)
from guardflow.engines.secrets.detect_secrets_engine import (
    DetectSecretsEngine,
)


class SecretsGuard(TextGuard):
    def __init__(
        self,
        engine: SecretsEngine | None = None,
        action: GuardAction = GuardAction.REDACT,
    ) -> None:
        if action not in {
            GuardAction.REDACT,
            GuardAction.WARN,
            GuardAction.BLOCK,
        }:
            raise ValueError(
                "SecretsGuard action must be redact, warn, or block"
            )

        self._engine = engine or DetectSecretsEngine()
        self._action = action

    def evaluate(self, text: str) -> GuardResult:
        started_at = perf_counter()

        detections = self._engine.detect(text)

        selected = self._resolve_overlaps(detections)

        latency_ms = (
            perf_counter() - started_at
        ) * 1000

        metadata = {
            "secret_count": len(selected),
            "secret_types": sorted(
                {
                    detection.secret_type
                    for detection in selected
                }
            ),
            "detections": [
                {
                    "secret_type": detection.secret_type,
                    "start": detection.start,
                    "end": detection.end,
                }
                for detection in selected
            ],
        }

        if not selected:
            return GuardResult(
                guard_name="secrets",
                passed=True,
                action=GuardAction.ALLOW,
                latency_ms=latency_ms,
                output_text=text,
                metadata=metadata,
            )

        if self._action == GuardAction.BLOCK:
            return GuardResult(
                guard_name="secrets",
                passed=False,
                action=GuardAction.BLOCK,
                reason="Potential secret detected",
                latency_ms=latency_ms,
                output_text=text,
                metadata=metadata,
            )

        if self._action == GuardAction.WARN:
            return GuardResult(
                guard_name="secrets",
                passed=False,
                action=GuardAction.WARN,
                reason="Potential secret detected",
                latency_ms=latency_ms,
                output_text=text,
                metadata=metadata,
            )

        redacted = self._redact(
            text=text,
            detections=selected,
        )

        return GuardResult(
            guard_name="secrets",
            passed=False,
            action=GuardAction.REDACT,
            reason="Potential secret detected and redacted",
            latency_ms=latency_ms,
            output_text=redacted,
            metadata=metadata,
        )

    @staticmethod
    def _redact(
        text: str,
        detections: list[SecretDetection],
    ) -> str:
        output = text

        for detection in sorted(
            detections,
            key=lambda item: item.start,
            reverse=True,
        ):
            output = (
                output[: detection.start]
                + "<SECRET>"
                + output[detection.end :]
            )

        return output

    @staticmethod
    def _resolve_overlaps(
        detections: list[SecretDetection],
    ) -> list[SecretDetection]:
        """
        Multiple secret plugins may detect the same span.

        Prefer the largest span and avoid replacing overlapping text
        more than once.
        """
        ranked = sorted(
            detections,
            key=lambda detection: (
                -(detection.end - detection.start),
                detection.start,
                detection.secret_type,
            ),
        )

        selected: list[SecretDetection] = []

        for candidate in ranked:
            overlaps = any(
                candidate.start < existing.end
                and candidate.end > existing.start
                for existing in selected
            )

            if not overlaps:
                selected.append(candidate)

        return sorted(
            selected,
            key=lambda detection: detection.start,
        )