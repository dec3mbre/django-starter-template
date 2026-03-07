import pytest
from django.test import RequestFactory

from core.exceptions import NotFoundError, PermissionDeniedError, ValidationError
from core.middleware import ExceptionHandlerMiddleware


@pytest.fixture
def rf():
    return RequestFactory()


@pytest.fixture
def middleware():
    return ExceptionHandlerMiddleware(get_response=lambda r: None)


class TestExceptionHandlerMiddleware:
    def test_ignores_non_application_errors(self, rf, middleware):
        request = rf.get("/")
        result = middleware.process_exception(request, ValueError("boom"))
        assert result is None

    def test_not_found_returns_404(self, rf, middleware):
        request = rf.get("/", HTTP_ACCEPT="application/json")
        response = middleware.process_exception(request, NotFoundError("No such item"))
        assert response.status_code == 404

    def test_validation_returns_400(self, rf, middleware):
        request = rf.get("/", HTTP_ACCEPT="application/json")
        response = middleware.process_exception(request, ValidationError("Bad input"))
        assert response.status_code == 400

    def test_permission_denied_returns_403(self, rf, middleware):
        request = rf.get("/", HTTP_ACCEPT="application/json")
        response = middleware.process_exception(request, PermissionDeniedError())
        assert response.status_code == 403

    def test_json_response_body(self, rf, middleware):
        request = rf.get("/", HTTP_ACCEPT="application/json")
        response = middleware.process_exception(request, NotFoundError("Gone", extra={"id": 42}))
        import json

        data = json.loads(response.content)
        assert data["error"] == "Gone"
        assert data["extra"] == {"id": 42}
