from organisations.models import AuditLog


def log(request, action, target_type="", target_id=None, details=None, user=None):
    """Add one line to the audit log.

    Pass user= only when the request is not logged in yet (for example login),
    because request.user is anonymous at that point.
    """
    if user is None and request.user.is_authenticated:
        user = request.user
    AuditLog.objects.create(
        user=user,
        action=action,
        target_type=target_type,
        target_id=target_id,
        details=details or {},
    )