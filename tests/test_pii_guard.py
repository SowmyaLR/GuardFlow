from guardflow.core.enums import GuardAction
from guardflow.engines.pii.base import (
    PIIDetection,
    PIIEngine,
)
from guardflow.guards.pii import PIIGuard


class FakePIIEngine(PIIEngine):
    def detect(self, text, entities=None):
        email = "john.smith@example.com"

        start = text.index(email)

        return [
            PIIDetection(
                entity_type="EMAIL_ADDRESS",
                start=start,
                end=start + len(email),
                score=0.99,
                text=email,
            )
        ]


def test_redacts_email_address():
    text = (
        "Please contact John Smith at "
        "john.smith@example.com regarding the application."
    )

    guard = PIIGuard(
        engine=FakePIIEngine(),
        action=GuardAction.REDACT,
    )

    result = guard.evaluate(text)

    assert result.action == GuardAction.REDACT
    assert "john.smith@example.com" not in result.output_text
    assert "<EMAIL_ADDRESS>" in result.output_text