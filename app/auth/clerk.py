"""Operator JWT auth for FastAPI.

Single-operator model: POST /api/auth/login verifies OPERATOR_PASSWORD and
returns a short-lived JWT signed with JWT_SECRET. Every protected route calls
require_user as a dependency.

The SSE endpoint cannot send Authorization headers, so it also accepts the
token as a ?token= query param — same pattern as the old Clerk implementation.
"""
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings

_bearer = HTTPBearer(auto_error=False)

_ALGORITHM = "HS256"
_TOKEN_TTL_HOURS = 12


def create_access_token() -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": "operator",
        "iat": now,
        "exp": now + timedelta(hours=_TOKEN_TTL_HOURS),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=_ALGORITHM)


def _verify_token(token: str) -> dict:
    if not settings.jwt_secret:
        return {"sub": "dev-operator"}
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[_ALGORITHM])
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired") from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc


async def require_user(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    token: str | None = Query(default=None),
) -> dict:
    raw = creds.credentials if creds else token
    if not raw:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return _verify_token(raw)
