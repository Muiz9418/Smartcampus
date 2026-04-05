import re
from flask import Blueprint, request, session
from extensions import ok, err, require_auth, current_user, db
from app.models.user import User

bp = Blueprint("auth", __name__, url_prefix="/api/auth")

def _detect_role(identifier):
    if re.match(r'^\d{4}/[A-Z]+/\d+$', identifier, re.IGNORECASE):
        return "student"
    if re.match(r'^STF-', identifier, re.IGNORECASE):
        return "lecturer"
    if re.match(r'^ADM-', identifier, re.IGNORECASE):
        return "admin"
    return None

@bp.route("/login", methods=["POST"])
def login():
    body       = request.get_json(force=True)
    identifier = (body.get("identifier") or "").strip()
    password   = body.get("password", "")
    if not identifier or not password:
        return err("Please provide your ID and password.", 400)
    user = User.query.filter(
        db.or_(User.matric == identifier, User.staff_id == identifier)
    ).first()
    if not user or not user.check_password(password):
        return err("Invalid ID or password.", 401)
    session["user_email"] = user.email
    return ok(user.to_dict())

@bp.route("/signup", methods=["POST"])
def signup():
    body       = request.get_json(force=True)
    identifier = (body.get("identifier") or "").strip()
    name       = (body.get("name")       or "").strip()
    email      = (body.get("email")      or "").strip().lower()
    password   = body.get("password", "")
    department = (body.get("department") or "").strip()
    if not identifier or not name or not email or not password:
        return err("Please fill in all required fields.", 400)
    if len(password) < 6:
        return err("Password must be at least 6 characters.", 400)
    role = _detect_role(identifier)
    if not role:
        return err("ID format not recognised. Use matric (e.g. 2021/CS/042) or staff ID (e.g. STF-0041).", 400)
    if User.query.filter_by(email=email).first():
        return err("An account with that email already exists.", 409)
    if User.query.filter(
        db.or_(User.matric == identifier, User.staff_id == identifier)
    ).first():
        return err("An account with that ID already exists.", 409)
    initials = "".join(w[0].upper() for w in name.split()[:2])
    user = User(
        email=email, name=name, initials=initials,
        role=role, department=department, status="active",
    )
    if role == "student":
        user.matric = identifier
    else:
        user.staff_id = identifier
    user.set_password(password)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    session["user_email"] = user.email
    return ok(user.to_dict()), 201

@bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return ok({"message": "Logged out."})

@bp.route("/me", methods=["GET"])
@require_auth()
def me():
    return ok(current_user().to_dict())
