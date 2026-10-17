from datetime import timedelta

from django.conf import settings
from django.db import IntegrityError, transaction
from django.db.models import F, Q
from django.utils import timezone
from rest_framework.permissions import AllowAny, IsAuthenticated
from core.permissions import IsAdminOrAbove
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken

from core.exceptions import AppError
from core.messages import get_message
from core.audit import log
from .models import Role, User
from .serializers import (
    CreateUserSerializer,
    LoginSerializer,
    ResetPasswordSerializer,
    UserSerializer,
)


# =====================================================================
# Role rules: the single place that defines who can do what
# =====================================================================

# Key = the role of the person acting. Value = roles that person may
# create, list, activate/deactivate and reset passwords for.
CREATABLE_ROLES = {
    Role.SUPER_ADMIN: {Role.SUPER_ADMIN, Role.ADMIN, Role.NORMAL_USER},
    Role.ADMIN: {Role.ADMIN, Role.NORMAL_USER},
    Role.NORMAL_USER: set(),
}


# def can_create_role(actor, role):
#     """True if `actor` is allowed to create a user with `role`."""
#     return role in CREATABLE_ROLES.get(actor.role, set())
def allowed_roles(actor):
    allowed = set()
    for name in actor.role_names():
        allowed |= CREATABLE_ROLES.get(name, set())
    return allowed


def can_create_role(actor, role):
    return role in allowed_roles(actor)

# Which users is this person allowed to see and act on?
# def manageable_users(actor):
#     """Users this actor may list / activate / deactivate / reset.
#     The actor and the bootstrap superuser are always excluded."""
#     allowed = CREATABLE_ROLES.get(actor.roles, set())
#     return (
#         User.objects.filter(role__in=allowed)
#         .exclude(pk=actor.pk)
#         .exclude(is_superuser=True)
#     )
def manageable_users(actor):
    """Users this actor may list / activate / deactivate / reset.
    The actor and the bootstrap superuser are always excluded."""
    allowed = allowed_roles(actor)
    # every role name the actor is NOT allowed to manage
    forbidden = set(Role.objects.values_list("name", flat=True)) - allowed
    return (
        User.objects.filter(roles__name__in=allowed)
        .exclude(roles__name__in=forbidden)   # hides anyone who also holds a higher role
        .exclude(pk=actor.pk)
        # .exclude(is_superuser=True)
        .distinct()
    )

def get_manageable_user_or_404(actor, pk):
    """Returns 404 (not 403) when the target is out of reach, so the
    existence of higher-role accounts is not revealed."""
    user = manageable_users(actor).filter(pk=pk).first()
    if not user:
        raise AppError("USER_NOT_FOUND", 404)
    return user


# =====================================================================
# Helpers
# =====================================================================

def ok(code, status_code=200, **extra):
    return Response(
        {"code": code, "message": get_message(code), **extra},
        status=status_code,
    )


def revoke_all_tokens(user):
    """Log the user out everywhere by blacklisting all their refresh tokens."""
    tokens = OutstandingToken.objects.filter(
        user=user, blacklistedtoken__isnull=True
    )
    BlacklistedToken.objects.bulk_create(
        [BlacklistedToken(token=t) for t in tokens],
        ignore_conflicts=True,
    )

# create_user_with_role is the helper that UsersView.post calls to actually create the user, after checking that the person creating them is allowed to.
# def create_user_with_role(request, data):
#     """Creates a user after checking that the actor may assign the role.
#     Raises AppError on any rule violation."""
#     actor = request.user
#     print(actor)
#     role = data["role"]                                   # CHANGED: single string

#     print(role)

#     if not can_create_role(actor, role):
#         log(
#             request,
#             "users.create.permission_denied",
#             user=actor,
#             details={                                     # CHANGED
#                 "actor_roles": sorted(actor.role_names()),
#                 "requested_role": role,
#             },
#         )
#         raise AppError("PERMISSION_DENIED", 403)

#     email = data["email"].strip().lower()
#     username = data["username"].strip().lower()

#     try:
#         with transaction.atomic():
#             if User.objects.filter(
#                 Q(email__iexact=email) | Q(username__iexact=username)
#             ).exists():
#                 log(
#                     request,
#                     "users.create.duplicate",
#                     user=actor,
#                     details={"username": username},
#                 )
#                 raise AppError("USER_EXISTS", 409)

#             user = User.objects.create_user(              # CHANGED: no role=role here
#                 email=email,
#                 username=username,
#                 password=data["password"],
#                 full_name=data.get("full_name", ""),
#             )
#             user.roles.add(Role.objects.get(name=role))   # CHANGED: saved in the link table
#             return user                                   # CHANGED
#     except IntegrityError:
#         # Two requests created the same email/username at the same moment.
#         raise AppError("USER_EXISTS", 409)

def create_user_with_role(request, data):
    """Creates a user after checking that the actor may assign the role.
    Raises AppError on any rule violation."""
    actor = request.user
    role = data["role"]                                   # single string, e.g. "admin"
                                                          # REMOVED: the two print() lines

    if not can_create_role(actor, role):
        log(
            request,
            "users.create.permission_denied",
            user=actor,
            details={
                "actor_roles": sorted(actor.role_names()),
                "requested_role": role,
            },
        )
        raise AppError("PERMISSION_DENIED", 403)

    email = data["email"].strip().lower()
    username = data["username"].strip().lower()

    try:
        with transaction.atomic():
            role_obj = Role.objects.get(name=role)        # NEW: look the role up once

            # CHANGED: block only when this email ALREADY has this SAME role
            # (was: block if the email OR the username existed)
            if User.objects.filter(email__iexact=email, roles__name=role).exists():
                log(
                    request,
                    "users.create.duplicate",
                    user=actor,
                    details={"email": email, "role": role},
                )
                raise AppError("USER_EXISTS", 409)

            # NEW: same email but a different role -> same person, just add the role
            user = User.objects.filter(email__iexact=email).first()
            if user:
                user.roles.add(role_obj)
                return user

            # NEW: brand-new email -> the username must still be free
            if User.objects.filter(username__iexact=username).exists():
                log(
                    request,
                    "users.create.duplicate",
                    user=actor,
                    details={"username": username},
                )
                raise AppError("USER_EXISTS", 409)

            user = User.objects.create_user(              # same as before
                email=email,
                username=username,
                password=data["password"],
                full_name=data.get("full_name", ""),
            )
            user.roles.add(role_obj)                      # saved in the link table
            return user
    except IntegrityError:
        # Two requests created the same email/username at the same moment.
        raise AppError("USER_EXISTS", 409)

# =====================================================================
# Login, logout, me (all roles)
# =====================================================================

class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        s = LoginSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        identifier = s.validated_data["identifier"].strip().lower()
        password = s.validated_data["password"]

        user = User.objects.filter(
            Q(email=identifier) | Q(username=identifier)
        ).first()

        if user and user.locked_until and user.locked_until > timezone.now():
            log(request, "login.locked", details={"identifier": identifier})
            raise AppError("ACCOUNT_LOCKED", 429)

        if not user or not user.is_active or not user.check_password(password):
            if user:
                self._register_failed_attempt(user)
            log(request, "login.failed", details={"identifier": identifier})
            raise AppError("INVALID_CREDENTIALS", 401)

        user.failed_login_attempts = 0
        user.locked_until = None
        user.save(update_fields=["failed_login_attempts", "locked_until"])

        # user= is passed because the request is not authenticated yet
        log(request, "login.ok", user=user)

        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            # contains role, so React knows which screen to show
            "user": UserSerializer(user).data,
        })

    @staticmethod
    def _register_failed_attempt(user):
        """Increments the counter in the database (safe under concurrent
        requests) and locks the account when the limit is reached."""
        User.objects.filter(pk=user.pk).update(
            failed_login_attempts=F("failed_login_attempts") + 1
        )
        user.refresh_from_db(fields=["failed_login_attempts"])

        if user.failed_login_attempts >= settings.LOGIN_MAX_ATTEMPTS:
            User.objects.filter(pk=user.pk).update(
                locked_until=timezone.now()
                + timedelta(minutes=settings.LOGIN_LOCK_MINUTES),
                failed_login_attempts=0,
            )


class LogoutView(APIView):
    permission_classes = [AllowAny]   # the refresh token is the proof
    authentication_classes = []

    def post(self, request):
        token = request.data.get("refresh")
        if not token:
            raise AppError("VALIDATION_ERROR", 400)
        try:
            RefreshToken(token).blacklist()
        except TokenError:
            raise AppError("TOKEN_INVALID", 401)
        return ok("LOGOUT_OK")


class MeView(APIView):
    permission_classes = [IsAuthenticated]   # every role may ask "who am I"

    def get(self, request):
        return Response(UserSerializer(request.user).data)


# =====================================================================
# User management (super_admin and admin only; scope depends on role)
# =====================================================================

class UsersView(APIView):
    permission_classes = [IsAdminOrAbove]

    def get(self, request):
        #show only those users that the login person can update , a normal user cant change or delete login of a superadmin
        users = manageable_users(request.user).order_by("-date_joined")
        print(f"**************{users}")
        log(
            request,
            "users.list",
            user=request.user,
            details={"count": users.count()},
        )
        return Response(UserSerializer(users, many=True).data)

    def post(self, request):
        s = CreateUserSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        print(s.validated_data)
        user = create_user_with_role(request, s.validated_data)

        log(
            request,
            "users.create.ok",
            user=request.user,
            details={
                "created_user_id": user.pk,
                "username": user.username,
                # "role": user.role,
                "roles": sorted(user.role_names()),
            },
        )
        return ok("USER_CREATED", 201, user=UserSerializer(user).data)


class SetActiveView(APIView):
    permission_classes = [IsAdminOrAbove]
    make_active = True   # set to False in urls.py via as_view(make_active=False)

    def post(self, request, pk):
        user = get_manageable_user_or_404(request.user, pk)
        user.is_active = self.make_active
        user.save(update_fields=["is_active"])

        if not self.make_active:
            revoke_all_tokens(user)

        log(
            request,
            "users.activate" if self.make_active else "users.deactivate",
            user=request.user,
            details={"target_user_id": user.pk},
        )
        return ok("USER_ACTIVATED" if self.make_active else "USER_DEACTIVATED")


class ResetPasswordView(APIView):
    permission_classes = [IsAdminOrAbove]

    def post(self, request, pk):
        user = get_manageable_user_or_404(request.user, pk)

        s = ResetPasswordSerializer(data=request.data)
        s.is_valid(raise_exception=True)

        user.set_password(s.validated_data["new_password"])
        user.failed_login_attempts = 0
        user.locked_until = None
        user.save(update_fields=["password", "failed_login_attempts", "locked_until"])
        revoke_all_tokens(user)

        log(
            request,
            "users.reset_password",
            user=request.user,
            details={"target_user_id": user.pk},
        )
        return ok("PASSWORD_RESET_OK")