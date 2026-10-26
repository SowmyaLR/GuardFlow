from dataclasses import dataclass

from guardflow.core.base import TextGuard
from guardflow.core.enums import GuardAction
from guardflow.core.result import GuardResult


@dataclass(slots=True)
class FlowResult:
    allowed: bool
    text: str
    results: list[GuardResult]

    @property
    def total_latency_ms(self) -> float:
        return sum(result.latency_ms for result in self.results)


class GuardFlow:
    def __init__(self, guards: list[TextGuard]) -> None:
        self._guards = guards

    def inspect(self, text: str) -> FlowResult:
        current_text = text
        results: list[GuardResult] = []

        for guard in self._guards:
            result = guard.evaluate(current_text)
            results.append(result)

            if result.output_text is not None:
                current_text = result.output_text

            if result.action == GuardAction.BLOCK:
                return FlowResult(
                    allowed=False,
                    text=current_text,
                    results=results,
                )

        return FlowResult(
            allowed=True,
            text=current_text,
            results=results,
        )