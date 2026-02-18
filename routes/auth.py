"""
Authentication Routes
Handles user and admin login, registration, and logout
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.user import User
from models.admin import Admin

# Create blueprint
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    # Redirect if already logged in
    if 'user_id' in session:
        return redirect(url_for('user.dashboard'))
    
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        phone = request.form.get('phone', '').strip()
        
        # Validation
        if not all([full_name, email, password, confirm_password]):
            flash('All required fields must be filled.', 'danger')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('auth/register.html')
        
        # Register user
        try:
            user = User.register(full_name, email, password, phone)
            
            if user:
                flash('Registration successful! Please login.', 'success')
                return redirect(url_for('auth.login'))
            else:
                flash('Email already exists. Please use a different email.', 'danger')
                return render_template('auth/register.html')
        except Exception as e:
            flash(f'Registration failed: {str(e)}', 'danger')
            return render_template('auth/register.html')
    
    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    # Redirect if already logged in
    if 'user_id' in session:
        return redirect(url_for('user.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        if not all([email, password]):
            flash('Please enter both email and password.', 'danger')
            return render_template('auth/login.html')
        
        try:
            user = User.login(email, password)
            
            if user:
                # Set session variables
                session.clear()  # Clear any existing session
                session['user_id'] = user['id']
                session['user_name'] = user['full_name']
                session['user_email'] = user['email']
                session['is_admin'] = False
                session.permanent = True  # Make session permanent
                
                flash(f'Welcome back, {user["full_name"]}!', 'success')
                
                # Redirect to next page if specified, otherwise dashboard
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                return redirect(url_for('user.dashboard'))

            
            # If user login failed, try ADMIN login
            # Admin.login now checks username OR email
            admin = Admin.login(email, password)
            
            if admin:
                # Set session variables for admin
                session.clear()  # Clear any existing session
                session['admin_id'] = admin['id']
                session['admin_name'] = admin['full_name'] or admin['username']
                session['admin_username'] = admin['username']
                session['is_admin'] = True
                session['is_super_admin'] = admin.get('is_super_admin', False)
                session.permanent = True
                
                flash(f'Welcome Admin, {admin["username"]}!', 'success')
                return redirect(url_for('admin.dashboard'))
                
            # If both fail
            flash('Invalid email or password.', 'danger')
            return render_template('auth/login.html')
        except Exception as e:
            flash(f'Login failed: {str(e)}', 'danger')
            return render_template('auth/login.html')
    
    return render_template('auth/login.html')


@auth_bp.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    """Admin login"""
    # Redirect if already logged in as admin
    if 'admin_id' in session and session.get('is_admin'):
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not all([username, password]):
            flash('Please enter both username and password.', 'danger')
            return render_template('auth/admin_login.html')
        
        try:
            admin = Admin.login(username, password)
            
            if admin:
                # Set session variables
                session.clear()  # Clear any existing session
                session['admin_id'] = admin['id']
                session['admin_name'] = admin['full_name'] or admin['username']
                session['admin_username'] = admin['username']
                session['is_admin'] = True
                session['is_super_admin'] = admin.get('is_super_admin', False)
                session.permanent = True  # Make session permanent
                
                flash(f'Welcome, {admin["username"]}!', 'success')
                return redirect(url_for('admin.dashboard'))
            else:
                flash('Invalid username or password.', 'danger')
                return render_template('auth/admin_login.html')
        except Exception as e:
            flash(f'Admin login failed: {str(e)}', 'danger')
            return render_template('auth/admin_login.html')
    
    return render_template('auth/admin_login.html')


@auth_bp.route('/logout')
def logout():
    """Logout (both user and admin)"""
    is_admin = session.get('is_admin', False)
    user_name = session.get('user_name') or session.get('admin_name')
    
    # Clear all session data
    session.clear()
    
    if user_name:
        flash(f'Goodbye {user_name}! You have been logged out successfully.', 'info')
    else:
        flash('You have been logged out successfully.', 'info')
    
    # Redirect based on who logged out
    if is_admin:
        return redirect(url_for('auth.admin_login'))
    return redirect(url_for('index'))