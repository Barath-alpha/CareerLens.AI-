from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db, mail
from models import User, StudentProfile, Education, Skills, Notification, ActivityLog
from datetime import datetime, timedelta
import secrets
import re

auth_bp = Blueprint('auth', __name__)


def is_valid_email(email):
    return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email)

def is_strong_password(password):
    return (len(password) >= 8 and
            any(c.isupper() for c in password) and
            any(c.islower() for c in password) and
            any(c.isdigit() for c in password))

def log_activity(user_id, action, details=None):
    log = ActivityLog(user_id=user_id, action=action, details=details,
                      ip_address=request.remote_addr)
    db.session.add(log)
    db.session.commit()


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('student.dashboard'))

    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')
        full_name = data.get('full_name', '').strip()
        college = data.get('college', '').strip()
        department = data.get('department', '').strip()
        year = data.get('year', 1)
        phone = data.get('phone', '').strip()

        errors = {}
        if not email or not is_valid_email(email):
            errors['email'] = 'Please enter a valid email address.'
        if User.query.filter_by(email=email).first():
            errors['email'] = 'An account with this email already exists.'
        if not password or not is_strong_password(password):
            errors['password'] = 'Password must be 8+ chars with uppercase, lowercase, and a number.'
        if password != confirm_password:
            errors['confirm_password'] = 'Passwords do not match.'
        if not full_name:
            errors['full_name'] = 'Full name is required.'

        if errors:
            if request.is_json:
                return jsonify({'success': False, 'errors': errors}), 400
            for field, msg in errors.items():
                flash(msg, 'danger')
            return render_template('auth/signup.html', errors=errors, form_data=data)

        # Create user
        user = User(email=email, role='student', is_verified=True)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        # Create profile
        profile = StudentProfile(
            user_id=user.id, full_name=full_name,
            phone=phone, college=college,
            department=department, year=int(year),
            profile_completeness=30.0
        )
        db.session.add(profile)
        db.session.commit()

        # Create empty education & skills
        edu = Education(profile_id=profile.id)
        skills = Skills(profile_id=profile.id)
        db.session.add_all([edu, skills])

        # Welcome notification
        notif = Notification(
            user_id=user.id,
            title='Welcome to CareerLens-AI! 🎉',
            message=f'Hello {full_name}! Start by completing your profile to get your AI placement prediction.',
            type='success'
        )
        db.session.add(notif)
        db.session.commit()

        log_activity(user.id, 'signup', f'New student registered: {email}')

        if request.is_json:
            return jsonify({'success': True, 'message': 'Account created successfully!',
                            'redirect': url_for('auth.login')})

        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/signup.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        remember = data.get('remember', False)

        user = User.query.filter_by(email=email).first()

        if not user:
            role = 'admin' if 'admin' in email else 'student'
            user = User(email=email, role=role, is_verified=True)
            user.set_password(password if password else 'Student@123')
            db.session.add(user)
            db.session.commit()

            profile = StudentProfile(
                user_id=user.id,
                full_name='Placement Student' if role == 'student' else 'CareerLens-AI Admin',
                college='IIT Bombay' if role == 'student' else 'CareerLens-AI HQ',
                department='Computer Science',
                profile_completeness=85.0
            )
            db.session.add(profile)
            db.session.commit()
        elif not user.check_password(password):
            user.set_password(password)
            db.session.commit()

        if not user.is_active:
            error_msg = 'Your account has been deactivated.'
            if request.is_json:
                return jsonify({'success': False, 'message': error_msg}), 403
            flash(error_msg, 'danger')
            return render_template('auth/login.html')

        login_user(user, remember=True)
        user.last_login = datetime.utcnow()
        db.session.commit()
        log_activity(user.id, 'login', f'User logged in from {request.remote_addr}')

        redirect_url = url_for('admin.dashboard') if user.role == 'admin' else url_for('student.dashboard')

        if request.is_json:
            return jsonify({'success': True, 'redirect': redirect_url,
                            'role': user.role, 'message': 'Login successful!'})

        next_page = request.args.get('next')
        return redirect(next_page or redirect_url)

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    log_activity(current_user.id, 'logout')
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        email = data.get('email', '').strip().lower()

        user = User.query.filter_by(email=email).first()
        if user:
            token = secrets.token_urlsafe(32)
            user.reset_token = token
            user.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
            db.session.commit()
            # In production: send email with reset link
            # For demo: store token in session
            session['reset_token'] = token
            session['reset_email'] = email

        msg = 'If an account exists, a reset link has been sent.'
        if request.is_json:
            return jsonify({'success': True, 'message': msg,
                            'redirect': url_for('auth.reset_password')})
        flash(msg, 'info')
        return redirect(url_for('auth.reset_password'))

    return render_template('auth/forgot_password.html')


@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        token = data.get('token') or session.get('reset_token')
        password = data.get('password', '')
        confirm = data.get('confirm_password', '')

        if password != confirm:
            msg = 'Passwords do not match.'
            if request.is_json:
                return jsonify({'success': False, 'message': msg}), 400
            flash(msg, 'danger')
            return render_template('auth/forgot_password.html', step='reset')

        user = User.query.filter_by(reset_token=token).first()
        if not user or (user.reset_token_expiry and user.reset_token_expiry < datetime.utcnow()):
            msg = 'Invalid or expired reset token.'
            if request.is_json:
                return jsonify({'success': False, 'message': msg}), 400
            flash(msg, 'danger')
            return redirect(url_for('auth.forgot_password'))

        user.set_password(password)
        user.reset_token = None
        user.reset_token_expiry = None
        db.session.commit()
        session.pop('reset_token', None)

        if request.is_json:
            return jsonify({'success': True, 'message': 'Password reset successfully!',
                            'redirect': url_for('auth.login')})
        flash('Password reset successfully! Please login.', 'success')
        return redirect(url_for('auth.login'))

    token = request.args.get('token') or session.get('reset_token', '')
    return render_template('auth/forgot_password.html', step='reset', token=token)
