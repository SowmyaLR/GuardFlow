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

from guardflow.engines.tokens.approximate import (
    ApproximateTokenCounter,
)


CASES = [
    {
        "id": "TOK_001",
        "category": "normal_question",
        "text": (
            "Can you compare a 15-year home loan "
            "with a 20-year home loan?"
        ),
        "expected": "MEASURE",
    },
    {
        "id": "TOK_002",
        "category": "customer_support",
        "text": (
            "The customer says the payment was deducted but "
            "the order still shows unpaid. Can you summarize "
            "the likely causes and troubleshooting steps?"
        ),
        "expected": "MEASURE",
    },
    {
        "id": "TOK_003",
        "category": "code_review",
        "text": (
            "Can you review this FastAPI endpoint and explain "
            "why the transaction isn't being committed?\n\n"
            + (
                "def update_order():\n"
                "    # example application code\n"
                "    pass\n"
            ) * 20
        ),
        "expected": "MEASURE",
    },
    {
        "id": "TOK_004",
        "category": "long_document",
        "text": (
            "I copied the terms from my loan agreement. "
            "Please summarize the important clauses:\n\n"
            + (
                "Loan agreement clause describing repayment "
                "obligations and applicable conditions. "
            ) * 500
        ),
        "expected": "MEASURE",
    },
    {
        "id": "TOK_005",
        "category": "large_support_history",
        "text": (
            "Here is our complete support history. "
            "Please summarize what went wrong:\n\n"
            + (
                "Customer contacted support regarding "
                "the recurring payment issue. "
            ) * 5000
        ),
        "expected": "MEASURE",
    },
    {
        "id": "TOK_006",
        "category": "tamil",
        "text": (
            "இந்த ஆவணத்தை படித்து வீட்டு கடனின் "
            "முக்கிய விதிமுறைகளை விளக்க முடியுமா?"
        ),
        "expected": "MEASURE",
    },
    {
        "id": "TOK_007",
        "category": "emoji",
        "text": (
            "I'm a software engineer 👩‍💻 and I'm trying "
            "to understand these deployment metrics 📈."
        ),
        "expected": "MEASURE",
    },
    {
        "id": "TOK_008",
        "category": "json",
        "text": (
            '{"customer_id":"C98765",'
            '"question":"Why did my payment fail?",'
            '"retry_count":3}'
        ),
        "expected": "MEASURE",
    },
    {
        "id": "TOK_009",
        "category": "empty_input",
        "text": "",
        "expected": "MEASURE",
    },
]


def test_approximate_token_counter_latency():
    validate_benchmark_cases(CASES)

    counter = ApproximateTokenCounter()

    records: list[BenchmarkRecord] = []

    for case in CASES:
        started = perf_counter()

        result = counter.count(
            case["text"]
        )

        latency_ms = (
            perf_counter() - started
        ) * 1000

        records.append(
            BenchmarkRecord(
                case_id=case["id"],
                category=case["category"],
                input_text=case["text"],
                expected="MEASURE",
                actual="MEASURE",
                passed=True,
                latency_ms=latency_ms,
                metadata={
                    "characters": len(
                        case["text"]
                    ),
                    "estimated_tokens": (
                        result.count
                    ),
                    "counter": (
                        result.counter_name
                    ),
                    "exact": result.exact,
                },
            )
        )

        print()
        print(
            f"{case['id']} | "
            f"{case['category']} | "
            f"chars={len(case['text'])} | "
            f"tokens={result.count} | "
            f"{latency_ms:.4f} ms"
        )

        assert result.count >= 0

    latency = calculate_latency_metrics(
        records
    )

    reporter = MarkdownBenchmarkReporter(
        output_path=(
            "benchmarks/results/"
            "TOKEN_LIMIT_BENCHMARK.md"
        ),
        title="Approximate Token Counter Benchmark",
    )

    reporter.write(
        records=records,
        latency=latency,
        environment={
            "Python": platform.python_version(),
            "Counter": "ApproximateTokenCounter",
            "Exact tokenizer": "No",
        },
    )

    assert len(records) == len(CASES)