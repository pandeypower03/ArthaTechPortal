from datetime import timedelta
from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken
from organisations.views import log
from core.exceptions import AppError
from core.messages import get_message
from core.permissions import IsSuperUser
from .models import User
from .serializers import (
    CreateUserSerializer, LoginSerializer, ResetPasswordSerializer, UserSerializer,
)


def ok(code, status_code=200, **extra):
    return Response({"code": code, "message": get_message(code), **extra}, status=status_code)


def revoke_all_tokens(user):
    """Log the user out everywhere by blacklisting all their refresh tokens."""
    for t in OutstandingToken.objects.filter(user=user):
        BlacklistedToken.objects.get_or_create(token=t)


def get_normal_user_or_404(pk):
    user = User.objects.filter(pk=pk, is_superuser=False).first()
    if not user:
        raise AppError("USER_NOT_FOUND", 404)
    return user


# ---------- Login, logout, me (both superuser and normal user) ----------


class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        s = LoginSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        identifier = s.validated_data["identifier"].strip().lower()
        password = s.validated_data["password"]

        user = User.objects.filter(Q(email=identifier) | Q(username=identifier)).first()

        if user and user.locked_until and user.locked_until > timezone.now():
            log(request, "login.locked", details={"identifier": identifier})
            raise AppError("ACCOUNT_LOCKED", 429)

        if not user or not user.is_active or not user.check_password(password):
            if user:
                user.failed_login_attempts += 1
                if user.failed_login_attempts >= settings.LOGIN_MAX_ATTEMPTS:
                    user.locked_until = timezone.now() + timedelta(minutes=settings.LOGIN_LOCK_MINUTES)
                    user.failed_login_attempts = 0
                user.save(update_fields=["failed_login_attempts", "locked_until"])
            log(request, "login.failed", details={"identifier": identifier})
            raise AppError("INVALID_CREDENTIALS", 401)

        user.failed_login_attempts = 0
        user.locked_until = None
        user.save(update_fields=["failed_login_attempts", "locked_until"])

        log(request, "login.ok", user=user)   # user= because the request is not authenticated yet

        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserSerializer(user).data,   # has is_superuser, so React knows which screen to show
        })

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
    permission_classes = [IsAuthenticated]   # both roles may ask "who am I"

    def get(self, request):
        return Response(UserSerializer(request.user).data)


# ---------- Login management (superuser only) ----------

class UsersView(APIView):
    permission_classes = [IsSuperUser]

    def get(self, request):
        users = User.objects.filter(is_superuser=False).order_by("-date_joined")
        return Response(UserSerializer(users, many=True).data)

    def post(self, request):
        s = CreateUserSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = s.validated_data
        email, username = d["email"].lower(), d["username"].lower()

        if User.objects.filter(Q(email=email) | Q(username=username)).exists():
            raise AppError("USER_EXISTS", 409)

        user = User.objects.create_user(
            email=email, username=username,
            password=d["password"], full_name=d.get("full_name", ""),
        )
        return ok("USER_CREATED", 201, user=UserSerializer(user).data)


class SetActiveView(APIView):
    permission_classes = [IsSuperUser]
    make_active = True

    def post(self, request, pk):
        user = get_normal_user_or_404(pk)
        user.is_active = self.make_active
        user.save(update_fields=["is_active"])
        if not self.make_active:
            revoke_all_tokens(user)
        return ok("USER_ACTIVATED" if self.make_active else "USER_DEACTIVATED")


class ResetPasswordView(APIView):
    permission_classes = [IsSuperUser]

    def post(self, request, pk):
        user = get_normal_user_or_404(pk)
        s = ResetPasswordSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        user.set_password(s.validated_data["new_password"])
        user.failed_login_attempts = 0
        user.locked_until = None
        user.save(update_fields=["password", "failed_login_attempts", "locked_until"])
        revoke_all_tokens(user)
        return ok("PASSWORD_RESET_OK")