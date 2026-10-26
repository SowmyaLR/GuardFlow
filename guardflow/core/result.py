from dataclasses import dataclass, field
from typing import Any

from guardflow.core.enums import GuardAction


@dataclass(slots=True)
class GuardResult:
    guard_name: str
    passed: bool
    action: GuardAction
    score: float | None = None
    reason: str | None = None
    latency_ms: float = 0.0
    output_text: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)