from time import perf_counter

from guardflow.core.base import TextGuard
from guardflow.core.enums import GuardAction
from guardflow.core.result import GuardResult
from guardflow.engines.pii.base import PIIEngine
from guardflow.engines.pii.presidio_engine import PresidioPIIEngine


class PIIGuard(TextGuard):
    def __init__(
        self,
        engine: PIIEngine | None = None,
        action: GuardAction = GuardAction.REDACT,
        entities: list[str] | None = None,
        threshold: float = 0.5,
    ) -> None:
        self._engine = engine or PresidioPIIEngine()
        self._action = action
        self._entities = entities
        self._threshold = threshold

    def evaluate(self, text: str) -> GuardResult:
        started_at = perf_counter()

        detections = self._engine.detect(
            text=text,
            entities=self._entities,
        )

        filtered = [
            detection
            for detection in detections
            if detection.score >= self._threshold
        ]

        latency_ms = (perf_counter() - started_at) * 1000

        if not filtered:
            return GuardResult(
                guard_name="pii",
                passed=True,
                action=GuardAction.ALLOW,
                latency_ms=latency_ms,
                output_text=text,
                metadata={
                    "detections": [],
                },
            )

        if self._action == GuardAction.BLOCK:
            return GuardResult(
                guard_name="pii",
                passed=False,
                action=GuardAction.BLOCK,
                reason="PII detected",
                latency_ms=latency_ms,
                output_text=text,
                metadata={
                    "detections": [
                        self._serialize_detection(item)
                        for item in filtered
                    ]
                },
            )

        if self._action == GuardAction.WARN:
            return GuardResult(
                guard_name="pii",
                passed=False,
                action=GuardAction.WARN,
                reason="PII detected",
                latency_ms=latency_ms,
                output_text=text,
                metadata={
                    "detections": [
                        self._serialize_detection(item)
                        for item in filtered
                    ]
                },
            )

        redacted = self._redact(
            text=text,
            detections=filtered,
        )

        return GuardResult(
            guard_name="pii",
            passed=False,
            action=GuardAction.REDACT,
            reason="PII detected and redacted",
            latency_ms=latency_ms,
            output_text=redacted,
            metadata={
                "detections": [
                    self._serialize_detection(item)
                    for item in filtered
                ]
            },
        )

    @staticmethod
    def _serialize_detection(detection) -> dict:
        return {
            "entity_type": detection.entity_type,
            "start": detection.start,
            "end": detection.end,
            "score": detection.score,
        }

    @staticmethod
    def _redact(text: str, detections) -> str:
        output = text

        for detection in sorted(
            detections,
            key=lambda item: item.start,
            reverse=True,
        ):
            replacement = f"<{detection.entity_type}>"

            output = (
                output[: detection.start]
                + replacement
                + output[detection.end :]
            )

        return output