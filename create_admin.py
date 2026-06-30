"""
One-off CLI script to create an admin account.
Run manually whenever a new admin needs to be created — never exposed as an API route.

Usage:
    python create_admin.py
"""

from app import create_app
from extensions import db
from app.models.user import User

app = create_app()

with app.app_context():
    print("=== Create Admin Account ===")
    staff_id = input("Staff ID (must start with ADM-, e.g. ADM-0001): ").strip()
    name     = input("Full name: ").strip()
    email    = input("Email: ").strip().lower()
    password = input("Password (min 6 chars): ").strip()

    if not staff_id.upper().startswith("ADM-"):
        print("Error: Staff ID must start with 'ADM-'.")
        raise SystemExit(1)

    if len(password) < 6:
        print("Error: Password must be at least 6 characters.")
        raise SystemExit(1)

    if User.query.filter_by(email=email).first():
        print("Error: An account with that email already exists.")
        raise SystemExit(1)

    if User.query.filter_by(staff_id=staff_id).first():
        print("Error: An account with that Staff ID already exists.")
        raise SystemExit(1)

    initials = "".join(w[0].upper() for w in name.split()[:2])

    admin = User(
        email=email,
        name=name,
        initials=initials,
        role="admin",
        staff_id=staff_id,
        status="active",
    )
    admin.set_password(password)

    db.session.add(admin)
    db.session.commit()

    print(f"\nAdmin account created successfully: {email} ({staff_id})")
