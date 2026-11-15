from guardflow.core.enums import GuardAction
from guardflow.core.flow import GuardFlow
from guardflow.guards.sanitizer import InputSanitizer
from guardflow.guards.token_limit import TokenLimitGuard


__all__ = [
    "GuardAction",
    "GuardFlow",
    "TokenLimitGuard",
    "InputSanitizer",
    "SecretsGuard",
    "PIIGuard",
    "PromptInjectionGuard",
]


def __getattr__(name: str):
    if name == "SecretsGuard":
        try:
            from guardflow.guards.secrets import SecretsGuard
        except ModuleNotFoundError as exc:
            if exc.name == "detect_secrets":
                raise ImportError(
                    "SecretsGuard requires the 'secrets' extra. "
                    "Install with: pip install 'guardflow[secrets]'"
                ) from exc
            raise
        return SecretsGuard

    if name == "PIIGuard":
        try:
            from guardflow.guards.pii import PIIGuard
        except ModuleNotFoundError as exc:
            if exc.name in {
                "presidio_analyzer",
                "flair",
            }:
                raise ImportError(
                    "PIIGuard requires the 'pii' extra. "
                    "Install with: pip install 'guardflow[pii]'"
                ) from exc
            raise
        return PIIGuard

    if name == "PromptInjectionGuard":
        try:
            from guardflow.guards.prompt_injection import (
                PromptInjectionGuard,
            )
        except ModuleNotFoundError as exc:
            if exc.name in {
                "transformers",
                "torch",
            }:
                raise ImportError(
                    "PromptInjectionGuard requires the 'injection' extra. "
                    "Install with: pip install 'guardflow[injection]'"
                ) from exc
            raise
        return PromptInjectionGuard

    raise AttributeError(
        f"module 'guardflow' has no attribute {name!r}"
    )