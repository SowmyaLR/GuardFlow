# GuardFlow

GuardFlow is a lightweight, local-first runtime guardrail SDK for LLM applications.

The first release focuses on two protections:

- PII detection and redaction using Presidio with a custom Flair recognizer
- Prompt-injection detection using a local classifier

GuardFlow is designed around pluggable engines, so detection models can be replaced without changing the public guard API.

---

## Current architecture

```text
Application
    |
    v
GuardFlow
    |
    +-- PIIGuard
    |      |
    |      +-- PresidioPIIEngine
    |              |
    |              +-- Presidio recognizers
    |              +-- custom FlairRecognizer
    |
    +-- PromptInjectionGuard
           |
           +-- ProtectAIPromptInjectionEngine