from functools import wraps
from flask import jsonify, session
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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

def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
    return response
