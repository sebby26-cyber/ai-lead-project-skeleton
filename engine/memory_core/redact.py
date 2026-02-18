"""
redact.py — Pattern-based redaction before persistence.

Strips sensitive tokens (API keys, bearer tokens, etc.) from content
before it reaches the database. Configurable via policy denylist.
"""

from __future__ import annotations

import re

PLACEHOLDER = "[REDACTED]"

# Built-in patterns (always applied)
_BUILTIN_PATTERNS: list[re.Pattern] = [
    # Authorization headers
    re.compile(r"(Authorization:\s*)(Bearer\s+)\S+", re.IGNORECASE),
    re.compile(r"(Authorization:\s*)(Basic\s+)\S+", re.IGNORECASE),
    # Bearer tokens standalone
    re.compile(r"(bearer\s+)[A-Za-z0-9\-._~+/]+=*", re.IGNORECASE),
    # API keys in common formats
    re.compile(r"((?:api[_-]?key|apikey|api_secret|secret_key)\s*[:=]\s*)['\"]?[A-Za-z0-9\-._~+/]{16,}['\"]?", re.IGNORECASE),
    # sk-... style keys (OpenAI, Anthropic, Stripe, etc.)
    re.compile(r"\b(sk-[A-Za-z0-9\-]{20,})\b"),
    # OAuth authorization codes
    re.compile(r"(code=)[A-Za-z0-9\-._~+/]{16,}", re.IGNORECASE),
    # Generic long hex/base64 tokens after common key names
    re.compile(r"((?:token|secret|password|credentials?)\s*[:=]\s*)['\"]?[A-Za-z0-9\-._~+/]{20,}['\"]?", re.IGNORECASE),
]


def _compile_denylist(denylist: list[str]) -> list[re.Pattern]:
    """Compile user-provided regex strings into patterns."""
    compiled = []
    for pattern_str in denylist:
        try:
            compiled.append(re.compile(pattern_str, re.IGNORECASE))
        except re.error:
            continue  # Skip invalid patterns silently
    return compiled


def redact(text: str, denylist: list[str] | None = None) -> str:
    """Redact sensitive patterns from text.

    Args:
        text: Content to redact.
        denylist: Additional regex patterns from policy.

    Returns:
        Redacted text with sensitive values replaced by [REDACTED].
    """
    if not text:
        return text

    result = text

    # Apply built-in patterns
    for pattern in _BUILTIN_PATTERNS:
        # For patterns with capture groups, keep the prefix and redact the value
        if pattern.groups:
            result = pattern.sub(lambda m: m.group(0)[:len(m.group(1))] + PLACEHOLDER, result)
        else:
            result = pattern.sub(PLACEHOLDER, result)

    # Apply user denylist patterns
    if denylist:
        for pattern in _compile_denylist(denylist):
            result = pattern.sub(PLACEHOLDER, result)

    return result
