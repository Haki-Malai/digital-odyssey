from functools import wraps
from flask import redirect, url_for, abort
from flask_login import current_user


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.has_permission(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    return permission_required('admin')(f)


def logout_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function    