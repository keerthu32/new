from flask import Flask

from .config import Config


def create_app() -> Flask:
    """Application factory for the ransomware detector dashboard."""
    app = Flask(__name__)
    app.config.from_object(Config)

    from .routes import bp

    app.register_blueprint(bp)
    return app
