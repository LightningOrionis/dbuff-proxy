from settings import CLIENTS


def get_client() -> None:
    """Get dotabuff client."""
    return CLIENTS["dotabuff"]
