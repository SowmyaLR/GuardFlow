from abc import ABC, abstractmethod

from guardflow.core.result import GuardResult


class TextGuard(ABC):
    @abstractmethod
    def evaluate(self, text: str) -> GuardResult:
        raise NotImplementedError