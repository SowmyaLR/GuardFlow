from guardflow.engines.sanitizer.base import (
    SanitizationFinding,
    SanitizationResult,
    SanitizerEngine,
)


ZERO_WIDTH_SPACE = "\u200b"
BYTE_ORDER_MARK = "\ufeff"

BIDI_CONTROL_CHARACTERS = {
    "\u202a",  # LEFT-TO-RIGHT EMBEDDING
    "\u202b",  # RIGHT-TO-LEFT EMBEDDING
    "\u202c",  # POP DIRECTIONAL FORMATTING
    "\u202d",  # LEFT-TO-RIGHT OVERRIDE
    "\u202e",  # RIGHT-TO-LEFT OVERRIDE
    "\u2066",  # LEFT-TO-RIGHT ISOLATE
    "\u2067",  # RIGHT-TO-LEFT ISOLATE
    "\u2068",  # FIRST STRONG ISOLATE
    "\u2069",  # POP DIRECTIONAL ISOLATE
}

REMOVABLE_CONTROL_CHARACTERS = {
    chr(code)
    for code in range(0x00, 0x20)
    if code not in {
        0x09,  # tab
        0x0A,  # newline
        0x0D,  # carriage return
    }
}

REMOVABLE_CONTROL_CHARACTERS.add(chr(0x7F))


class UnicodeSanitizerEngine(SanitizerEngine):
    """
    Conservative input sanitizer.

    Safe transformations:
    - normalizes CRLF to LF
    - removes a leading BOM
    - removes zero-width space
    - removes unsafe ASCII control characters

    Suspicious but potentially meaningful Unicode such as bidi
    controls is detected but not automatically removed.

    ZWJ and ZWNJ are preserved because they can be meaningful in
    Indic scripts and emoji sequences.
    """

    def sanitize(self, text: str) -> SanitizationResult:
        findings: list[SanitizationFinding] = []

        sanitized_text = self._normalize_line_endings(
            text=text,
            findings=findings,
        )

        sanitized_text = self._remove_leading_bom(
            text=sanitized_text,
            findings=findings,
        )

        sanitized_text = self._remove_safe_hidden_characters(
            text=sanitized_text,
            findings=findings,
        )

        self._detect_bidi_controls(
            text=sanitized_text,
            findings=findings,
        )

        return SanitizationResult(
            text=sanitized_text,
            findings=tuple(findings),
        )

    @staticmethod
    def _normalize_line_endings(
        text: str,
        findings: list[SanitizationFinding],
    ) -> str:
        count = text.count("\r\n")

        if count == 0:
            return text

        findings.extend(
            SanitizationFinding(
                finding_type="CRLF_NORMALIZED",
                position=None,
                modified=True,
            )
            for _ in range(count)
        )

        return text.replace("\r\n", "\n")

    @staticmethod
    def _remove_leading_bom(
        text: str,
        findings: list[SanitizationFinding],
    ) -> str:
        if not text.startswith(BYTE_ORDER_MARK):
            return text

        findings.append(
            SanitizationFinding(
                finding_type="LEADING_BOM",
                position=0,
                modified=True,
            )
        )

        return text[1:]

    @staticmethod
    def _remove_safe_hidden_characters(
        text: str,
        findings: list[SanitizationFinding],
    ) -> str:
        output: list[str] = []

        for index, character in enumerate(text):
            if character == ZERO_WIDTH_SPACE:
                findings.append(
                    SanitizationFinding(
                        finding_type="ZERO_WIDTH_SPACE",
                        position=index,
                        modified=True,
                    )
                )
                continue

            if character in REMOVABLE_CONTROL_CHARACTERS:
                findings.append(
                    SanitizationFinding(
                        finding_type="CONTROL_CHARACTER",
                        position=index,
                        modified=True,
                    )
                )
                continue

            output.append(character)

        return "".join(output)

    @staticmethod
    def _detect_bidi_controls(
        text: str,
        findings: list[SanitizationFinding],
    ) -> None:
        for index, character in enumerate(text):
            if character in BIDI_CONTROL_CHARACTERS:
                findings.append(
                    SanitizationFinding(
                        finding_type="BIDI_CONTROL_CHARACTER",
                        position=index,
                        modified=False,
                    )
                )