"""Single-athlete sessions, password provisioning, and same-origin write guards."""

import argparse
import getpass
import hashlib
import hmac
import secrets
import time
from urllib.parse import urlsplit

from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel, ConfigDict, Field, SecretStr

from src.utils.config import settings
from src.utils.state_store import state_store

COOKIE_NAME = "fitness_session"
SESSION_SECONDS = 12 * 60 * 60
PASSWORD_ROUNDS = 600_000
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


class AuthStatus(BaseModel):
    authenticated: bool
    auth_required: bool
    writes_enabled: bool
    csrf_token: str | None


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    password: SecretStr = Field(min_length=1, max_length=1024)


def hash_password(password: str) -> str:
    if not 12 <= len(password) <= 1024:
        raise ValueError("Use a password between 12 and 1024 characters")
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), PASSWORD_ROUNDS)
    return f"pbkdf2_sha256${PASSWORD_ROUNDS}${salt}${digest.hex()}"


def password_hash() -> str | None:
    return settings.get("PASSWORD_HASH") or state_store.configuration("password_hash")


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, rounds, salt, expected = encoded.split("$")
        if algorithm != "pbkdf2_sha256" or not PASSWORD_ROUNDS <= int(rounds) <= 2_000_000:
            return False
        if len(salt) != 32 or len(expected) != 64:
            return False
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), int(rounds)).hex()
        return secrets.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def auth_required() -> bool:
    return bool(settings.get("AUTH_REQUIRED", False) or password_hash())


def session_hash(cookie: str) -> str:
    return hmac.new((password_hash() or "").encode(), cookie.encode(), "sha256").hexdigest()


def validate_access_settings() -> None:
    encoded = password_hash()
    if (settings.get("AUTH_REQUIRED", False) or settings.get("ENABLE_WRITES", False)) and not encoded:
        raise ValueError("Provision an athlete password before requiring authentication or enabling writes")
    if encoded:
        try:
            algorithm, rounds, salt, digest = encoded.split("$")
            valid = algorithm == "pbkdf2_sha256" and PASSWORD_ROUNDS <= int(rounds) <= 2_000_000 and len(bytes.fromhex(salt)) == 16 and len(bytes.fromhex(digest)) == 32
        except (ValueError, TypeError):
            valid = False
        if not valid:
            raise ValueError("Malformed athlete password hash")


def current_session(request: Request) -> dict | None:
    cookie = request.cookies.get(COOKIE_NAME)
    if not cookie or len(cookie) > 128:
        return None
    return state_store.session(session_hash(cookie), int(time.time()))


def require_read_access(request: Request) -> None:
    if auth_required() and current_session(request) is None:
        raise HTTPException(status_code=401, detail="Sign in to access training data", headers={"WWW-Authenticate": "Session"})


def require_same_origin(request: Request) -> None:
    origin = request.headers.get("origin")
    if not origin:
        raise HTTPException(status_code=403, detail="A same-origin request is required")
    parsed = urlsplit(origin)
    if parsed.netloc.lower() != request.headers.get("host", "").lower() or parsed.scheme not in {"http", "https"} or parsed.path or parsed.query or parsed.fragment:
        raise HTTPException(status_code=403, detail="Cross-origin writes are not allowed")
    if settings.get("COOKIE_SECURE", False) and parsed.scheme != "https":
        raise HTTPException(status_code=403, detail="HTTPS is required")


def require_write_access(request: Request) -> None:
    if not settings.get("ENABLE_WRITES", False):
        raise HTTPException(status_code=403, detail="Workout and measurement editing is disabled")
    session = current_session(request)
    if session is None:
        raise HTTPException(status_code=401, detail="Sign in before editing training data")
    require_same_origin(request)
    token = request.headers.get("x-csrf-token", "")
    if not token or not secrets.compare_digest(token.encode(), session["csrf_token"].encode()):
        raise HTTPException(status_code=403, detail="Invalid or missing CSRF token")


def session_status(request: Request) -> AuthStatus:
    session = current_session(request)
    return AuthStatus(
        authenticated=session is not None,
        auth_required=auth_required(),
        writes_enabled=bool(settings.get("ENABLE_WRITES", False)),
        csrf_token=session["csrf_token"] if session else None,
    )


@auth_router.get("/status", response_model=AuthStatus)
def status(request: Request, response: Response) -> AuthStatus:
    response.headers["Cache-Control"] = "no-store"
    return session_status(request)


@auth_router.post("/login", response_model=AuthStatus)
def login(payload: LoginRequest, request: Request, response: Response) -> AuthStatus:
    require_same_origin(request)
    encoded = password_hash()
    if not encoded:
        raise HTTPException(status_code=403, detail="No athlete password has been provisioned")
    client = "single-athlete"
    now = int(time.time())
    if not state_store.allow_login(client, now):
        raise HTTPException(status_code=429, detail="Too many sign-in attempts; try again later", headers={"Retry-After": "900"})
    if not verify_password(payload.password.get_secret_value(), encoded):
        raise HTTPException(status_code=401, detail="Invalid password")
    cookie = secrets.token_urlsafe(32)
    csrf = secrets.token_urlsafe(32)
    state_store.create_session(session_hash(cookie), csrf, now + SESSION_SECONDS, now)
    previous = request.cookies.get(COOKIE_NAME)
    if previous:
        state_store.revoke_session(session_hash(previous))
    response.set_cookie(COOKIE_NAME, cookie, max_age=SESSION_SECONDS, httponly=True, secure=bool(settings.get("COOKIE_SECURE", False)), samesite="strict", path="/")
    response.headers["Cache-Control"] = "no-store"
    return AuthStatus(authenticated=True, auth_required=True, writes_enabled=bool(settings.get("ENABLE_WRITES", False)), csrf_token=csrf)


@auth_router.post("/logout", status_code=204)
def logout(request: Request) -> Response:
    require_same_origin(request)
    session = current_session(request)
    token = request.headers.get("x-csrf-token", "")
    if session is None or not secrets.compare_digest(token.encode(), session["csrf_token"].encode()):
        raise HTTPException(status_code=403, detail="Invalid session or CSRF token")
    cookie = request.cookies.get(COOKIE_NAME, "")
    state_store.revoke_session(session_hash(cookie))
    response = Response(status_code=204, headers={"Cache-Control": "no-store"})
    response.delete_cookie(COOKIE_NAME, path="/", httponly=True, secure=bool(settings.get("COOKIE_SECURE", False)), samesite="strict")
    return response


def main() -> None:
    parser = argparse.ArgumentParser(description="Provision or change the single-athlete password without exposing it to browser code.")
    parser.add_argument("--set-password", action="store_true", required=True)
    parser.parse_args()
    password = getpass.getpass("New athlete password: ")
    confirmation = getpass.getpass("Confirm password: ")
    if password != confirmation:
        raise SystemExit("Passwords do not match")
    state_store.configure("password_hash", hash_password(password))
    print("Athlete password saved; existing sessions revoked.")


if __name__ == "__main__":
    main()