from guardflow.core.enums import GuardAction
from guardflow.engines.pii.base import PIIDetection, PIIEngine
from guardflow.guards.pii import PIIGuard


class FakePIIEngine(PIIEngine):
    def detect(self, text, entities=None):
        return [
            PIIDetection(
                entity_type="EMAIL_ADDRESS",
                start=11,
                end=27,
                score=0.99,
                text="john@example.com",
            )
        ]


def test_pii_guard_redacts_detection():
    guard = PIIGuard(
        engine=FakePIIEngine(),
        action=GuardAction.REDACT,
    )

    result = guard.evaluate(
        "My email is john@example.com"
    )

    assert result.passed is False
    assert result.action == GuardAction.REDACT
    assert "<EMAIL_ADDRESS>" in result.output_text


def test_pii_guard_records_latency():
    guard = PIIGuard(
        engine=FakePIIEngine(),
    )

    result = guard.evaluate(
        "My email is john@example.com"
    )

    assert result.latency_ms >= 0