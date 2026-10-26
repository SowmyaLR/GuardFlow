from guardflow import (
    GuardAction,
    GuardFlow,
    PIIGuard,
    PromptInjectionGuard,
)


def print_result(result) -> None:
    print(f"\nGuard: {result.guard_name}")
    print(f"Passed: {result.passed}")
    print(f"Action: {result.action.value}")

    if result.score is not None:
        print(f"Score: {result.score:.4f}")

    print(f"Latency: {result.latency_ms:.2f} ms")

    if result.reason:
        print(f"Reason: {result.reason}")

    if result.metadata:
        print(f"Metadata: {result.metadata}")


def main() -> None:
    guardflow = GuardFlow(
        guards=[
            PIIGuard(
                action=GuardAction.REDACT,
            ),
            PromptInjectionGuard(
                threshold=0.85,
                action=GuardAction.BLOCK,
            ),
        ]
    )

    print("GuardFlow manual test")
    print("Enter an empty line to exit.")

    while True:
        text = input("\nEnter your prompt: ").strip()

        if not text:
            break

        result = guardflow.inspect(text)

        print("\nProcessed text:")
        print(result.text)

        print(
            f"\nTotal guard latency: "
            f"{result.total_latency_ms:.2f} ms"
        )

        print(f"Allowed: {result.allowed}")

        for guard_result in result.results:
            print_result(guard_result)


if __name__ == "__main__":
    main()