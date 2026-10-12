from rest_framework.permissions import BasePermission
# from accounts.views import views



class IsSuperUser(BasePermission):
    """Only the one superuser. Used for login-management APIs."""
    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and u.is_active and u.is_superuser)


class IsNormalUser(BasePermission):
    """Normal users only. Default for every module, so the superuser is blocked."""
    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and u.is_active and not u.is_superuser)