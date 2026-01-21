from flask import Blueprint

id_bp = Blueprint("id", __name__, url_prefix="/id")

@id_bp.route("/generate")
def generate():
    return "ID generation coming soon"
