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
            counter_name="test",
            exact=True,
        )


def test_allows_input_below_limit():
    guard = TokenLimitGuard(
        max_tokens=100,
        counter=FixedTokenCounter(50),
    )

    result = guard.evaluate("hello")

    assert result.passed is True
    assert result.action == GuardAction.ALLOW
    assert result.metadata["token_count"] == 50


def test_allows_input_exactly_at_limit():
    guard = TokenLimitGuard(
        max_tokens=100,
        counter=FixedTokenCounter(100),
    )

    result = guard.evaluate("hello")

    assert result.passed is True
    assert result.action == GuardAction.ALLOW


def test_blocks_input_above_limit():
    guard = TokenLimitGuard(
        max_tokens=100,
        counter=FixedTokenCounter(101),
    )

    result = guard.evaluate("hello")

    assert result.passed is False
    assert result.action == GuardAction.BLOCK
    assert result.metadata["token_count"] == 101


def test_warns_when_soft_limit_is_reached():
    guard = TokenLimitGuard(
        max_tokens=100,
        warning_tokens=80,
        counter=FixedTokenCounter(85),
    )

    result = guard.evaluate("hello")

    assert result.passed is False
    assert result.action == GuardAction.WARN


def test_rejects_invalid_configuration():
    with pytest.raises(ValueError):
        TokenLimitGuard(max_tokens=0)

    with pytest.raises(ValueError):
        TokenLimitGuard(
            max_tokens=100,
            warning_tokens=100,
        )


def test_records_latency():
    guard = TokenLimitGuard(
        max_tokens=100,
        counter=FixedTokenCounter(25),
    )

    result = guard.evaluate("hello")

    assert result.latency_ms >= 0