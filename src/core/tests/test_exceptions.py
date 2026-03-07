import pytest

from core.exceptions import ApplicationError, NotFoundError, PermissionDeniedError, ValidationError


class TestApplicationError:
    def test_default_message(self):
        err = ApplicationError()
        assert str(err) == "An application error occurred."
        assert err.extra == {}

    def test_custom_message_and_extra(self):
        err = ApplicationError("Something broke", extra={"id": 1})
        assert err.message == "Something broke"
        assert err.extra == {"id": 1}

    def test_is_exception(self):
        assert issubclass(ApplicationError, Exception)


class TestExceptionHierarchy:
    @pytest.mark.parametrize(
        "exc_class",
        [NotFoundError, ValidationError, PermissionDeniedError],
    )
    def test_subclass_of_application_error(self, exc_class):
        assert issubclass(exc_class, ApplicationError)

    def test_not_found_default(self):
        assert NotFoundError().message == "Resource not found."

    def test_validation_default(self):
        assert ValidationError().message == "Validation error."

    def test_permission_denied_default(self):
        assert PermissionDeniedError().message == "Permission denied."
