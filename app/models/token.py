from extensions import db
from datetime import datetime, timedelta
import secrets

class Token(db.Model):
    __tablename__ = "tokens"
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.String(36), db.ForeignKey("users.id"))
    token      = db.Column(db.String(100), unique=True)
    type       = db.Column(db.String(20))  # reset | verify
    expires_at = db.Column(db.String(30))
    used       = db.Column(db.Boolean, default=False)

    @staticmethod
    def create(user_id, token_type, hours=2):
        t = Token(
            user_id    = user_id,
            token      = secrets.token_urlsafe(32),
            type       = token_type,
            expires_at = (datetime.now() + timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M:%S"),
            used       = False,
        )
        db.session.add(t)
        db.session.commit()
        return t

    def is_valid(self):
        if self.used:
            return False
        expiry = datetime.strptime(self.expires_at, "%Y-%m-%d %H:%M:%S")
        return datetime.now() < expiry
