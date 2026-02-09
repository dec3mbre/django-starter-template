from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Custom user model. Extend with project-specific fields as needed."""

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"
        ordering = ["-date_joined"]

    def __str__(self):
        return self.get_full_name() or self.username
