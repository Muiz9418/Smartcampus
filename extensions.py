import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from functools import wraps
from flask import jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail

db = SQLAlchemy()
mail = Mail()

def ok(data=None, **kwargs):
    payload = {"success": True}
    if data is not None:
        payload["data"] = data
    payload.update(kwargs)
    return jsonify(payload)

def err(message: str, status: int = 400):
    return jsonify({"success": False, "error": message}), status

def current_user():
    from app.models.user import User
    email = session.get("user_email")
    if not email:
        return None
    return User.query.filter_by(email=email).first()

def require_auth(roles=None):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if "user_email" not in session:
                return err("Unauthorised — please log in.", 401)
            user = current_user()
            if user is None:
                session.clear()
                return err("Session invalid.", 401)
            if roles and user.role not in roles:
                return err("Forbidden.", 403)
            return f(*args, **kwargs)
        return wrapper
    return decorator

# ── Rate limiting store (in-memory) ──────────────────────────────────
import time
from collections import defaultdict
_login_attempts = defaultdict(list)  # ip -> [timestamp, ...]
LOGIN_MAX_ATTEMPTS = 5
LOGIN_WINDOW_SECS  = 60
LOGIN_LOCKOUT_SECS = 900  # 15 minutes

def check_rate_limit(ip: str) -> tuple[bool, int]:
    """Returns (is_allowed, seconds_until_reset)."""
    now = time.time()
    attempts = _login_attempts[ip]
    # Remove old attempts outside the window
    attempts = [t for t in attempts if now - t < LOGIN_WINDOW_SECS]
    _login_attempts[ip] = attempts
    if len(attempts) >= LOGIN_MAX_ATTEMPTS:
        oldest = attempts[0]
        wait = int(LOGIN_LOCKOUT_SECS - (now - oldest))
        return False, max(wait, 0)
    return True, 0

def record_login_attempt(ip: str):
    _login_attempts[ip].append(time.time())

def clear_login_attempts(ip: str):
    _login_attempts.pop(ip, None)

def add_cors_headers(response):
    import os
    allowed = os.environ.get("ALLOWED_ORIGIN", "http://127.0.0.1:5000")
    response.headers["Access-Control-Allow-Origin"]  = allowed
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response
