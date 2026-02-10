from flask import Flask
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf
from flask_wtf.csrf import CSRFError
from flask import request, jsonify
from app.extensions import db, migrate

login_manager = LoginManager()
login_manager.login_view = "auth.login"
csrf = CSRFProtect()


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = "dev-secret-key-change-later"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///eduid.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["ADMIN_SECRET"] = "admin-secret-123"  # Change this in production

    # init extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)

    # import models AFTER db init
    from app.models import User
    from app.models.student import Student, SchoolID
    from app.models.invitation import AdminInvitation

    # Flask-Login user loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # register blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.student import student_bp
    from app.routes.admin import admin_bp
    from app.routes.id_generator import id_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(id_bp)

    # Register CLI commands
    from app.cli import init_cli
    init_cli(app)

    # expose csrf token generator to templates
    @app.context_processor
    def inject_csrf_token():
        return dict(csrf_token=generate_csrf)

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        # Return JSON for AJAX/JSON requests to avoid HTML pages breaking JS
        if request.is_json or request.path.startswith('/admin'):
            return jsonify({'success': False, 'message': e.description}), 400
        return e.description, 400

    return app
