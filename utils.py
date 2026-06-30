from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user


def roles_required(*roles):
    """Decorator that restricts route access to users with one of the given roles."""
    def decorator(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            if current_user.role not in roles:
                abort(403)
            if current_user.is_blacklisted:
                flash('Your account has been suspended. Contact admin for help.', 'danger')
                return redirect(url_for('auth.logout'))
            return func(*args, **kwargs)
        return wrapped
    return decorator


def admin_required(func):
    return roles_required('admin')(func)


def staff_required(func):
    """Staff must have the role AND be approved by admin."""
    @wraps(func)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if current_user.role != 'staff':
            abort(403)
        if current_user.is_blacklisted:
            flash('Your account has been suspended. Contact admin for help.', 'danger')
            return redirect(url_for('auth.logout'))
        if not current_user.is_staff_approved:
            flash('Your guide account is pending admin approval. You will be notified once approved.', 'warning')
            return redirect(url_for('main.index'))
        return func(*args, **kwargs)
    return wrapped


def trekker_required(func):
    return roles_required('trekker')(func)