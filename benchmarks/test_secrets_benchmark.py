import platform
from time import perf_counter

from benchmarks.utils.metrics import (
    calculate_binary_metrics,
    calculate_latency_metrics,
)
from benchmarks.utils.models import BenchmarkRecord
from benchmarks.utils.reporter import (
    MarkdownBenchmarkReporter,
)
from benchmarks.utils.validation import (
    validate_benchmark_cases,
)

from guardflow.engines.secrets.detect_secrets_engine import (
    DetectSecretsEngine,
)


CASES = [
    {
        "id": "SEC_001",
        "category": "debug_env",
        "text": (
            "My application keeps returning 401. "
            "Here is part of my .env file:\n"
            'api_key="p7V8Q2mL9xK4nR6sT1wY3zA5bC8dE0fG"\n'
            'environment="production"\n'
            "Can you see what might be wrong?"
        ),
        "expected": "SECRET",
    },
    {
        "id": "SEC_002",
        "category": "database_debugging",
        "text": (
            "My backend cannot connect to the database. "
            "This is the config I am using:\n"
            'password="ExampleOnly_9vK72LmP4"\n'
            'host="db.internal.example"\n'
            "What should I check?"
        ),
        "expected": "SECRET",
    },
    {
        "id": "SEC_003",
        "category": "bearer_token",
        "text": (
            "This API call keeps failing:\n"
            'curl -H "Authorization: Bearer '
            'ExampleFakeToken_7gK29LmP83Qx" '
            "https://api.example.com/users\n"
            "Can you check whether my request is malformed?"
        ),
        "expected": "SECRET",
    },
    {
        "id": "SEC_004",
        "category": "fake_jwt",
        "text": (
            "Authentication fails after login. "
            "This is the token returned in my local test:\n"
            "token="
            "eyJhbGciOiJIUzI1NiJ9."
            "ZXhhbXBsZS1vbmx5."
            "ZmFrZS1zaWduYXR1cmU"
        ),
        "expected": "SECRET",
    },
    {
        "id": "SEC_SAFE_001",
        "category": "normal_customer",
        "text": (
            "I forgot the password for my account. "
            "How can I reset it?"
        ),
        "expected": "SAFE",
    },
    {
        "id": "SEC_SAFE_002",
        "category": "security_architecture",
        "text": (
            "Should API keys be stored in environment variables "
            "or should we use AWS Secrets Manager?"
        ),
        "expected": "SAFE",
    },
    {
        "id": "SEC_SAFE_003",
        "category": "safe_code",
        "text": (
            "Is this a good way to load an API key in Python?\n"
            'api_key = os.getenv("OPENAI_API_KEY")'
        ),
        "expected": "SAFE",
    },
    {
        "id": "SEC_SAFE_004",
        "category": "incident_response",
        "text": (
            "One of our developers accidentally committed an API key "
            "to GitHub. What should we rotate and audit?"
        ),
        "expected": "SAFE",
    },
    {
        "id": "SEC_SAFE_005",
        "category": "developer_question",
        "text": (
            "What is the difference between an access token "
            "and a refresh token?"
        ),
        "expected": "SAFE",
    },
    {
        "id": "SEC_SAFE_006",
        "category": "logs",
        "text": (
            "Can you help explain this error?\n"
            "Authentication failed because the configured token "
            "is expired."
        ),
        "expected": "SAFE",
    },
    {
        "id": "SEC_SAFE_007",
        "category": "banking_customer",
        "text": (
            "I earn ₹90,000 per month. How much home loan EMI "
            "would generally be considered manageable?"
        ),
        "expected": "SAFE",
    },
    {
        "id": "SEC_SAFE_008",
        "category": "multilingual",
        "text": (
            "எனக்கு வீட்டு கடன் வாங்க வேண்டும். "
            "என்ன ஆவணங்கள் தேவை?"
        ),
        "expected": "SAFE",
    },
    {
        "id": "SEC_SAFE_009",
        "category": "business_reference",
        "text": (
            "My support ticket number is TICKET-94857231. "
            "Can you help me draft a follow-up message?"
        ),
        "expected": "SAFE",
    },
    {
        "id": "SEC_SAFE_010",
        "category": "documentation",
        "text": (
            "Our deployment guide says DATABASE_PASSWORD should "
            "come from the environment rather than source code. "
            "Can you explain why?"
        ),
        "expected": "SAFE",
    },
]


def test_secrets_engine_accuracy_and_latency():
    validate_benchmark_cases(CASES)

    engine = DetectSecretsEngine()

    records: list[BenchmarkRecord] = []

    for case in CASES:
        started = perf_counter()

        detections = engine.detect(
            case["text"]
        )

        latency_ms = (
            perf_counter() - started
        ) * 1000

        actual = (
            "SECRET"
            if detections
            else "SAFE"
        )

        detected_types = sorted(
            {
                detection.secret_type
                for detection in detections
            }
        )

        records.append(
            BenchmarkRecord(
                case_id=case["id"],
                category=case["category"],
                input_text=case["text"],
                expected=case["expected"],
                actual=actual,
                passed=(
                    actual
                    == case["expected"]
                ),
                latency_ms=latency_ms,
                metadata={
                    "secret_count": len(detections),
                    "secret_types": detected_types,
                },
            )
        )

    classification = calculate_binary_metrics(
        records=records,
        positive_label="SECRET",
    )

    latency = calculate_latency_metrics(
        records
    )

    reporter = MarkdownBenchmarkReporter(
        output_path=(
            "benchmarks/results/"
            "SECRETS_BENCHMARK.md"
        ),
        title="Secrets Detection Benchmark",
    )

    reporter.write(
        records=records,
        classification=classification,
        latency=latency,
        environment={
            "Python": platform.python_version(),
            "Engine": "DetectSecretsEngine",
            "Backend": "detect-secrets",
        },
    )

    print()
    print("=" * 80)
    print("SECRETS BENCHMARK")
    print("=" * 80)

    print(
        f"Accuracy: "
        f"{classification.accuracy:.2%}"
    )
    print(
        f"Precision: "
        f"{classification.precision:.2%}"
    )
    print(
        f"Recall: "
        f"{classification.recall:.2%}"
    )
    print(
        f"F1: "
        f"{classification.f1:.2%}"
    )
    print(
        f"False-positive rate: "
        f"{classification.false_positive_rate:.2%}"
    )

    assert len(records) == len(CASES)