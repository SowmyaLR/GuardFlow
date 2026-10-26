from time import perf_counter

from guardflow.core.base import TextGuard
from guardflow.core.enums import GuardAction
from guardflow.core.result import GuardResult
from guardflow.engines.tokens.approximate import (
    ApproximateTokenCounter,
)
from guardflow.engines.tokens.base import TokenCounter


class TokenLimitGuard(TextGuard):
    def __init__(
        self,
        max_tokens: int,
        warning_tokens: int | None = None,
        counter: TokenCounter | None = None,
    ) -> None:
        if max_tokens <= 0:
            raise ValueError("max_tokens must be greater than zero")

        if warning_tokens is not None:
            if warning_tokens <= 0:
                raise ValueError(
                    "warning_tokens must be greater than zero"
                )

            if warning_tokens >= max_tokens:
                raise ValueError(
                    "warning_tokens must be lower than max_tokens"
                )

        self._max_tokens = max_tokens
        self._warning_tokens = warning_tokens
        self._counter = counter or ApproximateTokenCounter()

    def evaluate(self, text: str) -> GuardResult:
        started_at = perf_counter()

        token_count = self._counter.count(text)

        latency_ms = (
            perf_counter() - started_at
        ) * 1000

        metadata = {
            "token_count": token_count.count,
            "max_tokens": self._max_tokens,
            "counter": token_count.counter_name,
            "exact": token_count.exact,
        }

        if self._warning_tokens is not None:
            metadata["warning_tokens"] = self._warning_tokens

        if token_count.count > self._max_tokens:
            return GuardResult(
                guard_name="token_limit",
                passed=False,
                action=GuardAction.BLOCK,
                reason=(
                    "Input exceeds the configured token limit"
                ),
                latency_ms=latency_ms,
                output_text=text,
                metadata=metadata,
            )

        if (
            self._warning_tokens is not None
            and token_count.count >= self._warning_tokens
        ):
            return GuardResult(
                guard_name="token_limit",
                passed=False,
                action=GuardAction.WARN,
                reason=(
                    "Input is approaching the configured token limit"
                ),
                latency_ms=latency_ms,
                output_text=text,
                metadata=metadata,
            )

        return GuardResult(
            guard_name="token_limit",
            passed=True,
            action=GuardAction.ALLOW,
            latency_ms=latency_ms,
            output_text=text,
            metadata=metadata,
        )