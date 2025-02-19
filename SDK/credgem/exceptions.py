class CredGemError(Exception):
    """Base exception for all CredGem errors."""

    pass


class InsufficientCreditsError(CredGemError):
    """Raised when attempting to hold or debit more credits than are available."""

    pass


class InvalidRequestError(CredGemError):
    """Raised when the request is invalid."""

    pass


class AuthenticationError(CredGemError):
    """Raised when authentication fails."""

    pass


class NotFoundError(CredGemError):
    """Raised when a resource is not found."""

    pass


class ServerError(CredGemError):
    """Raised when the server returns a 5xx error."""

    pass
