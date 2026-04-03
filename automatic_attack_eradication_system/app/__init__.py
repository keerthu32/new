import logging
import os

from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
socketio = SocketIO(async_mode="threading", cors_allowed_origins="*")


def create_app():
    load_dotenv()
    app = Flask(__name__)

    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev-change-me"),
        SQLALCHEMY_DATABASE_URI=os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///data/attack_system.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JWT_EXPIRES_MINUTES=int(os.getenv("JWT_EXPIRES_MINUTES", "60")),
        AUTO_BLOCK_ENABLED=os.getenv("AUTO_BLOCK_ENABLED", "true").lower() == "true",
        DEFAULT_BLOCK_MINUTES=int(os.getenv("DEFAULT_BLOCK_MINUTES", "120")),
    )

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    socketio.init_app(app)

    _configure_logging()

    from app.routes import main, auth, api
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(api.bp)

    with app.app_context():
        db.create_all()

    return app


def _configure_logging():
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    os.makedirs("logs", exist_ok=True)
    logging.basicConfig(
        level=getattr(logging, level, logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        handlers=[
            logging.FileHandler("logs/app.log"),
            logging.StreamHandler(),
        ],
    )


@login_manager.user_loader
def load_user(user_id):
    from app.models.user import User
    return User.query.get(int(user_id))
