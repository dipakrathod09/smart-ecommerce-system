"""
Utility Decorators
Decorators for route protection and access control
"""

from functools import wraps
from flask import session, redirect, url_for, flash


def login_required(f):
    """
    Decorator to require user login for routes
    
    Usage:
        @app.route('/dashboard')
        @login_required
        def dashboard():
            return render_template('dashboard.html')
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """
    Decorator to require admin login for routes
    
    Usage:
        @app.route('/admin/dashboard')
        @admin_required
        def admin_dashboard():
            return render_template('admin/dashboard.html')
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session or not session.get('is_admin'):
            flash('Admin access required.', 'danger')
            return redirect(url_for('auth.admin_login'))
        return f(*args, **kwargs)
    return decorated_function


def logout_required(f):
    """
    Decorator to require user to be logged out
    Useful for login/register pages
    
    Usage:
        @app.route('/login')
        @logout_required
        def login():
            return render_template('login.html')
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' in session or 'admin_id' in session:
            if session.get('is_admin'):
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('user.dashboard'))
        return f(*args, **kwargs)
    return decorated_function
