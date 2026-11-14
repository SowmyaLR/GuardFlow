from guardflow.core.enums import GuardAction
from guardflow.engines.secrets.base import (
    SecretDetection,
    SecretsEngine,
)
from guardflow.guards.secrets import SecretsGuard


class FakeSecretsEngine(SecretsEngine):
    def __init__(
        self,
        detections: list[SecretDetection],
    ) -> None:
        self._detections = detections

    def detect(self, text: str) -> list[SecretDetection]:
        return self._detections


def test_allows_normal_business_question():
    text = (
        "What are the current eligibility requirements "
        "for a salaried employee applying for a home loan?"
    )

    guard = SecretsGuard(
        engine=FakeSecretsEngine([])
    )

    result = guard.evaluate(text)

    assert result.passed is True
    assert result.action == GuardAction.ALLOW


def test_redacts_detected_api_secret():
    secret = "sample-api-key-value-123456"
    text = (
        f'Please debug this configuration: api_key="{secret}"'
    )

    start = text.index(secret)

    guard = SecretsGuard(
        engine=FakeSecretsEngine(
            [
                SecretDetection(
                    secret_type="API_KEY",
                    start=start,
                    end=start + len(secret),
                )
            ]
        )
    )

    result = guard.evaluate(text)

    assert result.action == GuardAction.REDACT
    assert secret not in result.output_text
    assert "<SECRET>" in result.output_text


def test_does_not_expose_raw_secret_in_metadata():
    secret = "fake-private-token-987654"

    text = (
        f'The integration is failing with token="{secret}".'
    )

    start = text.index(secret)

    guard = SecretsGuard(
        engine=FakeSecretsEngine(
            [
                SecretDetection(
                    secret_type="TOKEN",
                    start=start,
                    end=start + len(secret),
                )
            ]
        )
    )

    result = guard.evaluate(text)

    assert secret not in str(result.metadata)


def test_can_block_input_containing_secret():
    text = (
        "Please troubleshoot this production credential."
    )

    guard = SecretsGuard(
        engine=FakeSecretsEngine(
            [
                SecretDetection(
                    secret_type="PRIVATE_KEY",
                    start=7,
                    end=18,
                )
            ]
        ),
        action=GuardAction.BLOCK,
    )

    result = guard.evaluate(text)

    assert result.action == GuardAction.BLOCK
    assert result.passed is False