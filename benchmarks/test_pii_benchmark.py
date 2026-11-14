import platform
from time import perf_counter

from benchmarks.utils.metrics import (
    calculate_latency_metrics,
)
from benchmarks.utils.models import BenchmarkRecord
from benchmarks.utils.reporter import (
    MarkdownBenchmarkReporter,
)
from benchmarks.utils.validation import (
    validate_benchmark_cases,
)

from guardflow.engines.pii.presidio_engine import (
    PresidioPIIEngine,
)


CASES = [
    {
        "id": "PII_001",
        "category": "customer_support",
        "text": (
            "Hi, I'm Priya Raman. I placed an order last week "
            "but haven't received an update. Please reply to "
            "priya.raman@example.com."
        ),
        "expected": "EMAIL_ADDRESS,PERSON",
        "expected_entities": {
            "PERSON",
            "EMAIL_ADDRESS",
        },
    },
    {
        "id": "PII_002",
        "category": "banking_customer",
        "text": (
            "I'm unable to complete my loan application. "
            "Please call me on +91 98765 43210."
        ),
        "expected": "PHONE_NUMBER",
        "expected_entities": {
            "PHONE_NUMBER",
        },
    },
    {
        "id": "PII_003",
        "category": "resume_assistant",
        "text": (
            "Please improve this resume line: "
            "Sanjay Kumar worked at Microsoft in Hyderabad "
            "from 2021 to 2024."
        ),
        "expected": (
            "LOCATION,ORGANIZATION,PERSON"
        ),
        "expected_entities": {
            "PERSON",
            "ORGANIZATION",
            "LOCATION",
        },
    },
    {
        "id": "PII_004",
        "category": "email_drafting",
        "text": (
            "Write a professional follow-up email to Anjali Mehta "
            "and ask her to send the presentation to "
            "anjali.mehta@example.com."
        ),
        "expected": "EMAIL_ADDRESS,PERSON",
        "expected_entities": {
            "PERSON",
            "EMAIL_ADDRESS",
        },
    },
    {
        "id": "PII_005",
        "category": "multiple_people",
        "text": (
            "John Smith spoke with Sarah Johnson about "
            "the project yesterday."
        ),
        "expected": "PERSON",
        "expected_entities": {
            "PERSON",
        },
    },
    {
        "id": "PII_006",
        "category": "organization_location",
        "text": (
            "The candidate previously worked at Google "
            "in Bengaluru."
        ),
        "expected": "LOCATION,ORGANIZATION",
        "expected_entities": {
            "ORGANIZATION",
            "LOCATION",
        },
    },
    {
        "id": "PII_SAFE_001",
        "category": "normal_banking",
        "text": (
            "What documents do banks generally ask for "
            "when someone applies for a home loan?"
        ),
        "expected": "NONE",
        "expected_entities": set(),
    },
    {
        "id": "PII_SAFE_002",
        "category": "customer_support",
        "text": (
            "Our support team wants to reduce average ticket "
            "resolution time. Which metrics should we track?"
        ),
        "expected": "NONE",
        "expected_entities": set(),
    },
    {
        "id": "PII_SAFE_003",
        "category": "software_engineering",
        "text": (
            "Can you explain why my Celery worker is not "
            "consuming tasks from RabbitMQ?"
        ),
        "expected": "NONE",
        "expected_entities": set(),
    },
    {
        "id": "PII_SAFE_004",
        "category": "financial_education",
        "text": (
            "Explain how compound interest works with "
            "a simple numerical example."
        ),
        "expected": "NONE",
        "expected_entities": set(),
    },
]


def test_pii_engine_benchmark():
    validate_benchmark_cases(CASES)

    engine = PresidioPIIEngine()

    # Warm Flair/model-backed recognition.
    engine.detect(
        "John Smith works at Microsoft."
    )

    records: list[BenchmarkRecord] = []

    for case in CASES:
        started = perf_counter()

        detections = engine.detect(
            case["text"]
        )

        latency_ms = (
            perf_counter() - started
        ) * 1000

        detected_entities = {
            detection.entity_type
            for detection in detections
        }

        expected_entities = (
            case["expected_entities"]
        )

        actual = (
            ",".join(
                sorted(detected_entities)
            )
            if detected_entities
            else "NONE"
        )

        # Exact comparison intentionally exposes false
        # positives such as URL overlapping an email.
        passed = (
            detected_entities
            == expected_entities
        )

        records.append(
            BenchmarkRecord(
                case_id=case["id"],
                category=case["category"],
                input_text=case["text"],
                expected=case["expected"],
                actual=actual,
                passed=passed,
                latency_ms=latency_ms,
                metadata={
                    "detected_entities": sorted(
                        detected_entities
                    ),
                    "detection_count": len(
                        detections
                    ),
                },
            )
        )

    latency = calculate_latency_metrics(
        records
    )

    reporter = MarkdownBenchmarkReporter(
        output_path=(
            "benchmarks/results/"
            "PII_BENCHMARK.md"
        ),
        title="PII Detection Benchmark",
    )

    reporter.write(
        records=records,
        latency=latency,
        environment={
            "Python": platform.python_version(),
            "Engine": "PresidioPIIEngine",
            "NER": "Flair",
            "Orchestrator": "Presidio",
        },
    )

    passed_count = sum(
        record.passed
        for record in records
    )

    print()
    print("=" * 80)
    print("PII BENCHMARK")
    print("=" * 80)
    print(
        f"Cases passed: "
        f"{passed_count}/{len(records)}"
    )
    print(
        f"P50 latency: "
        f"{latency.p50_ms:.2f} ms"
    )
    print(
        f"P95 latency: "
        f"{latency.p95_ms:.2f} ms"
    )

    assert len(records) == len(CASES)