from guardflow import GuardFlow
from guardflow.core.enums import GuardAction
from guardflow.core.result import GuardResult
from guardflow.core.base import TextGuard


class RedactGuard(TextGuard):
    def evaluate(self, text):
        return GuardResult(
            guard_name="redact",
            passed=False,
            action=GuardAction.REDACT,
            output_text="safe text",
        )


class BlockingGuard(TextGuard):
    def evaluate(self, text):
        return GuardResult(
            guard_name="block",
            passed=False,
            action=GuardAction.BLOCK,
            output_text=text,
        )


def test_flow_passes_transformed_text_to_next_guard():
    flow = GuardFlow(
        guards=[
            RedactGuard(),
        ]
    )

    result = flow.inspect("unsafe text")

    assert result.text == "safe text"


def test_flow_stops_on_block():
    flow = GuardFlow(
        guards=[
            BlockingGuard(),
            RedactGuard(),
        ]
    )

    result = flow.inspect("input")

    assert result.allowed is False
    assert len(result.results) == 1