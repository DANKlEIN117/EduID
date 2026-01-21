from flask import Blueprint, render_template

student_bp = Blueprint("student", __name__, url_prefix="/student")


@student_bp.route("/dashboard")
def dashboard():
    return render_template("student/dashboard.html")
