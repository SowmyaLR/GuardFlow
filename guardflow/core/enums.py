from enum import Enum


class GuardAction(str, Enum):
    ALLOW = "allow"
    WARN = "warn"
    SANITIZE = "sanitize"
    REDACT = "redact"
    BLOCK = "block"