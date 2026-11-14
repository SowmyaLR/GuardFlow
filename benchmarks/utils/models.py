from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class BenchmarkRecord:
    case_id: str
    category: str
    input_text: str

    expected: str
    actual: str

    passed: bool
    latency_ms: float

    score: float | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )