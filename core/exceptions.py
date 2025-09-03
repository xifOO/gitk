import logging
from typing import Optional

logger = logging.getLogger("gitk")


class BaseError(Exception):
    def __init__(self, message: str, *, cause: Optional[Exception] = None) -> None:
        self.message = message
        self.cause = cause

        log_msg = message
        if cause:
            log_msg += f" | Cause: {repr(cause)}"

        logger.error(log_msg)
        super().__init__(message)

    def __str__(self) -> str:
        return self.message


class ModelConfigError(BaseError): ...


class APIError(BaseError): ...


class CacheFileError(BaseError): ...


class EnvFileError(BaseError): ...


class PathError(BaseError): ...


class ConfigDirectoryError(PathError): ...


class CacheDirectoryError(PathError): ...


class ConfigFileError(BaseError): ...


class TemplateError(BaseError): ...


class TemplateLoadError(TemplateError): ...


class TemplateSaveError(TemplateError): ...


class MissingAPIKeyError(BaseError): ...


class UnsupportedProviderError(BaseError): ...


class ProviderAPIError(BaseError): ...


class ModelGenerationError(BaseError): ...
