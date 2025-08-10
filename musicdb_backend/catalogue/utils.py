from django.http import HttpResponseForbidden


def require_permission(user, allowed_roles):
    """
    Returns None if allowed, or HttpResponseForbidden if not.
    allowed_roles: list of strings like ['viewer', 'artist', 'editor']
    """
    if not user.is_authenticated:
        return HttpResponseForbidden("You must be logged in")

    try:
        role = user.musicmanageruser.permission
    except Exception:
        return HttpResponseForbidden("No profile found")

    if role not in allowed_roles:
        return HttpResponseForbidden("You do not have permission for this action")

    return None
