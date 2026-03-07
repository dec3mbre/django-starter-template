from apps.users.models import User


class TestUserModel:
    def test_str_with_full_name(self, user):
        user.first_name = "John"
        user.last_name = "Doe"
        user.save()
        assert str(user) == "John Doe"

    def test_str_falls_back_to_username(self, user):
        assert str(user) == "testuser"

    def test_ordering(self):
        assert User._meta.ordering == ["-date_joined"]
