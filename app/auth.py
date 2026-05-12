import os
from datetime import datetime, timedelta, timezone

import jwt
from werkzeug.security import check_password_hash, generate_password_hash


def determine_role_from_email(email: str) -> str:
    return "Admin" if email.lower().endswith("@nebula-corp.com") else "Standard"


def hash_password(password: str) -> str:
    return generate_password_hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return check_password_hash(password_hash, password)


def issue_token(user_id: int, email: str, role: str) -> str:
    expires_in = int(os.getenv("JWT_EXPIRES_IN_SECONDS", "86400"))
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "exp": datetime.now(tz=timezone.utc) + timedelta(seconds=expires_in),
    }
    return jwt.encode(payload, os.environ["JWT_SECRET"], algorithm="HS256")
