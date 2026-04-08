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

def find_user_by_identifier(identifier):
    """Find a user by matric number or staff ID."""
    return User.query.filter(
        db.or_(User.matric == identifier, User.staff_id == identifier)
    ).first()

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

@bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    from app.models.token import Token
    from app.utils.email import send_email
    body = request.get_json(force=True)
    identifier = (body.get("identifier") or "").strip()
    if not identifier:
        return err("Please enter your ID.")
    user = find_user_by_identifier(identifier)
    if not user:
        # Don't reveal if user exists
        return ok({"message": "If that ID exists, a reset link has been sent."})
    t = Token.create(user.id, "reset", hours=2)
    reset_url = f"http://localhost:5000/reset-password?token={t.token}"
    send_email(
        user.email,
        "SmartCampus - Password Reset",
        f"Dear {user.name},\n\nClick the link below to reset your password:\n{reset_url}\n\nThis link expires in 2 hours.\n\n- SmartCampus Team"
    )
    return ok({"message": "Reset link sent to your registered email."})


@bp.route("/reset-password", methods=["POST"])
def reset_password():
    from app.models.token import Token
    body = request.get_json(force=True)
    token_str   = (body.get("token") or "").strip()
    new_password = (body.get("password") or "").strip()
    if not token_str or not new_password:
        return err("Token and password are required.")
    if len(new_password) < 6:
        return err("Password must be at least 6 characters.")
    t = Token.query.filter_by(token=token_str, type="reset").first()
    if not t or not t.is_valid():
        return err("Invalid or expired reset link.", 400)
    user = User.query.get(t.user_id)
    if not user:
        return err("User not found.", 404)
    user.set_password(new_password)
    t.used = True
    db.session.commit()
    return ok({"message": "Password reset successfully. You can now log in."})


@bp.route("/send-verification", methods=["POST"])
@require_auth()
def send_verification():
    from app.models.token import Token
    from app.utils.email import send_email
    user = current_user()
    if user.verified:
        return ok({"message": "Already verified."})
    t = Token.create(user.id, "verify", hours=24)
    verify_url = f"http://localhost:5000/verify-email?token={t.token}"
    send_email(
        user.email,
        "SmartCampus - Verify Your Email",
        f"Dear {user.name},\n\nClick the link below to verify your email:\n{verify_url}\n\nThis link expires in 24 hours.\n\n- SmartCampus Team"
    )
    return ok({"message": "Verification email sent."})


@bp.route("/verify-email", methods=["POST"])
def verify_email():
    from app.models.token import Token
    body = request.get_json(force=True)
    token_str = (body.get("token") or "").strip()
    t = Token.query.filter_by(token=token_str, type="verify").first()
    if not t or not t.is_valid():
        return err("Invalid or expired verification link.", 400)
    user = User.query.get(t.user_id)
    if not user:
        return err("User not found.", 404)
    user.verified = True
    t.used = True
    db.session.commit()
    return ok({"message": "Email verified successfully!"})


@bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return ok({"message": "Logged out."})

@bp.route("/me", methods=["GET"])
@require_auth()
def me():
    return ok(current_user().to_dict())
