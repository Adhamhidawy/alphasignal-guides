"""Field normalization and validation for the document API."""

TITLE_MAX_LENGTH = 80
LIMIT_MIN = 1
LIMIT_MAX = 100
LIMIT_DEFAULT = 20
OFFSET_DEFAULT = 0


class FieldError(ValueError):
    """Raised when a request field violates the documented contract."""


def normalize_title(raw: str) -> str:
    """Strip outer whitespace, then require 1 to 80 characters."""
    title = raw.strip()
    if not 1 <= len(title) <= TITLE_MAX_LENGTH:
        raise FieldError(f"title must be 1 to {TITLE_MAX_LENGTH} characters after trimming")
    return title


def normalize_tags(tags: list[str]) -> list[str]:
    """Remove duplicate tags, keeping each tag's first position."""
    seen: set[str] = set()
    unique: list[str] = []
    for tag in tags:
        if tag not in seen:
            seen.add(tag)
            unique.append(tag)
    return unique


def validate_pagination(limit: int, offset: int) -> tuple[int, int]:
    """Limit must be 1 to 100 inclusive; offset must be nonnegative."""
    if limit < LIMIT_MIN or limit > LIMIT_MAX:
        raise FieldError(f"limit must be from {LIMIT_MIN} to {LIMIT_MAX}")
    if offset < 0:
        raise FieldError("offset must be nonnegative")
    return limit, offset
