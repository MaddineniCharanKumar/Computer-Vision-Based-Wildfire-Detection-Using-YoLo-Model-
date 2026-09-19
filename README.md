from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


def create_token(subject: str, secret: str | None = None, ttl_minutes: int = 60) -> str:
    secret = secret or os.getenv("JWT_SECRET", "dev-secret-change-me")
    now = datetime.now(timezone.utc)
    payload = {"sub": subject, "iat": int(now.timestamp()), "exp": int((now + timedelta(minutes=ttl_minutes)).timestamp())}
    return jwt.encode(payload, secret, algorithm="HS256")


def verify_token(token: str, secret: str | None = None) -> dict[str, Any]:
    secret = secret or os.getenv("JWT_SECRET", "dev-secret-change-me")
    return jwt.decode(token, secret, algorithms=["HS256"])
