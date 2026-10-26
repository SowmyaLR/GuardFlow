import math

from guardflow.engines.tokens.base import TokenCount, TokenCounter


class ApproximateTokenCounter(TokenCounter):
    """
    Lightweight token estimator.

    This is intentionally an approximation and should not be used when
    exact model-context accounting is required.

    A model-specific tokenizer can be supplied to TokenLimitGuard later
    through the TokenCounter interface.
    """

    def __init__(self, characters_per_token: float = 4.0) -> None:
        if characters_per_token <= 0:
            raise ValueError("characters_per_token must be greater than zero")

        self._characters_per_token = characters_per_token

    def count(self, text: str) -> TokenCount:
        if not text:
            return TokenCount(
                count=0,
                counter_name="approximate",
                exact=False,
            )

        estimated = math.ceil(
            len(text) / self._characters_per_token
        )

        return TokenCount(
            count=estimated,
            counter_name="approximate",
            exact=False,
        )