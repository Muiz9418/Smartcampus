from flask import Blueprint, request
from extensions import ok, err, require_auth, current_user, db

bp = Blueprint("profile", __name__, url_prefix="/api/profile")

@bp.route("", methods=["GET"])
@require_auth()
def get_profile():
    return ok(current_user().safe_profile())

@bp.route("", methods=["POST"])
@require_auth()
def update_profile():
    body = request.get_json(force=True)
    u = current_user()

    if body.get("name"):
        u.name = body["name"]
        # update initials
        parts = u.name.split()
        u.initials = (parts[0][0] + parts[-1][0]).upper() if len(parts) >= 2 else u.name[:2].upper()

    if body.get("new_password"):
        if not u.check_password(body.get("current_password", "")):
            return err("Current password is incorrect.")
        if len(body["new_password"]) < 6:
            return err("Password must be at least 6 characters.")
        u.set_password(body["new_password"])

    db.session.commit()
    return ok(u.safe_profile())
