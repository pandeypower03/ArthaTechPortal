from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

USERNAME_REGEX = r"^[a-zA-Z0-9_.]{3,30}$"


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create(self, email, username, password, is_superuser, **extra):
        if not email:
            raise ValueError("Email is required")
        if not username:
            raise ValueError("Username is required")
        user = self.model(
            email=self.normalize_email(email).lower(),
            username=username.lower(),
            is_superuser=is_superuser,
            **extra,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, username, password=None, **extra):
        extra.pop("is_superuser", None)
        return self._create(email, username, password, False, **extra)

    def create_superuser(self, email, username, password=None, **extra):
        if self.filter(is_superuser=True).exists():
            raise ValueError("A superuser already exists")
        extra.pop("is_superuser", None)
        return self._create(email, username, password, True, **extra)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[RegexValidator(USERNAME_REGEX, "Use 3-30 letters, numbers, _ or .")],
    )
    full_name = models.CharField(max_length=150, blank=True)
    is_active = models.BooleanField(default=True)
    failed_login_attempts = models.PositiveSmallIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(default=timezone.now)
    organisation = models.ForeignKey(
        "organisations.Organisation",
        null=True, blank=True, on_delete=models.PROTECT, related_name="users",
    )
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
    objects = UserManager()

    class Meta:
        constraints = [
            # The database itself allows only ONE row with is_superuser = true
            models.UniqueConstraint(
                fields=["is_superuser"],
                condition=models.Q(is_superuser=True),
                name="only_one_superuser",
            )
        ]

    def __str__(self):
        return self.email