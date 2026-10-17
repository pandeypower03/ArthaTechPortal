from rest_framework.permissions import BasePermission

from accounts.models import Role


def _active_user(request):
    """Returns the user if authenticated and active, otherwise None."""
    u = request.user
    if u and u.is_authenticated and u.is_active:
        return u
    return None


class IsSuperAdmin(BasePermission):
    """Only users who hold the super_admin role."""

    def has_permission(self, request, view):
        u = _active_user(request)
        return bool(u and u.has_role(Role.SUPER_ADMIN))


# Old name kept so any other module that still imports IsSuperUser keeps working.
IsSuperUser = IsSuperAdmin


class IsAdminOrAbove(BasePermission):
    """super_admin and admin. Used for user-management APIs."""

    def has_permission(self, request, view):
        u = _active_user(request)
        return bool(u and u.has_any_role(Role.SUPER_ADMIN, Role.ADMIN))


class IsNormalUser(BasePermission):
    """Anyone who holds at least one role other than super_admin."""

    def has_permission(self, request, view):
        u = _active_user(request)
        return bool(u and (u.role_names() - {Role.SUPER_ADMIN}))