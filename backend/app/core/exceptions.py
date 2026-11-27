"""Domain exceptions for Pigzel."""


class PigzelError(Exception):
    """Base exception for all Pigzel domain errors."""


class IngestionValidationError(PigzelError):
    """Raised when user brief or reference context cannot be normalized."""


class ProviderConfigError(PigzelError):
    """Raised when an AI provider is missing or misconfigured."""


class ProviderTransientError(PigzelError):
    """Raised on transient provider failures such as timeouts or rate limits."""


class ProviderResponseError(PigzelError):
    """Raised when a provider returns an unusable or protocol-invalid response."""


class AgentOutputValidationError(PigzelError):
    """Raised when an agent fails to produce schema-valid output after retries."""
