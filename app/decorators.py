from functools import wraps
from flask import redirect, url_for, abort
from flask_login import current_user
from typing import Callable


def permission_required(permission: str) -> Callable:
    """Decorator to check if user has permission to access a route.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.has_permission(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f: Callable) -> Callable:
    return permission_required('admin')(f)


def logout_required(f: Callable) -> Callable:
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function
