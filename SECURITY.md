# Security Policy

## Reporting a Vulnerability

GuardFlow is a security-focused project, and responsible vulnerability disclosure is important to us.

If you discover a security vulnerability, please **do not create a public GitHub issue containing exploit details, credentials, sensitive information, or proof-of-concept code that could put users at risk**.

Instead, please report the vulnerability privately.

### Preferred Reporting Method

Use GitHub's private vulnerability reporting or Security Advisory feature for this repository.

Navigate to:

```text
GitHub Repository
→ Security
→ Advisories
→ Report a vulnerability
```

If private vulnerability reporting is enabled, this allows security researchers to report issues without making them public.

Please include as much of the following information as possible:

- A clear description of the vulnerability
- The affected GuardFlow version
- The affected guard or component
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Potential security impact
- A minimal proof of concept, when appropriate
- Any suggested mitigation or fix

## Sensitive Information

Do not include real production credentials, API keys, passwords, access tokens, private keys, customer data, or personally identifiable information in vulnerability reports.

Use clearly fake or synthetic values whenever possible.

For example:

```text
api_key="example-only-fake-key-123456"
```

instead of a real API key.

## Scope

Security reports may include issues involving:

- Secret detection bypasses
- PII detection or redaction failures
- Prompt-injection bypasses
- Input-sanitization bypasses
- Unicode or encoding-based evasion
- Guard execution bypasses
- Incorrect BLOCK / ALLOW behavior
- Sensitive data exposure in logs or metadata
- Packaging or dependency-related vulnerabilities
- Unexpected network transmission of user input
- Vulnerabilities in GuardFlow integrations

Model-quality disagreements, such as ordinary false positives or false negatives that do not create a security vulnerability, may be reported through normal GitHub issues.

## Response Process

Security reports will be reviewed before public disclosure.

When a vulnerability is confirmed, the project may:

1. Investigate the affected component.
2. Develop and test a fix.
3. Prepare a patched release.
4. Publish a GitHub Security Advisory when appropriate.
5. Credit the reporter, unless they prefer to remain anonymous.

Please avoid publicly disclosing confirmed vulnerabilities before a fix or mitigation is available.

## Supported Versions

GuardFlow is currently an early-stage project.

Security fixes are generally provided for the latest released version.

| Version | Supported |
|---|---|
| Latest release | Yes |
| Older releases | Best effort |

## Security Philosophy

GuardFlow should be treated as one layer in a broader AI application security architecture.

No guardrail system can guarantee complete detection of malicious input, secrets, PII, prompt injection, or other adversarial behavior.

Applications using GuardFlow should still apply appropriate authentication, authorization, logging, rate limiting, data governance, model-provider controls, and infrastructure security.