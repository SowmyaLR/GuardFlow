from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(slots=True)
class PromptInjectionPrediction:
    injection_score: float
    label: str | None = None


class PromptInjectionEngine(ABC):
    @abstractmethod
    def predict(
        self,
        text: str,
    ) -> PromptInjectionPrediction:
        raise NotImplementedError