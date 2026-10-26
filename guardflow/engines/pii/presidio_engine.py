from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from presidio_analyzer.nlp_engine import NoOpNlpEngine

from guardflow.engines.pii.base import PIIDetection, PIIEngine
from guardflow.engines.pii.recognizers.flair_recognizer import (
    FlairRecognizer,
)


class PresidioPIIEngine(PIIEngine):
    """
    PII detection engine using Presidio as the orchestration layer.

    Architecture:
        Presidio AnalyzerEngine
            ├── Presidio predefined pattern/checksum recognizers
            └── FlairRecognizer for NER

    spaCy is intentionally not used for NER.
    """

    def __init__(
        self,
        flair_model: str = "flair/ner-english-large",
    ) -> None:
        # Presidio currently requires a model declaration even for
        # NoOpNlpEngine. It does not actually load this model.
        self._nlp_engine = NoOpNlpEngine(
            models=[
                {
                    "lang_code": "en",
                    "model_name": "noop",
                }
            ]
        )

        self._registry = RecognizerRegistry(
            supported_languages=["en"]
        )

        # IMPORTANT:
        # Passing NoOpNlpEngine here prevents Presidio from automatically
        # adding SpacyRecognizer.
        self._registry.load_predefined_recognizers(
            languages=["en"],
            nlp_engine=self._nlp_engine,
        )

        # Flair provides NER instead of spaCy.
        self._flair_recognizer = FlairRecognizer(
            model_name=flair_model
        )

        self._registry.add_recognizer(
            self._flair_recognizer
        )

        self._analyzer = AnalyzerEngine(
            registry=self._registry,
            nlp_engine=self._nlp_engine,
            supported_languages=["en"],
        )

    def detect(
        self,
        text: str,
        entities: list[str] | None = None,
    ) -> list[PIIDetection]:
        results = self._analyzer.analyze(
            text=text,
            language="en",
            entities=entities,
        )

        return [
            PIIDetection(
                entity_type=result.entity_type,
                start=result.start,
                end=result.end,
                score=float(result.score),
                text=text[result.start:result.end],
            )
            for result in results
        ]