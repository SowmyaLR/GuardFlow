from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SecretDetection:
    secret_type: str
    start: int
    end: int


class SecretsEngine(ABC):
    @abstractmethod
    def detect(self, text: str) -> list[SecretDetection]:
        raise NotImplementedError