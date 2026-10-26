from __future__ import annotations

from typing import Mapping

from presidio_analyzer import EntityRecognizer, RecognizerResult
from flair.data import Sentence
from flair.models import SequenceTagger


DEFAULT_ENTITY_MAPPING = {
    "PER": "PERSON",
    "PERSON": "PERSON",
    "LOC": "LOCATION",
    "LOCATION": "LOCATION",
    "ORG": "ORGANIZATION",
    "ORGANIZATION": "ORGANIZATION",
}


class FlairRecognizer(EntityRecognizer):
    def __init__(
        self,
        model_name: str = "flair/ner-english-large",
        entity_mapping: Mapping[str, str] | None = None,
        supported_language: str = "en",
    ) -> None:
        self._model_name = model_name
        self._tagger: SequenceTagger | None = None
        self._entity_mapping = dict(entity_mapping or DEFAULT_ENTITY_MAPPING)

        supported_entities = sorted(set(self._entity_mapping.values()))

        super().__init__(
            supported_entities=supported_entities,
            supported_language=supported_language,
            name="FlairRecognizer",
        )

    @property
    def tagger(self) -> SequenceTagger:
        if self._tagger is None:
            self._tagger = SequenceTagger.load(self._model_name)

        return self._tagger

    def load(self) -> None:
        _ = self.tagger

    def analyze(
        self,
        text: str,
        entities: list[str],
        nlp_artifacts=None,
    ) -> list[RecognizerResult]:
        sentence = Sentence(text)

        self.tagger.predict(sentence)

        results: list[RecognizerResult] = []

        requested_entities = set(entities)

        for span in sentence.get_spans("ner"):
            mapped_entity = self._entity_mapping.get(span.tag)

            if mapped_entity is None:
                continue

            if requested_entities and mapped_entity not in requested_entities:
                continue

            results.append(
                RecognizerResult(
                    entity_type=mapped_entity,
                    start=span.start_position,
                    end=span.end_position,
                    score=float(span.score),
                )
            )

        return results