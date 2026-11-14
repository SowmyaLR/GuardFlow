REQUIRED_CASE_FIELDS = {
    "id",
    "category",
    "text",
    "expected",
}


def validate_benchmark_cases(
    cases: list[dict],
) -> None:
    seen_ids: set[str] = set()

    for index, case in enumerate(cases):
        missing = (
            REQUIRED_CASE_FIELDS
            - set(case)
        )

        if missing:
            raise ValueError(
                f"Benchmark case at index "
                f"{index} is missing fields: "
                f"{sorted(missing)}"
            )

        case_id = case["id"]

        if case_id in seen_ids:
            raise ValueError(
                f"Duplicate benchmark case id: "
                f"{case_id}"
            )

        seen_ids.add(case_id)

        if not isinstance(
            case["text"],
            str,
        ):
            raise TypeError(
                f"{case_id}: text must be a string"
            )

        if not case["category"]:
            raise ValueError(
                f"{case_id}: category cannot be empty"
            )