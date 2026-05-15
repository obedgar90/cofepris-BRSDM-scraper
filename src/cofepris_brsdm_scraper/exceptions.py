"""Domain exceptions for the pipeline."""


class PipelineError(Exception):
    """Base error for pipeline failures."""


class PortalUIChangedError(PipelineError):
    """Raised when expected portal controls are missing."""


class DownloadError(PipelineError):
    """Raised when the portal file cannot be downloaded."""


class BotBlockedError(PipelineError):
    """Raised when anti-bot protection blocks the scraping session."""


class MissingColumnError(PipelineError):
    """Raised when required columns are missing."""


class EmptyDatasetError(PipelineError):
    """Raised when the source dataset has no records."""


class DatabaseUnavailableError(PipelineError):
    """Raised when database is not reachable."""
