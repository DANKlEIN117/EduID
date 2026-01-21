from flask import Blueprint, render_template
from flask_login import login_required

student_bp = Blueprint("student", __name__, url_prefix="/student")

@student_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("student/dashboard.html")

@student_bp.route("/upload")
@login_required
def upload():
    return render_template("student/upload.html")
