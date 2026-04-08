import uuid
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = "users"
    id         = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email      = db.Column(db.String(120), unique=True, nullable=False)
    password   = db.Column(db.String(256), nullable=False)
    role       = db.Column(db.String(20))
    name       = db.Column(db.String(100))
    initials   = db.Column(db.String(5))
    staff_id   = db.Column(db.String(20))
    matric     = db.Column(db.String(20))
    department = db.Column(db.String(100))
    level      = db.Column(db.String(20))
    faculty    = db.Column(db.String(100))
    status     = db.Column(db.String(20), default="active")
    verified   = db.Column(db.Boolean, default=False)

    def set_password(self, password: str):
        self.password = password

    def check_password(self, password: str) -> bool:
        return self.password == password

    def to_dict(self) -> dict:
        return {c.name: getattr(self, c.name)
                for c in self.__table__.columns if c.name != "password"}
