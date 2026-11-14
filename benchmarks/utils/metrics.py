from dataclasses import dataclass

from benchmarks.utils.models import BenchmarkRecord


@dataclass(slots=True)
class ClassificationMetrics:
    total: int

    true_positive: int
    true_negative: int
    false_positive: int
    false_negative: int

    accuracy: float
    precision: float
    recall: float
    f1: float
    false_positive_rate: float


@dataclass(slots=True)
class LatencyMetrics:
    minimum_ms: float
    maximum_ms: float
    average_ms: float
    p50_ms: float
    p95_ms: float


def calculate_binary_metrics(
    records: list[BenchmarkRecord],
    positive_label: str,
) -> ClassificationMetrics:
    tp = 0
    tn = 0
    fp = 0
    fn = 0

    for record in records:
        expected_positive = (
            record.expected == positive_label
        )

        actual_positive = (
            record.actual == positive_label
        )

        if expected_positive and actual_positive:
            tp += 1

        elif (
            not expected_positive
            and not actual_positive
        ):
            tn += 1

        elif (
            not expected_positive
            and actual_positive
        ):
            fp += 1

        else:
            fn += 1

    total = len(records)

    accuracy = (
        (tp + tn) / total
        if total
        else 0.0
    )

    precision = (
        tp / (tp + fp)
        if (tp + fp)
        else 0.0
    )

    recall = (
        tp / (tp + fn)
        if (tp + fn)
        else 0.0
    )

    f1 = (
        2 * precision * recall
        / (precision + recall)
        if (precision + recall)
        else 0.0
    )

    false_positive_rate = (
        fp / (fp + tn)
        if (fp + tn)
        else 0.0
    )

    return ClassificationMetrics(
        total=total,
        true_positive=tp,
        true_negative=tn,
        false_positive=fp,
        false_negative=fn,
        accuracy=accuracy,
        precision=precision,
        recall=recall,
        f1=f1,
        false_positive_rate=false_positive_rate,
    )


def calculate_latency_metrics(
    records: list[BenchmarkRecord],
) -> LatencyMetrics:
    values = sorted(
        record.latency_ms
        for record in records
    )

    if not values:
        return LatencyMetrics(
            minimum_ms=0.0,
            maximum_ms=0.0,
            average_ms=0.0,
            p50_ms=0.0,
            p95_ms=0.0,
        )

    return LatencyMetrics(
        minimum_ms=min(values),
        maximum_ms=max(values),
        average_ms=(
            sum(values) / len(values)
        ),
        p50_ms=_percentile(
            values,
            0.50,
        ),
        p95_ms=_percentile(
            values,
            0.95,
        ),
    )


def _percentile(
    values: list[float],
    percentile: float,
) -> float:
    if len(values) == 1:
        return values[0]

    position = (
        (len(values) - 1)
        * percentile
    )

    lower_index = int(position)

    upper_index = min(
        lower_index + 1,
        len(values) - 1,
    )

    fraction = (
        position - lower_index
    )

    lower = values[lower_index]
    upper = values[upper_index]

    return (
        lower
        + (upper - lower)
        * fraction
    )