from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

USERNAME_REGEX = r"^[a-zA-Z0-9_.]{3,30}$"


class Role(models.Model):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    NORMAL_USER = "normal_user"
    CHOICES = [
        (SUPER_ADMIN, "Super admin"),
        (ADMIN, "Admin"),
        (NORMAL_USER, "Normal user"),
    ]
    name = models.CharField(max_length=20, unique=True, choices=CHOICES)

    def __str__(self):
        return self.name


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
        user = self._create(email, username, password, True, **extra)
        role, _ = Role.objects.get_or_create(name=Role.SUPER_ADMIN)
        user.roles.add(role)
        return user


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
    roles = models.ManyToManyField(Role, related_name="users", blank=True)
    # models.py, on User
    last_active_role = models.CharField(max_length=50, blank=True, default="")

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

    def role_names(self):
        return set(self.roles.values_list("name", flat=True))

    def has_role(self, name):
        return self.roles.filter(name=name).exists()

    def has_any_role(self, *names):
        return self.roles.filter(name__in=names).exists()

    def __str__(self):
        return self.email