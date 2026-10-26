from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TokenCount:
    count: int
    counter_name: str
    exact: bool


class TokenCounter(ABC):
    @abstractmethod
    def count(self, text: str) -> TokenCount:
        raise NotImplementedError