from __future__ import annotations

from transformers import pipeline

from guardflow.engines.prompt_injection.base import (
    PromptInjectionEngine,
    PromptInjectionPrediction,
)


class ProtectAIPromptInjectionEngine(PromptInjectionEngine):
    def __init__(
        self,
        model_name: str = "protectai/deberta-v3-base-prompt-injection-v2",
    ) -> None:
        self._model_name = model_name
        self._classifier = None

    @property
    def classifier(self):
        if self._classifier is None:
            self._classifier = pipeline(
                "text-classification",
                model=self._model_name,
                tokenizer=self._model_name,
            )

        return self._classifier

    def predict(
        self,
        text: str,
    ) -> PromptInjectionPrediction:
        predictions = self.classifier(text)

        if not predictions:
            return PromptInjectionPrediction(
                injection_score=0.0,
                label=None,
            )

        prediction = predictions[0]

        label = str(prediction["label"])
        score = float(prediction["score"])

        normalized_label = label.lower()

        if "injection" in normalized_label:
            injection_score = score
        else:
            injection_score = 1.0 - score

        return PromptInjectionPrediction(
            injection_score=injection_score,
            label=label,
        )