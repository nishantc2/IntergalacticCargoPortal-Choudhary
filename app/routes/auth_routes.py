import sqlite3

from flask import Blueprint, jsonify, request

from app.auth import determine_role_from_email, hash_password, issue_token, verify_password
from app.db import get_connection

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/signup")
def signup():
    payload = request.get_json(silent=True) or {}
    name = payload.get("name")
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password")

    if not name or not email or not password:
        return jsonify({"message": "name, email, and password are required."}), 400

    role = determine_role_from_email(email)
    password_hash = hash_password(password)

    try:
        with get_connection() as conn:
            result = conn.execute(
                """
                INSERT INTO users (name, email, password_hash, role)
                VALUES (?, ?, ?, ?)
                """,
                (name, email, password_hash, role),
            )
            conn.commit()
            user_id = result.lastrowid
    except sqlite3.IntegrityError:
        return jsonify({"message": "Email already exists."}), 409
    except Exception:
        return jsonify({"message": "Unable to create user."}), 500

    token = issue_token(user_id=user_id, email=email, role=role)
    return (
        jsonify(
            {
                "user": {"id": user_id, "name": name, "email": email, "role": role},
                "token": token,
            }
        ),
        201,
    )


@auth_bp.post("/login")
def login():
    payload = request.get_json(silent=True) or {}
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password")

    if not email or not password:
        return jsonify({"message": "email and password are required."}), 400
    try:
        with get_connection() as conn:
            user = conn.execute(
                """
                SELECT id, name, email, password_hash, role
                FROM users
                WHERE email = ?
                """,
                (email,),
            ).fetchone()
    except Exception:
        return jsonify({"message": "Login failed."}), 500

    if not user:
        return jsonify({"message": "Invalid email or password."}), 401

    if not verify_password(password, user["password_hash"]):
        return jsonify({"message": "Invalid email or password."}), 401

    token = issue_token(user_id=user["id"], email=user["email"], role=user["role"])
    return (
        jsonify(
            {
                "user": {
                    "id": user["id"],
                    "name": user["name"],
                    "email": user["email"],
                    "role": user["role"],
                },
                "token": token,
            }
        ),
        200,
    )
