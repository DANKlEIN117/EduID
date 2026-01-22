from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
csrf = CSRFProtect()


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = "dev-secret-key-change-later"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///eduid.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # init extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # import models AFTER app + db are ready
    from app import models

    # register blueprints
    from app.routes.auth import auth_bp
    from app.routes.student import student_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(admin_bp)

    return app
