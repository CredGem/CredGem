class CredGemError(Exception):
    """Base exception for all CredGem SDK errors"""
    pass


class InsufficientCreditsError(CredGemError):
    """Raised when there are insufficient credits for an operation"""
    pass


class InvalidRequestError(CredGemError):
    """Raised when the request is invalid"""
    pass


class AuthenticationError(CredGemError):
    """Raised when there are authentication issues"""
    pass


class APIError(CredGemError):
    """Raised when the API returns an error"""
    pass 