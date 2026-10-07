"""Display text for the synthetic token-message endpoint.

This formats a message only. It performs no authentication, identity, or permission check.
"""


def _sentence(text: str) -> str:
    return text[:1].upper() + text[1:] + "."


_MESSAGES = {
    "expired": ("token expired", "please sign in again"),
}


def format_token_message(reason: str) -> str | None:
    parts = _MESSAGES.get(reason)
    if parts is None:
        return None
    return " ".join(_sentence(part) for part in parts)
