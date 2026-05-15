import os

from dotenv import load_dotenv
from flask import Flask

from app.db import init_db
from app.routes import auth_bp, cargo_bp, system_bp

# Load environment variables from `.env`.
load_dotenv()


def create_app() -> Flask:
    """Create and configure the Flask application instance."""
    app = Flask(__name__)
    app.register_blueprint(system_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(cargo_bp)
    return app


app = create_app()


def boot():
    """Validate required env vars and initialize the database."""
    if not os.getenv("JWT_SECRET"):
        raise RuntimeError("Missing JWT_SECRET in environment.")
    init_db()


if __name__ == "__main__":
    boot()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)
