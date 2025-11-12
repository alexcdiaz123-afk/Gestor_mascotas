import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from dotenv import load_dotenv
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
migrate = Migrate()


def create_app():
    # Cargar variables de entorno desde .env (desarrollo local)
    load_dotenv()

    app = Flask(__name__, template_folder="../templates", static_folder="../static")

    # Configuración desde Config (usa DATABASE_URL y SECRET_KEY)
    app.config.from_object(Config)
    # Normalizar prefijo postgres:// si aparece (Render)
    url = app.config.get("SQLALCHEMY_DATABASE_URI", "")
    if isinstance(url, str) and url.startswith("postgres://"):
        app.config["SQLALCHEMY_DATABASE_URI"] = url.replace("postgres://", "postgresql://", 1)

    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Registrar modelos y ML predictor
    from .models import User  # noqa: F401
    from .ml.predictor import Predictor
    predictor = Predictor()
    app.predictor = predictor

    # Blueprints
    from .auth.routes import auth_bp
    from .user.routes import user_bp
    from .admin.routes import admin_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)

    # Ruta raíz
    @app.route("/")
    def index():
        from flask_login import current_user
        from flask import redirect, url_for
        if current_user.is_authenticated:
            if current_user.is_admin():
                return redirect(url_for("admin.dashboard"))
            return redirect(url_for("user.dashboard"))
        return redirect(url_for("auth.login"))

    # Ruta para favicon (evita 404)
    @app.route("/favicon.ico")
    def favicon():
        from flask import Response
        return Response(status=204)  # No Content - evita el 404

    return app