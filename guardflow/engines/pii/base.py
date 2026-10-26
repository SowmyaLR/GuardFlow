from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(slots=True)
class PIIDetection:
    entity_type: str
    start: int
    end: int
    score: float
    text: str


class PIIEngine(ABC):
    @abstractmethod
    def detect(
        self,
        text: str,
        entities: list[str] | None = None,
    ) -> list[PIIDetection]:
        raise NotImplementedError