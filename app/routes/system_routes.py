from flask import Blueprint, jsonify

system_bp = Blueprint("system", __name__)


@system_bp.get("/health")
def health():
    """Return service health status."""
    return jsonify({"status": "ok"}), 200
