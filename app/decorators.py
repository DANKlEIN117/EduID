from functools import wraps
from flask import redirect, url_for, flash, abort
from flask_login import current_user


def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('You need to be logged in', 'danger')
            return redirect(url_for('auth.login'))
        if current_user.role != 'admin':
            flash('You do not have permission to access this page', 'danger')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def student_required(f):
    """Decorator to require student role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('You need to be logged in', 'danger')
            return redirect(url_for('auth.login'))
        if current_user.role != 'student':
            flash('You do not have permission to access this page', 'danger')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
