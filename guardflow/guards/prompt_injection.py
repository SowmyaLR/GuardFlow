from time import perf_counter

from guardflow.core.base import TextGuard
from guardflow.core.enums import GuardAction
from guardflow.core.result import GuardResult
from guardflow.engines.prompt_injection.base import PromptInjectionEngine
from guardflow.engines.prompt_injection.protectai_engine import (
    ProtectAIPromptInjectionEngine,
)


class PromptInjectionGuard(TextGuard):
    def __init__(
        self,
        engine: PromptInjectionEngine | None = None,
        threshold: float = 0.85,
        action: GuardAction = GuardAction.BLOCK,
    ) -> None:
        self._engine = engine or ProtectAIPromptInjectionEngine()
        self._threshold = threshold
        self._action = action

    def evaluate(self, text: str) -> GuardResult:
        started_at = perf_counter()

        prediction = self._engine.predict(text)

        latency_ms = (perf_counter() - started_at) * 1000

        detected = prediction.injection_score >= self._threshold

        if not detected:
            return GuardResult(
                guard_name="prompt_injection",
                passed=True,
                action=GuardAction.ALLOW,
                score=prediction.injection_score,
                latency_ms=latency_ms,
                output_text=text,
                metadata={
                    "label": prediction.label,
                },
            )

        return GuardResult(
            guard_name="prompt_injection",
            passed=False,
            action=self._action,
            score=prediction.injection_score,
            reason="Potential prompt injection detected",
            latency_ms=latency_ms,
            output_text=text,
            metadata={
                "label": prediction.label,
                "threshold": self._threshold,
            },
        )