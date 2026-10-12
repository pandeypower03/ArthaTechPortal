import logging
from django.http import Http404
from rest_framework.exceptions import (
    APIException, ValidationError, NotAuthenticated,
    AuthenticationFailed, PermissionDenied, NotFound,
)
from rest_framework.response import Response
from rest_framework.views import exception_handler
from .messages import get_message

logger = logging.getLogger("app")


class AppError(APIException):
    """Raise this anywhere: raise AppError("INVALID_CREDENTIALS", 401)"""
    def __init__(self, code, status_code=400):
        self.code = code
        self.status_code = status_code
        super().__init__(detail=get_message(code), code=code)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    # Unexpected crash: log details on server, send a safe message
    if response is None:
        logger.error("Unhandled error: %s", type(exc).__name__, exc_info=exc)
        return Response(
            {"code": "SERVER_ERROR", "message": get_message("SERVER_ERROR"), "details": None},
            status=500,
        )

    details = None
    if isinstance(exc, AppError):
        code = exc.code
    elif isinstance(exc, ValidationError):
        code, details = "VALIDATION_ERROR", response.data
    elif isinstance(exc, NotAuthenticated):
        code = "NOT_AUTHENTICATED"
    elif isinstance(exc, AuthenticationFailed):
        code = "TOKEN_INVALID"
    elif isinstance(exc, PermissionDenied):
        code = "PERMISSION_DENIED"
    elif isinstance(exc, (NotFound, Http404)):
        code = "NOT_FOUND"
    else:
        code = "SERVER_ERROR"

    response.data = {"code": code, "message": get_message(code), "details": details}
    return response