"""CAMARA standard error codes and responses."""

from enum import Enum
from pydantic import BaseModel, Field, ConfigDict
from typing import Literal


class ErrorCode400(str, Enum):
    """Standard 400 error codes."""
    INVALID_ARGUMENT = "INVALID_ARGUMENT"
    OUT_OF_RANGE = "OUT_OF_RANGE"


class ErrorCode401(str, Enum):
    """Standard 401 error codes."""
    UNAUTHENTICATED = "UNAUTHENTICATED"


class ErrorCode403(str, Enum):
    """Standard 403 error codes."""
    PERMISSION_DENIED = "PERMISSION_DENIED"
    INVALID_TOKEN_CONTEXT = "INVALID_TOKEN_CONTEXT"


class ErrorCode404(str, Enum):
    """Standard 404 error codes."""
    NOT_FOUND = "NOT_FOUND"
    IDENTIFIER_NOT_FOUND = "IDENTIFIER_NOT_FOUND"


class ErrorCode405(str, Enum):
    """Standard 405 error codes."""
    METHOD_NOT_ALLOWED = "METHOD_NOT_ALLOWED"


class ErrorCode406(str, Enum):
    """Standard 406 error codes."""
    NOT_ACCEPTABLE = "NOT_ACCEPTABLE"


class ErrorCode409(str, Enum):
    """Standard 409 error codes."""
    ABORTED = "ABORTED"
    ALREADY_EXISTS = "ALREADY_EXISTS"
    CONFLICT = "CONFLICT"
    INCOMPATIBLE_STATE = "INCOMPATIBLE_STATE"


class ErrorCode410(str, Enum):
    """Standard 410 error codes."""
    GONE = "GONE"


class ErrorCode412(str, Enum):
    """Standard 412 error codes."""
    FAILED_PRECONDITION = "FAILED_PRECONDITION"


class ErrorCode415(str, Enum):
    """Standard 415 error codes."""
    UNSUPPORTED_MEDIA_TYPE = "UNSUPPORTED_MEDIA_TYPE"


class ErrorCode422(str, Enum):
    """Standard 422 error codes."""
    SERVICE_NOT_APPLICABLE = "SERVICE_NOT_APPLICABLE"
    MISSING_IDENTIFIER = "MISSING_IDENTIFIER"
    UNSUPPORTED_IDENTIFIER = "UNSUPPORTED_IDENTIFIER"
    UNNECESSARY_IDENTIFIER = "UNNECESSARY_IDENTIFIER"


class ErrorCode429(str, Enum):
    """Standard 429 error codes."""
    QUOTA_EXCEEDED = "QUOTA_EXCEEDED"
    TOO_MANY_REQUESTS = "TOO_MANY_REQUESTS"


class ErrorCode500(str, Enum):
    """Standard 500 error codes."""
    INTERNAL = "INTERNAL"


class ErrorCode501(str, Enum):
    """Standard 501 error codes."""
    NOT_IMPLEMENTED = "NOT_IMPLEMENTED"


class ErrorCode502(str, Enum):
    """Standard 502 error codes."""
    BAD_GATEWAY = "BAD_GATEWAY"


class ErrorCode503(str, Enum):
    """Standard 503 error codes."""
    UNAVAILABLE = "UNAVAILABLE"


class ErrorCode504(str, Enum):
    """Standard 504 error codes."""
    TIMEOUT = "TIMEOUT"


# Specific error response models - standalone without inheritance
class Error400(BaseModel):
    """400 Bad Request error."""
    model_config = ConfigDict(use_enum_values=True)
    status: Literal[400] = 400
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")


class Error401(BaseModel):
    """401 Unauthorized error."""
    model_config = ConfigDict(use_enum_values=True)
    status: Literal[401] = 401
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")


class Error403(BaseModel):
    """403 Forbidden error."""
    model_config = ConfigDict(use_enum_values=True)
    status: Literal[403] = 403
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")


class Error404(BaseModel):
    """404 Not Found error."""
    model_config = ConfigDict(use_enum_values=True)
    status: Literal[404] = 404
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")


class Error422(BaseModel):
    """422 Unprocessable Entity error."""
    model_config = ConfigDict(use_enum_values=True)
    status: Literal[422] = 422
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")


class Error429(BaseModel):
    """429 Too Many Requests error."""
    model_config = ConfigDict(use_enum_values=True)
    status: Literal[429] = 429
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")


class Error500(BaseModel):
    """500 Internal Server Error."""
    model_config = ConfigDict(use_enum_values=True)
    status: Literal[500] = 500
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")


class Error503(BaseModel):
    """503 Service Unavailable error."""
    model_config = ConfigDict(use_enum_values=True)
    status: Literal[503] = 503
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
