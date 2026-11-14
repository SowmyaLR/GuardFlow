import pytest

from guardflow.core.enums import GuardAction
from guardflow.engines.tokens.base import TokenCount, TokenCounter
from guardflow.guards.token_limit import TokenLimitGuard


class FixedTokenCounter(TokenCounter):
    def __init__(self, count: int) -> None:
        self._count = count

    def count(self, text: str) -> TokenCount:
        return TokenCount(
            count=self._count,
            counter_name="test_counter",
            exact=True,
        )


def test_allows_normal_question_below_limit():
    text = (
        "What documents are required to apply for "
        "a home loan in India?"
    )

    guard = TokenLimitGuard(
        max_tokens=100,
        counter=FixedTokenCounter(20),
    )

    result = guard.evaluate(text)

    assert result.passed is True
    assert result.action == GuardAction.ALLOW
    assert result.output_text == text


def test_allows_input_exactly_at_limit():
    text = (
        "Summarize the following customer complaint "
        "and identify the main issue."
    )

    guard = TokenLimitGuard(
        max_tokens=100,
        counter=FixedTokenCounter(100),
    )

    result = guard.evaluate(text)

    assert result.passed is True
    assert result.action == GuardAction.ALLOW


def test_blocks_input_above_limit():
    text = (
        "Analyze this very large customer support history "
        "and produce a detailed summary."
    )

    guard = TokenLimitGuard(
        max_tokens=100,
        counter=FixedTokenCounter(101),
    )

    result = guard.evaluate(text)

    assert result.passed is False
    assert result.action == GuardAction.BLOCK
    assert result.metadata["token_count"] == 101


def test_warns_when_input_approaches_limit():
    text = (
        "Compare the repayment schedules for fixed-rate "
        "and floating-rate home loans."
    )

    guard = TokenLimitGuard(
        max_tokens=100,
        warning_tokens=80,
        counter=FixedTokenCounter(85),
    )

    result = guard.evaluate(text)

    assert result.action == GuardAction.WARN
    assert result.passed is False


def test_rejects_invalid_limits():
    with pytest.raises(ValueError):
        TokenLimitGuard(max_tokens=0)

    with pytest.raises(ValueError):
        TokenLimitGuard(
            max_tokens=100,
            warning_tokens=100,
        )


def test_token_guard_records_latency():
    text = "Explain the eligibility criteria for a housing loan."

    guard = TokenLimitGuard(
        max_tokens=100,
        counter=FixedTokenCounter(15),
    )

    result = guard.evaluate(text)

    assert result.latency_ms >= 0