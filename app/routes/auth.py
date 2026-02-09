
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from app.forms import LoginForm, RegisterForm

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
        role = form.role.data or 'student'
        admin_code = form.admin_code.data or ''

        from app.models import User
        from app.models.student import Student
        from app import db

        exists = User.query.filter_by(username=username).first()
        if exists:
            flash('Username already taken', 'danger')
            return render_template('auth/register.html', form=form)

        if role == 'admin':
            secret = current_app.config.get('ADMIN_SECRET')
            if not secret or admin_code != secret:
                flash('Invalid admin code', 'danger')
                return render_template('auth/register.html', form=form)

        pw_hash = generate_password_hash(password)
        user = User(username=username, password_hash=pw_hash, role=role)
        db.session.add(user)
        db.session.flush()  # Get the user ID
        
        # If student, create Student profile
        if role == 'student':
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


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
