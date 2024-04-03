from httpx import HTTPStatusError


class ItemNotFoundError(HTTPStatusError):
    """ItemNotFoundError."""


class UnhandledExternalError(HTTPStatusError):
    """Exception for unhandled errors on dotabuff side."""


class RateLimitExceededError(HTTPStatusError):
    """Exception for 429 response."""
