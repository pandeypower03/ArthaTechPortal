from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    LoginView, LogoutView, MeView,
    UsersView, SetActiveView, ResetPasswordView,
)

urlpatterns = [
    path("login/", LoginView.as_view()),
    path("logout/", LogoutView.as_view()),
    path("token/refresh/", TokenRefreshView.as_view()),
    path("me/", MeView.as_view()),

    # superuser only
    path("users/", UsersView.as_view()),
    path("users/<int:pk>/deactivate/", SetActiveView.as_view(make_active=False)),
    path("users/<int:pk>/activate/", SetActiveView.as_view(make_active=True)),
    path("users/<int:pk>/reset-password/", ResetPasswordView.as_view()),
]