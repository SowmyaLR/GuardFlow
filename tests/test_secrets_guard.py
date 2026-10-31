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


def test_allows_text_without_secrets():
    guard = SecretsGuard(
        engine=FakeSecretsEngine([])
    )

    result = guard.evaluate(
        "Explain fixed and floating interest rates."
    )

    assert result.passed is True
    assert result.action == GuardAction.ALLOW
    assert result.output_text.startswith("Explain")


def test_redacts_detected_secret():
    text = "token=super-secret-value"

    start = text.index("super-secret-value")
    end = start + len("super-secret-value")

    guard = SecretsGuard(
        engine=FakeSecretsEngine(
            [
                SecretDetection(
                    secret_type="API Token",
                    start=start,
                    end=end,
                )
            ]
        )
    )

    result = guard.evaluate(text)

    assert result.action == GuardAction.REDACT
    assert result.output_text == "token=<SECRET>"


def test_metadata_does_not_contain_secret_value():
    secret = "very-private-token"

    text = f"token={secret}"

    start = text.index(secret)

    guard = SecretsGuard(
        engine=FakeSecretsEngine(
            [
                SecretDetection(
                    secret_type="API Token",
                    start=start,
                    end=start + len(secret),
                )
            ]
        )
    )

    result = guard.evaluate(text)

    assert secret not in str(result.metadata)


def test_can_block_secret():
    guard = SecretsGuard(
        engine=FakeSecretsEngine(
            [
                SecretDetection(
                    secret_type="Credential",
                    start=0,
                    end=10,
                )
            ]
        ),
        action=GuardAction.BLOCK,
    )

    result = guard.evaluate("abcdefghij")

    assert result.action == GuardAction.BLOCK
    assert result.passed is False


def test_can_warn_about_secret():
    guard = SecretsGuard(
        engine=FakeSecretsEngine(
            [
                SecretDetection(
                    secret_type="Credential",
                    start=0,
                    end=10,
                )
            ]
        ),
        action=GuardAction.WARN,
    )

    result = guard.evaluate("abcdefghij")

    assert result.action == GuardAction.WARN


def test_resolves_overlapping_detections():
    text = "token=abcdefghijklmnop"

    guard = SecretsGuard(
        engine=FakeSecretsEngine(
            [
                SecretDetection(
                    secret_type="Generic Secret",
                    start=6,
                    end=22,
                ),
                SecretDetection(
                    secret_type="High Entropy String",
                    start=8,
                    end=22,
                ),
            ]
        )
    )

    result = guard.evaluate(text)

    assert result.metadata["secret_count"] == 1
    assert result.output_text == "token=<SECRET>"


def test_records_latency():
    guard = SecretsGuard(
        engine=FakeSecretsEngine([])
    )

    result = guard.evaluate("hello")

    assert result.latency_ms >= 0