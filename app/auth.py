import os
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from flask import Request
from jwt import InvalidTokenError
from werkzeug.security import check_password_hash, generate_password_hash


def determine_role_from_email(email: str) -> str:
    """Assign role based on domain business rule."""
    return "Admin" if email.lower().endswith("@nebula-corp.com") else "Standard"


def hash_password(password: str) -> str:
    """Generate a secure password hash for storage."""
    return generate_password_hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a plaintext password against a stored hash."""
    return check_password_hash(password_hash, password)


def issue_token(user_id: int, email: str, role: str) -> str:
    """Create a signed JWT token for authenticated users."""
    expires_in = int(os.getenv("JWT_EXPIRES_IN_SECONDS", "86400"))
    payload = {
        "sub": str(user_id),
        "email": email,
        "role": role,
        "exp": datetime.now(tz=timezone.utc) + timedelta(seconds=expires_in),
    }
    return jwt.encode(payload, os.environ["JWT_SECRET"], algorithm="HS256")


def decode_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT token."""
    return jwt.decode(token, os.environ["JWT_SECRET"], algorithms=["HS256"])


def extract_bearer_token(request: Request) -> str | None:
    """Extract bearer token from Authorization header."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    return auth_header[len("Bearer ") :].strip()


def get_claims_from_request(request: Request) -> dict[str, Any] | None:
    """Return JWT claims when a valid bearer token is present."""
    token = extract_bearer_token(request)
    if not token:
        return None
    try:
        return decode_token(token)
    except (InvalidTokenError, KeyError):
        return None
