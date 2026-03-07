import logging
import time

from django.http import HttpRequest, HttpResponse

logger = logging.getLogger(__name__)


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
