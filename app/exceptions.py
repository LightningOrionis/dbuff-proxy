from requests.exceptions import HTTPError


class ItemNotFoundError(HTTPError):
    """ItemNotFoundError."""


class UnhandledExternalError(HTTPError):
    """Exception for unhandled errors on dotabuff side."""


class RateLimitExceededError(HTTPError):
    """Exception for 429 response."""
