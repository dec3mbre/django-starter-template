import logging
import time

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.template.response import TemplateResponse

from core.exceptions import ApplicationError, NotFoundError, PermissionDeniedError, ValidationError

logger = logging.getLogger(__name__)

# ApplicationError subclass → HTTP status code
_STATUS_MAP: dict[type[ApplicationError], int] = {
    NotFoundError: 404,
    ValidationError: 400,
    PermissionDeniedError: 403,
}


class ExceptionHandlerMiddleware:
    """Convert ApplicationError exceptions into proper HTTP responses.

    Maps exception types to HTTP status codes:
    - NotFoundError → 404
    - ValidationError → 400
    - PermissionDeniedError → 403
    - ApplicationError (fallback) → 400

    Returns JSON for AJAX/API requests, renders error template otherwise.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        return self.get_response(request)

    def process_exception(self, request: HttpRequest, exception: Exception) -> HttpResponse | None:
        if not isinstance(exception, ApplicationError):
            return None

        status = _STATUS_MAP.get(type(exception), 400)

        is_json = request.headers.get("Accept", "").startswith("application/json") or (
            request.content_type == "application/json"
        )

        if is_json:
            return JsonResponse({"error": exception.message, "extra": exception.extra}, status=status)

        return TemplateResponse(
            request,
            f"errors/{status}.html",
            {"error": exception.message, "extra": exception.extra},
            status=status,
        )


class RequestLoggingMiddleware:
    """Log method, path, status code and response time for every request."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        start = time.monotonic()
        response = self.get_response(request)
        duration_ms = (time.monotonic() - start) * 1000

        logger.info(
            "%s %s %s (%.1fms)",
            request.method,
            request.get_full_path(),
            response.status_code,
            duration_ms,
        )
        return response
