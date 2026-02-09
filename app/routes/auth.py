
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from app.forms import LoginForm, RegisterForm, AdminRegistrationForm, AdminInviteForm
from app.decorators import admin_required

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        password = form.password.data
        remember = form.remember.data

        from app.models import User

        user = User.query.filter_by(username=username).first()
        if user:
            valid = False
            try:
                valid = check_password_hash(user.password_hash, password)
            except Exception:
                valid = (user.password_hash == password)

            if valid:
                login_user(user, remember=remember)
                next_page = request.args.get("next")
                if user.role == 'admin':
                    return redirect(next_page or url_for('admin.dashboard'))
                else:
                    return redirect(next_page or url_for('student.dashboard'))

        flash("Invalid username or password", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('student.dashboard'))

    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        reg_no = (form.reg_no.data or '').strip()
        password = form.password.data

        from app.models import User
        from app.models.student import Student
        from app import db

        exists = User.query.filter_by(username=username).first()
        if exists:
            flash('Username already taken', 'danger')
            return render_template('auth/register.html', form=form)

        pw_hash = generate_password_hash(password)
        user = User(username=username, password_hash=pw_hash, role='student')
        db.session.add(user)
        db.session.flush()
        
        # Create Student profile
        student = Student(
            user_id=user.id,
            reg_no=reg_no if reg_no else username,
            full_name=username
        )
        db.session.add(student)
        db.session.commit()
        
        flash('Account created. You can now sign in.', 'message')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)


@auth_bp.route('/admin/register/<token>', methods=['GET', 'POST'])
def register_admin(token):
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))

    from app.models.invitation import AdminInvitation
    from app.models import User
    from app import db

    invitation = AdminInvitation.query.filter_by(token=token).first()
    
    if not invitation or not invitation.is_valid():
        flash('Invalid or expired invitation link', 'danger')
        return redirect(url_for('auth.login'))

    form = AdminRegistrationForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        password = form.password.data

        exists = User.query.filter_by(username=username).first()
        if exists:
            flash('Username already taken', 'danger')
            return render_template('auth/register_admin.html', form=form, token=token)

        pw_hash = generate_password_hash(password)
        user = User(username=username, password_hash=pw_hash, role='admin')
        db.session.add(user)
        db.session.flush()
        
        invitation.mark_as_used(user.id)
        db.session.commit()
        
        flash('Admin account created! You can now sign in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register_admin.html', form=form, token=token, email=invitation.email)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
