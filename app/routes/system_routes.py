from flask import Blueprint, jsonify, render_template

system_bp = Blueprint("system", __name__)


@system_bp.get("/")
def index():
    """Serve the frontend dashboard application."""
    return render_template("index.html")


@system_bp.get("/health")
def health():
    """Return service health status."""
    return jsonify({"status": "ok"}), 200
