import time

from guardflow.engines.prompt_injection.base import (
    PromptInjectionEngine,
    PromptInjectionPrediction,
)
from guardflow.guards.prompt_injection import PromptInjectionGuard


class SlowFakeEngine(PromptInjectionEngine):
    def predict(self, text):
        time.sleep(0.02)

        return PromptInjectionPrediction(
            injection_score=0.1,
            label="SAFE",
        )


def test_latency_measurement_includes_engine_execution():
    guard = PromptInjectionGuard(
        engine=SlowFakeEngine(),
    )

    result = guard.evaluate("hello")

    assert result.latency_ms >= 15